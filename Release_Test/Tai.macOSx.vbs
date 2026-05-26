' .lnk -> wscript -> file nay -> Chay-Tai-macOSx.cmd (luon dung thu muc chua .vbs, ke ca sau khi copy sang o/may khac).
Option Explicit
Dim sh, fso, dir, cmd
Set fso = CreateObject("Scripting.FileSystemObject")
dir = fso.GetParentFolderName(WScript.ScriptFullName)
cmd = dir & "\Chay-Tai-macOSx.cmd"
If Not fso.FileExists(cmd) Then
  MsgBox "Khong tim thay: " & cmd, vbCritical, "Tai macOSx"
  WScript.Quit 1
End If
Set sh = CreateObject("WScript.Shell")
sh.Run Chr(34) & cmd & Chr(34), 1, True
