# Mission 2 — Ports, volumes and a tunnel

**Mode:** by hand · **Time:** 25 minutes

A container is closed off by default. Today you open a **port** so you can reach
the web server inside, see it in your own browser through an **SSH tunnel**, and
give it your own web page with a **volume**.

Your port for this mission is `$MYPORT`. See its number:

```
echo $MYPORT
```

---

## Steps

1. **Publish a port.** Start nginx again, this time connecting your port on the
   server to port 80 inside the container:

   ```
   docker run -d --name site -p 127.0.0.1:$MYPORT:80 nginx:1.27-alpine
   curl localhost:$MYPORT
   ```

   `-p 127.0.0.1:$MYPORT:80` means: on the server, at address 127.0.0.1 and
   your port, forward to port 80 inside the container. You get nginx's welcome
   page as HTML.

2. **See it in your browser, through a tunnel.** 127.0.0.1 means "only from
   this server", so the internet cannot reach it. An SSH tunnel brings it to
   your laptop. On your **laptop**, open a **new** terminal and run this, with
   your port number instead of `10010`:

   ```
   ssh -N -L 8080:localhost:10010 ws
   ```

   It looks like it hangs. That is the tunnel, working: leave it open. Now open
   http://localhost:8080 in your laptop's browser.

3. **Your own page, with a volume.** Back on the server, make a folder with a
   page in it, then start nginx again with that folder mounted into it:

   ```
   mkdir -p ~/s2/site
   echo "<h1>Hello from $USER</h1>" > ~/s2/site/index.html
   docker rm -f site
   docker run -d --name site -p 127.0.0.1:$MYPORT:80 \
     -v ~/s2/site:/usr/share/nginx/html:ro nginx:1.27-alpine
   ```

   Reload the page in your browser: it is yours now.

4. **Change it live.** Edit the page, then reload the browser. No restart
   needed:

   ```
   nano ~/s2/site/index.html
   ```

---

## Check

```
cd ~/course/seminar_2
./check 2
```

---

## Two "why" questions

Be ready to answer these if your instructor asks:

1. The page is published only on 127.0.0.1, so the internet cannot reach it.
   How did your laptop's browser see it?
2. You changed a file on the server, and the page in the container changed
   without a restart. Why?

---

**Bonus:** try to write a file from inside the container:
`docker exec site sh -c 'echo hi > /usr/share/nginx/html/x.html'`. Why does it
fail? Look at the end of the `-v` option.
