# SSH setup for the course server, on Windows (PowerShell).
#
#   & ([scriptblock]::Create((irm https://raw.githubusercontent.com/hakob-petro/aca_moderation_practicum/main/setup/ssh_setup.ps1))) key USERNAME
#   & ([scriptblock]::Create((irm https://raw.githubusercontent.com/hakob-petro/aca_moderation_practicum/main/setup/ssh_setup.ps1))) config USERNAME IP
#
# key     makes your SSH key if you have none, and prints the line to paste in
#         Cloud Shell. An existing id_ed25519 is reused, never replaced.
# config  adds a "ws" shortcut to your SSH config and tests the connection.
#         It only touches the block it writes itself, and keeps a backup.
#
# Keep this file plain ASCII. Windows PowerShell 5.1 misreads other characters.
param(
    [Parameter(Position = 0)][string]$Action,
    [Parameter(Position = 1)][string]$Username,
    [Parameter(Position = 2)][string]$Ip
)

$Raw   = 'https://raw.githubusercontent.com/hakob-petro/aca_moderation_practicum/main/setup'
$Begin = '# >>> course workspace >>>'
$End   = '# <<< course workspace <<<'

# No "exit" below: inside a script block it would close the student's window.
# Errors are thrown and shown as one red line by the catch at the bottom.
function Invoke-KeyStep {
    $sshDir = Join-Path $env:USERPROFILE '.ssh'
    $key    = Join-Path $sshDir 'id_ed25519'
    New-Item -ItemType Directory -Force -Path $sshDir | Out-Null

    if (Test-Path $key) {
        Write-Host "You already have a key ($key). It is reused, not replaced."
    } else {
        # An empty passphrase must be written differently before PowerShell 7.3.
        $v = $PSVersionTable.PSVersion
        if ($v.Major -gt 7 -or ($v.Major -eq 7 -and $v.Minor -ge 3)) { $empty = '' } else { $empty = '""' }
        & ssh-keygen -q -t ed25519 -C $Username -N $empty -f $key
        if ($LASTEXITCODE -ne 0) { throw 'ssh-keygen failed.' }
        Write-Host "Made your key: $key"
    }
    if (-not (Test-Path "$key.pub")) { throw "Missing $key.pub. Delete $key and run this again." }

    $pub = (Get-Content "$key.pub" -Raw).Trim()
    Write-Host ''
    Write-Host 'Your public key (safe to share; the file without .pub never is):'
    Write-Host ''
    Write-Host $pub
    Write-Host ''
    Write-Host 'Next: open Cloud Shell in the Google Cloud console (the >_ button at the top'
    Write-Host 'right), paste this whole line and press Enter:'
    Write-Host ''
    Write-Host "curl -fsSL $Raw/create_server.sh | bash -s -- $Username `"$pub`""
}

function Invoke-ConfigStep {
    if ($Ip -notmatch '^\d{1,3}(\.\d{1,3}){3}$') { throw 'IP must look like 34.123.45.67.' }
    $sshDir = Join-Path $env:USERPROFILE '.ssh'
    $cfg    = Join-Path $sshDir 'config'
    New-Item -ItemType Directory -Force -Path $sshDir | Out-Null

    $old = ''
    if (Test-Path $cfg) { $old = [System.IO.File]::ReadAllText($cfg) }

    # Everything in the config except an older block of ours.
    $rest = [regex]::Replace($old, '(?s)' + [regex]::Escape($Begin) + '.*?' + [regex]::Escape($End) + '\r?\n?', '')
    if ($rest -match '(?mi)^\s*host\s+([^#\r\n]*\s)?ws(\s|$)') {
        throw "Your $cfg already has a 'Host ws' entry that this script did not write. Delete or rename it, then run this again."
    }
    if ($old.Trim().Length -gt 0) {
        Copy-Item $cfg ("$cfg.bak-" + (Get-Date -Format 'yyyyMMddHHmmss'))
    }

    if ($rest.Length -gt 0 -and -not $rest.EndsWith("`n")) { $rest += "`n" }
    $block = @($Begin, 'Host ws', "    HostName $Ip", "    User $Username",
               '    IdentityFile ~/.ssh/id_ed25519', '    IdentitiesOnly yes', $End) -join "`n"
    # UTF-8 without a byte-order mark: OpenSSH rejects a config that starts with one.
    [System.IO.File]::WriteAllText($cfg, $rest + $block + "`n", (New-Object System.Text.UTF8Encoding($false)))
    Write-Host "Added the ws shortcut to $cfg"

    Write-Host 'Testing the connection (a new server can need a minute to be ready)...'
    $ok = $false
    $out = ''
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'   # ssh writes warnings to stderr; that is not an error
    for ($i = 0; $i -lt 12; $i++) {
        $out = & ssh -F $cfg -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new ws true 2>&1
        if ($LASTEXITCODE -eq 0) { $ok = $true; break }
        Start-Sleep -Seconds 5
    }
    $ErrorActionPreference = $prev

    Write-Host ''
    if ($ok) {
        Write-Host 'Connected. From now on, type:  ssh ws'
    } else {
        Write-Host 'Could not log in yet. The last message was:'
        # stderr lines arrive as error records: print only their text.
        Write-Host (($out | ForEach-Object { $_.ToString() }) -join "`n")
        Write-Host ''
        Write-Host 'Wait a minute and type:  ssh ws'
        Write-Host "If it still fails, see 'If something goes wrong' in the guide and send the exact error to the course chat."
    }
}

try {
    if ($Action -notin @('key', 'config')) { throw 'Usage: key USERNAME   or   config USERNAME IP' }
    if ($Username -notmatch '^[a-z][a-z0-9_-]{0,30}$') { throw 'USERNAME must be lowercase English letters, for example ani.' }
    if (-not (Get-Command ssh-keygen -ErrorAction SilentlyContinue)) {
        throw 'OpenSSH is not installed. Open Settings > Apps > Optional features > Add a feature, add "OpenSSH Client", then run this again.'
    }
    if ($Action -eq 'key') { Invoke-KeyStep } else { Invoke-ConfigStep }
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
}
