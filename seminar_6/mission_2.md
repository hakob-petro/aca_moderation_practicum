# Mission 2 — Similar cases

**Mode:** with agent · **Time:** 25 minutes

A moderator decides faster and more consistently with precedent: comments like
this one, and what happened to them. The console finds them by meaning, not by
exact words. A small embedding model turns each comment into a vector; similar
comments get vectors that point the same way. Memory is the labelled training
comments plus every comment decided in your log, so it learns from each
decision at once, without retraining.

1. **Read `memory.py` and `routing.py`:**

   ```bash
   cd ~/s6/console
   less memory.py
   less routing.py
   ```

   Find what a case is, `embed()`, `Memory.similar()`, the **vote** (the share
   of the 10 nearest cases that broke the rule) and the **precedent** (the
   similarity of the nearest removed case).

2. **Ask your agent to fill two TODOs.** Start `opencode` here. Give it:

   > Read memory.py and routing.py. Implement nearest in memory.py with numpy:
   > the similarities are vectors @ query; return the k most similar rows as
   > (row index, similarity) pairs, most similar first, as Python int and float.
   > Implement route in routing.py: approve becomes review when precedent is at
   > least precedent_at; every other decision stays as it was. Change only these
   > two files. Explain each change. Do not read or print .env.

   Review the changes. `route()` only ever sends an approval to a human. A
   similar comment is a reason to look, not proof that this one breaks the
   rule.

3. **Rebuild and look:**

   ```bash
   docker compose up --build -d
   ```

   In the console, try a comment that copies one you already removed, then a
   rewording of it. Read the three similar cases and the vote. Moderate five
   more inbox comments: the log now stores each one's vote and precedent.

4. **Measure memory against the model:**

   ```bash
   cd ~/course/seminar_6
   ./evaluate
   ```

   For each of the 401 dev comments, it takes the vote of its 10 nearest
   training comments, and your model's score through the gateway. Both
   become a dev AUC, as in Seminars 3 and 4. It also counts the model's
   approvals that broke the rule, and how many of them the precedent rule
   sends to a person. Put both AUCs on the board.

5. **Check:**

   ```bash
   ./check 2
   ```

## Two “why” questions

1. The vote alone scores a lower AUC than your model. Why keep it in the
   console at all?
2. Why does a precedent send a comment to review instead of removing it?

**Bonus:** we measured that putting retrieved examples in the model's prompt
does not raise its AUC. Why might a fine-tuned model ignore the examples in
its prompt? The homework repeats that measurement with your model.
