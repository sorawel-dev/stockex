# 📊 Stockex - Module de Gestion d'Inventaire Odoo 18/19

[![Version](https://img.shields.io/badge/version-18.0.5.0.0-blue.svg)](https://github.com/sorawel/stockex)
[![License](https://img.shields.io/badge/license-LGPL--3-green.svg)](LICENSE)
[![Odoo](https://img.shields.io/badge/Odoo-18.0%20%7C%2019.0-purple.svg)](https://www.odoo.com)

## 🎯 Description

**Stockex** est un module complet de gestion avancée des inventaires de stock pour Odoo 18 et 19, développé par **Sorawel**.

### ✨ Fonctionnalités Principales

- 📊 **Dashboard Interactif** avec KPIs temps réel et filtres avancés
- 🔌 **API REST** avec 6 endpoints pour intégrations externes
- 📱 **Application Mobile PWA** avec scan codes-barres et mode offline
- 📦 **Gestion Lots/Séries** avec traçabilité réglementaire complète
- 💊 **Conformité Pharma/Alimentaire** (certificats, alertes expiration)
- 📈 **Analytics Avancés** (5 KPIs + 3 graphiques Chart.js)
- 📥 **Import Multi-Format** (Excel, CSV, Kobo Collect)
- 💰 **Gestion Comptable** automatique avec génération d'écritures
- 🗺️ **Géolocalisation GPS** des entrepôts
- 🔄 **Comptage Cyclique** automatisé
- 📱 **Scan Codes-Barres** pour inventaire mobile
- 📷 **Pièces Jointes Photo** (3 photos/ligne)
- ✅ **Workflow d'Approbation** multi-niveaux
- 📈 **Rapports et Analyses** avancés
- 🌐 **Support i18n** (FR/EN)

## 📚 Documentation

La documentation complète est disponible dans le dossier [`docs/`](docs/) :

### 🚀 DÉMARRAGE - PROPOSITIONS D'ÉVOLUTION

🎯 **NOUVEAU** : Découvrez comment transformer Stockex en solution WMS Entreprise !

- [**⭐ INDEX COMPLET**](docs/INDEX_PROPOSITIONS.md) - Navigation des 7 documents (20 min)
- [**📊 SYNTHÈSE COMPLÈTE**](docs/SYNTHESE_COMPLETE.md) - Vue globale 26 propositions (20 min)
  - 15 Optimisations Techniques (13,500€)
  - 11 Enrichissements Fonctionnels (23,100€)
  - **ROI** : 8-12 mois | **Gains** : Performance x5, Productivité +60%

### 🚀 DÉmarrage Rapide
- [**Guide d'Installation**](docs/INSTALLATION.md) - Installation et configuration
- [**Quick Start**](docs/QUICK_START.md) - Démarrage rapide en 5 minutes
- [**Guide Utilisateur**](docs/GUIDE_UTILISATEUR.md) - Manuel utilisateur complet

### 💰 Gestion Comptable
- [**Gestion Comptable**](docs/GESTION_COMPTABLE.md) - Guide comptabilité complète
- [**Référence Rapide Comptabilité**](docs/REFERENCE_RAPIDE_COMPTABILITE.md) - Aide-mémoire

### 📥 Import de Données
- [**Guide Import CSV**](docs/GUIDE_IMPORT_CSV.md) - Import fichiers CSV
- [**Guide Acquisition Données**](docs/GUIDE_ACQUISITION_DONNEES.md) - Excel, CSV, Kobo
- [**Paramétrage Imports**](docs/PARAMETRAGE_IMPORTS.md) - Configuration imports

### 📊 Dashboard et Analytics
- [**Dashboard Guide**](docs/DASHBOARD_GUIDE.md) - Utilisation du dashboard
- [**Filtres Dynamiques**](docs/DASHBOARD_FILTRES_DYNAMIQUES.md) - Filtres avancés
- [**Page d'Accueil**](docs/PAGE_ACCUEIL.md) - Vue d'ensemble

### ⚙️ Configuration
- [**Configuration Catégories**](docs/CATEGORIES_PRODUITS_CONFIGURATION.md) - Catégories de produits
- [**Configuration Entrepôts**](docs/ENTREPOTS_CODE_WAREHOUSE.md) - Gestion entrepôts
- [**Affichage Emplacements**](docs/AFFICHAGE_EMPLACEMENTS.md) - Emplacements

### 📖 Référence Technique
- [**Index Documentation**](docs/DOCUMENTATION_INDEX.md) - Index complet
- [**Notes Techniques**](docs/NOTES_TECHNIQUES.md) - Documentation technique
- [**Changelog**](docs/CHANGELOG.md) - Historique des versions
- [**Nouvelles Fonctionnalités**](docs/NOUVELLES_FONCTIONNALITES.md) - Dernières features

### 🚀 Optimisations & Performance
- [**Guide Optimisations**](docs/OPTIMISATIONS_README.md) - Vue d'ensemble optimisations
- [**Propositions Détaillées**](docs/OPTIMISATIONS_PROPOSEES.md) - 15 optimisations prioritaires
- [**Exemples de Code**](docs/OPTIMISATIONS_CODE_EXEMPLES.md) - Code complet prêt à l'emploi
- [**Roadmap 12 Semaines**](docs/OPTIMISATIONS_ROADMAP.md) - Planning et budget
- [**Guide Implémentation**](docs/GUIDE_IMPLEMENTATION_OPTIMISATIONS.md) - Pas-à-pas technique

### 🎨 Enrichissements Fonctionnels
- [**Enrichissements Proposés**](docs/ENRICHISSEMENTS_FONCTIONNELS.md) - 11 enrichissements fonctionnels majeurs
  - Gestion Lots/Séries (traçabilité complète)
  - Application Mobile PWA (inventaire terrain)
  - Analytics Prédictifs ML (anticipation ruptures)
  - Intégration ERP Multi-systèmes
  - IoT & Capteurs Automatiques

### 🔄 Migration et Compatibilité
- [**Compatibilité Odoo 18/19**](docs/COMPATIBILITE_ODOO_18_19.md) - Guide compatibilité
- [**Migration Odoo 19**](docs/MIGRATION_ODOO19.md) - Guide migration
- [**Installation/Upgrade**](docs/INSTALLATION_UPGRADE.md) - Mise à jour

## 🔧 Installation Rapide

```bash
# 1. Copier le module dans addons
cp -r stockex /path/to/odoo/addons/

# 2. Installer les dépendances Python
pip install openpyxl python-barcode

# 3. Mettre à jour la liste des modules dans Odoo
# Apps → Mettre à jour la liste

# 4. Installer le module
# Apps → Rechercher "Stockex" → Installer
```

## 📦 Dépendances

### Modules Odoo
- `base`, `mail`, `stock`, `product`, `account`

### Bibliothèques Python
- `openpyxl` - Import/Export Excel
- `python-barcode` - Génération codes-barres

## 🆕 Nouveautés Version 18.0.4.0.0

### 🎯 Enrichissements Fonctionnels Phase 1 & 2

#### 🔌 API REST (Phase 1 - Fondations)
- ✅ **6 endpoints REST** pour intégrations externes
- ✅ Réponses JSON formatées avec gestion erreurs
- ✅ CORS headers pour accès cross-origin
- ✅ Pagination et filtres multiples
- 📖 Voir [Guide API REST](docs/QUICK_START_v18.0.4.md#-api-rest)

#### 📦 Gestion Lots & Traçabilité (Phase 2.1)
- ✅ **Inventaire par lot/série** avec alertes expiration
- ✅ **Traçabilité réglementaire** (pharma, alimentaire, cosmétique)
- ✅ **Alertes automatiques** : J-60, J-30, expiré (couleurs rouge/jaune)
- ✅ **Conformité qualité** : certificats, statut (approuvé/quarantaine/rejeté)
- ✅ **Menu "Lots Expirant"** pour gestion péremption
- ✅ **Historique inventaires par lot** (product recall)
- 📖 Voir [Guide Lots & Traçabilité](docs/QUICK_START_v18.0.4.md#-gestion-lots--traçabilité)

#### 📊 Dashboard Analytique Avancé (Phase 2.2)
- ✅ **5 KPIs essentiels** temps réel :
  - Total Inventaires / Validés
  - Précision Moyenne (%) → Objectif > 95%
  - Valeur Écarts (€)
  - Taux Rotation Stock
- ✅ **3 graphiques Chart.js** :
  - Tendance inventaires (12 mois)
  - Valeur stock par catégorie (Top 10)
  - Écarts par catégorie (Top 10, rouge/vert)
- ✅ **6 périodes** : Aujourd'hui / Semaine / Mois / Trimestre / Année / Personnalisé
- 📖 Voir [Guide Dashboard Analytics](docs/QUICK_START_v18.0.4.md#-dashboard-analytique)

**ROI Estimé** : 6,000€ investissement → 50,000€+ gains/an → **Breakeven 8-12 mois** ✅

---

## 🆕 Nouveautés Version 18.0.5.0.0

### 📱 Application Mobile PWA (Phase 4 - Mobilité)

#### 🚀 Progressive Web App Complète
- ✅ **Installation écran d'accueil** (iOS + Android) - Mode standalone
- ✅ **Mode offline complet** : Service Worker + IndexedDB
- ✅ **Synchronisation automatique** : Queue locale + upload quand online
- ✅ **Interface tactile** optimisée terrain (touch targets 48px)
- 📖 Voir [Guide Mobile PWA](docs/MOBILE_PWA_SUCCESS.md)

#### 📷 Scanner Codes-Barres
- ✅ **QuaggaJS 1.7.3** : Scan via caméra mobile
- ✅ **6 formats** : EAN-13, EAN-8, Code 128, Code 39, UPC, UPC-E
- ✅ **Feedback complet** : Beep sonore + vibration + overlay visuel
- ✅ **Flash/torche** toggleable (si supporté)
- ✅ **Debounce** anti-doublons (1 seconde)

#### 💾 Stockage Offline (IndexedDB)
- ✅ **2 stores** : pending_inventories + cached_products
- ✅ **Cache-first** : Recherche locale avant serveur
- ✅ **Queue locale** : Inventaires sauvegardés même sans réseau
- ✅ **Sync auto** : Upload quand connexion rétablie

#### 🎯 Features Mobile
- ✅ **5 pages HTML** : Accueil, Scanner, Nouveau, Détail, Offline
- ✅ **4 API JSON** : Sync, Search, Add-line, Get-lines
- ✅ **PWA Manifest** : 8 icônes + shortcuts + share target
- ✅ **2,279 lignes code** mobile (JS + CSS + Python + XML)

**ROI Mobile** : **0€ matériel** (vs PDA 10K€) → **+200% productivité** scan → **ROI immédiat** ✅

---

## 🆕 Nouveautés Version 18.0.4.0.0

### 💰 Gestion Comptable Intégrée
- ✅ Génération automatique d'écritures comptables
- ✅ Assistant de stock initial pour BD vide
- ✅ Configuration guidée des catégories de produits

### 📱 Fonctionnalités Mobiles
- ✅ Scan de codes-barres mobile
- ✅ Pièces jointes photo (3 photos/ligne)
- ✅ Intégration Kobo Collect améliorée

### 📊 Analytics Avancés
- ✅ Comparaison d'inventaires entre périodes
- ✅ Rapports de variance détaillés
- ✅ Dashboard avec filtres dynamiques

## 🎯 Cas d'Usage

- ✅ **PME/PMI** - Gestion inventaire complète
- ✅ **Grande Distribution** - Multi-entrepôts
- ✅ **ONG/Humanitaire** - Collecte mobile terrain (Kobo)
- ✅ **Industrie** - Comptage cyclique automatisé
- ✅ **Commerce** - Valorisation stock en temps réel

## 📊 Captures d'Écran

Pour des illustrations détaillées, consultez le [Guide Utilisateur](docs/GUIDE_UTILISATEUR.md).

## 🤝 Support et Contribution

### Contact
- **Développeur** : Sorawel
- **Site Web** : [www.sorawel.com](https://www.sorawel.com)
- **Email** : contact@sorawel.com

### Contribuer
Les contributions sont bienvenues ! Consultez notre [guide de contribution](docs/NOTES_TECHNIQUES.md).

## 📄 Licence

**LGPL-3** - Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🏆 Crédits

**Développé avec ❤️ par [Sorawel](https://www.sorawel.com)**

---

⭐ **Si ce module vous est utile, n'hésitez pas à le partager !**
