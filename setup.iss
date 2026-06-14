[Setup]
AppName=OmniScreen
AppVersion=1.2.0
AppPublisher=OmniScreen Technologies
AppCopyright=Copyright (C) 2026 OmniScreen

DisableDirPage=no
DefaultDirName={autopf}\OmniScreen
DefaultGroupName=OmniScreen

OutputDir=.\InstallerFinal
OutputBaseFilename=OmniScreen_Setup_v1.2.0
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Tasks]
Name: "desktopicon"; Description: "Créer un raccourci sur le bureau"; GroupDescription: "Raccourcis additionnels :"

[Files]
Source: "dist\OmniScreen\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\OmniScreen"; Filename: "{app}\OmniScreen.exe"
Name: "{autodesktop}\OmniScreen"; Filename: "{app}\OmniScreen.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\OmniScreen.exe"; Description: "Lancer OmniScreen maintenant"; Flags: nowait postinstall runasoriginaluser
