# Mission 1 — Finish and inspect your server

**Mode:** by hand · **Time:** 30 minutes

You rented a server before this session. Now make sure everything on it works,
and find out what exactly you rented.

---

## If `ws-check` is not all PASS yet

Run it first:

```
ws-check
```

If any line says **FAIL**, or you could not finish the setup guide, finish it
now: `~/course/setup/STUDENT_SETUP.md`, or the copy on GitHub. Your instructor
and the captains will come to you first. When `ws-check` is all PASS, continue
below.

---

## Inspect what you rented

Copy the answers template into a folder for today's work, and open it:

```
mkdir -p ~/s1
cp ~/course/seminar_1/templates/m1.txt ~/s1/m1.txt
nano ~/s1/m1.txt
```

Fill in each line after the `=` sign. Find the answers in the **Google Cloud
console** in your browser, or on your server:

| Line | Question | Where to look |
|---|---|---|
| `zone` | Which zone is your server in? | console: Compute Engine → VM instances, the **Zone** column |
| `machine_type` | What machine type is it? | console: click `ws`, then **Machine type** |
| `vcpus` | How many CPUs does it have? | on the server: `nproc` |
| `external_ip` | What is its public IP address? | console: the **External IP** column |
| `credit_used` | How much of your $300 have you used so far? | console: search **Billing**, then **Overview** or **Credits** |

**Saving in nano:** press Ctrl+O, then Enter to confirm, then Ctrl+X to exit.

---

## Check

```
cd ~/course/seminar_1
./check 1
```

---

## Two "why" questions

Your captain will ask you these:

1. Your laptop and your server both have a terminal. How do you tell which one
   you are typing into?
2. Your server costs credit while it runs. What still costs credit after you
   **stop** it, and why?

---

**Bonus:** find out how much memory your server has (`free -h`) and how much
disk (`df -h /`). Do those match what you chose when you created it?
