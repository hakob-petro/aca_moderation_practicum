# Mission 1 — Get onto the class server

**Mode:** by hand · **Time:** 30 minutes

In Sessions 1 and 2 the whole class works on one shared Linux server in the
cloud. Each of you has your own account on it, with your own private home
folder. From Session 3, each of you gets a server of your own.

---

## Part 1: your SSH key on GitHub

Skip this part if you did it before the session (`setup/STUDENT_SETUP.md`).

1. Make a key, on your laptop. **Windows:** open **PowerShell**. **macOS:** open
   **Terminal**. Then:

   ```
   ssh-keygen -t ed25519
   ```

   Press **Enter** three times.

2. Show the **public** half:

   | Windows (PowerShell) | macOS (Terminal) |
   |---|---|
   | `Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub` | `cat ~/.ssh/id_ed25519.pub` |

3. Copy that whole line. On GitHub: your picture (top right) → **Settings** →
   **SSH and GPG keys** → **New SSH key**. Title: `laptop`. Paste the key.
   Click **Add SSH key**.

4. If your instructor does not have your GitHub username yet, send it to the
   course chat now.

The server copies your public key from GitHub every minute. That is how it will
recognise you, without a password. Your private key never leaves your laptop.

---

## Part 2: connect

Your **server username** is your GitHub username in lower case: `Ani-K` becomes
`ani-k`. The server's address is on the board.

Make a shortcut, so you can connect by typing `ssh ws`.

**Windows (PowerShell):** `notepad $env:USERPROFILE\.ssh\config`
(if Notepad asks to create the file, click **Yes**)

**macOS (Terminal):** `nano ~/.ssh/config`

Paste this, with the address from the board and **your** username:

```
Host ws
    HostName 34.123.45.67
    User ani-k
```

Save and close. On Windows, the file must be called `config`, not
`config.txt`. Then:

```
ssh ws
```

Type `yes` the first time it asks. You are in when the prompt shows your
username and the server's name.

`Permission denied (publickey)` right after adding the key: wait one minute,
then try again.

**Prefer pasting to editing files?** This adds the same `ws` shortcut and tests
the connection, with your username and the server's address:

Windows (PowerShell):

```
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/hakob-petro/aca_moderation_practicum/main/setup/ssh_setup.ps1))) config ani-k 34.123.45.67
```

macOS (Terminal):

```
curl -fsSL https://raw.githubusercontent.com/hakob-petro/aca_moderation_practicum/main/setup/ssh_setup.sh | bash -s -- config ani-k 34.123.45.67
```

**How does SSH know it is you?** Read
[How SSH works](../materials/seminar_1/how_ssh_works.pdf): what your two keys
are for, and what happens when you type `ssh ws`.

---

## Part 3: inspect the server

```
cd ~/course && git pull
mkdir -p ~/s1
cp ~/course/seminar_1/templates/m1.txt ~/s1/m1.txt
nano ~/s1/m1.txt
```

Fill in each line after the `=`:

| Line | Question | How to find out |
|---|---|---|
| `cpus` | How many CPUs does this server have? | `nproc --all` |
| `memory_gb` | How much memory, in GB? | `free -h`, the **total** on the `Mem` line |
| `classmate` | The username of one classmate logged in right now | `who` |
| `home` | The full path of your home folder | `cd`, then `pwd` |
| `public_ip` | The server's public IP address | the `HostName` in your SSH config |

**Saving in nano:** Ctrl+O, Enter, then Ctrl+X.

---

## Check

```
cd ~/course/seminar_1
./check 1
```

---

## Two "why" questions

Be ready to answer these if your instructor asks:

1. Your laptop and the server both have a terminal. How do you tell which one
   you are typing into?
2. The server got your **public** key from GitHub. Why is it safe for anyone to
   see a public key, but never a private one?

---

**Bonus:** `w` shows who is logged in and what each person is running. What
are your classmates doing right now? Can you open their home folders
(`ls /home/their-username`)? Why not?
