# Data

`train.csv` is the training set of the Kaggle competition
[Jigsaw – Agile Community Rules Classification](https://www.kaggle.com/competitions/jigsaw-agile-community-rules)
(2025): 2,029 Reddit comments, each judged against one of two rules. The
competition's rules list its data as **public domain**. This copy comes from
[a mirror on Hugging Face](https://huggingface.co/datasets/phucthaiv02/Jigsaw-Agile-Community-Rules-Classification)
and is identical to the competition's `train.csv`, byte for byte (the same
SHA-256).

The hidden test set, with four more rules, stays on Kaggle. You submit to it
in Session 4.

| Column | What it is |
|---|---|
| `row_id` | the row's number, 0 to 2028 |
| `body` | the comment to judge |
| `rule` | "No Advertising: …" or "No legal advice: …" |
| `subreddit` | the community it was posted in |
| `positive_example_1`, `positive_example_2` | two other comments that break the rule |
| `negative_example_1`, `negative_example_2` | two other comments that follow it |
| `rule_violation` | 1 if the comment breaks the rule, 0 if not |

These are real comments that moderators had to deal with: they include spam,
sexual content, insults and violence.
