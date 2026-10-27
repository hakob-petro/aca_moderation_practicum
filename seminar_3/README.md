# Seminar 3 — Train I: data and baseline

Today you run code on a cloud GPU, look critically at the data your model
will learn from, see how a language model turns a question into a
probability, and measure how good the untrained model is. That number is
your **baseline**: in Session 4 you fine-tune the model to beat it.

---

## Before you start

Your GPU work runs on **Modal**, a cloud that rents you a GPU for exactly as
long as your code runs.

- **Make a free account** at https://modal.com/signup (sign in with GitHub).
- **Add a payment method:** Modal asks for one before it runs anything on a
  GPU, but charges nothing while you stay within the free $30 a month.
- **Set the spend limit to $0** in **Settings** → **Usage & Billing**, so
  that Modal can never charge you. Today uses a few cents of the free credit.

**No card, or you would rather not add one?** Tell your instructor before
the session. You will use the class's Modal account instead, and skip one
step of mission 1.

Then get today's files:

```
ssh ws
cd ~/course && git pull
cd ~/course/seminar_3
```

Mission 2 is done **with agent**. If OpenCode is not set up on this server
yet, do [Seminar 1's mission 4](../seminar_1/mission_4.md) at the start of
mission 2.

---

## Missions

| # | Mission | Mode | Minutes |
|---|---|---|---|
| 1 | [Hello, GPU](mission_1.md) | by hand | 25 |
| 2 | [Look at the data](mission_2.md) | with agent | 20 |
| – | Break | | 5 |
| 3 | [How the model answers](mission_3.md) | by hand | 35 |
| 4 | [Baseline AUC](mission_4.md) | by hand | 25 |

Each card ends with the command that checks your work, for example:

```
./check 1
```

It prints **PASS** or **FAIL** for each part, and a hint for anything that
failed. When everything passes, colour your cell on the board.

**Out of time?** Run `./catchup N` before mission N. Missions 3 and 4 need
mission 1's GPU, and mission 4 needs mission 2's data split, which
`./catchup 4` makes for you.

**Stuck for 10 minutes?** Put a sticky note on your laptop lid.

**By hand** means you type every command yourself. You may ask OpenCode to
explain an error, but not to do the mission. **With agent** means OpenCode may
do the work, but you must be able to answer the card's two "why" questions.

---

## Your files

Everything you make today goes into `~/s3`:

| File | Made by |
|---|---|
| `hello.txt` | mission 1 |
| `data/train.jsonl`, `data/dev.jsonl` | `prepare_data.py`, mission 2 |
| `m2.txt` | you, mission 2 |
| `m3.txt`, `my_comments.txt`, `my_scores.tsv` | you, and `./score --file`, mission 3 |
| `m4.txt` | you, mission 4 |
| `baseline.json`, `baseline_predictions.csv` | `./score --dev`, mission 4 |

---

## You are done when

- `./check 1` to `./check 4` all pass
- your baseline AUC is on the board

Anything you did not finish, finish at home before the next session: each
mission's `./check` still works.

**Homework, at home:** [A frontier baseline](homework/frontier.md). How does
one of Google's big Gemini models do on 100 of the same dev comments, with no
training? `./check frontier` checks it.

**Before Session 4, at home:** make a Kaggle account at https://www.kaggle.com,
verify it with your phone (Settings → Phone verification), and join the
[Jigsaw competition](https://www.kaggle.com/competitions/jigsaw-agile-community-rules)
(**Late Submission** → accept the rules). Phone verification can take a day.
