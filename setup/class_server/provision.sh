#!/usr/bin/env bash
# The shared class server for Seminars 1 and 2. For the instructor.
# Run once, as root, on a fresh Ubuntu 24.04 machine:
#
#   curl -fsSL https://raw.githubusercontent.com/hakob-petro/aca_moderation_practicum/main/setup/class_server/provision.sh | sudo bash
#
# Then add each student with:   sudo class-add-student GITHUB_USERNAME
#                          or:   sudo class-add-student --key "ssh-ed25519 AAAA..." USERNAME
#
# Do not add students' keys through the cloud console: on Google Cloud, accounts
# made from console SSH keys get sudo, and then every student can read everyone's
# files.
#
# Every student gets their own Linux account (no sudo), a private home folder,
# memory and CPU limits, the course repository in ~/course, and their SSH keys
# copied from github.com/GITHUB_USERNAME.keys every minute.
# Safe to run again.
set -euo pipefail

[ "$(id -u)" -eq 0 ] || { echo "Run as root: curl ... | sudo bash" >&2; exit 1; }
say() { printf '\n==> %s\n' "$*"; }

say "Packages"
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
  git tmux nano curl ca-certificates jq htop unzip python3 cron >/dev/null
timedatectl set-timezone Asia/Yerevan 2>/dev/null || ln -sf /usr/share/zoneinfo/Asia/Yerevan /etc/localtime

say "GitHub CLI"
if ! command -v gh >/dev/null; then
  mkdir -p -m 755 /etc/apt/keyrings
  curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg -o /etc/apt/keyrings/githubcli-archive-keyring.gpg
  chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
    > /etc/apt/sources.list.d/github-cli.list
  apt-get update -qq
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq gh >/dev/null
fi

say "Private home folders"
if grep -qE '^#?[[:space:]]*HOME_MODE' /etc/login.defs; then
  sed -i -E 's/^#?[[:space:]]*HOME_MODE.*/HOME_MODE 0750/' /etc/login.defs
else
  echo 'HOME_MODE 0750' >> /etc/login.defs
fi

say "Per-student limits: 3 GB of memory, 2 CPUs, 512 processes"
mkdir -p /etc/systemd/system/user-.slice.d
cat > /etc/systemd/system/user-.slice.d/50-class-limits.conf <<'EOF'
[Slice]
MemoryMax=3G
CPUQuota=200%
TasksMax=512
EOF
systemctl daemon-reload 2>/dev/null || true

say "Class scripts"
mkdir -p /etc/class
touch /etc/class/students

cat > /usr/local/sbin/class-sync-keys <<'EOF'
#!/usr/bin/env bash
# Copies students' public SSH keys from GitHub into their accounts.
# Runs every minute from cron.   class-sync-keys [username]
set -uo pipefail
while read -r user gh; do
  [ -z "${user:-}" ] && continue
  [ -n "${1:-}" ] && [ "$user" != "$1" ] && continue
  [ "$gh" = "-" ] && continue   # added with --key: keys are managed by hand
  home="/home/$user"
  [ -d "$home" ] || continue
  keys=$(curl -fsS -m 10 "https://github.com/$gh.keys" 2>/dev/null) || continue
  [ -n "$keys" ] || continue
  install -d -m 700 -o "$user" -g "$user" "$home/.ssh"
  printf '%s\n' "$keys" > "$home/.ssh/authorized_keys.new"
  chown "$user:$user" "$home/.ssh/authorized_keys.new"
  chmod 600 "$home/.ssh/authorized_keys.new"
  mv "$home/.ssh/authorized_keys.new" "$home/.ssh/authorized_keys"
done < /etc/class/students
EOF

cat > /usr/local/sbin/class-add-student <<'EOF'
#!/usr/bin/env bash
# Adds a student, without sudo.
#   sudo class-add-student GITHUB_USERNAME [SERVER_USERNAME]
#       keys copied from github.com/GITHUB_USERNAME.keys, refreshed every minute
#   sudo class-add-student --key "ssh-ed25519 AAAA... comment" SERVER_USERNAME
#       the given public key; add more keys by running it again
set -euo pipefail
[ "$(id -u)" -eq 0 ] || { echo "Run with sudo." >&2; exit 1; }

key=""
if [ "${1:-}" = "--key" ]; then
  key="${2:?Usage: class-add-student --key \"PUBLIC KEY\" SERVER_USERNAME}"
  user="${3:?Usage: class-add-student --key \"PUBLIC KEY\" SERVER_USERNAME}"
  gh="-"
  case "$key" in ssh-*|ecdsa-*|sk-*) ;; *) echo "That does not look like a public key: $key" >&2; exit 1 ;; esac
  # Keep the username exactly as given (dots and capitals too): it is what the
  # student already has after User in ~/.ssh/config.
  printf '%s' "$user" | grep -Eq '^[A-Za-z_][A-Za-z0-9._-]{0,31}$' \
    || { echo "Not a valid username: $user (letters, digits, . _ -, at most 32)" >&2; exit 1; }
else
  gh="${1:?Usage: class-add-student GITHUB_USERNAME [SERVER_USERNAME], or --key \"PUBLIC KEY\" SERVER_USERNAME}"
  user="${2:-$gh}"
  user=$(printf '%s' "$user" | tr '[:upper:]' '[:lower:]' | tr -c 'a-z0-9_-' '_')
  case "$user" in [a-z_]*) ;; *) user="u$user" ;; esac
  user="${user:0:32}"
fi

id "$user" >/dev/null 2>&1 || useradd -m -s /bin/bash "$user"
chmod 750 "/home/$user"
awk -v u="$user" '$1 == u {found=1} END {exit !found}' /etc/class/students || echo "$user $gh" >> /etc/class/students

if [ -n "$key" ]; then
  install -d -m 700 -o "$user" -g "$user" "/home/$user/.ssh"
  touch "/home/$user/.ssh/authorized_keys"
  grep -qxF "$key" "/home/$user/.ssh/authorized_keys" || printf '%s\n' "$key" >> "/home/$user/.ssh/authorized_keys"
  chown "$user:$user" "/home/$user/.ssh/authorized_keys"
  chmod 600 "/home/$user/.ssh/authorized_keys"
else
  /usr/local/sbin/class-sync-keys "$user"
fi

if [ ! -d "/home/$user/course/.git" ]; then
  sudo -u "$user" git clone -q https://github.com/hakob-petro/aca_moderation_practicum.git "/home/$user/course"
fi

# Docker, once docker_rootless.sh has been run on this server.
if [ -x /usr/local/sbin/class-docker-user ]; then /usr/local/sbin/class-docker-user "$user" >/dev/null || echo "$user: Docker setup FAILED, see /home/$user/.docker-setup.log"; fi

keys=$(grep -c . "/home/$user/.ssh/authorized_keys" 2>/dev/null || echo 0)
if [ "$gh" = "-" ]; then note="$keys SSH key(s), added by hand"
elif [ "$keys" -gt 0 ]; then note="$keys SSH key(s) from GitHub"
else note="no SSH key on GitHub yet; it is picked up within a minute of being added"; fi
uid=$(id -u "$user")
printf '%-20s ports %s-%s   %s\n' "$user" $((10000 + (uid - 1000) * 10)) $((10009 + (uid - 1000) * 10)) "$note"
EOF

cat > /usr/local/sbin/class-list <<'EOF'
#!/usr/bin/env bash
# Lists students: server username, GitHub username, keys, logged in now.
printf '%-20s %-20s %-12s %-6s %s\n' USER GITHUB PORTS KEYS "LOGGED IN"
while read -r user gh; do
  [ -z "${user:-}" ] && continue
  uid=$(id -u "$user" 2>/dev/null) || continue
  keys=$(grep -c . "/home/$user/.ssh/authorized_keys" 2>/dev/null || echo 0)
  on=$(who | awk -v u="$user" '$1 == u {print "yes"; exit}')
  printf '%-20s %-20s %-12s %-6s %s\n' "$user" "$gh" "$((10000 + (uid - 1000) * 10))-$((10009 + (uid - 1000) * 10))" "$keys" "${on:-no}"
done < /etc/class/students
EOF

cat > /usr/local/sbin/class-modal-token <<'EOF'
#!/usr/bin/env bash
# Gives a student without a card the class's Modal account (Seminar 3 onwards).
#
#   ... | sudo class-modal-token USERNAME       the token comes in on stdin
#   sudo class-modal-token --remove USERNAME    takes it away again
#
# stdin is the "modal token set --token-id ak-... --token-secret as-..." line
# that Modal shows when you create a token. It becomes the profile "aca-class"
# in the student's ~/.modal.toml, and their active one. The token is never
# printed.
set -euo pipefail
[ "$(id -u)" -eq 0 ] || { echo "Run with sudo." >&2; exit 1; }
remove=0
if [ "${1:-}" = "--remove" ]; then remove=1; shift; fi
user="${1:?Usage: ... | sudo class-modal-token USERNAME   or   sudo class-modal-token --remove USERNAME}"
id "$user" >/dev/null 2>&1 || { echo "No user called $user." >&2; exit 1; }
file="/home/$user/.modal.toml"
input=""
[ "$remove" -eq 0 ] && input="$(cat)"

REMOVE="$remove" INPUT="$input" python3 - "$file" <<'PY'
import os, re, sys, tomllib
from pathlib import Path

path = Path(sys.argv[1])
profiles = tomllib.loads(path.read_text()) if path.exists() else {}
if os.environ["REMOVE"] == "1":
    if profiles.pop("aca-class", None) is None:
        sys.exit("No class token there.")
    if profiles and not any(p.get("active") for p in profiles.values()):
        next(iter(profiles.values()))["active"] = True
else:
    token_id = re.search(r"\bak-[A-Za-z0-9]+", os.environ["INPUT"])
    token_secret = re.search(r"\bas-[A-Za-z0-9]+", os.environ["INPUT"])
    if not (token_id and token_secret):
        sys.exit("No token on stdin: pipe in the 'modal token set --token-id ak-... --token-secret as-...' line.")
    for p in profiles.values():
        p["active"] = False
    profiles["aca-class"] = {"token_id": token_id.group(), "token_secret": token_secret.group(), "active": True}

def value(v):
    return ("true" if v else "false") if isinstance(v, bool) else '"' + str(v).replace("\\", "\\\\").replace('"', '\\"') + '"'

path.write_text("".join(
    f"[{name}]\n" + "".join(f"{k} = {value(v)}\n" for k, v in fields.items()) + "\n"
    for name, fields in profiles.items()
))
PY
[ -f "$file" ] && { chown "$user:$user" "$file"; chmod 600 "$file"; }
if [ "$remove" -eq 1 ]; then echo "$user: class Modal token removed"
else echo "$user now uses the class's Modal account (profile aca-class)"; fi
EOF

chmod 755 /usr/local/sbin/class-sync-keys /usr/local/sbin/class-add-student /usr/local/sbin/class-list /usr/local/sbin/class-modal-token
echo '* * * * * root /usr/local/sbin/class-sync-keys' > /etc/cron.d/class-sync-keys
systemctl enable --now cron >/dev/null 2>&1 || true

say "Done"
echo "Add students:   sudo class-add-student GITHUB_USERNAME"
echo "            or: sudo class-add-student --key \"ssh-ed25519 AAAA...\" USERNAME"
echo "See them:       sudo class-list"
echo "Class Modal account for a student without a card:  ... | sudo class-modal-token USERNAME"
echo "Students log in with:  ssh SERVER_USERNAME@$(curl -fsS -m 5 https://api.ipify.org 2>/dev/null || echo THIS-SERVER-IP)"
