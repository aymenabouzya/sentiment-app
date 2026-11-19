#ifndef AppVersion
  #define AppVersion "1.0.0"
#endif

#define AppName "sentiment-app"
#define AppPublisher "A. Larhlimi"
#define AppId "{{29BBD78A-4C31-42B7-A6C1-3E18AA19BC17}"

[Setup]
AppId={#AppId}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={localappdata}\Programs\sentiment-app
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64
OutputDir=Output
OutputBaseFilename=sentiment-app-{#AppVersion}-setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
UninstallDisplayName={#AppName} {#AppVersion}
UninstallDisplayIcon={app}\python\python.exe
CloseApplications=yes
ChangesEnvironment=yes

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "addtopath"; Description: "Ajouter sentiment-app au PATH de l'utilisateur"; Flags: checkedonce

[Files]
Source: "build\app\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\sentiment-app\Analyser un avis"; Filename: "{cmd}"; Parameters: "/K """"{app}\sentiment.cmd"""" --help"; WorkingDir: "{app}"
Name: "{autoprograms}\sentiment-app\Désinstaller"; Filename: "{uninstallexe}"

[Code]
const
  WM_SETTINGCHANGE = $001A;
  SMTO_ABORTIFHUNG = $0002;

function SendMessageTimeout(hWnd: LongInt; Msg: LongInt; wParam: LongInt;
  lParam: String; fuFlags: LongInt; uTimeout: LongInt;
  var lpdwResult: LongInt): LongInt;
  external 'SendMessageTimeoutW@user32.dll stdcall';

function NormalizedPath(Value: String): String;
begin
  Result := Trim(Value);
  while (Length(Result) > 3) and (Result[Length(Result)] = '\') do
    Delete(Result, Length(Result), 1);
end;

function ContainsPath(PathValue: String; Entry: String): Boolean;
var
  Item: String;
  Separator: Integer;
begin
  Result := False;
  while PathValue <> '' do
  begin
    Separator := Pos(';', PathValue);
    if Separator > 0 then
    begin
      Item := Copy(PathValue, 1, Separator - 1);
      Delete(PathValue, 1, Separator);
    end
    else
    begin
      Item := PathValue;
      PathValue := '';
    end;
    if CompareText(NormalizedPath(Item), NormalizedPath(Entry)) = 0 then
    begin
      Result := True;
      Exit;
    end;
  end;
end;

function AddPath(PathValue: String; Entry: String): String;
begin
  if PathValue = '' then
    Result := Entry
  else if ContainsPath(PathValue, Entry) then
    Result := PathValue
  else
    Result := PathValue + ';' + Entry;
end;

function RemovePath(PathValue: String; Entry: String): String;
var
  Item: String;
  Separator: Integer;
begin
  Result := '';
  while PathValue <> '' do
  begin
    Separator := Pos(';', PathValue);
    if Separator > 0 then
    begin
      Item := Copy(PathValue, 1, Separator - 1);
      Delete(PathValue, 1, Separator);
    end
    else
    begin
      Item := PathValue;
      PathValue := '';
    end;
    if (CompareText(NormalizedPath(Item), NormalizedPath(Entry)) <> 0) and
       (Item <> '') then
    begin
      if Result <> '' then
        Result := Result + ';';
      Result := Result + Item;
    end;
  end;
end;

procedure NotifyEnvironmentChanged;
var
  MessageResult: LongInt;
begin
  SendMessageTimeout(HWND_BROADCAST, WM_SETTINGCHANGE, 0, 'Environment',
    SMTO_ABORTIFHUNG, 5000, MessageResult);
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  PathValue: String;
  InstallPath: String;
begin
  if CurStep = ssPostInstall then
  begin
    if WizardIsTaskSelected('addtopath') then
    begin
      InstallPath := ExpandConstant('{app}');
      if not RegQueryStringValue(HKCU, 'Environment', 'Path', PathValue) then
        PathValue := '';
      RegWriteStringValue(HKCU, 'Environment', 'Path', AddPath(PathValue, InstallPath));
      RegWriteStringValue(HKCU, 'Software\sentiment-app', 'PathEntry', InstallPath);
      NotifyEnvironmentChanged;
    end;
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  PathValue: String;
  InstallPath: String;
begin
  if CurUninstallStep = usUninstall then
  begin
    if RegQueryStringValue(HKCU, 'Software\sentiment-app', 'PathEntry', InstallPath) then
    begin
      if RegQueryStringValue(HKCU, 'Environment', 'Path', PathValue) then
      begin
        RegWriteStringValue(HKCU, 'Environment', 'Path', RemovePath(PathValue, InstallPath));
        NotifyEnvironmentChanged;
      end;
      RegDeleteValue(HKCU, 'Software\sentiment-app', 'PathEntry');
      RegDeleteKeyIfEmpty(HKCU, 'Software\sentiment-app');
    end;
  end;
end;
