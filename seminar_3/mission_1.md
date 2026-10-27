# Mission 1 — Hello, GPU

**Mode:** by hand · **Time:** 25 minutes

Training and running a language model needs a **GPU**, a chip that does
thousands of multiplications at once. The class server has none. **Modal**
rents you one for exactly as long as your code runs: it starts a machine with
a GPU, runs your function on it, and shuts it down when the function returns.
You pay for those seconds only, out of Modal's free $30 a month.

---

## Steps

1. **Install uv**, the tool that installs Python programs and their
   packages, on the class server:

   ```
   ssh ws
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source ~/.local/bin/env
   uv --version
   ```

2. **Install Modal's command**, with uv:

   ```
   uv tool install modal
   modal --version
   ```

3. **Connect it to your Modal account:**

   ```
   modal token new
   ```

   The server has no browser, so it prints a link. Open the link in your
   **laptop's** browser, sign in to Modal, and approve. The terminal then says
   the token is verified. It is saved in `~/.modal.toml`: like an SSH key,
   never share that file.

   **Using the class's Modal account** (because you have no card)? Skip
   `modal token new`: your instructor has put the class token in your
   `~/.modal.toml` already. Check with `modal profile current`: it says
   `aca-class`. That token runs on your instructor's account: use it for the
   course only, and never copy it anywhere else.

4. **Run your first function on a GPU:**

   ```
   mkdir -p ~/s3
   cd ~/course/seminar_3
   cat hello_modal.py
   modal run hello_modal.py
   ```

   Read `hello_modal.py` while it runs. The first time takes about a minute:
   Modal builds the **image** your function runs in, a Docker-like package
   with Python and PyTorch, the library that talks to the GPU. Later runs
   reuse it and take about 15 seconds. Then it prints which GPU you got (an
   L4, an A10 or a T4: the first one Modal has free), and how long a big
   matrix multiplication took on the CPU and on the GPU.

5. **Bring the file back.** `hello_modal.py` wrote `hello.txt` to a Modal
   **volume** called `aca-models`, a disk in Modal's cloud that outlives the
   machine. Your trained models will live there in Session 4.

   ```
   modal volume ls aca-models
   modal volume get aca-models hello.txt ~/s3/hello.txt
   cat ~/s3/hello.txt
   ```

6. **See what it cost.** On your laptop, open https://modal.com/apps: your
   run of `aca-hello-gpu` is listed. Then **Settings** → **Usage & Billing**.
   The whole mission costs a cent or two.

---

## Check

```
cd ~/course/seminar_3
./check 1
```

---

## Two "why" questions

Be ready to answer these if your instructor asks:

1. Your terminal waited while `hello()` ran. Where did the code actually run,
   and what happened to that machine afterwards?
2. Why does `hello.txt` go into a volume, and not just into a file on the
   machine that ran `hello()`?

---

**Bonus:** in `hello.txt`, divide `matmul_cpu_ms` by `matmul_gpu_ms`. How many
times faster is the GPU? Why can a GPU do so much more of this one kind of work?
