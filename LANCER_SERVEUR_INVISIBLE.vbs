' Lance le serveur LED en arrière-plan (fenêtre invisible)
Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Récupère le chemin du dossier contenant ce script
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

' Lance Python avec le serveur LED en mode invisible
WshShell.Run "cmd /c cd /d """ & scriptDir & "\serveur"" && python led_serveur.py", 0
Set WshShell = Nothing
Set fso = Nothing
