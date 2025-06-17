# Script PowerShell pour publier sur GitHub
# Automatise la publication sur https://github.com/JULIEN-85/Projet_FTP.git

Write-Host "🚀 Publication du Projet Photo Transfer System sur GitHub" -ForegroundColor Cyan
Write-Host "Repository: https://github.com/JULIEN-85/Projet_FTP.git" -ForegroundColor Yellow
Write-Host ""

# Configuration Git (ajustez avec votre email)
Write-Host "⚙️  Configuration Git..." -ForegroundColor Yellow
git config --global user.name "JULIEN-85"
git config --global user.email "votre.email@example.com"  # CHANGEZ ICI

# Vérifier si Git est initialisé
if (-not (Test-Path ".git")) {
    Write-Host "📁 Initialisation Git..." -ForegroundColor Yellow
    git init
}

# Ajouter le remote (supprime s'il existe déjà)
Write-Host "🔗 Configuration du repository distant..." -ForegroundColor Yellow
git remote remove origin 2>$null
git remote add origin https://github.com/JULIEN-85/Projet_FTP.git

# Remplacer le README par la version GitHub
if (Test-Path "README_GITHUB.md") {
    Write-Host "📝 Mise à jour du README pour GitHub..." -ForegroundColor Yellow
    if (Test-Path "README.md") {
        Move-Item "README.md" "README_ORIGINAL.md" -Force
    }
    Move-Item "README_GITHUB.md" "README.md" -Force
}

# Ajouter tous les fichiers
Write-Host "📦 Ajout des fichiers..." -ForegroundColor Yellow
git add .

# Vérifier les fichiers ajoutés
Write-Host "📋 Fichiers à publier:" -ForegroundColor Green
git status --porcelain

# Demander confirmation
Write-Host ""
$confirm = Read-Host "Continuer la publication? (o/N)"
if ($confirm -ne "o" -and $confirm -ne "O") {
    Write-Host "❌ Publication annulée" -ForegroundColor Red
    exit
}

# Commit
Write-Host "💾 Création du commit..." -ForegroundColor Yellow
$commitMessage = "Initial commit: Photo Transfer System v1.0

🚀 Complete automated photo transfer solution for Raspberry Pi

Features:
✅ gPhoto2 integration for cameras and Android phones
✅ Modern web interface with real-time monitoring  
✅ Automatic FTP upload with retry mechanism
✅ Systemd services for auto-start
✅ Raspberry Pi 5 optimizations
✅ Comprehensive testing and documentation

Supported hardware:
📸 Canon, Nikon, Sony cameras (gPhoto2 compatible)
📱 Android phones in PTP mode
🥧 Raspberry Pi 4/5

Ready for production deployment!"

git commit -m $commitMessage

# Pousser vers GitHub
Write-Host "🚀 Publication vers GitHub..." -ForegroundColor Yellow
git branch -M main
git push -u origin main

# Créer un tag pour la version
Write-Host "🏷️  Création du tag v1.0.0..." -ForegroundColor Yellow
git tag -a v1.0.0 -m "Version 1.0.0 - Initial release

Complete photo transfer system with:
- Camera and phone support
- Web interface
- FTP automation
- Raspberry Pi optimization"

git push origin v1.0.0

Write-Host ""
Write-Host "🎉 Publication terminée avec succès!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Votre projet est maintenant disponible sur:" -ForegroundColor Cyan
Write-Host "   👉 https://github.com/JULIEN-85/Projet_FTP" -ForegroundColor White
Write-Host ""
Write-Host "📝 Prochaines étapes recommandées:" -ForegroundColor Yellow
Write-Host "   1. Aller sur GitHub et vérifier que tout est publié" -ForegroundColor White
Write-Host "   2. Ajouter une description au repository" -ForegroundColor White
Write-Host "   3. Ajouter des topics: raspberry-pi, python, photography, automation" -ForegroundColor White
Write-Host "   4. Étoiler votre propre projet 🌟" -ForegroundColor White
Write-Host ""
Write-Host "🔗 Lien direct: https://github.com/JULIEN-85/Projet_FTP" -ForegroundColor Cyan

# Ouvrir le repository dans le navigateur
$openBrowser = Read-Host "Ouvrir le repository dans le navigateur? (o/N)"
if ($openBrowser -eq "o" -or $openBrowser -eq "O") {
    Start-Process "https://github.com/JULIEN-85/Projet_FTP"
}
