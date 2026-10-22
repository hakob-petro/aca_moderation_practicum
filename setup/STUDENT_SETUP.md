# Before the first lesson: set up your workspace

You are going to rent your own Linux server in the cloud, connect to it from
your laptop, and install everything the course uses. It is free: Google Cloud
gives new accounts $300 of credit for 90 days, and this server will use roughly
$10–30 of it over the whole course.

**Time:** about 45–60 minutes. Do it at least two days before the first lesson,
so there is time to ask for help.

**If you get stuck,** do as many steps as you can and bring your laptop to the
first lesson. We will finish it at the start. Write down the exact error text,
not a description of it.

---

## What you need

- A laptop with Windows 10/11, macOS or Linux. Nothing else to install.
- A Google account (a Gmail address).
- A bank card that works for online payments abroad (Visa or Mastercard).
  Google checks it but does not charge it, unless you upgrade the account
  yourself, which you will not do.
- A GitHub account. Step 1 creates one if you do not have it.

---

## Step 1. GitHub account

If you already have one, skip to step 2.

1. Go to https://github.com/signup and create an account.
2. Write down your **GitHub username**. You will send it to your instructor at
   the end.

---

## Step 2. Make your SSH key

An SSH key is how your laptop proves who you are to your server, instead of a
password. It has two halves: a **private key** that never leaves your laptop,
and a **public key** you can give to anyone.

First, pick a **username** for your server: lowercase English letters only, no
spaces, for example `ani` or `davit`. It is used in this step and in step 6.

**Windows:** open **PowerShell** (press Start, type `PowerShell`, press Enter).
**macOS:** open **Terminal** (press Cmd+Space, type `Terminal`, press Enter).

Type this, with your username instead of `ani`:

```
ssh-keygen -t ed25519 -C ani
```

Press **Enter** three times: once to accept the file location, twice to leave
the passphrase empty.

Now show the public key:

| Windows (PowerShell) | macOS (Terminal) |
|---|---|
| `Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub` | `cat ~/.ssh/id_ed25519.pub` |

You will see one line like this:

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI...long...text ani
```

Keep this window open. You will paste that whole line in step 5.

> Never share the file **without** `.pub` at the end (`id_ed25519`). That is
> your private key.

---

## Step 3. Start the Google Cloud free trial

1. Open https://console.cloud.google.com in your browser and sign in with your
   Google account.
2. Click **Start free** (or **Activate**, or **Try for free**) in the banner at
   the top. If you see no banner, open https://cloud.google.com/free and click
   **Get started for free**.
3. Fill in the form: country **Armenia**, account type **Individual**, your
   card details.
4. Google may place a small temporary hold on your card to check it. It is
   released automatically.

When it finishes, you have **$300 of credit for 90 days** and a project called
**My First Project**. We use that project for everything.

> **Never click "Upgrade" or "Activate full account".** As long as you do not,
> Google cannot charge your card. When the credit or the 90 days run out, your
> server simply stops.

---

## Step 4. Set a budget alert

This emails you if spending ever looks wrong, for example a server you forgot
about.

1. In the search bar at the top of the console, type **Budgets & alerts** and
   open it.
2. Click **Create budget**.
3. Name: `course`. Click **Next** until you reach **Amount**.
4. Target amount: **50** (dollars). Click **Next**.
5. Leave the alert thresholds at 50%, 90% and 100%. Click **Finish**.

---

## Step 5. Create your server

1. In the search bar at the top, type **Compute Engine** and open it. If it
   asks to **Enable** the Compute Engine API, click **Enable** and wait one or
   two minutes.
2. Click **Create instance**.
3. Fill in the settings below. Anything not in this table: leave as it is.
   The name `ws` is short for **workspace**. Use exactly that name: later
   steps refer to it.

| Section | Setting | Value |
|---|---|---|
| Machine configuration | Name | `ws` |
| | Region | `us-central1 (Iowa)` |
| | Zone | `us-central1-a` |
| | Series | `E2` |
| | Machine type | `e2-medium` (2 vCPU, 4 GB memory) |
| OS and storage | Click **Change** | Operating system **Ubuntu**, version **Ubuntu 24.04 LTS**, the **x86/64** one (not Arm, not Minimal), boot disk type **Balanced persistent disk**, size **30 GB**. Click **Select** |
| Networking | Firewall | leave **Allow HTTP traffic** and **Allow HTTPS traffic** **unticked** |
| | Network interfaces → External IPv4 address | **Reserve static external IP address**, name it `ws-ip`, click **Reserve** |
| Security | Manage access → **Add manually generated SSH keys** | click **Add item** and paste the whole public-key line from step 2 |

4. Check the cost estimate on the right: about **$25 a month** if left running
   all the time. You will stop it between lessons, so it will cost much less.
5. Click **Create**. After a minute, your server appears with a green tick.
6. Write down its **External IP**, for example `34.123.45.67`.

> **Why these choices.** `e2-medium` is the smallest machine with enough memory
> for the course. `us-central1` is one of the cheapest regions and is outside
> the EU, where Google treats some free services differently. A static IP
> keeps the same address every time you restart the server; it costs about $7
> a month of your credit.

---

## Step 6. Connect to your server

Make a shortcut so you can connect by typing `ssh ws`.

**Windows (PowerShell):**

```
notepad $env:USERPROFILE\.ssh\config
```

If Notepad asks to create the file, click **Yes**.

**macOS (Terminal):**

```
nano ~/.ssh/config
```

Paste this, with **your** IP and **your** username from step 2:

```
Host ws
    HostName 34.123.45.67
    User ani
```

Save and close.

- **Windows:** File → Save. The file must be called `config` with no `.txt`.
- **macOS:** press Ctrl+O, then Enter, then Ctrl+X.

Now connect:

```
ssh ws
```

The first time, it asks `Are you sure you want to continue connecting?`. Type
`yes` and press Enter.

You are in when the prompt looks like `ani@ws:~$`. Everything you type now runs
on your server, not your laptop.

---

## Step 7. Install everything

Still on your server, paste this one line and press Enter:

```
curl -fsSL https://raw.githubusercontent.com/hakob-petro/aca_moderation_practicum/main/setup/bootstrap.sh | bash
```

It installs Docker, git, GitHub CLI, tmux, uv, OpenCode, and the Modal and
Kaggle tools. It takes about five minutes, and it asks for nothing. It is safe
to run again if anything fails halfway.

When it says **Done**, log out and back in, so your new permissions apply:

```
exit
ssh ws
```

Then run the check:

```
ws-check
```

Every line should start with **PASS**. Copy the **whole** output, including the
last lines; you will send it in step 9.

---

## Step 8 (optional). Make it stop by itself every night

You can skip this step. A server you forget to stop keeps using credit, about
$0.80 a day, but even a server left running for the whole 90 days uses only
about a third of your $300. So this is a safety net, not a requirement. If you
skip it, stop your server yourself after each lesson (see "Every day after
this" below).

This step stops your server at 23:00 Yerevan time every night. You can always
start it again in the morning.

1. In the console, click the **Activate Cloud Shell** button at the top right
   (it looks like `>_`). A terminal opens at the bottom of the page. This is
   Google's terminal, not your server.
2. Check it knows your project:

   ```
   gcloud config get-value project
   ```

   If it prints nothing, open the console's **Dashboard**, copy your **Project
   ID**, and run `gcloud config set project YOUR-PROJECT-ID`.

3. Paste these commands, all at once:

   ```
   PROJECT=$(gcloud config get-value project)
   NUMBER=$(gcloud projects describe "$PROJECT" --format='value(projectNumber)')
   gcloud projects add-iam-policy-binding "$PROJECT" \
     --member="serviceAccount:service-${NUMBER}@compute-system.iam.gserviceaccount.com" \
     --role="roles/compute.instanceAdmin.v1"
   gcloud compute resource-policies create instance-schedule nightly-stop \
     --region=us-central1 --vm-stop-schedule="0 23 * * *" --timezone="Asia/Yerevan"
   gcloud compute instances add-resource-policies ws \
     --zone=us-central1-a --resource-policies=nightly-stop
   ```

The first command lets Google's own scheduler stop your server. The other two
create the nightly schedule and attach it to `ws`.

---

## Step 9. Send your details

Send your instructor, in the course chat:

1. Your name
2. Your GitHub username
3. Your server's external IP
4. The whole output of `ws-check`

---

## Every day after this

| To | Do |
|---|---|
| Start your server before a lesson | Compute Engine → VM instances → tick `ws` → **Start**, wait a minute, then `ssh ws` |
| Stop it after a lesson | Compute Engine → VM instances → tick `ws` → **Stop**. If you did step 8, it also stops by itself at 23:00 |
| See how much credit you have used | search **Billing** in the console → **Overview** |

When a server stops, your files stay. Programs that were running stop and need
starting again.

**What costs credit:** a running server (about $0.80 a day), its disk and static
IP even when stopped (together about $0.30 a day). Nothing else in this course
uses Google Cloud credit.

---

## If something goes wrong

| You see | It means | Do this |
|---|---|---|
| `Permission denied (publickey)` | the server does not recognise your key, or the username is wrong | check that `User` in your `config` is exactly the name at the end of your public key; check the key you pasted in step 5 is the `.pub` one |
| `Connection timed out` | the server is stopped, or the IP is wrong | start it in the console; compare the External IP with `HostName` in your `config` |
| `Could not resolve hostname ws` | the `config` file was not saved, or was saved as `config.txt` | open it again with the command from step 6; on Windows choose "All files" when saving |
| The machine type or zone is not available | Google is short of that machine in that zone | pick zone `us-central1-b` or `us-central1-c` instead; if you do step 8, use that zone there too |
| Your card is declined | the card does not allow online payments abroad | try another card. If none works, tell your instructor: you will get a server another way |
| `ws-check` says docker needs a fresh login | you did not log out after step 7 | `exit`, then `ssh ws`, then `ws-check` again |
| Anything else | – | copy the exact error and send it to the course chat |

---

## Rules

- Never upgrade the account, and never create a second server unless a lesson
  tells you to.
- Never send anyone your private key (the file without `.pub`).
- Do not tick HTTP or HTTPS, or open other ports. You will learn to do that
  safely in the lessons.
- At the end of the course, delete the server and its static IP: Compute
  Engine → VM instances → `ws` → **Delete**; then search **IP addresses** and
  release `ws-ip`.
