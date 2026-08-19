' DeepSeek Harness 一键启动器 - 无控制台窗口启动
Set objShell = CreateObject("WScript.Shell")
strPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
objShell.Run "python """ & strPath & "\dsh_launcher.py""", 0, False
