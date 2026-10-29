# Mission 2 — Submit to Kaggle

**Mode:** by hand · **Time:** 35 minutes

The competition's real test set is hidden: you never see its comments or
their labels. So you do not send Kaggle predictions; you send a **notebook**
that makes them. Kaggle runs it on the hidden test, with the internet off,
and scores what it writes. Everything it needs must be on Kaggle already: the
model (Qwen3-0.6B is on Kaggle Models), the competition data, and your
adapter, which you upload as a private **dataset**.

You do it all from the class server, with the `kaggle` command. Do it now,
straight after training: Kaggle takes about 20 minutes to score a
submission, and you need the score in mission 4.

---

## Steps

1. **Connect the kaggle command to your account.** On the class server:

   ```
   uv tool install kaggle
   ```

   On your **laptop**, open https://www.kaggle.com/settings, find **API**,
   and click **Create New Token**. Copy the token it shows. Back on the
   server, paste it into a file of its own:

   ```
   mkdir -p ~/.kaggle
   nano ~/.kaggle/access_token
   chmod 600 ~/.kaggle/access_token
   kaggle config view
   ```

   `kaggle config view` should show your Kaggle username. The token is a
   password: never put it anywhere else.

2. **Check that you joined the competition:**

   ```
   kaggle competitions files jigsaw-agile-community-rules
   ```

   It lists three files. A "403" or "rules" error means you have not
   accepted the rules: on the competition page, **Late Submission**, then
   accept.

3. **Get your adapter and the notebook ready:**

   ```
   cd ~/course/seminar_4
   ./kaggle_prepare
   ```

   It takes your best run's adapter from your Modal volume and fills in two
   folders in `~/s4/kaggle`, each with the small JSON file Kaggle needs.
   Look at them:

   ```
   cat ~/s4/kaggle/adapter/dataset-metadata.json
   cat ~/s4/kaggle/notebook/kernel-metadata.json
   ```

   The second says what the notebook runs on: a GPU, no internet, and three
   inputs (the competition, the model, your adapter). Then read
   `~/s4/kaggle/notebook/submission.py`: find `add_lora`, which folds your
   adapter into the model, and the line that writes `submission.csv`.

4. **Upload your adapter** as a private dataset (the exact command was
   printed by `./kaggle_prepare`):

   ```
   kaggle datasets create -p ~/s4/kaggle/adapter
   kaggle datasets status YOUR_KAGGLE_NAME/aca-adapter
   ```

   Repeat the second command until it says `ready`.

5. **Push the notebook,** and wait for it to run on Kaggle's sample of 10
   test comments (about two minutes):

   ```
   kaggle kernels push -p ~/s4/kaggle/notebook
   kaggle kernels status YOUR_KAGGLE_NAME/aca-jigsaw-submission
   ```

   Note the **version** number `push` prints. Repeat `status` until it says
   `COMPLETE`. If it says `ERROR`, read why:

   ```
   kaggle kernels output YOUR_KAGGLE_NAME/aca-jigsaw-submission -p ~/s4/kaggle/output
   tail -20 ~/s4/kaggle/output/*.log
   ```

6. **Submit it:**

   ```
   kaggle competitions submit jigsaw-agile-community-rules -k YOUR_KAGGLE_NAME/aca-jigsaw-submission -v VERSION -f submission.csv -m "my first model"
   kaggle competitions submissions jigsaw-agile-community-rules | head -3
   ```

   Kaggle now runs your notebook again, on the hidden test. Your submission
   stays `PENDING` until it has scored it: go on with mission 3, and look
   again at the start of mission 4.

---

## Check

```
cd ~/course/seminar_4
./check 2
```

---

## Two "why" questions

Be ready to answer these if your instructor asks:

1. Why does the competition make you send a notebook instead of a file of
   predictions?
2. Your adapter is 20 MB, the model 1.5 GB. Why upload only the adapter?
