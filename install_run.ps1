# install_run.ps1
# Ejecuta con:  PowerShell -ExecutionPolicy Bypass -File .\install_run.ps1

$ErrorActionPreference = "Continue"
Set-StrictMode -Version Latest

# --- Config ---
$VenvName     = "constru"
$PythonExe    = "python-3.11.5-amd64.exe"
$GitExeSetup  = "Git-2.51.0-64-bit.exe"
$IconRelPath  = "media\pavez_P_logo.ico"
$DoGitPush    = $true   # <-- pon en $false si no quieres el push automático
$GitRemoteUrl = "https://github.com/dpv20/papa_funcional"
$ShortcutName = "Pavez Budget.lnk"

# --- Paths ---
$Root       = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

$PythonInstaller = Join-Path $Root $PythonExe
$GitInstaller    = Join-Path $Root $GitExeSetup
$IconPath        = Join-Path $Root $IconRelPath

# --- Helpers ---
function Test-Command($cmd) {
  $old = $ErrorActionPreference; $ErrorActionPreference = "SilentlyContinue"
  $exists = (Get-Command $cmd).Path -ne $null
  $ErrorActionPreference = $old
  return $exists
}

Write-Host "==> Instalando/Verificando Python..."
if (-not (Test-Command "python") -and -not (Test-Command "py")) {
  if (-not (Test-Path $PythonInstaller)) {
    Write-Error "No se encontró $PythonExe en $Root. Copia el instalador aquí."
    exit 1
  }
  # Instalación silenciosa usuario actual, agrega a PATH
  Start-Process -FilePath $PythonInstaller -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1 Include_pip=1" -Wait
  Write-Host "Python instalado (puede requerir nueva sesión para actualizar PATH)."
} else {
  Write-Host "Python ya presente."
}

# Elige mejor comando Python disponible
$PyCmd = $null
if (Test-Command "py") {
  # Intenta específicamente 3.11
  try { & py -3.11 -V | Out-Null; $PyCmd = "py -3.11" } catch { $PyCmd = $null }
}
if (-not $PyCmd) { $PyCmd = "python" }

Write-Host "==> Instalando/Verificando Git..."
if (-not (Test-Command "git")) {
  if (-not (Test-Path $GitInstaller)) {
    Write-Error "No se encontró $GitExeSetup en $Root. Copia el instalador aquí."
    exit 1
  }
  # Git for Windows usa Inno Setup: /VERYSILENT /NORESTART /SUPPRESSMSGBOXES
  Start-Process -FilePath $GitInstaller -ArgumentList "/VERYSILENT /NORESTART /SUPPRESSMSGBOXES" -Wait
  Write-Host "Git instalado."
} else {
  Write-Host "Git ya presente."
}

# En esta sesión, PATH podría no estar actualizado; intentamos ruta por defecto si 'git' no aparece aún:
$GitCmd = if (Test-Command "git") { "git" } else { "C:\Program Files\Git\bin\git.exe" }

Write-Host "==> Creando venv '$VenvName'..."
& $PyCmd -m venv $VenvName

$VenvPython = Join-Path $Root "$VenvName\Scripts\python.exe"
$VenvPip    = Join-Path $Root "$VenvName\Scripts\pip.exe"

if (-not (Test-Path $VenvPython)) {
  Write-Error "No se encontró $VenvPython. Algo falló creando el venv."
  exit 1
}

Write-Host "==> Actualizando pip..."
& $VenvPython -m pip install --upgrade pip

Write-Host "==> Instalando requirements..."
if (-not (Test-Path (Join-Path $Root "requirements.txt"))) {
  Write-Error "No existe requirements.txt en $Root"
  exit 1
}
& $VenvPip install -r requirements.txt

Write-Host "==> Generando lanzador 'run_app.cmd'..."
$RunCmdPath = Join-Path $Root "run_app.cmd"
@"
@echo off
setlocal
cd /d "%~dp0"
call "%~dp0$VenvName\Scripts\activate.bat"
streamlit run app.py
"@ | Out-File -Encoding ascii $RunCmdPath -Force

# Permisos de ejecución por si acaso
try { icacls $RunCmdPath /grant "*S-1-1-0:(RX)" | Out-Null } catch {}

Write-Host "==> Creando acceso directo en el Escritorio..."
$Desktop = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $Desktop $ShortcutName

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $RunCmdPath
$Shortcut.WorkingDirectory = $Root
if (Test-Path $IconPath) { $Shortcut.IconLocation = $IconPath }
$Shortcut.Description = "Abrir la app de presupuesto (Streamlit)"
$Shortcut.Save()

Write-Host "==> Acceso directo creado: $ShortcutPath"

if ($DoGitPush -and (Test-Path (Join-Path $Root ".git"))) {
  Write-Host "==> Intentando git push al repositorio $GitRemoteUrl ..."
  try {
    # Asegura remoto origin
    $origin = & $GitCmd remote get-url origin 2>$null
    if (-not $origin) {
      & $GitCmd remote add origin $GitRemoteUrl
    }

    & $GitCmd add -A
    & $GitCmd commit -m ("Installer auto-commit " + (Get-Date -Format s)) 2>$null
    & $GitCmd push origin main
  } catch {
    Write-Warning "Push directo falló. Intentando pull --rebase y reintentar..."
    try {
      & $GitCmd pull --rebase origin main
      & $GitCmd push origin main
    } catch {
      Write-Warning "No se pudo completar el push. Verifica credenciales/permiso."
    }
  }
} else {
  Write-Host "==> Git push omitido (no .git o DoGitPush=false)."
}

Write-Host "`nTodo listo. Usa el acceso directo del Escritorio para abrir la app."
