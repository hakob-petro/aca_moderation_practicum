# /// script
# requires-python = ">=3.10"
# dependencies = ["torch==2.14.1", "transformers==5.20.2"]
# ///
"""Score comments on this machine's GPU (or, slowly, its CPU).

    uv run score.py --comment "Buy followers cheap at example.com"
    uv run score.py --comment "Can my landlord keep my deposit?" --rule legal
    uv run score.py --file ~/s3/my_comments.txt
    uv run score.py --dev

The same as modal_score.py, which runs it on a Modal GPU instead. ./score
picks the right one for you. How the model judges a comment: scorer.py.
"""

import argparse

import scorer


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--comment", default="", help="one comment to judge")
    p.add_argument("--rule", default="advertising", help="advertising, legal, or the full text of another rule")
    p.add_argument("--file", default="", help="a file with one 'rule | comment' per line")
    p.add_argument("--dev", action="store_true", help="score the whole dev split and compute the AUC")
    p.add_argument("--show-prompt", action="store_true", help="also print the prompt the model reads")
    args = p.parse_args()

    model = scorer.Scorer()
    scorer.run(
        model.score,
        model.prompt,
        ran_on=f"this machine ({model.device_name()})",
        comment=args.comment,
        rule=args.rule,
        file=args.file,
        dev=args.dev,
        want_prompt=args.show_prompt,
    )


if __name__ == "__main__":
    main()
