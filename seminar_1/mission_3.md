# Mission 3 — tmux and git

**Mode:** by hand · **Time:** 25 minutes

Two skills you will use in every session from now on: keeping a program running
when your laptop disconnects, and sharing work with your team.

---

## Part 1: tmux

A program you start over SSH dies when the connection drops, for example when
your laptop goes to sleep. **tmux** keeps it running on the server.

1. Start a tmux session called `long`:

   ```
   tmux new -s long
   ```

2. Inside it, start a job that counts for 15 minutes:

   ```
   ~/course/seminar_1/long_job.sh
   ```

3. **Detach**, leaving it running: press **Ctrl+B**, let go, then press **D**.
4. **Close your laptop lid** for one minute. Open it again.
5. Your SSH connection is probably dead. Connect again with `ssh ws`, then:

   ```
   tmux attach -t long
   ```

   It is still counting. Detach again (Ctrl+B, then D) and leave it running.

---

## Part 2: git with your team

Your captain tells you your team's repository, for example
`hakob-petro/aca-team-3`.

1. Tell git who you are (once per server):

   ```
   git config --global user.name "Your Name"
   git config --global user.email "you@example.com"
   ```

2. Log in to GitHub:

   ```
   gh auth login
   ```

   Choose **GitHub.com** → **HTTPS** → **Yes** (authenticate git) → **Login
   with a web browser**. It prints a code. On your **laptop**, open
   https://github.com/login/device and type the code.

3. Clone your team's repository, using your team's name:

   ```
   gh repo clone hakob-petro/aca-team-3 ~/team
   cd ~/team
   ```

4. Make a branch, add a file about yourself, and push it. The file name must
   be your **GitHub username**, exactly as GitHub spells it, capitals
   included. This prints it:

   ```
   gh api user --jq .login
   ```

   Then:

   ```
   git switch -c add-yourname
   mkdir -p members
   nano members/your-github-username.md
   ```

   Write your name and one sentence about yourself. Save and exit. Then:

   ```
   git add members
   git commit -m "Add yourname"
   git push -u origin add-yourname
   gh pr create --fill
   ```

5. Tell your captain. They review your pull request and merge it.

---

## Check

When your pull request is merged:

```
cd ~/course/seminar_1
./check 3
```

---

## Two "why" questions

1. What happened to the counting job when your laptop lid was closed, and what
   would have happened without tmux?
2. Why do you work on a branch and open a pull request, instead of pushing
   straight to `main`?

---

**Bonus:** open a second window inside tmux (Ctrl+B, then C) and switch
between windows (Ctrl+B, then N).
