# Mission 1 — Containers by hand

**Mode:** by hand · **Time:** 25 minutes

An **image** is a packaged program with everything it needs. A **container** is
that image running. Today's first one is a web server, nginx.

**What is a container, really?** Read
[How Docker works](../materials/seminar_2/how_docker_works.pdf), sections 2–4.

---

## Steps

1. Your first container:

   ```
   docker run hello-world
   ```

   Read what it prints: Docker explains the four things it just did.

2. See which images you have:

   ```
   docker images
   ```

3. Start a web server in the background (`-d`), with a name (`--name`):

   ```
   docker run -d --name web nginx:1.27-alpine
   ```

4. See it running, and read what it has printed so far:

   ```
   docker ps
   docker logs web
   ```

5. Go **inside** the running container:

   ```
   docker exec -it web sh
   ```

   The prompt changes: you are now inside the container, not on the server.
   Look around:

   ```
   cat /etc/os-release
   nginx -v
   ls /usr/share/nginx/html
   exit
   ```

6. Write down two things you saw:

   ```
   mkdir -p ~/s2
   cp ~/course/seminar_2/templates/m1.txt ~/s2/m1.txt
   nano ~/s2/m1.txt
   ```

   | Line | What to write |
   |---|---|
   | `container_os` | the `ID` from `/etc/os-release` inside the container |
   | `nginx_version` | the version number `nginx -v` printed, for example `1.27.5` |

7. Stop it, and see what is left:

   ```
   docker stop web
   docker ps
   docker ps -a
   ```

   `docker ps` shows running containers; `docker ps -a` shows all of them,
   stopped ones too. Now remove it:

   ```
   docker rm web
   docker ps -a
   ```

---

## Check

```
cd ~/course/seminar_2
./check 1
```

---

## Two "why" questions

Be ready to answer these if your instructor asks:

1. What is the difference between an image and a container?
2. After `docker stop web`, `docker ps -a` still listed it. What did
   `docker rm` remove that `docker stop` did not?

---

**Bonus:** `docker system df` shows how much disk your images and containers
use. Which image is the biggest?
