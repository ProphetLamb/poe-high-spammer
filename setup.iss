[Setup]
AppName=PoE High Spammer
AppVersion=1.1.0
WizardStyle=modern
DefaultDirName={autopf}\PoE High Spammer
DefaultGroupName=PoE High Spammer
UninstallDisplayIcon={app}\PoE High Spammer.exe
LicenseFile=LICENSE
Compression=lzma2
SolidCompression=yes
SetupIconFile=assets\logo.ico
OutputDir=dist
OutputBaseFilename=PoE High Spammer - Setup
; "ArchitecturesAllowed=x64" specifies that Setup cannot run on
; anything but x64.
ArchitecturesAllowed=x64
; "ArchitecturesInstallIn64BitMode=x64" requests that the install be
; done in "64-bit mode" on x64, meaning it should use the native
; 64-bit Program Files directory and the 64-bit view of the registry.
ArchitecturesInstallIn64BitMode=x64

[Files]
Source: "dist\PoE High Spammer\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs
Source: "README.txt"; DestDir: "{app}"; Flags: isreadme

[Icons]
Name: "{group}\PoE High Spammer"; Filename: "{app}\PoE High Spammer.exe"

[Code]

procedure InitializeWizard();
var
  LicenseFile: string;
begin
  LicenseFile := ExpandConstant('{src}\LICENSE');
  if FileExists(LicenseFile) then
  begin
    Log(Format('%s exists, loading a license', [LicenseFile]));
    WizardForm.LicenseMemo.Lines.LoadFromFile(LicenseFile);
  end
    else
  begin
    Log(Format('%s does not exist, keeping the default license', [LicenseFile]));
  end;
end;
