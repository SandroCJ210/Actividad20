$Config = Get-Content -Path "legacy/config.cfg"
foreach ($line in $Config) {
    if ($line -match "PORT=(\d+)") {
        $env:PORT = $matches[1]
    }
}

Write-Output "Arrancando $env:PORT"