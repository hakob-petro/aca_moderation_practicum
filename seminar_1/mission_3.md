# Mission 3 — git and GitHub

**Mode:** by hand · **Time:** 25 minutes

Everything you build in this course lives in your own GitHub repository. Today
you create it and add one file to it, the way professional teams do: on a
branch, through a pull request that is reviewed and then merged.

You are the only person in your repository, so you will review and merge your
own pull request. In a team, someone else would.

---

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

3. Create your repository, and copy it to your server:

   ```
   cd ~
   gh repo create aca-work --private --add-readme --clone
   cd ~/aca-work
   ```

   Your repository is now `your-github-username/aca-work`, in the folder
   `~/aca-work`. It is private: only you can see it.

4. Make a branch, add a file about yourself, and push it:

   ```
   git switch -c add-about
   nano about.md
   ```

   Write your name and one sentence about yourself. Save and exit. Then:

   ```
   git add about.md
   git commit -m "Add about.md"
   git push -u origin add-about
   gh pr create --fill
   ```

5. Review your pull request, the way a teammate would. This prints what
   changed:

   ```
   gh pr diff
   ```

   Is it only the file you meant to add? Then merge it:

   ```
   gh pr merge --merge --delete-branch
   ```

6. Bring the merged work back to your server:

   ```
   git switch main
   git pull
   ```

---

## Check

```
cd ~/course/seminar_1
./check 3
```

---

## Two "why" questions

1. What is the difference between `git commit` and `git push`?
2. In a team, why does everyone work on a branch and open a pull request,
   instead of pushing straight to `main`?

---

**Bonus:** run `git log --oneline --graph`. Find the commit that merged your
branch into `main`. Then look at your pull request on your laptop: open
`https://github.com/your-github-username/aca-work/pulls?q=is%3Apr`.
