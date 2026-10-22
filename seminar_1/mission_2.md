# Mission 2 — Linux scavenger hunt

**Mode:** by hand · **Time:** 25 minutes

Six questions about your server, answered with the commands below. Your
answers are different from your neighbour's, so you cannot copy them.

---

## Start the hunt

```
~/course/seminar_1/hunt/start.sh
```

It hides some files in `~/hunt` and starts a program that uses a lot of
memory. Then open your answer sheet:

```
cp ~/course/seminar_1/templates/m2.txt ~/s1/m2.txt
nano ~/s1/m2.txt
```

---

## The commands you need

| Command | What it does |
|---|---|
| `pwd` | shows which folder you are in |
| `ls` | lists a folder; `ls -la` also shows hidden files (names starting with `.`) and who owns each file |
| `cd folder` | goes into a folder; `cd ~` goes home; `cd ..` goes up one level |
| `cat file` | prints a whole file |
| `less file` | shows a long file page by page; `q` quits |
| `tail -n 5 file` | shows the last 5 lines of a file |
| `find ~/hunt -name 'something'` | searches for files by name |
| `df -h /` | how full the disk is |
| `free -h` | how much memory is used |
| `htop` | live list of programs; press F6 to sort, `q` to quit |
| `ps aux --sort=-%mem \| head` | the programs using the most memory |
| `sudo command` | runs a command as the administrator |
| `kill PID` | stops the program with that process ID |

---

## The questions

| Line | Question |
|---|---|
| `q1` | Which program is using the most memory? Give its name |
| `q2` | How full is your disk, in percent? Just the number |
| `q3` | What is the code word on the **last** line of `~/hunt/logs/app.log`? |
| `q4` | A file called `treasure.txt` is hidden somewhere inside `~/hunt`. What word is in it? |
| `q5` | Who owns the file `~/hunt/locked.txt`? |
| `q6` | What word is in `~/hunt/locked.txt`? You will need `sudo` |

**Then stop the memory-hungry program** from `q1`: find its process ID (the
`PID` column) and `kill` it.

---

## Check

```
cd ~/course/seminar_1
./check 2
```

---

## Two "why" questions

1. Why could you not see `treasure.txt` with a plain `ls`?
2. Why could you not read `locked.txt` without `sudo`, even though it is in
   your own home folder?

---

**Bonus:** how many lines does `~/hunt/logs/app.log` have? (`wc -l`)
