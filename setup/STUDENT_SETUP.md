# Before the first session

You need three things, about 15 minutes in total:

1. a GitHub account
2. an SSH key on your laptop
3. that key added to your GitHub account

In Sessions 1 and 2 the whole class works on one shared server in the cloud,
and your account on it lets you in with this key, without a password. From
Session 3, each of you gets a server of your own, reached the same way.

If you get stuck, do what you can and bring your laptop: mission 1 of the
first session covers the same steps.

---

## Step 1. GitHub account

If you already have one, skip to step 2.

1. Go to https://github.com/signup and create an account.
2. Write down your **GitHub username**.

---

## Step 2. Make your SSH key

An SSH key is how your laptop proves who you are to a server, instead of a
password. It has two halves: a **private key** that never leaves your laptop,
and a **public key** you can give to anyone.

**Windows:** open **PowerShell** (press Start, type `PowerShell`, press Enter).
**macOS:** open **Terminal** (press Cmd+Space, type `Terminal`, press Enter).

```
ssh-keygen -t ed25519
```

Press **Enter** three times: once to accept the file location, twice to leave
the passphrase empty.

Now show the public key:

| Windows (PowerShell) | macOS (Terminal) |
|---|---|
| `Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub` | `cat ~/.ssh/id_ed25519.pub` |

You see one line starting with `ssh-ed25519`. Copy the whole line.

> Never share the file **without** `.pub` at the end (`id_ed25519`). That is
> your private key.

---

## Step 3. Add the key to GitHub

1. On GitHub, click your picture (top right) → **Settings**.
2. In the left menu: **SSH and GPG keys** → **New SSH key**.
3. Title: `laptop`. Key: paste the line from step 2.
4. Click **Add SSH key**.

To check it worked, open `https://github.com/YOUR-USERNAME.keys` in your
browser. It shows your public key. That is exactly where the class server
picks it up.

---

## Step 4. Send your GitHub username

Send your **GitHub username** to the course chat. Your instructor creates your
account on the class server with it. Your username on the server is your GitHub
username in lower case.

That is all. In the first session you will connect to the server and start
working.

---

## If something goes wrong

| You see | Do this |
|---|---|
| `ssh-keygen` is not found (Windows) | Settings → Apps → Optional features → add **OpenSSH Client**, then open a new PowerShell |
| `ssh-keygen` says the file already exists | you already have a key: answer `n`, and use the existing `.pub` file in step 3 |
| `github.com/YOUR-USERNAME.keys` is empty | the key was not saved on GitHub; repeat step 3 |
| Anything else | copy the exact error and send it to the course chat |
