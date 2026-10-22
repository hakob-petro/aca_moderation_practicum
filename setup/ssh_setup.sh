#!/usr/bin/env bash
# SSH setup for the course server, on your own computer (macOS or Linux).
#
#   curl -fsSL https://raw.githubusercontent.com/hakob-petro/aca_moderation_practicum/main/setup/ssh_setup.sh | bash -s -- key USERNAME
#   curl -fsSL https://raw.githubusercontent.com/hakob-petro/aca_moderation_practicum/main/setup/ssh_setup.sh | bash -s -- config USERNAME IP
#
# key     makes your SSH key if you have none, and prints the line to paste in
#         Cloud Shell. An existing ~/.ssh/id_ed25519 is reused, never replaced.
# config  adds a "ws" shortcut to ~/.ssh/config and tests the connection.
#         It only touches the block it writes itself, and keeps a backup.
set -euo pipefail

RAW=https://raw.githubusercontent.com/hakob-petro/aca_moderation_practicum/main/setup
BEGIN='# >>> course workspace >>>'
END='# <<< course workspace <<<'

die() { echo "ERROR: $*" >&2; exit 1; }

check_user() {
  [[ ${1:-} =~ ^[a-z][a-z0-9_-]{0,30}$ ]] \
    || die "USERNAME must be lowercase English letters, for example ani."
}

do_key() {
  local user=$1 key=$HOME/.ssh/id_ed25519
  command -v ssh-keygen >/dev/null || die "ssh-keygen is not installed."
  mkdir -p "$HOME/.ssh"
  chmod 700 "$HOME/.ssh"
  if [ -f "$key" ]; then
    echo "You already have a key ($key). It is reused, not replaced."
  else
    ssh-keygen -q -t ed25519 -C "$user" -N '' -f "$key"
    echo "Made your key: $key"
  fi
  [ -f "$key.pub" ] || ssh-keygen -y -f "$key" >"$key.pub"
  cat <<EOF

Your public key (safe to share; the file without .pub never is):

$(cat "$key.pub")

Next: open Cloud Shell in the Google Cloud console (the >_ button at the top
right), paste this whole line and press Enter:

curl -fsSL $RAW/create_server.sh | bash -s -- $user "$(cat "$key.pub")"
EOF
}

do_config() {
  local user=$1 ip=$2 cfg=$HOME/.ssh/config rest ok=0 i out
  [[ $ip =~ ^[0-9]{1,3}(\.[0-9]{1,3}){3}$ ]] || die "IP must look like 34.123.45.67."
  mkdir -p "$HOME/.ssh"
  chmod 700 "$HOME/.ssh"
  touch "$cfg"
  chmod 600 "$cfg"

  # Everything in the config except an older block of ours.
  rest=$(mktemp)
  awk -v b="$BEGIN" -v e="$END" '
    $0 == b { skip = 1 }
    !skip   { print }
    $0 == e { skip = 0 }
  ' "$cfg" >"$rest"
  if grep -Eiq '^[[:space:]]*host[[:space:]]+([^#]*[[:space:]])?ws([[:space:]]|$)' "$rest"; then
    rm -f "$rest"
    die "Your $cfg already has a 'Host ws' entry that this script did not write. Delete or rename it, then run this again."
  fi

  if [ -s "$cfg" ]; then
    cp "$cfg" "$cfg.bak-$(date +%Y%m%d%H%M%S)"
  fi
  { [ -s "$rest" ] && [ -n "$(tail -c 1 "$rest")" ] && echo; } >>"$rest" || true
  cat >>"$rest" <<EOF
$BEGIN
Host ws
    HostName $ip
    User $user
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
$END
EOF
  cat "$rest" >"$cfg"
  rm -f "$rest"
  echo "Added the ws shortcut to $cfg"

  echo "Testing the connection (a new server can need a minute to be ready)..."
  for i in 1 2 3 4 5 6 7 8 9 10 11 12; do
    # -n: ssh must not read stdin, which is this script when run through curl.
    if out=$(ssh -n -F "$cfg" -o BatchMode=yes -o ConnectTimeout=10 \
        -o StrictHostKeyChecking=accept-new ws true 2>&1); then
      ok=1
      break
    fi
    sleep 5
  done
  if [ "$ok" -eq 1 ]; then
    echo
    echo "Connected. From now on, type:  ssh ws"
  else
    echo
    echo "Could not log in yet. The last message was:"
    echo "$out"
    echo
    echo "Wait a minute and type:  ssh ws"
    echo "If it still fails, see 'If something goes wrong' in the guide and send the exact error to the course chat."
    return 1
  fi
}

main() {
  case ${1:-} in
    key)    check_user "${2:-}"; do_key "$2" ;;
    config) check_user "${2:-}"; do_config "$2" "${3:-}" ;;
    *)      die "Usage: key USERNAME   or   config USERNAME IP" ;;
  esac
}

main "$@"
