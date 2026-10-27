# Mission 2 — Look at the data

**Mode:** with agent · **Time:** 20 minutes

Before you train a model, look at what it will learn from. The data is the
Kaggle competition's training set, `~/course/data/train.csv`: 2,029 real
Reddit comments, each with a rule and a label saying whether moderators found
it broke the rule.

> **Content warning.** These are real comments that moderators had to deal
> with: spam, sexual content, insults, violence. That is what moderation is.
> Read them as data.

Each row has these columns:

| Column | What it is |
|---|---|
| `row_id` | the row's number |
| `body` | the comment to judge |
| `rule` | the rule it is judged against: "No Advertising" or "No legal advice" |
| `subreddit` | the community it was posted in |
| `positive_example_1`, `_2` | two other comments that **break** the rule |
| `negative_example_1`, `_2` | two other comments that **follow** the rule |
| `rule_violation` | the label: 1 breaks the rule, 0 follows it |

---

## Steps

1. **Make your train and dev split:**

   ```
   cd ~/course/seminar_3
   python3 prepare_data.py
   ```

   It puts 401 comments aside as the **dev** split: the comments you measure
   your model on, today and in Session 4. The model never trains on them.
   Everyone's split is the same, so everyone's results can be compared.

2. **Read some rows:**

   ```
   python3 show.py --random 3
   python3 show.py 1505
   ```

3. **Answer five questions** about `train.csv`:

   ```
   cp ~/course/seminar_3/templates/m2.txt ~/s3/m2.txt
   nano ~/s3/m2.txt
   ```

   Questions 1 to 4 are counting, and this card is **with agent**. Ask
   OpenCode to write a short Python script that answers them. Then read the
   script, run it, and check that each answer makes sense. Two hints:

   - Python's built-in `csv` module reads the file: `python3 your_script.py`.
   - If the agent wants pandas, there is no need to install it:
     `uv run --with pandas python3 your_script.py`.

4. **Find three wrong labels** (question 5). Question 4 tells you that some
   comments appear several times with *different* labels: at least one of
   those labels must be wrong. Look for rows like that, or for anything else
   that looks mislabelled. Read each candidate with `python3 show.py ROW_ID`,
   and write down why you think its label is wrong.

---

## Check

```
cd ~/course/seminar_3
./check 2
```

---

## Two "why" questions

Be ready to answer these if your instructor asks:

1. `prepare_data.py` splits by comment text: a text that appears several
   times goes entirely into train or entirely into dev. What would go wrong
   if it split row by row?
2. Some labels are wrong. What does that do to the best score any model
   could reach on this data?

---

**Bonus:** which subreddits have the most comments? Does the share of
comments that break the rule differ between them?
