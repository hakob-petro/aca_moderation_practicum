# Mission 4 — Your first agent

**Mode:** with agent · **Time:** 25 minutes

**OpenCode** is a coding agent that runs in your terminal: you ask in plain
language, and it reads files, runs commands and writes code. It needs a
**provider**: a service that runs the AI model. Today you connect two free
ones.

---

## Part 1: install OpenCode

```
curl -fsSL https://opencode.ai/install | bash
opencode --version
```

Probably you see **`opencode: command not found`**. That is normal after an
install: the installer told your shell where to find OpenCode, but your current
shell started before that. Open a fresh one:

```
exec bash
opencode --version
```

Now it prints a version number. You will meet this "not found until you open
a new shell" surprise after almost every install.

---

## Part 2: the first provider, OpenCode Zen

1. On your **laptop**, open https://opencode.ai/auth, sign in, and create an API
   key. Copy it.
2. On your server:

   ```
   opencode auth login
   ```

   Choose **OpenCode Zen** and paste the key.

## Part 3: the second provider, Google Gemini

1. On your laptop, open https://aistudio.google.com/apikey, sign in with your
   Google account, and click **Create API key**. Copy it.
2. On your server:

   ```
   opencode auth login
   ```

   Choose **Google** and paste the key.

Check that both are there:

```
opencode auth list
```

> An API key is a password. Never paste it into a chat, a file in git, or a
> screenshot.

---

## Part 4: use it

```
cd ~/hunt
opencode
```

1. Type `/models` and pick one of the **free** models from OpenCode Zen.
2. Ask it: *"Explain what `ps aux --sort=-%mem | head -5` does, line by line."*
3. Type `/models` again, pick a **Gemini** model, and ask the same question.
   Which answer was clearer?
4. Ask it to explain one command from mission 2 you did not understand.

Quit with `/exit` or Ctrl+C.

A provider is just three things: **an address** (where the model runs), **a
key** (proof you are allowed to use it) and **a model name**. Every AI tool you
will ever configure asks for those three.

---

## Check

```
cd ~/course/seminar_1
./check 4
```

---

## Two "why" questions

1. What three things does any AI tool need to talk to a provider?
2. Where on your server does OpenCode keep your keys, and who else could read
   them?

---

**Bonus:** ask OpenCode to write a one-line command that shows the five
biggest files in your home folder, then run it yourself and check it is right.
