"""How the model judges a comment. Shared by score.py and modal_score.py.

The model is Qwen3-0.6B, not trained for this task at all. It reads a prompt
with the rule, two comments that break it, two that do not, and the comment to
judge, and is asked to answer Yes or No. We do not let it write an answer: we
look at how likely its very next word is "Yes" and how likely it is "No".

    score  = logit(Yes) - logit(No)      how much more the model leans to Yes
    P(Yes) = 1 / (1 + e^-score)          the same, as a probability
"""

import json
import math
import sys
import time
from pathlib import Path

MODEL = "Qwen/Qwen3-0.6B"
REVISION = "c1899de289a04d12100db370d81485cdf75e47ca"  # a fixed version of the weights

RULES = {
    "advertising": "No Advertising: Spam, referral links, unsolicited advertising, and promotional content are not allowed.",
    "legal": "No legal advice: Do not offer or request legal advice.",
}
SHORT_NAME = {text: name for name, text in RULES.items()}
SYSTEM = "You are a moderator of an online community. You decide whether a comment breaks the community's rule."

HERE = Path(__file__).resolve().parent
OUT = Path.home() / "s3"


# ---------- the prompt ----------

def build_chat(rule: str, comment: str, examples: dict | None = None, subreddit: str = "") -> list[dict]:
    """The conversation the model reads: the rule, example comments, and the comment to judge."""
    lines = []
    if subreddit:
        lines.append(f"Community: r/{subreddit}")
    lines.append(f"Rule: {rule}")
    if examples:
        lines += [
            "",
            "Comments that break the rule:",
            f"- {examples['positive_example_1']}",
            f"- {examples['positive_example_2']}",
            "",
            "Comments that follow the rule:",
            f"- {examples['negative_example_1']}",
            f"- {examples['negative_example_2']}",
        ]
    lines += [
        "",
        "Comment to judge:",
        comment,
        "",
        "Does the comment to judge break the rule? Answer Yes or No.",
    ]
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": "\n".join(lines)}]


# Example comments for students' own comments. The dev split uses each row's own
# examples, as the competition does; many of those are real spam and abuse.
EXAMPLES = {
    "advertising": {
        "positive_example_1": "Check out my online store, 50% off all sneakers this week: www.example-sneakers.com",
        "positive_example_2": "Earn $500 a day from home! Sign up with my referral link: bit.ly/abc123",
        "negative_example_1": "I bought these sneakers last year and the soles wore out in three months.",
        "negative_example_2": "Has anyone tried the new budget phones? Which one has the best camera?",
    },
    "legal": {
        "positive_example_1": "Take your landlord to small claims court. By law he has to return the deposit within 30 days.",
        "positive_example_2": "Don't sign anything. Tell the police you want a lawyer and say nothing else.",
        "negative_example_1": "My landlord finally fixed the heating after three weeks. What a relief.",
        "negative_example_2": "I watched a documentary about the Supreme Court last night. Fascinating.",
    },
}


def chat_for(rule_name: str, comment: str) -> list[dict]:
    """A known rule (advertising, legal) comes with example comments. Any other text is used as the rule, without examples."""
    key = rule_name.strip().lower()
    if key in RULES:
        return build_chat(RULES[key], comment, EXAMPLES[key])
    return build_chat(rule_name.strip(), comment)


def p_yes(score: float) -> float:
    return 1 / (1 + math.exp(-score))


# ---------- the model ----------

class Scorer:
    """Loads the model once, then scores many conversations. With adapter=PATH,
    it adds a LoRA adapter trained in Session 4 on top of the model."""

    def __init__(self, adapter: str | None = None):
        import os

        os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")  # no progress bars or warnings
        os.environ.setdefault("HF_HUB_VERBOSITY", "error")
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from transformers.utils import logging

        logging.disable_progress_bar()

        self.torch = torch
        if torch.cuda.is_available():
            # bfloat16 on GPUs built for it (L4, A10 and newer); float16 on older ones
            # (T4), which only emulate bfloat16, slowly.
            self.device = "cuda"
            dtype = torch.bfloat16 if torch.cuda.get_device_capability(0)[0] >= 8 else torch.float16
        elif torch.backends.mps.is_available():
            self.device, dtype = "mps", torch.float32
        else:
            self.device, dtype = "cpu", torch.float32
        self.batch_size = 32 if self.device == "cuda" else 8

        self.tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=REVISION)
        self.tokenizer.padding_side = "left"  # so that every prompt in a batch ends at the same position
        self.model = AutoModelForCausalLM.from_pretrained(MODEL, revision=REVISION, dtype=dtype).to(self.device)
        if adapter:
            from peft import PeftModel

            # Fold the adapter's small matrices into the model's own: same answers, faster.
            self.model = PeftModel.from_pretrained(self.model, adapter).merge_and_unload()
        self.model.eval()

        # "Yes" and "No" are each one token: one entry in the model's vocabulary.
        [self.yes] = self.tokenizer.encode("Yes", add_special_tokens=False)
        [self.no] = self.tokenizer.encode("No", add_special_tokens=False)

    def device_name(self) -> str:
        if self.device == "cuda":
            return self.torch.cuda.get_device_name(0)
        return {"mps": "Apple GPU", "cpu": "CPU"}[self.device]

    def prompt(self, chat: list[dict]) -> str:
        # enable_thinking=False: Qwen3 would otherwise first "think" out loud for
        # hundreds of words. We want its answer as the very next word.
        return self.tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True, enable_thinking=False)

    def score(self, chats: list[list[dict]]) -> list[float]:
        texts = [self.prompt(chat) for chat in chats]
        scores = []
        for i in range(0, len(texts), self.batch_size):
            batch = self.tokenizer(texts[i : i + self.batch_size], return_tensors="pt", padding=True).to(self.device)
            with self.torch.no_grad():
                # The model's scores for every possible next token, after the last prompt token.
                logits = self.model(**batch, logits_to_keep=1).logits[:, -1, :].float()
            scores += (logits[:, self.yes] - logits[:, self.no]).tolist()
        return scores


# ---------- what score.py and modal_score.py do ----------

def run(score, show_prompt, ran_on: str, comment: str = "", rule: str = "advertising",
        file: str = "", dev: bool = False, want_prompt: bool = False) -> None:
    """score(chats) -> scores and show_prompt(chat) -> text run the model, here or on Modal."""
    OUT.mkdir(exist_ok=True)

    if comment:
        chat = chat_for(rule, comment)
        if want_prompt:
            print("---- the prompt, exactly as the model reads it ----")
            print(show_prompt(chat))
            print("---- end of the prompt: the model's next token is its answer ----\n")
        [s] = score([chat])
        print(f"Rule:    {RULES.get(rule.strip().lower(), rule)}")
        print(f"Comment: {comment}")
        print(f"P(Yes) = {p_yes(s):.2f}   (score {s:+.2f})")

    elif file:
        items = []
        for line in Path(file).expanduser().read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            if "|" not in line:
                sys.exit(f"Each line must be:  rule | comment\nThis one is not:  {line}")
            rule_name, text = (part.strip() for part in line.split("|", 1))
            items.append((rule_name, text))
        if not items:
            sys.exit(f"No comments in {file}. Each line:  rule | comment")
        scores = score([chat_for(r, t) for r, t in items])
        with (OUT / "my_scores.tsv").open("w", encoding="utf-8") as f:
            f.write("rule\tp_yes\tscore\tcomment\n")
            for (r, t), s in zip(items, scores):
                f.write(f"{r}\t{p_yes(s):.4f}\t{s:.4f}\t{t}\n")
                print(f"P(Yes) {p_yes(s):.2f}  {r:<12} {t[:70]}")
        print(f"\nSaved to {OUT / 'my_scores.tsv'}")

    elif dev:
        sys.path.insert(0, str(HERE))
        from auc import column_averaged_auc

        dev_file = OUT / "data" / "dev.jsonl"
        if not dev_file.exists():
            sys.exit("No dev split yet. Run:  python3 prepare_data.py")
        rows = [json.loads(line) for line in dev_file.open(encoding="utf-8")]
        chats = [build_chat(r["rule"], r["body"], r, r["subreddit"]) for r in rows]

        print(f"Scoring {len(rows)} dev comments with {MODEL} on {ran_on}...")
        start = time.time()
        scores = score(chats)
        seconds = time.time() - start

        results = [
            {"row_id": r["row_id"], "rule": SHORT_NAME.get(r["rule"], r["rule"]), "label": r["rule_violation"], "score": s}
            for r, s in zip(rows, scores)
        ]
        mean, per_rule = column_averaged_auc(results)
        with (OUT / "baseline_predictions.csv").open("w", encoding="utf-8") as f:
            f.write("row_id,rule,label,score\n")
            for r in results:
                f.write(f"{r['row_id']},{r['rule']},{r['label']},{r['score']:.6f}\n")
        summary = {
            "model": MODEL,
            "revision": REVISION,
            "ran_on": ran_on,
            "comments": len(rows),
            "auc": round(mean, 4),
            "auc_per_rule": {name: round(v, 4) for name, v in per_rule.items()},
            "seconds": round(seconds, 1),
        }
        (OUT / "baseline.json").write_text(json.dumps(summary, indent=2) + "\n")

        for name, v in per_rule.items():
            print(f"  AUC {name:<12} {v:.3f}")
        print(f"  AUC averaged over the two rules, Kaggle's way: {mean:.3f}")
        print(f"\n{len(rows)} comments in {seconds:.0f} s. Saved to {OUT / 'baseline.json'}")

    else:
        print('Nothing to do. Try:  ./score --comment "Buy followers at example.com"')
