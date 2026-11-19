[CmdletBinding()]
param(
    [string]$Roue,
    [string]$PythonVersion,
    [switch]$SansCompilation
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$InstallateurDir = $PSScriptRoot
$Racine = Split-Path -Parent $InstallateurDir
$BuildDir = Join-Path $InstallateurDir 'build'
$AppDir = Join-Path $BuildDir 'app'
$PythonDir = Join-Path $AppDir 'python'
$SitePackages = Join-Path $PythonDir 'Lib\site-packages'
$Contraintes = Join-Path $BuildDir 'contraintes.txt'
$ArchivePython = Join-Path $BuildDir 'python-embed.zip'
$ScriptPip = Join-Path $BuildDir 'get-pip.py'

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][string]$Description
    )

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Description a échoué (code $LASTEXITCODE)."
    }
}

function Get-ActivePython {
    $venv = $env:VIRTUAL_ENV
    if ($venv) {
        $candidate = Join-Path $venv 'Scripts\python.exe'
        if (Test-Path $candidate) {
            return (Resolve-Path $candidate).Path
        }
    }

    $projectPython = Join-Path $Racine '.venv\Scripts\python.exe'
    if (Test-Path $projectPython) {
        return (Resolve-Path $projectPython).Path
    }

    $command = Get-Command python -ErrorAction Stop
    return $command.Source
}

function Invoke-PythonSnippet {
    param(
        [Parameter(Mandatory = $true)][string]$PythonExe,
        [Parameter(Mandatory = $true)][string]$Code,
        [string[]]$PythonArguments = @(),
        [string[]]$Arguments = @()
    )

    $scriptPath = Join-Path $env:TEMP (
        'sentiment-app-installer-' + [guid]::NewGuid().ToString('N') + '.py'
    )
    try {
        [IO.File]::WriteAllText($scriptPath, $Code, [Text.UTF8Encoding]::new($false))
        $output = & $PythonExe @PythonArguments $scriptPath @Arguments
        if ($LASTEXITCODE -ne 0) {
            throw "Le script Python temporaire a échoué (code $LASTEXITCODE)."
        }
        return $output
    }
    finally {
        if (Test-Path -LiteralPath $scriptPath) {
            Remove-Item -LiteralPath $scriptPath -Force
        }
    }
}

function Get-ActiveMetadata {
    param([string]$PythonExe)

    $code = @'
import json
import sys
import joblib
import numpy
import scipy
import sklearn
print(json.dumps({
    "executable": sys.executable,
    "version": ".".join(map(str, sys.version_info[:3])),
    "bits": 64 if sys.maxsize > 2**32 else 32,
    "joblib": joblib.__version__,
    "numpy": numpy.__version__,
    "scipy": scipy.__version__,
    "scikit_learn": sklearn.__version__,
}))
'@
    try {
        $result = Invoke-PythonSnippet -PythonExe $PythonExe -Code $code
    }
    catch {
        throw "Impossible de lire l'environnement Python actif ou ses dépendances : $_"
    }
    return ($result -join "`n" | ConvertFrom-Json)
}

function Get-WheelMetadata {
    param([string]$WheelPath)

    $python = Get-ActivePython
    $code = @'
import hashlib
import sys
import zipfile
wheel = sys.argv[1]
model_paths = sys.argv[2:4]
with zipfile.ZipFile(wheel) as archive:
    metadata_name = next(name for name in archive.namelist()
                         if name.endswith(".dist-info/METADATA"))
    metadata = archive.read(metadata_name).decode("utf-8")
    model_name = "sentiment_app/modele/sentiment.joblib"
    if model_name not in archive.namelist():
        raise SystemExit("La roue ne contient pas le modèle embarqué.")
    wheel_hash = hashlib.sha256(archive.read(model_name)).hexdigest()
for model_path in model_paths:
    with open(model_path, "rb") as model_file:
        if hashlib.sha256(model_file.read()).hexdigest() != wheel_hash:
            raise SystemExit("Le modèle de la roue ne correspond pas au modèle entraîné et copié dans le paquet.")
fields = dict(line.split(": ", 1) for line in metadata.splitlines()
              if line.startswith(("Name: ", "Version: ")))
print(fields["Name"])
print(fields["Version"])
'@
    try {
        $result = Invoke-PythonSnippet -PythonExe $python -Code $code -Arguments @(
            $WheelPath,
            (Join-Path $Racine 'models\sentiment.joblib'),
            (Join-Path $Racine 'src\sentiment_app\modele\sentiment.joblib')
        )
    }
    catch {
        throw "Lecture des métadonnées de la roue impossible ou modèle incohérent : $_"
    }
    if ($result.Count -lt 2) {
        throw 'Lecture des métadonnées de la roue impossible ou modèle absent.'
    }
    return [PSCustomObject]@{
        Name    = [string]$result[-2]
        Version = [string]$result[-1]
    }
}

try {
    $PythonExe = Get-ActivePython
    $PythonInfo = Get-ActiveMetadata -PythonExe $PythonExe
    if ($PythonInfo.bits -ne 64) {
        throw 'Un Python 64 bits est requis pour construire l’installateur Windows x64.'
    }

    if (-not $PythonVersion) {
        $PythonVersion = [string]$PythonInfo.version
    }
    if ($PythonVersion -notmatch '^3\.(11|12|13)\.\d+$') {
        throw "Version Python embarquée non prise en charge : $PythonVersion. Utilisez Python 3.11.9, 3.12.x ou 3.13.x."
    }
    $ActiveMinor = ([string]$PythonInfo.version -split '\.')[1]
    $TargetMinor = ($PythonVersion -split '\.')[1]
    $PythonMajor = ($PythonVersion -split '\.')[0]
    $PythonTag = "python$PythonMajor$TargetMinor"
    $PythonAbi = "cp$PythonMajor$TargetMinor"
    if ($ActiveMinor -ne $TargetMinor) {
        throw "Python actif $($PythonInfo.version) et Python embarqué $PythonVersion doivent avoir la même version majeure et mineure."
    }
    if ($ActiveMinor -eq '11' -and [version]$PythonVersion -gt [version]'3.11.9') {
        throw 'Les distributions embarquées Python 3.11 sont disponibles jusqu’à 3.11.9. Utilisez -PythonVersion 3.11.9.'
    }
    if ($PythonInfo.scikit_learn -notlike '1.5.*') {
        throw "scikit-learn $($PythonInfo.scikit_learn) ne correspond pas au modèle prévu pour scikit-learn 1.5.x."
    }

    $WheelPath = $null
    if ($Roue) {
        $candidate = if ([IO.Path]::IsPathRooted($Roue)) {
            $Roue
        }
        else {
            Join-Path $Racine $Roue
        }
        if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) {
            throw "Roue introuvable : $candidate"
        }
        $WheelPath = (Resolve-Path -LiteralPath $candidate).Path
    }
    else {
        $latest = Get-ChildItem (Join-Path $Racine 'dist') -Filter 'sentiment_app-*.whl' -File |
            Sort-Object LastWriteTimeUtc -Descending |
            Select-Object -First 1
        if (-not $latest) {
            throw 'Aucune roue sentiment_app trouvée dans dist/. Construisez-la avec python -m build.'
        }
        $WheelPath = $latest.FullName
    }

    $WheelInfo = Get-WheelMetadata -WheelPath $WheelPath
    if ($WheelInfo.Name -ne 'sentiment-app') {
        throw "La roue sélectionnée n’est pas sentiment-app : $($WheelInfo.Name)"
    }
    if ($WheelInfo.Version -notmatch '^\d+\.\d+\.\d+$') {
        throw "Version de roue non prise en charge : $($WheelInfo.Version)"
    }

    $Compiler = $null
    if (-not $SansCompilation) {
        $compilerCommand = Get-Command ISCC.exe -ErrorAction SilentlyContinue
        if ($compilerCommand) {
            $Compiler = $compilerCommand.Source
        }
        else {
            foreach ($compilerPath in @(
                    (Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 6\ISCC.exe'),
                    (Join-Path $env:ProgramFiles 'Inno Setup 6\ISCC.exe'),
                    (Join-Path $env:LOCALAPPDATA 'Programs\Inno Setup 6\ISCC.exe')
                )) {
                if ($compilerPath -and (Test-Path $compilerPath)) {
                    $Compiler = $compilerPath
                    break
                }
            }
        }
        if (-not $Compiler) {
            throw 'Inno Setup 6 est introuvable. Installez-le avec winget install JRSoftware.InnoSetup ou utilisez -SansCompilation.'
        }
    }

    Write-Host "roue : $(Split-Path -Leaf $WheelPath) ($($WheelInfo.Version))"
    Write-Host "python actif : $($PythonInfo.version) ($PythonExe)"
    Write-Host "python embarqué : $PythonVersion"
    Write-Host "versions modèle : scikit-learn $($PythonInfo.scikit_learn), numpy $($PythonInfo.numpy), scipy $($PythonInfo.scipy), joblib $($PythonInfo.joblib)"

    if (Test-Path -LiteralPath $BuildDir) {
        Remove-Item -LiteralPath $BuildDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $PythonDir, $SitePackages | Out-Null

    $PythonUrl = "https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion-embed-amd64.zip"
    Invoke-WebRequest -Uri $PythonUrl -OutFile $ArchivePython
    Expand-Archive -LiteralPath $ArchivePython -DestinationPath $PythonDir -Force
    Remove-Item -LiteralPath $ArchivePython -Force

    $PythonExeName = "$PythonTag._pth"
    $PythonPth = Join-Path $PythonDir $PythonExeName
    if (-not (Test-Path -LiteralPath $PythonPth)) {
        throw "Fichier de configuration du Python embarqué absent : $PythonPth"
    }
    $PthLines = @(
        "$PythonTag.zip"
        '.'
        'Lib\site-packages'
        'import site'
    )
    [IO.File]::WriteAllLines(
        $PythonPth,
        $PthLines,
        [Text.UTF8Encoding]::new($false)
    )
    Write-Host "OK  $([IO.Path]::GetFileName($PythonPth)) : $($PthLines -join ' ; ')"

    $GetPipUrl = 'https://bootstrap.pypa.io/get-pip.py'
    Invoke-WebRequest -Uri $GetPipUrl -OutFile $ScriptPip
    $EmbeddedPython = Join-Path $PythonDir 'python.exe'
    Invoke-Checked -FilePath $EmbeddedPython `
        -Arguments @('-I', $ScriptPip, '--no-warn-script-location') `
        -Description 'Installation de pip dans le Python embarqué'
    Remove-Item -LiteralPath $ScriptPip -Force

    $FreezeLines = & $PythonExe -m pip freeze --all
    if ($LASTEXITCODE -ne 0 -or -not $FreezeLines) {
        throw 'Impossible de relever les versions exactes avec pip freeze.'
    }
    $ExactConstraints = @(
        $FreezeLines | Where-Object { $_ -match '^[A-Za-z0-9][A-Za-z0-9_.-]*==[^=]+$' }
    )
    if ($ExactConstraints.Count -eq 0) {
        throw 'pip freeze ne fournit aucune contrainte de version exacte.'
    }
    [IO.File]::WriteAllLines(
        $Contraintes,
        $ExactConstraints,
        [Text.UTF8Encoding]::new($false)
    )

    $PipArguments = @(
        '-I',
        '-m', 'pip', 'install',
        '--disable-pip-version-check',
        '--only-binary=:all:',
        '--platform', 'win_amd64',
        '--python-version', "3.$TargetMinor",
        '--implementation', 'cp',
        '--abi', $PythonAbi,
        '--constraint', $Contraintes,
        '--target', $SitePackages,
        $WheelPath
    )
    Invoke-Checked -FilePath $EmbeddedPython `
        -Arguments $PipArguments `
        -Description 'Installation de la roue et des dépendances Windows'

    $Launcher = Join-Path $AppDir 'sentiment.cmd'
    Copy-Item -LiteralPath (Join-Path $InstallateurDir 'sentiment.cmd') -Destination $Launcher
    Copy-Item -LiteralPath (Join-Path $InstallateurDir 'LISEZMOI.txt') -Destination $AppDir

    $RuntimePath = & $EmbeddedPython -I -c 'import sys; print(sys.executable)'
    if ($LASTEXITCODE -ne 0 -or -not $RuntimePath) {
        throw 'Le Python embarqué ne démarre pas.'
    }
    if ([IO.Path]::GetFullPath($RuntimePath.Trim()) -ne [IO.Path]::GetFullPath($EmbeddedPython)) {
        throw "Le lanceur Python pointe vers un autre interpréteur : $RuntimePath"
    }

    $RuntimeCheck = @'
import importlib.metadata
import json
import joblib
import numpy
import scipy
import site
import sklearn
import sys
print(json.dumps({
    "joblib": joblib.__version__,
    "numpy": numpy.__version__,
    "scipy": scipy.__version__,
    "scikit_learn": sklearn.__version__,
    "package": importlib.metadata.version("sentiment-app"),
    "isolated": sys.flags.isolated,
    "user_site_enabled": site.ENABLE_USER_SITE,
}))
'@
    try {
        $RuntimeInfo = Invoke-PythonSnippet `
            -PythonExe $EmbeddedPython `
            -Code $RuntimeCheck `
            -PythonArguments @('-I')
    }
    catch {
        throw "Les dépendances Windows ou le paquet ne se chargent pas avec le Python embarqué : $_"
    }
    $RuntimeInfo = ($RuntimeInfo -join "`n") | ConvertFrom-Json
    foreach ($dependency in @('joblib', 'numpy', 'scipy', 'scikit_learn')) {
        if ([string]$RuntimeInfo.$dependency -ne [string]$PythonInfo.$dependency) {
            throw "Version incohérente de $dependency : environnement $($PythonInfo.$dependency), Python embarqué $($RuntimeInfo.$dependency)."
        }
    }
    if ($RuntimeInfo.package -ne $WheelInfo.Version) {
        throw "Version du paquet installé ($($RuntimeInfo.package)) différente de la roue ($($WheelInfo.Version))."
    }
    if ($RuntimeInfo.isolated -ne 1 -or $RuntimeInfo.user_site_enabled) {
        throw 'Le Python embarqué doit tourner en mode isolé et désactiver les paquets utilisateur.'
    }

    $VersionOutput = & $Launcher --version
    if ($LASTEXITCODE -ne 0 -or ($VersionOutput -join "`n").Trim() -ne "sentiment $($WheelInfo.Version)") {
        throw "Échec de la commande --version : $($VersionOutput -join ' ')"
    }
    Write-Host 'OK  sentiment --version'

    $PositiveOutput = & $Launcher 'Livraison rapide, très satisfait'
    if ($LASTEXITCODE -ne 0 -or ($PositiveOutput -join "`n") -notmatch '^positive \(confiance \d+%\)$') {
        throw "Échec de la prédiction positive : $($PositiveOutput -join ' ')"
    }
    Write-Host "OK  $($PositiveOutput -join ' ')"

    $NegativeOutput = & $Launcher --json 'Produit cassé et service client injoignable'
    if ($LASTEXITCODE -ne 0) {
        throw "Échec de la commande JSON : $($NegativeOutput -join ' ')"
    }
    try {
        $NegativeResult = ($NegativeOutput -join "`n") | ConvertFrom-Json
    }
    catch {
        throw "La sortie JSON du lanceur est invalide : $($NegativeOutput -join ' ')"
    }
    if ($NegativeResult.label -ne 'negative') {
        throw "La prédiction négative attendue est incorrecte : $($NegativeOutput -join ' ')"
    }
    Write-Host "OK  JSON : $($NegativeOutput -join ' ')"

    $PreviousErrorActionPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $EmptyOutput = & $Launcher ' ' 2>&1
        $EmptyExitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $PreviousErrorActionPreference
    }
    if ($EmptyExitCode -ne 2 -or ($EmptyOutput -join "`n") -notmatch 'erreur\s*:\s*texte vide') {
        throw "Le texte vide doit produire le code 2 et « erreur : texte vide » : $($EmptyOutput -join ' ')"
    }
    Write-Host 'OK  texte vide : code 2'

    $AppSize = [math]::Round(
        ((Get-ChildItem -LiteralPath $AppDir -Recurse -File |
                Measure-Object -Property Length -Sum).Sum / 1MB),
        1
    )
    Write-Host "Taille de l’application : $AppSize Mo"

    if ($SansCompilation) {
        Write-Host 'Compilation Inno Setup ignorée (-SansCompilation).'
        exit 0
    }

    Invoke-Checked -FilePath $Compiler `
        -Arguments @(
            "/DAppVersion=$($WheelInfo.Version)",
            (Join-Path $InstallateurDir 'sentiment.iss')
        ) `
        -Description 'Compilation Inno Setup'
    $SetupExe = Join-Path $InstallateurDir "Output\sentiment-app-$($WheelInfo.Version)-setup.exe"
    if (-not (Test-Path -LiteralPath $SetupExe)) {
        throw "Inno Setup n’a pas produit le fichier attendu : $SetupExe"
    }
    Write-Host "Installateur : $SetupExe"
}
catch {
    Write-Error $_
    exit 1
}
