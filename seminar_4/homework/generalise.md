# Homework — A rule it never saw

**Mode:** at home, on your own · **Time:** about 20 minutes, most of it waiting

Kaggle's hidden test has four rules your model never trained on. You can
build the same situation yourself: train on one rule only, and see how the
model does on the other.

---

## Steps

1. **Train on the legal rule alone,** in tmux as in mission 1:

   ```
   tmux new -s home
   cd ~/course/seminar_4
   modal run train.py --only legal --epochs 2
   ```

   It trains only on your legal-advice comments, then scores your whole dev
   split, both rules. One rule is half your comments, so 2 epochs give the
   model as many training steps as one epoch on both rules: otherwise you
   would be comparing a model that trained half as long.

2. **Compare.** The result prints the AUC of each rule. Your mission 1 run
   trained on both rules:

   ```
   cd ~/course/seminar_4
   ./check generalise
   cat ~/s4/results/*.json | grep -A 3 auc_per_rule
   ```

3. **And the other way round,** if you have time: `--only advertising --epochs 2`.

---

## Check

```
cd ~/course/seminar_4
./check generalise
```

---

## Two "why" questions

1. How much worse is the model on the rule it never trained on? Is it still
   better than the untrained model (0.487)?
2. Which number from this experiment would have predicted your Kaggle score
   best: your mission 1 dev AUC, or this one?
