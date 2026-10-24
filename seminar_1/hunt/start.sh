#!/usr/bin/env bash
# Seminar 1, mission 2: sets up the scavenger hunt in ~/hunt.
# Every run picks new random answers, so neighbours' answers differ.
# Safe to run again: it starts the hunt over.
set -euo pipefail

H="$HOME/hunt"
S="$HOME/.hunt"

words=(apricot basalt cobalt dune ember fjord granite harbor indigo jasper
       kestrel lagoon meadow nectar onyx prairie quartz raven saffron tundra
       umber velvet willow xenon yarrow zephyr)
pick() { echo "${words[RANDOM % ${#words[@]}]}"; }
digest() { printf '%s' "$1" | tr '[:upper:]' '[:lower:]' | sha256sum | cut -d' ' -f1; }

# Start over: stop your old memory-hungry program, remove old files.
pkill -u "$USER" -x memory_hog 2>/dev/null || true
chmod -R u+rwx "$H" 2>/dev/null || true
rm -rf "$H" "$S"
mkdir -p "$H" "$S"

w_log=$(pick)
w_treasure=$(pick)
w_locked=$(pick)

# q3: a log whose last line holds a code word.
mkdir -p "$H/logs"
for i in $(seq 1 240); do
  printf '%s INFO request %d served in %dms\n' \
    "$(date -d "-$((240 - i)) min" '+%F %T')" "$i" "$((RANDOM % 400 + 20))"
done > "$H/logs/app.log"
printf '%s WARN shutting down, code word: %s\n' "$(date '+%F %T')" "$w_log" >> "$H/logs/app.log"

# q4: a treasure hidden inside folders whose names start with a dot.
mkdir -p "$H/.cache/x/.old/notes" "$H/docs" "$H/data"
echo "$w_treasure" > "$H/.cache/x/.old/notes/treasure.txt"
echo "Not here. Keep looking." > "$H/docs/readme.txt"
echo "id,comment" > "$H/data/comments.csv"

# q5, q6: a file you own but cannot read until you change its permissions.
echo "$w_locked" > "$H/locked.txt"
chmod 000 "$H/locked.txt"

# q1: a program that holds about 300 MB of memory, called memory_hog.
ln -sf "$(command -v python3)" "$S/memory_hog"
nohup "$S/memory_hog" -c '
import time
x = bytearray(b"\x01") * (300 * 1024 * 1024)
time.sleep(4 * 3600)
' >/dev/null 2>&1 &

# Hashed answers for ./check 2. The words themselves are not stored here.
{
  echo "q3=$(digest "$w_log")"
  echo "q4=$(digest "$w_treasure")"
  echo "q6=$(digest "$w_locked")"
} > "$S/answers"

sleep 2
echo
echo "The hunt is ready, in ~/hunt."
echo "Now:  mkdir -p ~/s1 && cp ~/course/seminar_1/templates/m2.txt ~/s1/m2.txt && nano ~/s1/m2.txt"
