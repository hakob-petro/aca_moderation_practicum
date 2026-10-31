# Mission 2 — Build the gateway

**Mode:** with agent · **Time:** 30 minutes

The model scores text. Your gateway owns the application's policy and its
failure contract. A caller sends a rule and comment, and gets a score plus
`approve`, `review`, or `remove`.

1. **Open your starter:**

   ```bash
   cd ~/aca-work/deploy
   ls -a
   less app.py
   ```

   It already validates inputs, checks a separate gateway key, calls the model
   with a 15-second deadline, and writes a JSON log line. `/healthz` only says
   that the gateway is alive; Docker's repeated health checks must not wake a
   GPU. A warm model must be tested separately with a real comment.

2. **Ask your agent to fill three TODOs.** Start `opencode` here. Give it:

   > Read policy.py and compose.yml. Implement decide: below approve_below is
   > approve; at or above remove_at is remove; everything else is review.
   > Publish container port 8000 on 127.0.0.1 at ${PORT}. Set the restart policy
   > to unless-stopped. Change only these two files. Explain each change. Do
   > not read or print .env; it contains private keys.

   Review the changes. The equality cases matter: with today's defaults,
   exactly 0.30 means review, and exactly 0.80 means remove. The thresholds
   come from `.env`; do not hard-code them in the function.

3. **Build and start:**

   ```bash
   docker compose up --build -d
   docker compose ps
   docker compose logs --tail 10
   ```

   `Dockerfile` copies only code. Compose supplies the private settings when
   the container starts. A key is permission to use your service, not part of
   your model or your source code.

4. **Warm the model, then make the real check:**

   ```bash
   cd ~/course/seminar_5
   uv run client.py
   ./check 2
   ```

   A cold model may take longer than the gateway's deadline. A 504 is an
   honest timeout, not a reason to silently approve the comment. The direct
   client allows up to ten minutes for classroom warm-up.

5. **Open the API from your laptop.** On the server, `echo $((MYPORT+2))`
   prints your port. In another terminal **on your laptop**, replace `PORT`:

   ```bash
   ssh -N -L 8000:127.0.0.1:PORT ws
   ```

   Open http://localhost:8000/docs. The interactive API describes `/moderate`.
   To try it, enter `Bearer YOUR_GATEWAY_KEY` in the `authorization` header
   field, and a JSON body with `rule` and `comment`. Read the key locally in
   `nano ~/aca-work/deploy/.env`; close the editor after copying it. The model
   key stays between your gateway and Modal.

## Two “why” questions

1. Why are there two different API keys? Which service accepts each one?
2. Why can `/healthz` return 200 while `/moderate` returns 503 or 504?

**Bonus:** change the thresholds in `.env`, then run
`docker compose up -d --force-recreate`. Explain why the same model score can
now produce a different decision. Restore 0.30/0.80 before the class comparison.
