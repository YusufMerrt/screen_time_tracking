Set WshShell = CreateObject("WScript.Shell")
On Error Resume Next

' Python dosyasının yolu
strProgramPath = "C:\Users\mert\Desktop\Yeni klasör\ekran_takip.pyw"

' Programı başlat
WshShell.Run chr(34) & strProgramPath & chr(34), 0
If Err.Number <> 0 Then
    WScript.Echo "Hata: Program başlatılamadı! Hata kodu: " & Err.Number
End If

Set WshShell = Nothing 