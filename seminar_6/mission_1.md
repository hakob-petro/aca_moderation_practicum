# Mission 1 — Console and decision log

**Mode:** with agent · **Time:** 35 minutes

The gateway decides; a person is responsible. A moderator needs the comments
the model is unsure about, a way to correct it, and a record of who decided
what. Container logs rotate and disappear with the container; the decision log
is a database kept on purpose.

1. **Prepare the console:**

   ```bash
   cd ~/course/seminar_6
   ./prepare
   ```

   It copies the starter to `~/s6/console`, finds the Docker network of your
   running gateway, copies the training comments (memory) and dev comments
   (inbox), and writes `.env` with your gateway key. It does not print the
   key. If it says your gateway is not running, start it as the README says.

2. **Read the starter:**

   ```bash
   cd ~/s6/console
   ls -a
   less app.py
   less decisions.py
   ```

   `app.py` is the console: Streamlit runs it again after every click, so
   everything lasting is in the database. Read the `decisions` table in
   `decisions.py`: what the model said (`model_decision`), what the console
   did (`routed`), and what was finally done (`final`, `decided_by`).

3. **Ask your agent to fill the TODOs.** Start `opencode` here. Give it:

   > Read decisions.py and compose.yml. In decisions.py, implement record and
   > set_final exactly as their docstrings say. Use ? placeholders for every
   > value in SQL, never string formatting. In compose.yml: publish container
   > port 8501 on 127.0.0.1 at ${PORT}; keep /data in a named volume called
   > decisions; mark the network gateway as external, with the name
   > ${GATEWAY_NETWORK}. Change only these two files. Explain each change.
   > Do not read or print .env; it contains a private key.

   Review the changes. An override must never overwrite `model_decision`:
   the log shows both what the model said and what a person decided.

4. **Build and start:**

   ```bash
   docker compose up --build -d
   docker compose ps
   docker compose logs --tail 10
   ```

   The first build takes about a minute: it installs Streamlit and downloads
   the 30 MB embedding model into the image.

5. **Open the console from your laptop.** On the server, `echo $((MYPORT+4))`
   prints your port. In another terminal **on your laptop**, replace `PORT`:

   ```bash
   ssh -N -L 8501:127.0.0.1:PORT ws
   ```

   Open http://localhost:8501.

6. **Moderate.** In **Inbox**, press **Moderate the next 5** twice. Each
   comment goes through your gateway: `approve` and `remove` are final at
   once, `review` waits in the **Review queue**. Decide every comment there.
   Then, in **Decision log**, find an automatic decision you disagree with
   and override it. Try **Try a comment** with one of your own.

7. **Check:**

   ```bash
   cd ~/course/seminar_6
   ./check 1
   ```

   The check tests your two functions, inspects the container, reads the
   database, then runs `docker compose down` and `up` and reads it again. The
   log survives because it lives on the volume, not in the container.

## Two “why” questions

1. Why does the log keep the model's decision when a person overrides it?
2. Why is the decision log a database on a volume and not the gateway's
   container logs?

**Bonus:** this database stores the comments. Who should be able to read it,
and for how long should it keep them, before real users' comments go in?
