# Build a moderation service, end to end

Online communities have rules: "No advertising", "No legal advice". Moderators
cannot read every comment, so over six sessions you will build the service that
reads them first:

```
comment in → probability it breaks the rule → approve, send to a human, or remove
```

You will rent your own server, fine-tune a language model on a real Kaggle
competition, deploy it, and build the moderator's console around it. Along the
way you will learn the tools every ML engineer uses daily: SSH, Linux, git,
Docker, cloud GPUs and a coding agent.

---

## Before the first session

Follow **[setup/STUDENT_SETUP.md](setup/STUDENT_SETUP.md)**. It takes about
45–60 minutes: you create a GitHub account, rent a free cloud server, connect
to it and install the basic tools. Do it at least two days before Session 1. If you
get stuck, do what you can and bring your laptop; we finish it together at the
start.

---

## The six sessions

Each session's mission cards and checks are in its folder: start with
[seminar_1](seminar_1/README.md).

| Session | You will |
|---|---|
| 1. **Workspace** | find your way around Linux, work in git with your team, connect a coding agent to free model providers |
| 2. **Docker** | run, fix and compose containers, and learn what exposing a port really does |
| 3. **Train I: data and baseline** | run code on a cloud GPU, look at the data critically, see how a language model produces a probability, measure a baseline |
| 4. **Train II: fine-tune and submit** | fine-tune the model, compare runs with your team, submit to Kaggle, and find out how your score holds up on rules your model has never seen |
| 5. **Deploy** | serve your model, put your own service in front of it, make it survive failures, and stand up a second server in minutes |
| 6. **Product** | build the moderator console, log every decision, show similar past cases, and attack another team's console |

---

## How a session works

Each session is four **missions** of 15–35 minutes. In every mission:

1. Your instructor shows the commands for a few minutes.
2. You do it yourself on your own server, from a one-page mission card in
   `missions/`.
3. You run `./check N`. It prints PASS or FAIL. When it passes, colour your
   cell on the board.

Some cards say **by hand**: type every command yourself, and use the coding
agent only to explain errors. Others say **with agent**: the agent may do the
work, but you must be able to answer the card's two "why" questions.

**Stuck for 10 minutes?** Put a sticky note on your laptop lid. Someone will
come.

**Out of time?** Run `./catchup N` to start the next mission with everyone
else. You can finish the missed one in the open lab.

**Teams.** You work on your own server, but in a team of four with a captain.
Your team shares a GitHub repository, a row on the board, and an opponent in
the final session's game.

---

## Between sessions: the open lab

There is a supervised open lab between sessions. Use it to finish missions,
do homework cards from `homework/`, and complete sign-ups that need
verification. Homework is optional; nothing in a session depends on it.

One sign-up must be done in an open lab, because its phone verification can
take time: before Session 4, a Kaggle account, verified with your phone, and
joined to the Jigsaw competition.

---

## The accounts you will use

All free.

| Account | When |
|---|---|
| GitHub, Google | before Session 1 |
| Google Cloud free trial | before Session 1, from the setup guide |
| OpenCode Zen, Google AI Studio key | Session 1 |
| Modal | Session 3 |
| Kaggle | open lab before Session 4 |
| OpenRouter | homework |

---

## Credit rules

You have free credit on Google Cloud ($300) and Modal ($30 a month). The course
uses a small part of each, as long as you follow three rules:

1. **Never upgrade your Google Cloud account.** As long as you do not, your
   card cannot be charged.
2. **Stop what you are not using.** Stop your server after each session (or
   set it to stop itself every night, the optional step 8 of the setup guide),
   and stop your Modal apps.
3. **Never set `min_containers` in a Modal app.** It keeps a GPU running
   around the clock, about $19 a day.

---

## At the end of the course

Delete your server and its static IP (the setup guide says how), and stop your
Modal apps. Everything you built stays in your team's GitHub repository.
