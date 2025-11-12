# 📱 MÉMO D'UTILISATION - STOCKEX MOBILE

## 🎯 Accès à l'Application

**URL d'accès :**
```
https://odoo-minee.kesafrica.com/stockex/mobile
```

**Prérequis :**
- Compte utilisateur Odoo actif
- Smartphone Android/iOS
- Navigateur : Chrome, Safari, Firefox ou Edge

---

## 📲 Installation PWA

### Sur Android (Chrome)
1. Ouvrir l'URL dans Chrome
2. Cliquer sur la bannière "Ajouter à l'écran d'accueil"
3. Ou : Menu (⋮) → "Installer l'application"
4. L'icône Stockex apparaît sur l'écran d'accueil

### Sur iOS (Safari)
1. Ouvrir l'URL dans Safari
2. Appuyer sur le bouton Partager (□↑)
3. Sélectionner "Sur l'écran d'accueil"
4. Nommer : "Stockex"
5. Appuyer sur "Ajouter"

---

## 🔐 Première Utilisation

1. **Connexion :** Identifiants Odoo habituels
2. **Autorisations à accorder :**
   - 📸 Caméra (pour scan codes-barres)
   - 📍 Localisation (optionnel)
   - 🔔 Notifications (pour alertes sync)

---

## 📋 Créer un Inventaire

### Étapes
1. Page d'accueil → **"Nouvel Inventaire"**
2. Sélectionner **l'emplacement** (liste déroulante)
3. Choisir la **date** (par défaut : aujourd'hui)
4. Cliquer **"Créer l'inventaire"**

✅ Vous êtes redirigé vers l'interface de scan

---

## 📸 Scanner des Produits

### Utilisation du Scanner
1. Cliquer **"Scanner Code-Barres"**
2. Pointer la caméra vers le code-barres
3. **Bip + vibration** = code détecté
4. Informations produit affichées
5. Saisir la **quantité comptée**
6. Cliquer **"Ajouter à l'inventaire"**

### Formats codes-barres supportés
- EAN-13, EAN-8
- Code 128, Code 39
- UPC, UPC-E

### Astuces
- 💡 Bouton flash disponible (si compatible)
- ⏱️ Anti-doublon : 1 seconde entre chaque scan
- 🔍 Cadre vert = zone de scan optimale

---

## 🔌 Mode Hors Ligne

### Fonctionnement
- ✅ **Création inventaire** : stocké localement
- ✅ **Scan codes-barres** : fonctionne sans réseau
- ✅ **Ajout lignes** : enregistré dans cache
- 🔄 **Synchronisation auto** : au retour en ligne

### Indicateurs
- 🟢 Badge vert : "En ligne"
- 🟡 Badge jaune : "Hors ligne"
- 🔄 Badge bleu : "Synchronisation..."

### Capacité de stockage
- ~1000 inventaires possibles hors ligne
- Produits scannés mis en cache automatiquement

---

## 🔄 Synchronisation

### Automatique
- Détection automatique du retour en ligne
- Notification : "Connexion rétablie"
- Synchronisation immédiate
- Confirmation : "X inventaire(s) synchronisé(s)"

### Manuelle
1. Page d'accueil
2. Bouton **"Synchroniser (X)"**
3. Attendre confirmation

### En cas d'erreur
- Message d'erreur affiché
- Inventaire conservé en local
- Retenter la synchronisation plus tard

---

## 🗂️ Navigation

### Barre de navigation (bas d'écran)

| Icône | Fonction |
|-------|----------|
| 🏠 Accueil | Page principale |
| 📸 Scanner | Lancer le scan |
| ➕ Nouveau | Créer inventaire |

---

## 📊 Voir les Inventaires

1. Créer inventaire
2. Scanner plusieurs produits
3. Menu → **"Voir inventaires"**
4. Liste détaillée des lignes :
   - Produit
   - Quantité théorique
   - Quantité réelle
   - Écart (en couleur)

---

## ⚙️ Paramètres Caméra

### Optimiser le scan
- Bien éclairer le code-barres
- Distance : 10-20 cm
- Maintenir stable 1-2 secondes
- Utiliser le flash si nécessaire

### Activer/désactiver flash
- Bouton dédié pendant le scan
- Compatible Android uniquement

---

## 🚨 Résolution de Problèmes

### Le scanner ne fonctionne pas
- ✅ Vérifier autorisation caméra
- ✅ Rafraîchir la page
- ✅ Redémarrer l'application

### Produit non trouvé
- ❓ Code-barres non enregistré dans Odoo
- 💡 Vérifier dans Odoo Desktop
- 📝 Ajouter le code-barres manuellement

### Synchronisation bloquée
- 🌐 Vérifier connexion Internet
- 🔄 Réessayer manuellement
- 📞 Contacter support si persiste

### Application lente
- 🗑️ Vider le cache navigateur
- 📱 Libérer espace de stockage
- 🔄 Réinstaller l'application

---

## 💡 Bonnes Pratiques

### Avant le terrain
- ✅ Installer l'application PWA
- ✅ Tester le scanner
- ✅ Vérifier batterie smartphone
- ✅ Télécharger produits fréquents (scan à vide)

### Pendant l'inventaire
- ⚡ Activer mode avion (économie batterie)
- 📝 Scanner méthodiquement par zone
- 💾 Sauvegarder régulièrement (auto)
- 🔋 Recharger si batterie < 20%

### Après l'inventaire
- 🌐 Se reconnecter au WiFi
- 🔄 Attendre synchronisation complète
- ✅ Vérifier dans Odoo Desktop
- 📊 Générer rapport si besoin

---

## 📞 Support

**En cas de problème :**
- 📧 Email : support@stockex.com
- 📱 Telegram : Notification automatique
- 🌐 Documentation : Odoo → Stockex → Aide

---

**Version :** 1.0.0  
**Dernière mise à jour :** Novembre 2025  
**Compatible :** Odoo 18/19
