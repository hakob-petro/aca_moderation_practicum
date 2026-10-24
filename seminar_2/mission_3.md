# Mission 3 — Your own Open WebUI

**Mode:** by hand · **Time:** 30 minutes

**Open WebUI** is a chat interface, like ChatGPT's, that you run yourself and
connect to any AI model provider. Today you run your own copy in Docker on the
server, connect it to a free model on **OpenRouter**, and use it from your
laptop's browser through an SSH tunnel.

Your port for Open WebUI is `$((MYPORT+1))`. See its number:

```
echo $((MYPORT+1))
```

---

## Steps

1. **Get an OpenRouter key.** On your **laptop**, open https://openrouter.ai,
   sign in (Google or GitHub works), then go to **Keys** → **Create key**. Copy
   the key: it starts with `sk-or-`.

   > An API key is a password. Never paste it into a chat, a file in git, or a
   > screenshot.

2. **Run Open WebUI** on the server, with a volume for its data:

   ```
   docker run -d --name openwebui \
     -p 127.0.0.1:$((MYPORT+1)):8080 \
     -v openwebui-data:/app/backend/data \
     ghcr.io/open-webui/open-webui:main-slim
   ```

   It takes up to a minute to start. Watch it, and press Ctrl+C when it says it
   is running (that only stops the watching, not Open WebUI):

   ```
   docker logs -f openwebui
   ```

   Then check it answers:

   ```
   curl localhost:$((MYPORT+1))/health
   ```

3. **Open a tunnel from your laptop.** On your **laptop**, in a new terminal,
   with your port number instead of `10011`:

   ```
   ssh -N -L 3000:localhost:10011 ws
   ```

   Leave it open, and open http://localhost:3000 in your laptop's browser.

4. **Create your account, now.** The **first** account created on an Open WebUI
   becomes its **administrator**. Everyone on this server can reach your port,
   so do this before anything else. Any email address works; it never leaves
   your server.

5. **Connect OpenRouter.** Click your name (bottom left) → **Admin Panel** →
   **Settings** → **Connections**, and add a connection:

   | Field | Value |
   |---|---|
   | Provider | **OpenAI** (OpenRouter speaks the same API) |
   | URL | `https://openrouter.ai/api/v1` |
   | Key | your `sk-or-` key |
   | Prefix ID | `openrouter` |
   | Model IDs | one free model, see below |

   OpenRouter has thousands of models, so list only the one you want. On your
   laptop, open https://openrouter.ai/models, filter by **free**, and copy the
   ID of one model. Free models' IDs end in `:free`. Paste it into **Model
   IDs**, then **Save**.

6. **Chat.** Click **New Chat**, pick your model at the top, and ask it
   something.

---

## Check

```
cd ~/course/seminar_2
./check 3
```

---

## Two "why" questions

Be ready to answer these if your instructor asks:

1. Why did you create your account the moment Open WebUI opened?
2. Open WebUI is published only on 127.0.0.1 on the server. Describe the path
   your browser's request takes to reach it.

---

**Bonus:** add a second free model to the connection's Model IDs, ask both the
same question, and compare the answers.
