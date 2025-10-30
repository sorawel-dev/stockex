@echo off
echo ====================================
echo  MISE A JOUR MODULE STOCKEX
echo ====================================
echo.

echo [1/3] Arret du service Odoo...
net stop odoo-server-18.0
timeout /t 3 /nobreak >nul

echo.
echo [2/3] Demarrage du service Odoo...
net start odoo-server-18.0
timeout /t 10 /nobreak >nul

echo.
echo [3/3] Mise a jour terminee !
echo.
echo IMPORTANT: Allez maintenant dans Odoo :
echo   1. Applications
echo   2. Recherchez "stockex"
echo   3. Cliquez sur "Mettre a niveau"
echo.
echo Puis verifiez le menu :
echo   Gestion d'Inventaire ^> Import ^> Stock Initial
echo.
pause
