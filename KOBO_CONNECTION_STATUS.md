# 🔌 Connexion Kobo Collect - Configuration Complète

## ✅ État de la Connexion

**Statut** : ✅ CONNECTÉ ET FONCTIONNEL

### Informations de connexion
- **URL Kobo** : `https://kf.kobotoolbox.org`
- **Utilisateur** : `kes237`
- **Token API** : `9f93fe1e5a6537bfabb6c935ca852264cefa30ee`
- **ID Formulaire** : `aQJVWdSP4xyzhru6Ztfo4Q`
- **Nom du formulaire** : `001_Bassa_Distribution_Central_Warehouse`

### Statistiques actuelles (Test réussi le 2025-11-04)
- ✅ **53 soumissions** disponibles
- ✅ **40 soumissions** importables
- ⚠️ **13 soumissions** avec des données incomplètes
- 📦 **38 produits uniques**
- 📊 **511 215 unités** en stock
- 📍 **5 emplacements** différents

## 📋 Configuration automatique

Le fichier `data/kobo_config_data.xml` configure automatiquement :

### 1. Connexion API
```xml
<field name="kobo_url">https://kf.kobotoolbox.org</field>
<field name="api_token">9f93fe1e5a6537bfabb6c935ca852264cefa30ee</field>
<field name="form_id">aQJVWdSP4xyzhru6Ztfo4Q</field>
```

### 2. Mapping des champs

| Champ Odoo | Champ Kobo | Description |
|------------|-----------|-------------|
| Code produit | `begin_group_TSW6h0mGE/material_description` | Code article ERP |
| Nom produit | `begin_group_TSW6h0mGE/nom_materiel` | Description du matériel |
| Quantité | `begin_group_TSW6h0mGE/quantity` | Quantité comptée |
| Emplacement | `begin_group_TSW6h0mGE/Sous_magasin` | Magasin/Sous-magasin |
| Marque | `begin_group_TSW6h0mGE/marque` | Fabricant |
| Type | `begin_group_TSW6h0mGE/type_article` | Sérialisé/Non sérialisé |
| GPS | `_geolocation` | Coordonnées [lat, lon] |
| Photo produit | `begin_group_TSW6h0mGE/photo` | Nom fichier photo |
| Photo étiquette | `begin_group_HZpqEzA1G/Ajouter_une_photo_de_te_d_inventaire_ENEO` | Photo étiquette |

## 🚀 Utilisation dans Odoo

### Import manuel
1. Menu : **Stockex → Kobo Collect → Importer depuis Kobo**
2. Sélectionner la configuration active
3. Choisir le mode d'import :
   - **Nouvelles soumissions uniquement** : Import incrémental
   - **Toutes les soumissions** : Import complet (53 soumissions)
   - **Plage de dates** : Import sélectif
4. Cliquer sur **Importer**

### Import automatique (Cron)
Activer dans **Configuration Kobo → Import Automatique**

## 📊 Données d'exemple

### Soumission type :
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
  "begin_group_TSW6h0mGE/type_article": "non_serialise"
}
```

### Résultat dans Odoo :
- **Produit créé** : `[200000825] TWISTED ALU LV CABLE 2X16mm²`
- **Marque** : EVERWELL (dans description)
- **Quantité** : 222 234 unités
- **Emplacement** : General bassa
- **GPS** : 4.047888°N, 9.740594°E
- **Type** : Non sérialisé

## 🧪 Tests disponibles

### Test de connexion
```bash
python3 scripts/test_kobo_api.py
```
**Résultat attendu** : ✅ Connexion réussie, 53 soumissions

### Test d'import (simulation)
```bash
python3 scripts/test_kobo_import.py
```
**Résultat attendu** : ✅ 40/53 soumissions importables

### Analyse de structure
```bash
python3 scripts/analyze_kobo_structure.py
```
**Résultat** : Structure complète des données

## 📍 Répartition des emplacements

| Emplacement | Articles | Pourcentage |
|-------------|----------|-------------|
| GÉNÉRAL BASSA | 19 | 47.5% |
| HANGAR MAGASIN | 16 | 40.0% |
| Général bassa | 3 | 7.5% |
| General bassa | 1 | 2.5% |
| SÉNÉGAL BASSA | 1 | 2.5% |

## 🏷️ Top Marques

1. Schneider Electric (3 articles)
2. EVERWELL (2 articles)
3. CAHORS (2 articles)
4. SADTEM, CANADA, Nexans, etc. (1 article chacun)

## ⚙️ Options de configuration

- ✅ **Créer les produits manquants** : Activé
- ✅ **Créer les emplacements manquants** : Activé
- ⬜ **Import automatique** : Désactivé par défaut
- ⬜ **Validation automatique** : Désactivé (recommandé)
- ✅ **Importer la géolocalisation** : Activé

## 🔧 Dépannage

### Problème : Soumissions ignorées
**Cause** : Certaines soumissions ont des champs None ou vides
**Solution** : Vérifier les données dans KoboToolbox, compléter si nécessaire

### Problème : Erreur "unsupported format string"
**Cause** : Valeur None dans le champ quantité ou nom
**Solution** : Le wizard filtre automatiquement ces soumissions

### Problème : Doublons d'emplacements
**Observé** : "General bassa" vs "GÉNÉRAL BASSA" vs "Général bassa"
**Solution** : Normaliser les noms dans KoboToolbox ou fusionner manuellement dans Odoo

## 📈 Prochaines améliorations possibles

1. ✨ Normalisation automatique des noms d'emplacements
2. 📸 Téléchargement automatique des photos (actuellement URL uniquement)
3. 🔄 Gestion des mises à jour (si une soumission est modifiée)
4. 📊 Dashboard de suivi des imports
5. 🔔 Notifications d'import réussi/échoué

## 📚 Documentation complète

Voir : `/home/one/apps/stockex/GUIDE_KOBO_INTEGRATION.md`

---

**Dernière mise à jour** : 2025-11-04  
**Status** : ✅ PRODUCTION READY  
**Version** : 1.0
