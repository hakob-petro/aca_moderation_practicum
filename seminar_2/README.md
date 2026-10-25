# Seminar 2 — Docker

Today you learn the tool almost every server runs on: containers. You run them,
look inside them, and give them ports and volumes. Then you run your own Open
WebUI, a ChatGPT-like interface connected to a free AI model, use it from your
laptop through an SSH tunnel, and make it permanent with Docker Compose.

---

## Before you start

If you can, make a free account at https://openrouter.ai before the session:
mission 3 needs it.

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
need two: `$MYPORT` for mission 2 and `$((MYPORT+1))` for Open WebUI.

---

## Missions

| # | Mission | Mode | Minutes |
|---|---|---|---|
| 1 | [Containers by hand](mission_1.md) | by hand | 25 |
| 2 | [Ports, volumes and a tunnel](mission_2.md) | by hand | 25 |
| – | Break | | 5 |
| 3 | [Your own Open WebUI](mission_3.md) | by hand | 30 |
| 4 | [Make it permanent with Compose](mission_4.md) | by hand | 30 |

Each card ends with the command that checks your work, for example:

```
./check 1
```

It prints **PASS** or **FAIL** for each part, and a hint for anything that
failed. When everything passes, colour your cell on the board.

**Out of time?** Run `./catchup N` before the next mission. Missions 1, 2 and 3
do not depend on each other. Mission 4 builds on mission 3, and `./catchup 4`
tells you how to start it anyway.

**Stuck for 10 minutes?** Put a sticky note on your laptop lid.

**By hand** means you type every command yourself. You may ask OpenCode to
explain an error, but not to do the mission.

---

## You are done when

- `./check 1` to `./check 4` all pass
- you chat with a free model in your own Open WebUI, from your laptop
- it comes back by itself after a Docker restart, with your chats still there

Anything you did not finish, finish at home before the next session: each
mission's `./check` still works.

**Want to know how Docker really works?** Read
[How Docker works](../materials/seminar_2/how_docker_works.pdf): images and
containers, what happens when you type `docker run`, ports, volumes, Compose,
and how Docker works on the class server.

**Homework, at home:** [Broken on purpose](homework/broken.md). An app with
three bugs, found and fixed from what Docker tells you. `./check broken` checks
it.
