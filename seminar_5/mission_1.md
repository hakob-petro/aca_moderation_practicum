# Mission 1 — Serve your model

**Mode:** by hand · **Time:** 25 minutes

A training job ends. A deployed model keeps an address where another program
can call it. Modal starts a GPU when a request arrives and can release it when
traffic stops. The wait to load the model is a **cold start**.

1. **Prepare your adapter and keys:**

   ```bash
   cd ~/course/seminar_5
   ./prepare
   ```

   It selects your highest dev-AUC run, copies its adapter to a separate Modal
   volume, records both files' SHA-256 hashes, and creates two random API keys.
   This is convenient run selection, not evidence that it will generalise best.
   To select a particular run on the first setup: `./prepare --run RUN_NAME`.
   Re-running preparation keeps your edits and keys.

   Students sharing the class Modal account: use your own Linux username.
   The app and snapshot names include it. Ask the instructor which Seminar 4
   run to copy if your old run path was shared with somebody else.

2. **Deploy:**

   ```bash
   modal deploy serve.py
   ```

   Read `serve.py` while it builds. Find the GPU, the adapter path,
   `max_containers=1`, and `scaledown_window=60`. `base` and `moderator` share
   one base model in GPU memory; the latter applies your LoRA adapter.

   Copy the HTTPS endpoint printed next to `model`, then save it:

   ```bash
   python3 configure.py https://YOUR-PRINTED-MODAL-URL
   ```

   Use your actual URL. The helper appends `/v1`, the API path, and keeps the
   keys private. It does not print them.

3. **Call both models:**

   ```bash
   uv run client.py --model base
   uv run client.py --model moderator
   uv run client.py --model moderator --rule legal --comment "My landlord fixed the heating yesterday."
   ```

   The first call can take several minutes. Later calls should be faster.
   Record the two scores and timings. A single comment does not measure AUC.
   Read `client.py` and `gateway/model_client.py`: the client asks for one
   token, the same non-thinking chat template as Seminar 3, and both candidate
   log probabilities. The sampled word itself is not used as the score.

4. **Check the endpoint and its key:**

   ```bash
   ./check 1
   ```

   The check makes real calls to `/v1/models` with a good, missing, and bad key.
   A missing key must return HTTP 401, not a model answer. Keep `.env` and
   `model.env` out of git, screenshots, and agent prompts.

5. **Observe a cold start.** While you read mission 2, leave the model idle.
   Watch its container count reach zero in Modal, then run `uv run client.py`
   again. Compare timings. Sixty idle seconds is the scale-down setting, not
   a promise that the next cold start takes sixty seconds.

## Two “why” questions

1. Why can the same SDK call your Qwen model without an OpenAI account?
2. Why does an endpoint that costs less while idle sometimes answer slowly?

**Bonus:** inspect the response fields in `read_score()`. Why does subtracting
two log probabilities give the same difference as subtracting their logits?

If the GPU is unavailable, use `./catchup 2` and start the gateway edits while
the instructor helps. Do not deploy repeatedly under different app names.
