# Mission 4 — Make it permanent with Compose

**Mode:** by hand · **Time:** 30 minutes

Your Open WebUI runs, but only because you typed a long `docker run` command
once. **Docker Compose** describes it in a file, `compose.yml`, so anyone can
start it again with one command. You will also make it **restart by itself**,
and prove that your account and chats live in the **volume**, not in the
container.

---

## Steps

1. **Set it up.** Copy the template, give it your port, and open it:

   ```
   mkdir -p ~/s2/openwebui
   cp ~/course/seminar_2/openwebui/compose.yml ~/s2/openwebui/
   cd ~/s2/openwebui
   echo "PORT=$((MYPORT+1))" > .env
   cat .env
   nano compose.yml
   ```

   Compose reads `PORT` from `.env` by itself. Fill in the three `TODO`s.

2. **Throw away the container from mission 3**, but keep its volume:

   ```
   docker rm -f openwebui
   docker volume ls
   ```

   The container is gone. The volume `openwebui-data`, with your account and
   chats in it, is still there.

3. **Start it with Compose:**

   ```
   docker compose up -d
   docker compose ps
   ```

   If it complains, read the message: it names the line. Your tunnel from
   mission 3 uses the same port, so just reload http://localhost:3000. You are
   still logged in, and your chat is still there: it came from the volume.

4. **Take it down, and bring it back:**

   ```
   docker compose down
   docker compose up -d
   ```

   Reload the page. Still there.

5. **Restart your whole Docker:**

   ```
   systemctl --user restart docker
   sleep 15
   docker compose ps
   docker ps -a
   ```

   Open WebUI is back by itself, because of its restart policy. The `site`
   container from mission 2 did **not** come back: it had no restart policy.

---

## Check

```
cd ~/course/seminar_2
./check 4
```

---

## Two "why" questions

Be ready to answer these if your instructor asks:

1. You deleted the container from mission 3, yet your account and chats
   survived. Why?
2. Where is your OpenRouter key stored now? Why is that better than writing it
   into `compose.yml`?

---

**Bonus:** stop Open WebUI with `docker compose stop`, then restart Docker
again. Does it come back this time? Why not? (Look at what `unless-stopped`
means.)
