# Mission 4 — Rebuild from git

**Mode:** by hand · **Time:** 20 minutes

Your service is reproducible when committed code plus separately supplied
settings can start it again. Today you prove this in a fresh clone and a second
Compose project on the **same class server**. This is a recovery exercise; it
does not create a second VM or test a host failure.

1. **Commit the service to your private repo:**

   ```bash
   cd ~/aca-work
   git status --short
   git add deploy/app.py deploy/policy.py deploy/model_client.py deploy/scorer.py \
     deploy/Dockerfile deploy/requirements.txt deploy/compose.yml \
     deploy/.dockerignore deploy/.gitignore deploy/.env.example
   git diff --cached --stat
   git diff --cached
   git commit -m "Deploy my moderation gateway"
   git push
   ```

   Check the staged files before committing. `.env` must be absent. If git
   says there is nothing to commit, check `git log -1` and continue. Resolve
   any unrelated staged work separately; do not include it by accident.

2. **Warm the model, then rebuild:**

   ```bash
   cd ~/course/seminar_5
   uv run client.py
   python3 recover.py
   ```

   Read the script. It clones your committed repository into a new temporary
   folder, records the commit, supplies a private copy of the configuration,
   and runs `docker compose up --build` as a different project on your next
   port. It sends a real comment, then removes that deployment and its copied
   key file. Your original gateway keeps running.

   Cloning the local repo avoids another GitHub login during the drill. It
   proves committed source can be reused. Your `git push` is the separate step
   that puts a copy off the class server.

3. **Check both the evidence and the original:**

   ```bash
   cat ~/s5/recovery.json
   cd ~/aca-work/deploy
   docker compose ps
   cd ~/course/seminar_5
   ./check 4
   ```

   You should have `answered: true`, `removed: true`, and the tested commit.
   The original service should still answer. The recovery drill's temporary
   folder contains no edits that need saving: its source came from git.

4. **Finish the session:** stop your own Modal app as described in the README.
   Keep the gateway code and keys ready for Seminar 6. A stopped model will
   make the gateway return an error until you deploy it again.

## Two “why” questions

1. Which things came from git, and which had to be supplied separately?
2. What would you still need if the whole class server disappeared?

**Bonus:** on an instructor-provided second host, clone the same commit,
install Docker if needed, supply the keys privately, and start Compose. That
adds a real host change; do not claim today's same-host drill already tested it.
