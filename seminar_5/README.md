# Seminar 5 — Deploy

Your model answered a notebook. Today it answers an API, through a service you
can restart, test under load, and recreate from git.

```text
laptop → SSH tunnel → your Docker gateway on the class server → vLLM on Modal
                       approve / review / remove                 base + LoRA
```

**vLLM** loads a model once and batches requests from many callers. Its
OpenAI-compatible API lets us use the OpenAI Python client with our own model;
these requests go to Modal, not to OpenAI. The **gateway** is your small web
service: it checks the caller, asks the model, and applies your decision policy.

## Before you start

You need rootless Docker from Seminar 2, a working Modal account, and an adapter
from Seminar 4. Kaggle does not need to have finished scoring it.

```bash
ssh ws
cd ~/course && git pull
docker info
echo "$MYPORT"
modal profile current
ls ~/s4/results
cd ~/course/seminar_5
```

Today's work goes in `~/s5`; `./prepare` creates `~/s5/gateway` for your
service. No personal GitHub repository or GitHub login is required. Mission 4
creates a local Git repository to practise rebuilding from committed code.

Already prepared with a different path? Run `./prepare` to see the saved gateway
path and use it in place of `~/s5/gateway`. Your existing files are kept.

Your gateway uses `$MYPORT+2`; the recovery drill uses `$MYPORT+3`. Seminar 2's
Open WebUI can keep using `$MYPORT+1`. Nothing needs `sudo` or a firewall change.

## Missions

| # | Mission | Mode | Minutes |
|---|---|---|---|
| 0 | Architecture and what we are deploying | together | 5 |
| 1 | [Serve your model](mission_1.md) | by hand | 25 |
| 2 | [Build the gateway](mission_2.md) | with agent | 30 |
| – | Break | | 5 |
| 3 | [Break it and measure it](mission_3.md) | by hand | 30 |
| 4 | [Rebuild from git](mission_4.md) | by hand | 20 |
| – | Results and shutdown | together | 5 |

Run `./check N` from this folder after each mission. Run `./catchup N` if you
are behind. A failed check prints what still needs fixing; finish it at home.

## What you keep

| Location | Contents |
|---|---|
| `~/s5/gateway/` | your gateway source, Dockerfile and Compose configuration; commit these |
| `~/s5/gateway/.env` | private keys and runtime settings; ignored by git and excluded from the image |
| `~/s5/serve.json`, `~/s5/model.env` | model deployment settings and its private key |
| your `aca-s5-…` Modal volume | a hash-checked copy of the Seminar 4 adapter |
| `~/s5/calls.jsonl`, `failure.json`, `load.json`, `recovery.json` | measurements and drill results |

The model returns `score = logit(Yes) − logit(No)` and
`p_yes = sigmoid(score)`. `p_yes` is conditional on the two candidate answers;
it is **not a calibrated probability of a rule violation**. Today's 0.30 and
0.80 thresholds demonstrate a policy. AUC alone cannot choose them. See the
[evaluation report](../materials/seminar_3/yes_no_scores_and_auc.md) before
claiming a false-positive rate or deploying automatic removal for real users.

## After class

Leave the gateway source ready for Seminar 6's console. Stop your model app
from the [Modal dashboard](https://modal.com/apps), or use `modal app stop APP_ID`
with the ID from `modal app list`. Stop only your own `aca-s5-…` app. An idle
deployment can scale to zero, but repeated requests keep its GPU billable.
Do not set `min_containers=1` for this exercise.

You may leave the small CPU gateway running, or stop it with
`cd ~/s5/gateway && docker compose down`. Before using it next time,
redeploy `serve.py`, warm the model with `uv run client.py`, and start Compose.

**Homework:** [Connect your model to Open WebUI](homework/openwebui.md).
