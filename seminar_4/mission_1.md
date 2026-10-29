# Mission 1 — Fine-tune

**Mode:** by hand · **Time:** 35 minutes

In Seminar 3 the untrained model scored AUC 0.487: a coin flip. Today you
teach it the task. You show it each of your 1,628 training comments, with
its prompt and the right answer ("Yes" or "No"), and nudge it, step by step,
to make the right answer likelier. Then you score your dev split again.

**LoRA.** Changing all 596 million numbers of the model would need a lot of
GPU memory and give you a 1.2 GB file per experiment. **LoRA** (low-rank
adaptation) leaves them frozen and learns a small pair of extra matrices
next to each layer instead: 5 million numbers, **0.8%** of the model, saved
as a **20 MB** file called an **adapter**. The model plus your adapter is
your fine-tuned model.

**ms-swift** is the training tool: one command, `swift sft`, with the model,
the data and the settings. `train.py` runs it for you on a Modal GPU.

**Your setting.** Everyone trains with a different combination of
**learning rate** (how big each nudge is), **epochs** (how many times the
model sees each comment) and **data** (all of your training comments, or
half). In mission 2 the class compares them.

---

## Steps

1. **Get today's files:**

   ```
   ssh ws
   cd ~/course && git pull
   ls ~/s3/data
   ```

   You need `train.jsonl` and `dev.jsonl` from Seminar 3. Missing? Run
   `python3 ~/course/seminar_3/prepare_data.py`.

2. **Start tmux.** Training takes 4 to 8 minutes. If your laptop sleeps or
   your Wi-Fi drops, your SSH connection ends and everything running in it
   stops, including the training. **tmux** keeps a terminal running on the
   server even when you are not connected to it.

   ```
   tmux new -s train
   ```

   The bottom line turns green: you are inside tmux.

3. **Train:**

   ```
   cd ~/course/seminar_4
   modal run train.py
   ```

   Read what it prints. First your setting, then the exact `swift sft`
   command it runs, then a line every 10 training steps. Watch `loss`
   (how wrong the model still is: it should go down) and `remaining_time`.

4. **Leave tmux running.** Press **Ctrl+b**, let go, then press **d**
   ("detach"). You are back in your normal terminal, and the training goes
   on without you. See it is still there:

   ```
   tmux ls
   ```

   You could close your laptop now. To go back in:

   ```
   tmux attach -t train
   ```

5. **While it trains,** read `train.py` (`less train.py`, q to quit): find
   the `swift sft` command and the lines that turn a comment into a
   training conversation.

6. **When it finishes,** it prints the AUC of each rule and their average,
   and saves everything:

   ```
   ls ~/s4/results
   modal volume ls aca-models runs
   ```

   The JSON file is your result; the adapter is in your Modal volume. Leave
   tmux with `exit` when you are done with it. Then go straight on to
   mission 2: the sooner you submit to Kaggle, the sooner you get your score.

---

## Check

```
cd ~/course/seminar_4
./check 1
```

---

## Two "why" questions

Be ready to answer these if your instructor asks:

1. Your laptop slept for two minutes during training, yet the training
   finished. Why?
2. Training changed only 0.8% of the model's numbers. Why was that enough to
   turn a coin flip into a useful moderator?

---

**Bonus:** train a second setting in a second tmux window: **Ctrl+b** then
**c** opens one; **Ctrl+b** then **n** switches between them. For example
`modal run train.py --epochs 2`, or `--lr 2e-4 --data half`.
