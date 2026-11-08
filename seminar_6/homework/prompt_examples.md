# Homework — Does retrieval help the model?

**Done independently, at home.** In mission 2, the similar cases went to the
moderator. Could they help the model instead? The prompt already has slots for
two comments that break the rule and two that follow it, and your adapter
was trained with them filled. This measures what happens when you fill them
with the most similar labelled comments.

1. Redeploy your model if you stopped it, and warm it:

   ```bash
   cd ~/course/seminar_5
   modal deploy serve.py
   uv run client.py
   ```

2. Read `prompt_examples.py`, then run it:

   ```bash
   cd ~/course/seminar_6/homework
   uv run prompt_examples.py
   ```

   It scores the 401 dev comments four times, about 1,600 requests: with each
   comment's own examples (as in Seminar 4), the gateway's fixed examples, the
   two most similar rule-breaking and clean training comments, and none.
   Retrieval never uses a dev comment.

3. Run it once more for the untrained model: `uv run prompt_examples.py --model base`.

4. In `~/s6/homework.txt`, write the eight AUCs and three sentences: did
   retrieved examples help either model; why might a fine-tuned model hardly
   read its examples; and what, if anything, could make retrieval help.

5. Stop your model app when finished.

**Done when:** `~/s6/prompt_examples.json` exists and your three sentences
use your own numbers. The instructor reads them; there is no automated check.
