#!/usr/bin/env bash
# Seminar 1, mission 3: counts for 15 minutes, one line every 10 seconds.
# Start it inside tmux. ./check 3 reads its log.
log="$HOME/s1/long_job.log"
mkdir -p "$HOME/s1"

if [ -n "${TMUX:-}" ]; then where=tmux; else where=plain; fi
echo "started $(date +%s) in $where" > "$log"
[ "$where" = plain ] && echo "Warning: you are not inside tmux. Press Ctrl+C, run: tmux new -s long, then start this again."

for i in $(seq 1 90); do
  echo "tick $i $(date '+%H:%M:%S')" | tee -a "$log"
  sleep 10
done
echo "finished $(date +%s)" >> "$log"
echo "Done: the job ran for 15 minutes."
