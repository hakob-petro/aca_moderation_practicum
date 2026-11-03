# Mission 4 — Rebuild from git

**Mode:** by hand · **Time:** 20 minutes

Your service is reproducible when committed code plus separately supplied
settings can start it again. Today you prove this in a fresh clone and a second
Compose project on the **same class server**. This is a recovery exercise; it
does not create a second VM or test a host failure.

1. **Create a local Git repository and commit the service:**

   Git records a snapshot of your source files on this server. This step needs
   no GitHub account, login, or remote repository.

   ```bash
   cd ~/s5/gateway
   git init
   git status --short
   git add app.py policy.py model_client.py scorer.py \
     Dockerfile requirements.txt compose.yml \
     .dockerignore .gitignore .env.example
   git diff --cached --stat
   git diff --cached
   git commit -m "Deploy my moderation gateway"
   ```

   Check the staged files before committing. `.env` must be absent. If git
   says there is nothing to commit, check `git log -1` and continue. Resolve
   any unrelated staged work separately; do not include it by accident.

   If Git reports **Author identity unknown**, set your name and email for
   this repository, then repeat the commit command:

   ```bash
   git config user.name "Your Name"
   git config user.email "you@example.com"
   git commit -m "Deploy my moderation gateway"
   ```

   Replace the example name and email with yours. These identify the author
   of a commit; they do not log you into any service.

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

   The clone comes directly from your local repository. This proves committed
   source can be reused. Both copies are on the same server, so this exercise
   does not give you an off-server backup.

3. **Check both the evidence and the original:**

   ```bash
   cat ~/s5/recovery.json
   cd ~/s5/gateway
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

**Optional, after class:** push your source code to your own private GitHub
repository to keep an off-server copy. No mission check requires this. Keep
`.env` and API keys out of Git.
