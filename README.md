# Build a moderation service, end to end

Online communities have rules: "No advertising", "No legal advice". Moderators
cannot read every comment, so over six sessions you will build the service that
reads them first:

```
comment in → probability it breaks the rule → approve, send to a human, or remove
```

You will work on a Linux server in the cloud, fine-tune a language model on a
real Kaggle competition, deploy it, and build the moderator's console around it. Along the
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

Follow **[setup/STUDENT_SETUP.md](setup/STUDENT_SETUP.md)**: a GitHub account,
an SSH key, and that key added to GitHub. About 15 minutes. Then send your
GitHub username to the course chat.

**Where you work:** the whole class shares one server, each with your own
account on it. From Session 3 your GPU work runs on Modal, a cloud that rents
you a GPU for exactly as long as your code runs.

---

## The six sessions

Each session's mission cards and checks are in its folder:
[seminar_1](seminar_1/README.md), [seminar_2](seminar_2/README.md),
[seminar_3](seminar_3/README.md).

| Session | You will |
|---|---|
| 1. **Workspace** | find your way around Linux, work in git and GitHub, connect a coding agent to free model providers |
| 2. **Docker** | run, fix and compose containers, and learn what exposing a port really does |
| 3. **Train I: data and baseline** | run code on a cloud GPU, look at the data critically, see how a language model produces a probability, measure a baseline |
| 4. **Train II: fine-tune and submit** | fine-tune the model, compare your runs, submit to Kaggle, and find out how your score holds up on rules your model has never seen |
| 5. **Deploy** | serve your model, put your own service in front of it, make it survive failures, and stand up a second server in minutes |
| 6. **Product** | build the moderator console, log every decision, show similar past cases, and attack a classmate's console |

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
| OpenCode Zen, Google AI Studio key | Session 1 |
| Modal, with a payment method (no card? the class's account) | before Session 3 |
| Kaggle | at home, before Session 4 |
| OpenRouter | homework |

---

## Credit rules

You have free credit on Modal: $30 a month. Modal asks for a payment method
before it runs anything on a GPU, but charges nothing within the free credit.
If you have no card, you use the class's account instead. The course uses a
small part of the credit, as long as you follow three rules:

1. **Set your spend limit to $0** (Settings → Usage & Billing), so Modal can
   never charge you. On the class's account, your instructor has set it.
2. **Stop your Modal apps** at the end of each session.
3. **Never set `min_containers` in a Modal app.** It keeps a GPU running
   around the clock, about $19 a day.

---

## At the end of the course

Stop your Modal apps. Everything you built stays in your own GitHub
repository.
