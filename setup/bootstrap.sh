#!/usr/bin/env bash
# Course workspace setup for Ubuntu 24.04 (Google Cloud e2-medium).
#
#   curl -fsSL https://raw.githubusercontent.com/hakob-petro/aca_moderation_practicum/main/setup/bootstrap.sh | bash
#
# Run as your normal user, not root. Safe to run again after a failure.
#
# Installs only what needs sudo: git, tmux, nano, Docker, GitHub CLI.
# Students install OpenCode, uv, Modal and Kaggle themselves during the
# lessons, each when first needed.
set -euo pipefail

if [ "$(id -u)" -eq 0 ]; then
  echo "Run this as your normal user, without sudo in front." >&2
  exit 1
fi

say() { printf '\n==> %s\n' "$*"; }

say "System packages"
sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
  git tmux nano curl ca-certificates jq htop unzip >/dev/null
sudo timedatectl set-timezone Asia/Yerevan

say "2 GB of swap, so builds do not run out of memory"
if ! swapon --show | grep -q '/swapfile'; then
  [ -f /swapfile ] || sudo fallocate -l 2G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile >/dev/null
  sudo swapon /swapfile
fi
grep -q '^/swapfile ' /etc/fstab || echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab >/dev/null

say "Docker"
if ! command -v docker >/dev/null; then
  curl -fsSL https://get.docker.com | sudo sh >/dev/null
fi
sudo usermod -aG docker "$USER"

say "GitHub CLI"
if ! command -v gh >/dev/null; then
  sudo mkdir -p -m 755 /etc/apt/keyrings
  curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
    | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg >/dev/null
  sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
    | sudo tee /etc/apt/sources.list.d/github-cli.list >/dev/null
  sudo apt-get update -qq
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq gh >/dev/null
fi

say "The ws-check command"
mkdir -p "$HOME/.local/bin"
cat > "$HOME/.local/bin/ws-check" <<'CHECK'
#!/usr/bin/env bash
# Prints PASS or FAIL for everything the course needs on this server
# before Session 1.
pass=0; fail=0
ok()  { printf 'PASS  %-9s %s\n' "$1" "$2"; pass=$((pass + 1)); }
bad() { printf 'FAIL  %-9s %s\n' "$1" "$2"; fail=$((fail + 1)); }

. /etc/os-release
if [ "$VERSION_ID" = "24.04" ]; then ok os "$PRETTY_NAME"
else bad os "$PRETTY_NAME (expected Ubuntu 24.04)"; fi

mem=$(awk '/MemTotal/ {printf "%.1f", $2 / 1048576}' /proc/meminfo)
if awk -v m="$mem" 'BEGIN { exit !(m >= 3.5) }'; then ok memory "$mem GB"
else bad memory "$mem GB (expected 4 GB: machine type e2-medium)"; fi

free_gb=$(df -BG --output=avail / | tail -n 1 | tr -dc '0-9')
if [ "$free_gb" -ge 15 ]; then ok disk "$free_gb GB free"
else bad disk "$free_gb GB free (expected a 30 GB disk)"; fi

if swapon --show | grep -q .; then ok swap "$(free -h | awk '/Swap/ {print $2}')"
else bad swap "none: run the setup script again"; fi

for c in git nano gh; do
  if command -v "$c" >/dev/null 2>&1; then
    ver=$("$c" --version 2>/dev/null | head -n 1)
    ok "$c" "${ver:-installed}"
  else
    bad "$c" "not found: run the setup script again"
  fi
done

if command -v tmux >/dev/null; then ok tmux "$(tmux -V)"
else bad tmux "not found: run the setup script again"; fi

if docker run --rm hello-world >/dev/null 2>&1; then ok docker "$(docker --version)"
elif command -v docker >/dev/null; then bad docker "installed, but needs a fresh login: type exit, then ssh ws, then ws-check"
else bad docker "not found: run the setup script again"; fi

ip=$(curl -fsS --max-time 5 https://api.ipify.org 2>/dev/null || echo unknown)
echo
echo "user: $USER   host: $(hostname)   public IP: $ip"
if [ "$fail" -eq 0 ]; then
  echo "ALL $pass CHECKS PASSED. Send this whole block to the course chat."
else
  echo "$fail CHECK(S) FAILED. Send this whole block to the course chat anyway."
fi
CHECK
chmod +x "$HOME/.local/bin/ws-check"

say "Done"
echo "Now type:  exit"
echo "Then:      ssh ws"
echo "Then:      ws-check"
