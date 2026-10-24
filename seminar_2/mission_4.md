# Mission 4 — Compose, a crash and a restart

**Mode:** by hand · **Time:** 30 minutes

Typing long `docker run` commands does not scale. **Docker Compose** describes an
app in one file, `compose.yml`, and starts it with one command. Today's app counts
visits and keeps the count in a **volume**, so the count survives the container
being thrown away. And it **restarts itself** when it crashes.

---

## Steps

1. **Set it up.** Copy the app, give it your port, and open the file:

   ```
   mkdir -p ~/s2
   cp -r ~/course/seminar_2/counter ~/s2/counter
   cd ~/s2/counter
   echo "PORT=$((MYPORT+2))" > .env
   cat .env
   nano compose.yml
   ```

   Compose reads `PORT` from `.env` by itself. Fill in the three `TODO`s in
   `compose.yml`, then start it:

   ```
   docker compose up -d --build
   ```

   If it complains, read the message: it names the line.

2. **Use it.** Visit a few times:

   ```
   curl localhost:$((MYPORT+2))
   curl localhost:$((MYPORT+2))
   curl localhost:$((MYPORT+2))
   ```

3. **Crash it.**

   ```
   curl localhost:$((MYPORT+2))/crash
   docker compose ps
   curl localhost:$((MYPORT+2))
   ```

   `docker compose ps` says it has been up only a few seconds: it came back by
   itself. And the count went on where it was.

4. **Throw it away, and restart Docker itself.**

   ```
   docker compose down
   docker compose up -d
   curl localhost:$((MYPORT+2))
   ```

   `down` deletes the container. The count is still there: it lives in the
   volume, not in the container. Now restart your whole Docker:

   ```
   systemctl --user restart docker
   sleep 10
   docker compose ps
   curl localhost:$((MYPORT+2))
   ```

   It is back by itself, because of its restart policy. Now look at all your
   containers:

   ```
   docker ps -a
   ```

   `site` and `fixed` from missions 2 and 3 did **not** come back: they had no
   restart policy. Start them again with `docker start site fixed` if you want
   them.

5. **Open it to the internet, then close it again.** Only if your instructor
   says the server's firewall is open for your ports.
   - In `compose.yml`, change `"127.0.0.1:${PORT}:8000"` to `"${PORT}:8000"`,
     then `docker compose up -d`.
   - Ask a neighbour to open `http://SERVER-IP:YOUR-PORT` in **their laptop's**
     browser. Your app is now on the internet.
   - Put `127.0.0.1:` back, then `docker compose up -d`. Your neighbour's
     browser can no longer reach it.
   - Now ask your neighbour to run `curl localhost:YOUR-PORT` **on the server**.
     It still works. 127.0.0.1 hides a port from the internet, not from other
     people on the same server.

---

## Check

```
cd ~/course/seminar_2
./check 4
```

---

## Two "why" questions

Be ready to answer these if your instructor asks:

1. After `docker compose down`, the container was gone. Why was the count still
   there?
2. On a shared server, what is the difference between publishing on
   `127.0.0.1` and publishing on every address?

---

**Bonus:** `docker volume ls`, then `docker volume inspect counter_counter-data`.
Where on the server does your count actually live?
