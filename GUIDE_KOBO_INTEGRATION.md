# 📱 Guide d'Intégration Kobo Collect avec Odoo Stockex

## 🎯 Vue d'ensemble

Ce guide explique comment connecter votre instance Odoo au système KoboToolbox pour importer automatiquement les données d'inventaire collectées sur le terrain.

## ✅ Prérequis

### 1. Dépendances Python
```bash
pip3 install requests
```

### 2. Informations de connexion Kobo
- **URL Kobo** : `https://kf.kobotoolbox.org`
- **Token API** : `9f93fe1e5a6537bfabb6c935ca852264cefa30ee`
- **ID Formulaire** : `aQJVWdSP4xyzhru6Ztfo4Q`
- **Nom du formulaire** : `001_Bassa_Distribution_Central_Warehouse`

## 📋 Configuration dans Odoo

### Étape 1 : Installer le module Stockex
1. Copier le module dans votre dossier `addons`
2. Mettre à jour la liste des applications
3. Installer le module `Stockex`

### Étape 2 : Configuration automatique
Le module crée automatiquement une configuration Kobo avec les paramètres suivants :

**Mapping des champs Kobo → Odoo :**
- **Code produit** : `begin_group_TSW6h0mGE/material_description`
- **Nom produit** : `begin_group_TSW6h0mGE/nom_materiel`
- **Quantité** : `begin_group_TSW6h0mGE/quantity`
- **Emplacement** : `begin_group_TSW6h0mGE/Sous_magasin`
- **Marque** : `begin_group_TSW6h0mGE/marque`
- **Type d'article** : `begin_group_TSW6h0mGE/type_article`
- **GPS** : `_geolocation` (tableau [latitude, longitude])
- **Photo produit** : `begin_group_TSW6h0mGE/photo`
- **Photo étiquette** : `begin_group_HZpqEzA1G/Ajouter_une_photo_de_te_d_inventaire_ENEO`

### Étape 3 : Vérifier la configuration
1. Aller dans **Stockex → Configuration → Configuration Kobo Collect**
2. Ouvrir la configuration "Configuration Kobo - Magasin Douala"
3. Cliquer sur **Tester la Connexion**
4. Vérifier que la connexion est réussie ✅

## 🔄 Importer les données

### Option 1 : Import manuel

1. **Menu** : `Stockex → Kobo Collect → Importer depuis Kobo`
2. **Remplir le formulaire** :
   - Nom de l'inventaire : `Inventaire Terrain Douala - [Date]`
   - Date : Sélectionner la date
   - Configuration Kobo : Sélectionner la configuration active
   - Mode d'import :
     - **Nouvelles soumissions uniquement** : Import depuis la dernière synchronisation
     - **Toutes les soumissions** : Import complet
     - **Plage de dates** : Import d'une période spécifique

3. **Options** :
   - ✅ Créer les produits manquants
   - ✅ Créer les emplacements manquants
   - ✅ Importer la géolocalisation
   - ⬜ Valider automatiquement (déconseillé)

4. **Lancer l'import** : Cliquer sur "Importer"

### Option 2 : Import automatique (cron)

1. Activer l'import automatique dans la configuration Kobo
2. Le système importera automatiquement toutes les nouvelles soumissions

## 📊 Données importées

### Pour chaque soumission Kobo, le système crée :

1. **Produit** (si n'existe pas) :
   - Code : `200000825`
   - Nom : `TWISTED ALU LV CABLE 2X16mm²`
   - Marque : Ajoutée dans la description
   - Type de tracking : Sérialisé ou non selon le type d'article

2. **Emplacement** (si n'existe pas) :
   - Entrepôt principal : Ex. "Bassa"
   - Sous-emplacement : Ex. "GÉNÉRAL BASSA"

3. **Ligne d'inventaire** :
   - Produit
   - Quantité : `222234`
   - Emplacement
   - Coordonnées GPS (latitude, longitude)
   - Notes : Marque, type, photos, etc.

## 🗺️ Structure des données Kobo

### Exemple de soumission :
```json
{
  "_id": 584574064,
  "_submission_time": "2025-10-17T09:22:29",
  "_geolocation": [4.0478878, 9.740594],
  "begin_group_TSW6h0mGE/material_description": "200000825",
  "begin_group_TSW6h0mGE/nom_materiel": "TWISTED ALU LV CABLE 2X16mm²",
  "begin_group_TSW6h0mGE/quantity": "222234",
  "begin_group_TSW6h0mGE/Sous_magasin": "General bassa",
  "begin_group_TSW6h0mGE/marque": "EVERWELL",
  "begin_group_TSW6h0mGE/type_article": "non_serialise",
  "begin_group_TSW6h0mGE/photo": "1760692176687.jpg",
  "_attachments": [...]
}
```

## 🛠️ Tests et Diagnostic

### Test de connexion API
```bash
cd /home/one/apps/stockex
python3 scripts/test_kobo_api.py
```

### Résultat attendu :
```
✅ Connexion réussie!
   - Nom du formulaire: 001_Bassa_Distribution_Central_Warehouse
   - Nombre de soumissions: 53
📊 Total de soumissions: 53
📍 Répartition par magasin: ...
```

### Analyser la structure des données
```bash
python3 scripts/analyze_kobo_structure.py
```

## 📈 Statistiques actuelles

D'après le fichier Excel analysé (291025) :
- **Total d'articles** : 494 articles
- **Quantité totale** : 4 790 489 unités
- **Magasins** :
  - Koumassi : 412 articles (83.4%)
  - Bassa : 53 articles (10.7%)
  - Bassa Kits Comp : 15 articles (3.0%)
  - Bassa Kits : 14 articles (2.8%)

## ⚙️ Configuration avancée

### Modifier le mapping des champs

Si la structure de votre formulaire Kobo change :

1. Aller dans **Configuration Kobo Collect**
2. Modifier les champs de mapping selon la nouvelle structure
3. Tester la connexion
4. Lancer un import test

### Créer une nouvelle configuration

Pour un nouveau formulaire Kobo :

1. Créer une nouvelle configuration
2. Entrer l'ID du formulaire
3. Configurer le mapping des champs
4. Désactiver l'ancienne configuration
5. Activer la nouvelle

## 🔐 Sécurité

- Le token API est stocké de manière sécurisée dans la base de données Odoo
- Seuls les utilisateurs avec les droits appropriés peuvent accéder à la configuration Kobo
- Les imports sont tracés et journalisés

## 🐛 Dépannage

### Problème : "requests module not found"
**Solution** : `pip3 install requests`

### Problème : "Erreur de connexion à Kobo"
**Vérifier** :
- La connexion Internet
- Le token API est valide
- L'ID du formulaire est correct

### Problème : "Produits non créés"
**Vérifier** :
- L'option "Créer les produits manquants" est activée
- Les codes produits sont valides dans les soumissions Kobo

### Problème : "Emplacements non trouvés"
**Solution** : Activer "Créer les emplacements manquants"

## 📞 Support

Pour toute question ou problème :
1. Consulter les logs Odoo
2. Vérifier les messages d'erreur dans l'inventaire créé
3. Utiliser les scripts de test pour diagnostiquer

## 🔄 Flux de travail recommandé

1. **Collecte terrain** : Utilisez Kobo Collect sur mobile/tablette
2. **Synchronisation** : Les données sont envoyées à KoboToolbox
3. **Import Odoo** : Lancez l'import manuel ou attendez l'import automatique
4. **Vérification** : Vérifiez l'inventaire créé
5. **Validation** : Validez l'inventaire après vérification
6. **Génération comptable** : Les écritures comptables sont générées automatiquement

## ✨ Fonctionnalités avancées

- 📸 Import des photos (URLs stockées dans les notes)
- 🗺️ Géolocalisation GPS des emplacements
- 🔄 Synchronisation incrémentale (nouvelles soumissions uniquement)
- 📊 Statistiques d'import
- ⚡ Création automatique des produits et emplacements
- 🏷️ Gestion des articles sérialisés/non sérialisés

---

**Date de création** : 2025-11-04  
**Version** : 1.0  
**Module** : Stockex pour Odoo 18/19
