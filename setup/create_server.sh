#!/usr/bin/env bash
# Creates your course server in Google Cloud. Run it in Cloud Shell:
#
#   curl -fsSL https://raw.githubusercontent.com/hakob-petro/aca_moderation_practicum/main/setup/create_server.sh | bash -s -- USERNAME "ssh-ed25519 AAAA..."
#
# Does what steps 4 and 5 of STUDENT_SETUP.md do by hand: a monthly budget
# that only sends emails, a static IP called ws-ip, and the server ws
# (e2-medium, Ubuntu 24.04, 50 GB disk). Safe to run again: anything that
# already exists is left alone.
set -euo pipefail

RAW=https://raw.githubusercontent.com/hakob-petro/aca_moderation_practicum/main/setup
NAME=${NAME:-ws}          # the instructor can set NAME=ws-test to try it out
REGION=us-central1
BUDGET=30

die() { echo "ERROR: $*" >&2; exit 1; }
say() { printf '\n==> %s\n' "$*"; }

# When this script is piped from curl, its stdin is the script itself, so
# gcloud must never read the terminal.
gcloud() { command gcloud --quiet "$@" </dev/null; }

KEYFILE=
trap '[ -z "$KEYFILE" ] || rm -f "$KEYFILE"' EXIT

make_budget() {
  local project=$1 acct names
  acct=$(gcloud billing projects describe "$project" --format='value(billingAccountName)') || return 1
  acct=${acct#billingAccounts/}
  [ -n "$acct" ] || return 1
  gcloud services enable billingbudgets.googleapis.com --project "$project" || return 1
  names=$(gcloud billing budgets list --billing-account "$acct" --billing-project "$project" \
    --format='value(displayName)') || return 1
  if grep -qx course <<<"$names"; then
    echo "A budget called course already exists."
    return 0
  fi
  # Credits are left out of the sum: your free credit pays for everything,
  # so counting it would keep the total at 0 and no alert would ever fire.
  gcloud billing budgets create --billing-account "$acct" --billing-project "$project" \
    --display-name course --budget-amount "$BUDGET" --calendar-period month \
    --credit-types-treatment exclude-all-credits \
    --threshold-rule percent=0.5 --threshold-rule percent=0.9 --threshold-rule percent=1.0
}

main() {
  local user=${1:-} key=${2:-} ktype kdata project billing list zone out ip_name ip

  [[ $user =~ ^[a-z][a-z0-9_-]{0,30}$ ]] \
    || die "USERNAME must be lowercase English letters (digits allowed after the first), for example ani."
  [ "$user" != root ] || die "USERNAME cannot be root."
  read -r ktype kdata _ <<<"$key"
  case $ktype in
    ssh-ed25519|ssh-rsa|ecdsa-sha2-nistp*) ;;
    *) die "The second argument must be your PUBLIC key line, the one that starts with ssh-ed25519. Never paste the file without .pub." ;;
  esac
  [ -n "$kdata" ] || die "The public key line is incomplete."

  say "Project"
  project=$(gcloud config get-value project 2>/dev/null || true)
  if [ -z "$project" ] || [ "$project" = "(unset)" ]; then
    list=$(gcloud projects list --format='value(projectId)')
    if [ "$(printf '%s\n' "$list" | grep -c .)" -eq 1 ]; then
      project=$list
      gcloud config set project "$project" >/dev/null 2>&1
    else
      die "Cloud Shell does not know your project. Copy the Project ID from the console Dashboard and run: gcloud config set project YOUR-PROJECT-ID"
    fi
  fi
  echo "$project"
  billing=$(gcloud billing projects describe "$project" --format='value(billingEnabled)' 2>/dev/null || true)
  [ "$billing" != False ] || die "Billing is not switched on for $project. Finish step 3 (the free trial), then run this again."

  say "Turning on Compute Engine (about a minute the first time)"
  gcloud services enable compute.googleapis.com

  say "Budget: $BUDGET dollars a month, emails only"
  if ! make_budget "$project"; then
    echo "Could not create the budget. The server is not affected: carry on, and do step 4 of the guide in the console afterwards."
  fi

  ip_name=$NAME-ip
  say "Static IP $ip_name"
  if gcloud compute addresses describe "$ip_name" --region "$REGION" >/dev/null 2>&1; then
    echo "It already exists."
  else
    gcloud compute addresses create "$ip_name" --region "$REGION"
  fi

  say "Server $NAME"
  zone=$(gcloud compute instances list --filter="name=$NAME" --format='value(zone.basename())' 2>/dev/null | head -n 1 || true)
  if [ -n "$zone" ]; then
    echo "It already exists in $zone, so it is left as it is."
  else
    KEYFILE=$(mktemp)
    printf '%s:%s %s %s\n' "$user" "$ktype" "$kdata" "$user" >"$KEYFILE"
    for z in a b c; do
      zone=$REGION-$z
      if out=$(gcloud compute instances create "$NAME" --zone "$zone" \
          --machine-type e2-medium \
          --image-family ubuntu-2404-lts-amd64 --image-project ubuntu-os-cloud \
          --boot-disk-size 50GB --boot-disk-type pd-balanced \
          --address "$ip_name" \
          --metadata-from-file ssh-keys="$KEYFILE" 2>&1); then
        echo "$out"
        break
      fi
      case $out in
        *RESOURCE_POOL_EXHAUSTED*|*"does not have enough resources"*)
          echo "No room in $zone, trying the next zone."
          zone=
          continue ;;
      esac
      echo "$out" >&2
      die "Could not create the server. Copy the error above and send it to the course chat."
    done
    [ -n "$zone" ] || die "No zone in $REGION has room right now. Run this again in a few minutes."
  fi

  ip=$(gcloud compute instances describe "$NAME" --zone "$zone" \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)')

  cat <<EOF

==> Your server is ready

    username     $user
    external IP  $ip

Send the IP to your instructor (step 9 of the guide). Now go back to your own
computer and run the line for your system. It adds the "ws" shortcut and tests
the connection.

Windows (PowerShell):

& ([scriptblock]::Create((irm $RAW/ssh_setup.ps1))) config $user $ip

macOS or Linux (Terminal):

curl -fsSL $RAW/ssh_setup.sh | bash -s -- config $user $ip
EOF
}

main "$@"
