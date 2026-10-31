# Homework — Your model in Open WebUI

**Done independently, at home.** Open WebUI from Seminar 2 already knows how to
call an OpenAI-compatible API. Add the endpoint you deployed today.

1. Redeploy your own model if you stopped it:

   ```bash
   cd ~/course/seminar_5
   modal deploy serve.py
   uv run client.py
   ```

2. Open your Seminar 2 Open WebUI through its SSH tunnel. In its admin
   connection settings, add an OpenAI-compatible connection. Use `MODEL_URL`
   and `MODEL_KEY` from your gateway's private `.env`. Select `moderator`.
   Save the key in the application, never in your git repository.

3. Ask it whether a comment breaks the advertising rule, and request only Yes
   or No. Try the base model too. Save three observations in
   `~/s5/homework.txt`, with no keys or private URLs.

4. Explain why this chat is not the same evaluation as the gateway: Open WebUI
   may use a different system prompt and thinking settings; its displayed
   answer does not expose the two candidate log probabilities. A generated
   “Yes” is not a calibrated probability or an AUC measurement.

5. Stop your model app when finished. Close the tunnel if you no longer need it.

**Done when:** both models appear in the provider connection, a chat completes,
and you can explain the difference between that chat and `/moderate`.
The instructor checks this demonstration; there is no automated homework check.
