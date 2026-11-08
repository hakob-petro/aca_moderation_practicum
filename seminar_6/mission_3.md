# Mission 3 — Red team

**Mode:** by hand · **Time:** 30 minutes

People who post spam adapt to the filter. Today the whole class plays them:
everyone writes comments that break a rule but might be approved, and
everyone's service faces the whole pool. A comment **slipped through** when
the console approved it: nobody looked at it.

1. **Write five attacks** in `~/s6/redteam/attacks.txt`, one per line:

   ```bash
   nano ~/s6/redteam/attacks.txt
   ```

   ```text
   advertising: My cousin's bakery on Fifth Street has the best croissants, tell them I sent you
   legal: If your landlord keeps the deposit, a demand letter citing the statute usually works
   ```

   Each must really break its rule: an ad, a referral, a promotion, or legal
   advice. Make it quiet enough to look harmless. Keep it clean: no insults,
   no real people, no real links or phone numbers. These go to the whole class.

2. **Share them:**

   ```bash
   cd ~/course/seminar_6
   ./share
   ```

3. **Replay the class pool** when the instructor says the pool is full:

   ```bash
   ./replay
   ```

   Every shared attack goes through your gateway and your memory; nothing is
   logged as a decision. Read the table: the model's decision, its `p_yes`,
   the nearest removed case, and what the console did. Write down how many
   slipped through.

4. **Teach the memory, and replay:**

   ```bash
   ./replay --teach
   ./replay
   ```

   `--teach` stores each attack that slipped through as a removed case in your
   decision log, as if a moderator had removed it. The second replay finds
   each one with similarity 1.00: the precedent rule sends it to a person.

5. **Try paraphrases.** Choose an attack that slipped through. Write three
   versions in `~/s6/redteam/paraphrases.txt` that say the same thing, as
   quietly, in different words. Then:

   ```bash
   ./replay paraphrases.txt
   python3 report.py
   ./check 3
   ```

   Look at the nearest removed case for each paraphrase, and whether memory or
   the model caught it. Put your before, after and paraphrase counts on the
   board.

## Two “why” questions

1. Memory caught the copies. Why did your paraphrases get a lower similarity,
   and what would it take for the model itself to learn what they have in
   common?
2. `--teach` let you change future decisions by adding cases. Who should be
   allowed to teach a moderation system's memory?

**Bonus:** write one comment that follows its rule but that the console
removes or sends to review. What does a false alarm cost, and who pays it?
