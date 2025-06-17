@echo off
REM Script Windows pour publier sur GitHub
REM Alternative au script PowerShell

title Publication GitHub - Photo Transfer System

echo.
echo ==========================================
echo   PUBLICATION SUR GITHUB
echo ==========================================
echo.
echo Repository: https://github.com/JULIEN-85/Projet_FTP.git
echo.

REM Configuration Git (changez l'email)
echo [1/6] Configuration Git...
git config --global user.name "JULIEN-85"
set /p email="Entrez votre email GitHub: "
git config --global user.email "%email%"

echo.
echo [2/6] Preparation du repository...

REM Initialiser Git si necessaire
if not exist .git (
    git init
)

REM Configurer le remote
git remote remove origin 2>nul
git remote add origin https://github.com/JULIEN-85/Projet_FTP.git

echo.
echo [3/6] Preparation des fichiers...

REM Remplacer le README
if exist README_GITHUB.md (
    if exist README.md (
        move README.md README_ORIGINAL.md >nul
    )
    move README_GITHUB.md README.md >nul
    echo README mis a jour pour GitHub
)

echo.
echo [4/6] Ajout des fichiers...
git add .

echo.
echo [5/6] Verification des fichiers a publier...
git status --porcelain

echo.
set /p confirm="Continuer la publication? (o/N): "
if not "%confirm%"=="o" if not "%confirm%"=="O" (
    echo Publication annulee
    pause
    exit /b
)

echo.
echo [6/6] Publication en cours...

REM Commit
git commit -m "Initial commit: Photo Transfer System v1.0 - Complete automated photo transfer solution for Raspberry Pi with web interface, gPhoto2 integration, and Raspberry Pi 5 optimizations"

REM Push
git branch -M main
git push -u origin main

REM Tag
git tag -a v1.0.0 -m "Version 1.0.0 - Initial release with full feature set"
git push origin v1.0.0

echo.
echo ==========================================
echo        PUBLICATION TERMINEE !
echo ==========================================
echo.
echo ✅ Votre projet est maintenant sur GitHub:
echo    👉 https://github.com/JULIEN-85/Projet_FTP
echo.
echo 📝 Prochaines etapes:
echo    1. Verifier sur GitHub que tout est publie
echo    2. Ajouter une description au repository  
echo    3. Ajouter des topics (raspberry-pi, python, etc.)
echo    4. Partager votre projet !
echo.

set /p open="Ouvrir GitHub dans le navigateur? (o/N): "
if "%open%"=="o" start https://github.com/JULIEN-85/Projet_FTP
if "%open%"=="O" start https://github.com/JULIEN-85/Projet_FTP

pause
