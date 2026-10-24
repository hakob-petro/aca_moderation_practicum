# Seminar 2 — Docker

Today you learn the tool almost every server runs on: containers. You run them,
look inside them, build your own, fix a broken one, and describe a whole app in
one file that brings itself back after a crash.

---

## Before you start

Connect to the class server:

```
ssh ws
```

Not on the class server yet? Do parts 1 and 2 of
[Seminar 1's mission 1](../seminar_1/mission_1.md) first, and send your GitHub
username to the course chat.

Then get today's files, and check your Docker answers:

```
cd ~/course && git pull
cd ~/course/seminar_2
docker info
echo $MYPORT
```

**Docker on this server is yours alone.** `docker ps` shows only your
containers; your classmates cannot see yours, and you cannot see theirs. If
`docker info` says it cannot connect, run `systemctl --user start docker` and
try again.

**Your ports.** Everyone shares this server, so everyone gets their own ten
port numbers: `$MYPORT` to `$MYPORT + 9`. Never use anyone else's. Today you
need three: `$MYPORT`, `$((MYPORT+1))` and `$((MYPORT+2))`.

---

## Missions

| # | Mission | Mode | Minutes |
|---|---|---|---|
| 1 | [Containers by hand](mission_1.md) | by hand | 25 |
| 2 | [Ports, volumes and a tunnel](mission_2.md) | by hand | 25 |
| – | Break | | 5 |
| 3 | [Broken on purpose](mission_3.md) | by hand | 30 |
| 4 | [Compose, a crash and a restart](mission_4.md) | by hand | 30 |

Each card ends with the command that checks your work, for example:

```
./check 1
```

It prints **PASS** or **FAIL** for each part, and a hint for anything that
failed. When everything passes, colour your cell on the board.

**Out of time?** Run `./catchup N` before the next mission. Today's missions do
not depend on each other, so you can always start the next one.

**Stuck for 10 minutes?** Put a sticky note on your laptop lid.

**By hand** means you type every command yourself. You may ask OpenCode to
explain an error, but not to do the mission.

---

## You are done when

- `./check 1` to `./check 4` all pass
- your counter app comes back by itself after a crash and after a Docker
  restart, and still remembers its count

Anything you did not finish, finish at home before the next session: each
mission's `./check` still works.
