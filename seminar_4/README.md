# Seminar 4 — Train II: fine-tune and submit

Today you fine-tune your model, compare your run with the whole class, submit
it to the Kaggle competition, and find out how well it does on rules it has
never seen.

---

## Before you start

You need, from Seminar 3:

- **Modal working:** `modal profile current` answers, and Seminar 3's
  `./check 1` passes.
- **Your train/dev split:** `ls ~/s3/data` shows `train.jsonl` and
  `dev.jsonl`.

And, done at home after Seminar 3:

- **A Kaggle account** at https://www.kaggle.com, **verified with your
  phone** (Settings → Phone verification).
- **The competition joined:** on the
  [Jigsaw competition](https://www.kaggle.com/competitions/jigsaw-agile-community-rules)
  page, **Late Submission** → accept the rules.

Then get today's files:

```
ssh ws
cd ~/course && git pull
cd ~/course/seminar_4
```

---

## Missions

| # | Mission | Mode | Minutes |
|---|---|---|---|
| 1 | [Fine-tune](mission_1.md) | by hand | 35 |
| 2 | [Submit to Kaggle](mission_2.md) | by hand | 35 |
| – | Break | | 5 |
| 3 | [Read the results](mission_3.md) | with agent | 20 |
| 4 | [The honest number](mission_4.md) | by hand | 15 |

Each card ends with the command that checks your work, for example:

```
./check 1
```

It prints **PASS** or **FAIL** for each part, and a hint for anything that
failed. When everything passes, colour your cell on the board.

**Out of time?** Run `./catchup N` before mission N. Missions 2 and 3 need a
model trained in mission 1. Submit to Kaggle (mission 2) as early as you can:
it takes about 20 minutes to score, and mission 4 needs the score.
If it has not arrived by the end, finish mission 4 at home.

**Stuck for 10 minutes?** Put a sticky note on your laptop lid.

---

## Your files

Everything you make today goes into `~/s4`:

| File | Made by |
|---|---|
| `results/RUN.json`, `results/RUN_predictions.csv` | `modal run train.py`, mission 1 |
| the adapter, in your Modal volume `aca-models`, under `runs/RUN` | `modal run train.py`, mission 1 |
| `m3.txt` | you, mission 3 |
| `m4.txt` | you, mission 4 |

---

## You are done when

- `./check 1` to `./check 4` all pass
- your dev AUC and your Kaggle score are on the board

**Homework, at home:** [A rule it never saw](homework/generalise.md). Train on
one rule only, and see how the model does on the other. `./check generalise`
checks it.
