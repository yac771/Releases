@echo off
echo =======================================================
echo      Compilation d'OmniScreen (CMS + Player)
echo =======================================================
echo.

set "PATH=%LOCALAPPDATA%\Programs\Python\Python312\Scripts\;%LOCALAPPDATA%\Programs\Python\Python312\;%PATH%"

if exist build rmdir /S /Q build
if exist dist rmdir /S /Q dist

python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    py --version >nul 2>&1
    IF %ERRORLEVEL% NEQ 0 (
        echo [ERREUR FATALE] Impossible de trouver Python. 
        pause
        exit /b
    ) ELSE (
        set "PYTHON_CMD=py"
    )
) ELSE (
    set "PYTHON_CMD=python"
)

echo [1/3] Installation des modules (pip)...
%PYTHON_CMD% -m pip install -r requirements.txt >nul

echo [2/3] Creation de l'executable (Veuillez patienter 1 a 2 minutes)...
:: On telecharge une petite icone .ico gratuite et professionnelle pour remplacer le canard !
%PYTHON_CMD% -c "import urllib.request; urllib.request.urlretrieve('https://raw.githubusercontent.com/yac771/Releases/main/icon.ico', 'icon.ico')" >nul 2>&1

:: On l'integre a l'exe avec l'option --icon
%PYTHON_CMD% -m PyInstaller --noconfirm --onedir --windowed --name "OmniScreen" --icon "icon.ico" --hidden-import PyQt5.QtWebEngineWidgets --add-data "cms/templates;cms/templates" --add-data "version.txt;." "launcher.py"

echo [3/3] Copie de la configuration...
mkdir "dist\OmniScreen\config" 2>nul
xcopy /E /I /Y "player\config\*" "dist\OmniScreen\config\" >nul

IF NOT EXIST "dist\OmniScreen\OmniScreen.exe" (
    echo [ERREUR FATALE] Le fichier OmniScreen.exe a ete supprime (Windows Defender ?).
    pause
    exit /b
)

echo =======================================================
echo [SUCCES TOTAL] Logiciel Pret. Ouvrez setup.iss dans Inno Setup.
echo =======================================================
pause
