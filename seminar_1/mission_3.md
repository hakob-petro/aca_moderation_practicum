# Mission 3 — git with your team

**Mode:** by hand · **Time:** 25 minutes

From now on your team shares its work through one GitHub repository. Today
you each add one file to it, the way professional teams do: on a branch,
through a pull request that someone else reviews and merges.

---

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

1. What is the difference between `git commit` and `git push`?
2. Why do you work on a branch and open a pull request, instead of pushing
   straight to `main`?

---

**Bonus:** after your teammates' files are merged, run `git switch main`,
then `git pull`, then `git log --oneline --graph`. Whose commits do you see?
