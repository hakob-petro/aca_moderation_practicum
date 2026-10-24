# Seminar 1 — Workspace

Today you get comfortable on a Linux server: finding your way around, working
in git and GitHub, and connecting a coding agent to free AI models.

In Sessions 1 and 2 the whole class shares one server; each of you has your own
account on it. From Session 3, each of you gets a server of your own.

**Start with [mission 1](mission_1.md):** it gets you onto the class server.
Once you are logged in, today's files are in `~/course/seminar_1`.

---

## Missions

| # | Mission | Mode | Minutes |
|---|---|---|---|
| 1 | [Get onto the class server](mission_1.md) | by hand | 30 |
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

Anything you did not finish, finish at home before the next session: each
mission's `./check` still works.

**Want to know how SSH really works?** Read
[How SSH works](../materials/seminar_1/how_ssh_works.pdf): what your public and
private keys are for, and what happens when you type `ssh ws`.
