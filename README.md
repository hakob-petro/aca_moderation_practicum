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

## The Kaggle competition

The task you train your model on comes from a real machine-learning competition:
**[Jigsaw – Agile Community Rules Classification](https://www.kaggle.com/competitions/jigsaw-agile-community-rules)**,
run on Kaggle by Jigsaw, a unit of Google, in 2025.

Each example is a Reddit comment, one of that community's rules, and a few
example comments that do and do not break the rule. The task is to predict the
probability that the comment breaks the rule. Submissions are scored by AUC:
1.0 is perfect, 0.5 is guessing.

What makes it interesting is that the training data has only two rules ("No
advertising" and "No legal advice"), while the hidden test set adds rules the
model has never seen. That is exactly what a real moderation service faces
when a new community joins with its own rules. 2,445 teams took part, and the
best scored about 0.93. The competition has ended, but Kaggle still scores late
submissions, so in Session 4 you will submit your own model and see where it
would have placed.

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
else. Finish the missed one at home: its `./check` still works.

**Teams.** You work on your own server, but in a team of four with a captain.
Your team shares a GitHub repository, a row on the board, and an opponent in
the final session's game.

---

## Between sessions: at home

Between sessions you work at home, on your own:

- finish any mission you ran out of time for; its `./check` still works
- do the homework cards in `homework/`
- complete the sign-ups the next session needs

Homework is independent work. Nothing in a session depends on it, and it counts
towards your grade.

One sign-up takes time because of phone verification, so do it early: before
Session 4, a Kaggle account, verified with your phone, and joined to the Jigsaw
competition.

---

## The accounts you will use

All free.

| Account | When |
|---|---|
| GitHub, Google | before Session 1 |
| Google Cloud free trial | before Session 1, from the setup guide |
| OpenCode Zen, Google AI Studio key | Session 1 |
| Modal | Session 3 |
| Kaggle | at home, before Session 4 |
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
