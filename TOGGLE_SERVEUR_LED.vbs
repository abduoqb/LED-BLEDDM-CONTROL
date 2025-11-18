' ========================================
' TOGGLE_SERVEUR_LED.vbs
' Script unique pour démarrer/arrêter le serveur LED
' ========================================
' Double-clic pour basculer :
'   - Si serveur arrêté → Démarre + ouvre navigateur
'   - Si serveur actif → Arrête

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Récupère le chemin du dossier contenant ce script
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

' ========================================
' FONCTION: Vérifier si le serveur tourne
' ========================================
Function IsServerRunning()
    On Error Resume Next
    Set objExec = WshShell.Exec("cmd /c wmic process where ""name='python.exe'"" get commandline")
    Do While objExec.Status = 0
        WScript.Sleep 100
    Loop
    strCommandLines = objExec.StdOut.ReadAll()

    If InStr(strCommandLines, "led_serveur.py") > 0 Then
        IsServerRunning = True
    Else
        IsServerRunning = False
    End If
    On Error GoTo 0
End Function

' ========================================
' FONCTION: Compter les instances
' ========================================
Function CountServerInstances()
    On Error Resume Next
    Set objExec = WshShell.Exec("netstat -ano | findstr :5000")
    Do While objExec.Status = 0
        WScript.Sleep 100
    Loop
    strOutput = objExec.StdOut.ReadAll()

    If Len(strOutput) = 0 Then
        CountServerInstances = 0
        Exit Function
    End If

    ' Compter les PIDs uniques
    arrLines = Split(strOutput, vbCrLf)
    Set pidList = CreateObject("Scripting.Dictionary")

    For Each line In arrLines
        If Len(Trim(line)) > 0 Then
            arrParts = Split(Trim(line))
            If UBound(arrParts) >= 0 Then
                pid = arrParts(UBound(arrParts))
                If IsNumeric(pid) And Not pidList.Exists(pid) Then
                    pidList.Add pid, True
                End If
            End If
        End If
    Next

    CountServerInstances = pidList.Count
    On Error GoTo 0
End Function

' ========================================
' FONCTION: Tuer tous les processus LED
' ========================================
Sub KillAllLEDProcesses()
    On Error Resume Next

    ' Méthode 1: Tuer par port 5000
    Set objExec = WshShell.Exec("netstat -ano | findstr :5000")
    Do While objExec.Status = 0
        WScript.Sleep 100
    Loop
    strOutput = objExec.StdOut.ReadAll()

    arrLines = Split(strOutput, vbCrLf)
    Set pidList = CreateObject("Scripting.Dictionary")

    For Each line In arrLines
        If Len(Trim(line)) > 0 Then
            arrParts = Split(Trim(line))
            If UBound(arrParts) >= 0 Then
                pid = arrParts(UBound(arrParts))
                If IsNumeric(pid) And Not pidList.Exists(pid) Then
                    pidList.Add pid, True
                    WshShell.Run "taskkill /F /PID " & pid, 0, True
                End If
            End If
        End If
    Next

    ' Méthode 2: Tuer par nom de fichier (cherche led_serveur.py)
    WshShell.Run "cmd /c wmic process where ""commandline like '%led_serveur.py%'"" call terminate", 0, True
    WScript.Sleep 500

    ' Méthode 3: Forcer avec taskkill si nécessaire
    WshShell.Run "cmd /c for /f ""tokens=2"" %i in ('wmic process where ""commandline like '%led_serveur.py%'"" get processid 2^>nul ^| findstr [0-9]') do @taskkill /F /PID %i 2>nul", 0, True

    On Error GoTo 0
End Sub

' ========================================
' LOGIQUE PRINCIPALE: TOGGLE
' ========================================

If IsServerRunning() Then
    ' ========================================
    ' SERVEUR ACTIF -> ARRETER
    ' ========================================

    ' Utiliser la fonction de nettoyage robuste
    Call KillAllLEDProcesses()

    ' Attendre que les processus se terminent complètement
    WScript.Sleep 3000

    ' Vérifier que tout est arrêté
    If CountServerInstances() = 0 And Not IsServerRunning() Then
        MsgBox "Serveur LED arrete avec succes !" & vbCrLf & vbCrLf & _
               "Tous les processus ont ete termines." & vbCrLf & vbCrLf & _
               "Double-cliquez a nouveau pour redemarrer.", vbInformation, "Toggle Serveur LED"
    Else
        ' Essayer une dernière fois avec force maximale
        WshShell.Run "taskkill /F /IM python.exe /FI ""WINDOWTITLE eq led_serveur*""", 0, True
        WScript.Sleep 1000

        If CountServerInstances() = 0 And Not IsServerRunning() Then
            MsgBox "Serveur LED arrete (apres nettoyage force)." & vbCrLf & vbCrLf & _
                   "Double-cliquez a nouveau pour redemarrer.", vbInformation, "Toggle Serveur LED"
        Else
            MsgBox "Attention: Certains processus resistant encore." & vbCrLf & vbCrLf & _
                   "Solutions:" & vbCrLf & _
                   "1. Redemarrez votre ordinateur" & vbCrLf & _
                   "2. Ouvrez le Gestionnaire des taches et tuez manuellement python.exe" & vbCrLf & _
                   "3. Executez en tant qu'administrateur: taskkill /F /IM python.exe", _
                   vbExclamation, "Toggle Serveur LED"
        End If
    End If

Else
    ' ========================================
    ' SERVEUR ARRETE -> DEMARRER
    ' ========================================

    ' Lance Python avec le serveur LED en mode invisible
    WshShell.Run "cmd /c cd /d """ & scriptDir & "\serveur"" && python led_serveur.py", 0

    ' Attendre 3 secondes pour laisser le serveur demarrer
    WScript.Sleep 3000

    ' Verifier que le serveur a bien demarre
    If IsServerRunning() Then
        MsgBox "Serveur LED demarre avec succes en arriere-plan !" & vbCrLf & vbCrLf & _
               "Interface web: http://localhost:5000/dashboard" & vbCrLf & _
               "API status: http://localhost:5000/api/status" & vbCrLf & vbCrLf & _
               "Le navigateur va s'ouvrir automatiquement..." & vbCrLf & vbCrLf & _
               "Double-cliquez a nouveau pour arreter.", vbInformation, "Toggle Serveur LED"

        ' Ouvrir le navigateur par defaut sur le dashboard
        WshShell.Run "http://localhost:5000/dashboard"
    Else
        MsgBox "Erreur: Le serveur n'a pas pu demarrer." & vbCrLf & vbCrLf & _
               "Verifiez que:" & vbCrLf & _
               "• Python est installe" & vbCrLf & _
               "• Les dependances sont installees (pip install -r requirements.txt)" & vbCrLf & _
               "• Le fichier .env existe" & vbCrLf & vbCrLf & _
               "Double-cliquez a nouveau pour reessayer.", vbCritical, "Toggle Serveur LED"
    End If

End If

' Nettoyage
Set WshShell = Nothing
Set fso = Nothing
