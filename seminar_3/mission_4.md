# Mission 4 — Baseline AUC

**Mode:** by hand · **Time:** 25 minutes

How good is the untrained model? You score all 401 dev comments and measure
it the way the Kaggle competition does: with **AUC**. That number is your
**baseline**, the one to beat when you fine-tune the model in Session 4.

**AUC in one sentence:** pick a random comment that breaks the rule and a
random one that does not; AUC is the chance that the model gives the
breaking one the higher score. 1.0 is perfect, 0.5 is guessing.

AUC looks only at the **order** of the scores, not at a threshold. Whether a
moderator wants to remove everything above 0.9 or only above 0.99 is decided
later, in the product. Kaggle computes AUC for each rule separately and
averages the two.

---

## Steps

1. **AUC by hand,** on five comments:

   ```
   cp ~/course/seminar_3/templates/m4.txt ~/s3/m4.txt
   nano ~/s3/m4.txt
   ```

2. **Read how the code does it.** It is the same idea in twenty lines:

   ```
   cd ~/course/seminar_3
   cat auc.py
   ```

3. **Score the dev split:**

   ```
   ./score --dev
   ```

   It sends 401 prompts to the GPU in batches and prints the AUC of each rule
   and their average. It takes about half a minute; the GPU itself needs only
   about ten seconds of it.

4. **Look at the results:**

   ```
   cat ~/s3/baseline.json
   head ~/s3/baseline_predictions.csv
   ```

   **Write your AUC on the board.**

5. **Where it goes wrong.** The five comments that follow the rule but got the
   highest scores, then one of them in full:

   ```
   sort -t, -k4 -g -r ~/s3/baseline_predictions.csv | awk -F, '$3 == 0' | head -5
   python3 show.py ROW_ID
   ```

   Is the model wrong, or the label?

---

## Check

```
cd ~/course/seminar_3
./check 4
```

---

## Two "why" questions

Be ready to answer these if your instructor asks:

1. Why does the competition use AUC, not accuracy (the share of comments the
   model gets right)?
2. The model leans towards "Yes" for most comments. Why does that, on its
   own, not make its AUC worse?

---

**Bonus:** one rule's AUC is lower than the other's. Read three of that rule's
comments from step 5, the ones labelled "follows the rule" with the highest
scores. What do they have in common, and what does that tell you about how
the labels were made?
