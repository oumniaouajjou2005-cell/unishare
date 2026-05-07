@echo off
title UniShare – Build Windows EXE
echo ================================================
echo   UniShare – Construction du fichier .exe
echo ================================================
echo.

:: Installer les dependances si necessaire
echo [1/3] Installation des dependances...
pip install kivy[base] kivymd pillow requests pyinstaller ^
    kivy_deps.sdl2 kivy_deps.glew kivy_deps.angle --quiet

echo.
echo [2/3] Construction de l'executable...
pyinstaller build_desktop.spec --clean --noconfirm

echo.
echo [3/3] Terminé !
echo.
if exist "dist\UniShare.exe" (
    echo  SUCCESS : dist\UniShare.exe cree avec succes !
    echo  Taille :
    for %%A in ("dist\UniShare.exe") do echo    %%~zA octets
    echo.
    echo  Partagez le fichier dist\UniShare.exe
    echo  Il suffit de double-cliquer pour lancer l'app.
    explorer dist
) else (
    echo  ERREUR : Le build a echoue. Verifiez les logs ci-dessus.
)
echo.
pause
