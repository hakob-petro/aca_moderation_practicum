# Mission 3 — How the model answers

**Mode:** by hand · **Time:** 35 minutes

Your model is **Qwen3-0.6B**, a small language model, not trained for this
task at all. Today you open it up yourself with **transformers**, the Python
library almost every language-model project uses, and follow one comment from
text to probability. Then you score comments of your own.

**The prompt.** For every comment, the model reads a short conversation:

```
system:     You are a moderator of an online community. ...
user:       Rule: No legal advice: Do not offer or request legal advice.
            Comments that break the rule:  (two examples)
            Comments that follow the rule: (two examples)
            Comment to judge: Can my landlord keep my deposit?
            Does the comment to judge break the rule? Answer Yes or No.
assistant:  <think> </think>        <- thinking is switched off
            ...the next word is the answer
```

**The score.** We do not let the model write its answer. For every possible
next word, a language model computes a number called a **logit**: the higher
it is, the likelier that word. We read two of them:

```
score  = logit("Yes") - logit("No")       how much more the model leans to Yes
P(Yes) = 1 / (1 + e^-score)               the same, as a probability from 0 to 1
```

---

## Steps

1. **Open a Python session on a GPU.** On the class server:

   ```
   mkdir -p ~/s3 && cp ~/course/seminar_3/templates/m3.txt ~/s3/m3.txt
   cd ~/course/seminar_3
   modal shell explore.py
   ```

   The prompt changes: you are now on a Modal machine with a T4 GPU,
   PyTorch and transformers. **It is billed while it is open**, so leave it
   when you are done (step 7). Start Python:

   ```
   python3
   ```

   Open a **second** terminal on your laptop, `ssh ws`, and
   `nano ~/s3/m3.txt` there: write your answers in it as you go.

2. **Text becomes tokens.** Type each line, one at a time, and read what it
   prints:

   ```python
   from transformers import AutoTokenizer
   tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
   tok.tokenize("Get 1000 Instagram followers for $5")
   tok.encode("Get 1000 Instagram followers for $5")
   ```

   A model reads **tokens**, pieces of text with a number each. `Ġ` marks a
   space in front of the piece. How many tokens is the sentence?
   (`tokens_in_sentence`)

   ```python
   tok.encode("Yes")
   tok.encode(" Yes")
   tok.encode("No")
   ```

   Write down the three numbers (`yes_id`, `space_yes_id`, `no_id`). To the
   model, "Yes" and " Yes" are two different words.

3. **The conversation becomes one text:**

   ```python
   import scorer
   chat = scorer.chat_for("legal", "Can my landlord keep my deposit?")
   print(tok.apply_chat_template(chat, tokenize=False, add_generation_prompt=True, enable_thinking=False))
   ```

   This is exactly what `./score` sends to the model. Run the same line with
   `enable_thinking=True`: what is missing at the end?

4. **One pass through the model:**

   ```python
   import torch
   from transformers import AutoModelForCausalLM
   model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-0.6B", dtype=torch.float16).to("cuda")
   inputs = tok.apply_chat_template(chat, add_generation_prompt=True, enable_thinking=False, return_tensors="pt", return_dict=True).to("cuda")
   with torch.no_grad():
       logits = model(**inputs).logits

   logits.shape
   ```

   Press Enter twice after the `with` line. `float16` stores each of the
   model's 0.6 billion numbers in two bytes: 1.2 GB of the GPU's 16.
   `logits.shape` is (1, tokens in the prompt, words in the vocabulary): a
   score for every possible next word, after every position. Write it down
   (`logits_shape`).

5. **The next word.** The scores after the last position, as probabilities,
   and the five likeliest words:

   ```python
   last = logits[0, -1]
   probs = torch.softmax(last.float(), dim=-1)
   top = torch.topk(probs, 5)
   for p, i in zip(top.values, top.indices):
       print(f"{p:.3f}  {tok.decode(i)!r}")
   ```

   Press Enter twice after the `print` line. One of the five is neither Yes
   nor No. That is why we compare only those two.

6. **Your turn: P(Yes).** With `last` and your ids from step 2, compute the
   score and P(Yes) yourself: two lines. Hints: `last[9999]` is the logit of
   token 9999, and `torch.sigmoid(x)` computes `1 / (1 + e^-x)`. Write P(Yes)
   with two decimals (`p_yes_landlord`).

7. **Leave the GPU:** `exit()` leaves Python, then `exit` leaves the shell and
   stops the machine. Back on the class server, check that `./score` agrees
   with you:

   ```
   ./score --rule legal --comment 'Can my landlord keep my deposit?'
   ```

   Use **single quotes** around comments. Inside double quotes the shell
   reads `$5` as a variable and removes it.

8. **Your own comments.** Write at least five, for both rules, and score them:

   ```
   cp ~/course/seminar_3/templates/my_comments.txt ~/s3/
   nano ~/s3/my_comments.txt
   ./score --file ~/s3/my_comments.txt
   ```

   Make some of them tricky: recommending a product you honestly like, a link
   to Wikipedia, asking whether something is legal, the story of your own
   court case. Which ones does the model get wrong?

---

## Check

```
cd ~/course/seminar_3
./check 3
```

---

## Two "why" questions

Be ready to answer these if your instructor asks:

1. Why do we read the probability of the next word, instead of letting the
   model write its answer and checking whether it says "Yes"?
2. Qwen3 normally "thinks" out loud before it answers. Why is that switched
   off here?

---

**Bonus:** the Kaggle test set has rules the model never saw. Make up one of
your own:

```
./score --rule 'No politics: Do not discuss elections or political parties.' --comment 'Everyone should vote green next week.'
```
