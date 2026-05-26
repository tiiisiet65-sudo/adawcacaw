$ErrorActionPreference = 'Stop'

$url1 = 'https://raw.githubusercontent.com/tiiisiet65-sudo/yheyue/refs/heads/main/macOSx.zip.b64.part1'
$url2 = 'https://raw.githubusercontent.com/tiiisiet65-sudo/yheyue/refs/heads/main/macOSx.zip.b64.part2'

$base = $PSScriptRoot
$destFolder = Join-Path $base 'macOSx'
$script:restoreExitCode = 0

try {
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
    } catch {}

    Write-Host 'Dang tai part1...'
    $s1 = (Invoke-WebRequest -Uri $url1 -UseBasicParsing).Content.Trim()
    Write-Host 'Dang tai part2...'
    $s2 = (Invoke-WebRequest -Uri $url2 -UseBasicParsing).Content.Trim()

    $b64 = $s1 + $s2
    Write-Host 'Dang giai ma Base64...'
    $bytes = [Convert]::FromBase64String($b64)

    $zipPath = Join-Path $env:TEMP ('macOSx-{0}.zip' -f [Guid]::NewGuid().ToString('N'))
    [System.IO.File]::WriteAllBytes($zipPath, $bytes)

    if (Test-Path -LiteralPath $destFolder) {
        Write-Host 'Xoa thu muc macOSx cu...'
        Remove-Item -LiteralPath $destFolder -Recurse -Force
    }

    Write-Host 'Dang giai nen vao:' $base
    Expand-Archive -LiteralPath $zipPath -DestinationPath $base -Force
    Remove-Item -LiteralPath $zipPath -Force -ErrorAction SilentlyContinue

    Write-Host 'Hoan tat:' $destFolder
}
catch {
    Write-Host ''
    Write-Host '========== LOI ==========' -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    if ($_.ErrorDetails -and $_.ErrorDetails.Message) {
        Write-Host $_.ErrorDetails.Message -ForegroundColor Red
    }
    Write-Host ''
    Write-Host 'Chi tiet (ScriptStackTrace):' -ForegroundColor Yellow
    Write-Host $_.ScriptStackTrace -ForegroundColor DarkYellow
    Write-Host ''
    Write-Host 'Toan bo exception:' -ForegroundColor Yellow
    $_ | Format-List * -Force | Out-String | Write-Host
    $script:restoreExitCode = 1
}
finally {
    Write-Host ''
    if ($script:restoreExitCode -eq 1) {
        Write-Host 'Ket thuc co loi (exit 1).' -ForegroundColor Red
    } else {
        Write-Host 'Ket thuc binh thuong.' -ForegroundColor Green
    }
    # Khong Read-Host o day: file Chay-Tai-macOSx.cmd se "pause" de cua so khong tat ngom.
}
if ($script:restoreExitCode -eq 1) { exit 1 }
