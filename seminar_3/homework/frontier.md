# Homework — A frontier baseline

**Mode:** at home, on your own · **Time:** about 30 minutes, most of it waiting

Your untrained 0.6B model scored about 0.5: no better than guessing. How do
the big models do, with no training at all? You ask one of Google's Gemini
models, through the AI Studio key you made in Seminar 1, about 100 dev
comments (50 for each rule), and compute its AUC the same way.

The question is the same as your model's, with one difference: Gemini is
asked for a number from 0 to 100 instead of Yes or No, because AI Studio does
not show the probabilities of the next word. AUC needs only the order of the
scores, so a number works just as well.

---

## Steps

1. **Your key.** Find it again at https://aistudio.google.com/apikey. Put it
   in this terminal only; it is not saved anywhere:

   ```
   cd ~/course/seminar_3
   export AI_KEY=your-key
   ```

2. **Pick a model.** List the ones your key can use, and choose a "flash"
   model: fast, and with a generous free tier.

   ```
   python3 frontier.py --list-models
   ```

3. **Score the 100 comments:**

   ```
   python3 frontier.py --model THE_MODEL_NAME
   ```

   It waits a few seconds between comments, to stay within the free tier's
   limits, so this takes about ten minutes. Some models' free tiers allow only
   a few dozen requests a day: if it stops with a "rate-limited" message (or
   you press Ctrl+C), run the same command again later, or the next day, or
   with another model. The comments already answered are kept.

4. **Compare** your 0.6B baseline with the frontier model:

   ```
   cat ~/s3/baseline.json ~/s3/frontier.json
   ```

---

## Check

```
cd ~/course/seminar_3
./check frontier
```

---

## Two "why" questions

1. The big model probably scores much higher. So why would anyone fine-tune
   a small model instead of calling the big one?
2. Your 0.6B baseline was measured on 401 comments, this one on 100. Why
   does that make the comparison less certain?

---

**Bonus:** the same 100 comments with a free model on OpenRouter, with your
OpenRouter key from Seminar 2:

```
export AI_KEY=your-openrouter-key
python3 frontier.py --base-url https://openrouter.ai/api/v1 --model SOME_MODEL:free --wait 4
```

OpenRouter's free models allow about 50 requests a day, so this takes two
days. Is a free open model better or worse than Gemini?
