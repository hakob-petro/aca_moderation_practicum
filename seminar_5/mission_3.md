# Mission 3 — Break it and measure it

**Mode:** by hand · **Time:** 30 minutes

A useful service has predictable failures. A broken model must not become an
“approve” decision. A crashed gateway should restart. A latency number needs
both the workload and its error count.

1. **Read the failure drill before running it:**

   ```bash
   cd ~/course/seminar_5
   less verify_deploy.py
   python3 verify_deploy.py
   ```

   It terminates the server process inside your gateway container and waits
   for Docker to restart it.
   `docker stop` or `docker kill` is a deliberate operator action and suppresses
   the restart policy; the drill signals the server process from inside instead.
   It then temporarily replaces the upstream model with a small HTTP service
   that produces three controlled faults:

   | Fault | Gateway response |
   |---|---|
   | model unavailable | 503, no decision |
   | model takes ten seconds; test deadline is two | 504 in about two seconds, no decision |
   | model returns malformed data | 502, no decision |

   This tests the gateway's behaviour, not Modal's outage behaviour. It avoids
   stopping another student's shared model. The drill restores the real URL
   and normal deadline even when a check fails or you press Ctrl+C.
   If the shell itself is killed, restore manually with
   `cd ~/s5/gateway && docker compose up -d --force-recreate gateway`.

2. **Read a log line:**

   ```bash
   cd ~/s5/gateway
   docker compose logs --tail 15
   ```

   Find `status`, `ms`, and `request_id`. A successful response returns that
   same ID so you can find its log. Comments and API keys are not logged.
   These rotating container logs help diagnose failures; Seminar 6 adds a
   persistent decision log for moderators.

3. **Warm the real model and send 200 requests:**

   ```bash
   cd ~/course/seminar_5
   uv run client.py
   python3 load.py
   cat ~/s5/load.json
   ```

   Four callers run concurrently. `p50` is the median successful request;
   `p95` is the time at or below which 95% of successful requests finished.
   The script uses the nearest-rank definition and reports errors separately.
   If errors are nonzero, fix the cause and rerun; fast failures are not fast
   inference. Put p50, p95, successes and concurrency on the board.

   This default test measures **class server → gateway → Modal**, with a warm
   model and similar prompts. It excludes your laptop's network; shared
   prefixes can hit vLLM's cache. It is not a maximum-capacity benchmark.

4. **Check:**

   ```bash
   ./check 3
   ```

## Two “why” questions

1. Why do we report p95 as well as an average? What does it omit if we report
   successful requests only?
2. Why could automatic retries make an overloaded model even slower?

**Bonus: include your laptop's network.** Download `load.py` and `common.py`
to a local folder, create a private file containing only
`GATEWAY_KEY=YOUR_KEY` and `PORT=8000` (`chmod 600 laptop.env`), keep mission 2's
tunnel open, then run:

```bash
python3 load.py --url http://127.0.0.1:8000 --env laptop.env --output laptop-load.json
```

Compare it with the server result at the same concurrency. Never copy the
model key just to test the gateway.
