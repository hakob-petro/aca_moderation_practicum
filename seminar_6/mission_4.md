# Mission 4 — Demo and shutdown

**Mode:** together · **Time:** 20 minutes

Six sessions ago you had an empty server. Now you have a fine-tuned model
behind an authenticated API, and a console with a memory and a decision log.
Show it, keep it, and stop what costs money.

1. **Demos.** Four or five volunteers, two minutes each, through their own
   tunnel: one comment through the console, one thing that works, one thing
   that broke and how you found out.

2. **The class table:**

   ```bash
   cd ~/course/seminar_6
   python3 report.py
   ```

   Which attacks slipped past the most services? What do they have in common?

3. **Commit the console.** As in Seminar 5, a local repository needs no
   GitHub account:

   ```bash
   cd ~/s6/console
   git init
   git add app.py decisions.py memory.py routing.py pipeline.py gateway_client.py \
     evaluate.py replay.py Dockerfile requirements.txt compose.yml \
     .dockerignore .gitignore .env.example data/cases.jsonl data/inbox.jsonl
   git diff --cached --stat
   git commit -m "Moderator console"
   ```

   `.env` must be absent from the commit. The two data files are public-domain
   course data; the image cannot be built without them. If Git asks who you
   are, set `git config user.name` and `user.email` as in Seminar 5's mission 4.

   The class server will be deleted after the course. To keep your work,
   push `~/s5/gateway` and `~/s6/console` to a private GitHub repository, or
   clone them onto your laptop: `git clone ws:s6/console`. Both copy only
   committed files, never `.env`.

4. **Stop your model:**

   ```bash
   modal app list
   modal app stop APP_ID
   ```

   Answer `y` to confirm. Stop only your own `aca-s5-…` app, using its ID
   from the list; on the class workspace you see everyone's. Your adapter
   snapshot stays in its volume: `modal deploy serve.py` brings the model back.
   Then stop the containers; the decision log stays on its volume:

   ```bash
   cd ~/s6/console && docker compose down
   cd ~/s5/gateway && docker compose down
   ```

5. **Check:**

   ```bash
   cd ~/course/seminar_6
   ./check 4
   ```

## Two “why” questions

1. Which parts of your service could a new server rebuild from git, and which
   would you have to bring separately?
2. Of everything you built, what would you change first before real users'
   comments went through it?
