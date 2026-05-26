$dir = Join-Path $env:TEMP 'reltest'
New-Item -ItemType Directory -Path $dir -Force | Out-Null
$cmdPath = Join-Path $dir 'hello.cmd'
Set-Content -Path $cmdPath -Value '@echo OK'
$lnkPath = Join-Path $dir 't.lnk'
$w = New-Object -ComObject WScript.Shell
$s = $w.CreateShortcut($lnkPath)
$s.TargetPath = 'hello.cmd'
$s.WorkingDirectory = '.'
$s.Save()
$r = $w.CreateShortcut($lnkPath)
Write-Host "Target readback: [$($r.TargetPath)]"
Write-Host "WD readback: [$($r.WorkingDirectory)]"
Remove-Item $dir -Recurse -Force
