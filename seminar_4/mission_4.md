# Mission 4 — The honest number

**Mode:** by hand · **Time:** 15 minutes

You now have two numbers for the same model: your **dev AUC**, measured on
401 comments you set aside, and your **Kaggle score**, measured by Kaggle on
comments you have never seen. They are not the same. Explaining why is the
most useful thing you will do today.

What differs between the two:

| | Your dev split | Kaggle's hidden test |
|---|---|---|
| Rules | the same 2 as your training data | those 2, and **4 more** your model never saw |
| Comments | from the same 2,029 as your training data | new ones |

---

## Steps

1. **Your two numbers:**

   ```
   cat /srv/aca/results/$USER.json
   ```

   (That is the run you shared in mission 3.)

   Your Kaggle score is on the competition's **Submissions** page, or:

   ```
   kaggle competitions submissions jigsaw-agile-community-rules | head -5
   ```

2. **Explain the gap** in two sentences, then write it down with both
   numbers:

   ```
   cp ~/course/seminar_4/templates/m4.txt ~/s4/m4.txt
   nano ~/s4/m4.txt
   ```

3. **Put your Kaggle score on the board,** next to your dev AUC.

---

## Check

```
cd ~/course/seminar_4
./check 4
```

---

## Two "why" questions

Be ready to answer these if your instructor asks:

1. A new community wants your moderator for its own rules. Which of your two
   numbers do you tell them, and why?
2. How could you build a dev split that warns you about new rules before
   Kaggle does? (The homework tries it.)
