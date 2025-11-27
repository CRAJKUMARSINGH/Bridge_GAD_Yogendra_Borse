; Bridge_GAD Windows Installer Script
; Developed by Er. Rajkumar Singh Chauhan

#define MyAppVersion
#expression ReadFile(AddBackslash(SourcePath) + "VERSION.txt")
#emit 'AppVersion=' + MyAppVersion

[Setup]
AppName=Bridge_GAD
AppVersion={#MyAppVersion}
AppPublisher=Er. Rajkumar Singh Chauhan
AppPublisherURL=https://github.com/CRAJKUMARSINGH/Bridge_GAD_Yogendra_Borse
AppSupportURL=https://github.com/CRAJKUMARSINGH/Bridge_GAD_Yogendra_Borse/issues
AppUpdatesURL=https://github.com/CRAJKUMARSINGH/Bridge_GAD_Yogendra_Borse/releases
DefaultDirName={pf}\Bridge_GAD
DefaultGroupName=Bridge_GAD
OutputDir=dist
OutputBaseFilename=Bridge_GAD_Setup
SetupIconFile=bridge.ico
UninstallDisplayIcon={app}\Bridge_GAD_GUI.exe
Compression=lzma
SolidCompression=yes
LicenseFile=LICENSE
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
Source: "dist\Bridge_GAD.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Bridge_GAD_GUI.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "docs\Bridge_GAD_User_Manual.pdf"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "bridge.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Bridge_GAD (CLI)"; Filename: "{app}\Bridge_GAD.exe"; WorkingDir: "{app}"
Name: "{group}\Bridge_GAD (GUI)"; Filename: "{app}\Bridge_GAD_GUI.exe"; WorkingDir: "{app}"
Name: "{group}\Bridge_GAD User Manual"; Filename: "{app}\docs\Bridge_GAD_User_Manual.pdf"
Name: "{commondesktop}\Bridge_GAD (GUI)"; Filename: "{app}\Bridge_GAD_GUI.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Bridge_GAD_GUI.exe"; Description: "Launch Bridge_GAD"; Flags: nowait postinstall skipifsilent