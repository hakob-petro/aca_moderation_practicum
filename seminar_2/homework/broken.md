# Homework — Broken on purpose

**Mode:** by hand, at home · **Time:** about 30 minutes

A tiny web app that should say "Hello from" your name. It has **three bugs**.
Find and fix them, using only what Docker tells you. This is most of the job of
running containers: something fails, and you work out why from what it prints.

`app.py` is fine. The bugs are in the `Dockerfile` and in the `docker run`
command below.

---

## Start

```
mkdir -p ~/s2
cp -r ~/course/seminar_2/homework/broken ~/s2/broken
cd ~/s2/broken
cat app.py
cat Dockerfile
```

Then build the image and run it, exactly as written:

```
docker build -t broken-app .
docker run -d --name fixed -p 127.0.0.1:$((MYPORT+3)):80 broken-app
curl localhost:$((MYPORT+3))
```

It will not work. That is the point.

---

## How to find the bugs

| Tool | What it tells you |
|---|---|
| the last lines of `docker build` | why a build failed |
| `docker ps -a` | whether the container is running, or `Exited` |
| `docker logs fixed` | everything the app printed, including why it crashed |
| `docker port fixed` | which port on the server goes to which port in the container |
| `curl -v localhost:$((MYPORT+3))` | what happens when you connect |

**Each time you change something:** remove the old container
(`docker rm -f fixed`), rebuild if you changed the `Dockerfile`, and run again.

`./check broken` gives a hint for whichever bug you are stuck on.

---

## Check

When `curl localhost:$((MYPORT+3))` answers "Hello from" a name:

```
cd ~/course/seminar_2
./check broken
```

---

## Two "why" questions

Be ready to answer these if your instructor asks:

1. The container started and stopped at once. Where did you find out why?
2. In `-p 127.0.0.1:10013:8000`, which number is a port on the server, and
   which is a port inside the container?

---

**Bonus:** set the name in the `Dockerfile` with an `ENV` line, so the
`docker run` command does not need `-e`. Then think: where should a secret, like
an API key, go instead, and why neither of these?
