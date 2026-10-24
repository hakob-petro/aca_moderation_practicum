#!/usr/bin/env bash
# Session 2 on the shared class server: Docker for every student, rootless.
# For the instructor. Run once, as root, after provision.sh and after adding
# the students:
#
#   curl -fsSL https://raw.githubusercontent.com/hakob-petro/aca_moderation_practicum/main/setup/class_server/docker_rootless.sh | sudo bash
#
# Each student gets their own Docker daemon, running as them: they see only
# their own containers and images, and their containers count against their
# own memory and CPU limits. Each student also gets 10 ports of their own,
# starting at $MYPORT. Students added later get Docker from class-add-student.
# Safe to run again.
set -euo pipefail

[ "$(id -u)" -eq 0 ] || { echo "Run as root: curl ... | sudo bash" >&2; exit 1; }
say() { printf '\n==> %s\n' "$*"; }

say "Docker packages"
if ! command -v docker >/dev/null; then
  curl -fsSL https://get.docker.com | sh >/dev/null
fi
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
  uidmap dbus-user-session slirp4netns iptables iproute2 kmod docker-ce-rootless-extras >/dev/null

say "Load the nf_tables kernel module: rootless Docker needs it, and only root can load it"
modprobe nf_tables 2>/dev/null || echo "Could not load nf_tables; students' Docker will run without iptables."
echo nf_tables > /etc/modules-load.d/class-docker.conf

say "Stop the system-wide Docker: every student runs their own"
systemctl disable --now docker.service docker.socket >/dev/null 2>&1 || true

say "Allow rootless Docker under Ubuntu 24.04's AppArmor"
cat > /etc/apparmor.d/usr.bin.rootlesskit <<'EOF'
abi <abi/4.0>,
include <tunables/global>

/usr/bin/rootlesskit flags=(unconfined) {
  userns,

  include if exists <local/usr.bin.rootlesskit>
}
EOF
apparmor_parser -r /etc/apparmor.d/usr.bin.rootlesskit 2>/dev/null || systemctl reload apparmor 2>/dev/null || true

say "DOCKER_HOST and MYPORT for every login"
cat > /etc/profile.d/class-docker.sh <<'EOF'
# Each student's own Docker, and their own 10 ports: MYPORT to MYPORT+9.
export DOCKER_HOST="unix:///run/user/$(id -u)/docker.sock"
export MYPORT=$(( 10000 + ($(id -u) - 1000) * 10 ))
EOF

say "The class-docker-user command"
cat > /usr/local/sbin/class-docker-user <<'EOF'
#!/usr/bin/env bash
# Sets up rootless Docker for one student.   sudo class-docker-user USERNAME
set -uo pipefail
user="${1:?Usage: class-docker-user USERNAME}"
uid=$(id -u "$user") || exit 1
home="/home/$user"
sock="/run/user/$uid/docker.sock"
log="$home/.docker-setup.log"

if ! grep -q "^$user:" /etc/subuid || ! grep -q "^$user:" /etc/subgid; then
  echo "$user: no /etc/subuid or /etc/subgid entry; rootless Docker needs one" >&2
  exit 1
fi
loginctl enable-linger "$user"
for _ in $(seq 1 40); do [ -S "/run/user/$uid/bus" ] && break; sleep 0.5; done

as_user() {
  sudo -u "$user" env HOME="$home" XDG_RUNTIME_DIR="/run/user/$uid" \
    DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$uid/bus" \
    DOCKER_HOST="unix://$sock" PATH=/usr/bin:/bin:/usr/sbin:/sbin "$@"
}

# Pull from Google's mirror of Docker Hub: twenty students behind one IP
# address would otherwise hit Docker Hub's limit on anonymous downloads.
install -d -m 755 -o "$user" -g "$user" "$home/.config" "$home/.config/docker"
echo '{ "registry-mirrors": ["https://mirror.gcr.io"] }' > "$home/.config/docker/daemon.json"
chown "$user:$user" "$home/.config/docker/daemon.json"

if [ ! -S "$sock" ]; then
  if ! as_user dockerd-rootless-setuptool.sh install > "$log" 2>&1; then
    # Without nf_tables, fall back to Docker without iptables: published ports
    # still work; containers lose outbound internet, which today's missions do
    # not need.
    if grep -q -- '--skip-iptables' "$log"; then
      echo "Retrying with --skip-iptables" >> "$log"
      as_user dockerd-rootless-setuptool.sh install --skip-iptables >> "$log" 2>&1
    fi
  fi
  chown "$user:$user" "$log"
fi
as_user systemctl --user enable --now docker >/dev/null 2>&1
as_user systemctl --user restart docker >/dev/null 2>&1

for _ in $(seq 1 40); do as_user docker info >/dev/null 2>&1 && break; sleep 1; done
if as_user docker info >/dev/null 2>&1; then
  for img in hello-world nginx:1.27-alpine python:3.12-slim; do
    as_user docker pull -q "$img" >/dev/null 2>&1 || echo "$user: could not pull $img"
  done
  printf '%-20s Docker OK, ports %s-%s\n' "$user" $((10000 + (uid - 1000) * 10)) $((10009 + (uid - 1000) * 10))
else
  printf '%-20s Docker FAILED: see %s\n' "$user" "$log"
  exit 1
fi
EOF
chmod 755 /usr/local/sbin/class-docker-user

say "Docker for every student already added"
failed=0
while read -r user gh; do
  [ -z "${user:-}" ] && continue
  /usr/local/sbin/class-docker-user "$user" || failed=$((failed + 1))
done < /etc/class/students

say "Done"
if [ "$failed" -gt 0 ]; then
  echo "$failed student(s) FAILED. The usual cause is AppArmor blocking user namespaces;"
  echo "check with:  sudo -iu USERNAME dockerd-rootless-setuptool.sh check"
  echo "Last resort: sudo sysctl -w kernel.apparmor_restrict_unprivileged_userns=0, then run this again."
fi
echo "Students added later get Docker automatically from class-add-student."
echo "For the exposure step in mission 4, open TCP 10000-10999 in the cloud firewall, then close it after the session."
