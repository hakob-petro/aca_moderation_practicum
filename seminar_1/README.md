# Seminar 1 — Workspace

Today you get comfortable on your own server: finding your way around Linux,
working in git and GitHub, and connecting a coding agent to free AI models.

**Before you start:** your server is running (Google Cloud console → Compute
Engine → VM instances → `ws` → **Start**), and you are logged in with `ssh ws`.
Then get today's files:

```
cd ~/course && git pull
cd ~/course/seminar_1
```

If `~/course` does not exist yet:

```
git clone https://github.com/hakob-petro/aca_moderation_practicum.git ~/course
cd ~/course/seminar_1
```

---

## Missions

| # | Mission | Mode | Minutes |
|---|---|---|---|
| 1 | [Finish and inspect your server](mission_1.md) | by hand | 30 |
| – | Break | | 5 |
| 2 | [Linux scavenger hunt](mission_2.md) | by hand | 25 |
| 3 | [git and GitHub](mission_3.md) | by hand | 25 |
| 4 | [Your first agent](mission_4.md) | with agent | 25 |

Each card ends with the command that checks your work:

```
./check 1
```

It prints **PASS** or **FAIL** for each part, and a hint for anything that
failed. When everything passes, colour your cell on the board.

**Out of time?** Run `./catchup N` before the next mission. Today's missions do
not depend on each other, so you can always start the next one.

**Stuck for 10 minutes?** Put a sticky note on your laptop lid.

**By hand** means you type every command yourself. You may ask the coding agent
(from mission 4 onwards) to explain an error, but not to do the mission.

---

## You are done when

- `./check 1`, `./check 2`, `./check 3` and `./check 4` all pass
- your `about.md` is merged into your own repository, `aca-work`
- OpenCode answers you through two different providers

**After the session,** stop your server: Compute Engine → VM instances → `ws`
→ **Stop**. Your files stay; programs that were running stop.

Anything you did not finish, finish at home before the next session: each
mission's `./check` still works.

**Want to know how SSH really works?** Read
[How SSH works](../materials/seminar_1/how_ssh_works.pdf): what your public and
private keys are for, and what happens when you type `ssh ws`.
