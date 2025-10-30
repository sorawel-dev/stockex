# Script de mise à jour forcée du module Stockex
Write-Host "====================================" -ForegroundColor Cyan
Write-Host " MISE A JOUR MODULE STOCKEX" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier les droits admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠️  ATTENTION: Ce script necessite des droits administrateur" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Solutions alternatives :" -ForegroundColor Yellow
    Write-Host "  1. Faites clic droit sur ce fichier > Executer en tant qu'administrateur" -ForegroundColor White
    Write-Host "  2. OU utilisez la methode manuelle ci-dessous" -ForegroundColor White
    Write-Host ""
    Write-Host "METHODE MANUELLE :" -ForegroundColor Green
    Write-Host "  1. Win + R > tapez 'services.msc' > Entree" -ForegroundColor White
    Write-Host "  2. Trouvez 'odoo-server-18.0'" -ForegroundColor White
    Write-Host "  3. Clic droit > Redemarrer" -ForegroundColor White
    Write-Host "  4. Puis dans Odoo : Applications > stockex > Mettre a niveau" -ForegroundColor White
    Write-Host ""
    pause
    exit
}

Write-Host "[1/3] Arret du service Odoo..." -ForegroundColor Yellow
try {
    Stop-Service -Name "odoo-server-18.0" -Force -ErrorAction Stop
    Write-Host "✅ Service arrete" -ForegroundColor Green
} catch {
    Write-Host "❌ Erreur lors de l'arret du service: $_" -ForegroundColor Red
}

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "[2/3] Demarrage du service Odoo..." -ForegroundColor Yellow
try {
    Start-Service -Name "odoo-server-18.0" -ErrorAction Stop
    Write-Host "✅ Service demarre" -ForegroundColor Green
} catch {
    Write-Host "❌ Erreur lors du demarrage du service: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Attente du demarrage complet d'Odoo (10 secondes)..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "[3/3] Service Odoo redémarre !" -ForegroundColor Green
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " PROCHAINES ETAPES" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Ouvrez Odoo : http://localhost:8069" -ForegroundColor White
Write-Host "2. Allez dans : Applications" -ForegroundColor White
Write-Host "3. Recherchez : 'stockex' ou 'StockInv'" -ForegroundColor White
Write-Host "4. Cliquez sur : 'Mettre a niveau' (icone fleche circulaire)" -ForegroundColor White
Write-Host "5. Attendez 10-20 secondes" -ForegroundColor White
Write-Host "6. Rafraichissez la page (F5)" -ForegroundColor White
Write-Host ""
Write-Host "Puis verifiez le menu :" -ForegroundColor Yellow
Write-Host "  Gestion d'Inventaire > Import > 📦 Stock Initial" -ForegroundColor White
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

pause
