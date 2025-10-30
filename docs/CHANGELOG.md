# Changelog - Module Stockex

Tous les changements notables de ce projet seront documentés dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

---

## [18.0.2.0.0] - 2025-10-24

### ✨ Ajouté

#### Fonctionnalités Utilisateur
- **Scan de codes-barres mobile** pour saisie rapide des inventaires
  - Champ `scanned_barcode` sur lignes d'inventaire
  - Auto-détection et remplissage du produit
  - Validation en temps réel avec messages d'erreur
  
- **Pièces jointes photo** sur les lignes d'inventaire
  - Support de 3 photos par ligne (`image_1`, `image_2`, `image_3`)
  - Champ notes (`note`) pour remarques
  - Stockage optimisé en base64 avec `attachment=True`
  
- **Workflow d'approbation multi-niveaux**
  - Nouveaux états : `pending_approval`, `approved`
  - Nouveaux champs : `approver_id`, `approval_date`, `validator_id`, `validation_date`
  - Méthodes : `action_request_approval()`, `action_approve()`, `action_reject()`
  - Création automatique d'activités pour les managers
  
- **Comparaison d'inventaires entre périodes**
  - Nouveau modèle `stockex.inventory.comparison` (assistant)
  - Nouveau modèle `stockex.inventory.comparison.result` (résultats)
  - Comparaison quantités, valeurs, écarts
  - Génération de rapports HTML
  - Filtrage par différences uniquement
  
- **Comptage cyclique automatisé**
  - Nouveau modèle `stockex.cycle.count.config` (configuration)
  - Nouveau modèle `stockex.cycle.count.scheduler` (planificateur)
  - Fréquences : quotidien, hebdomadaire, mensuel, trimestriel
  - Sélection intelligente de produits par ABC
  - Génération automatique d'inventaires
  
- **Génération de codes-barres pour emplacements**
  - Nouveau champ `barcode` sur `stock.location`
  - Nouveau champ calculé `barcode_image` (Code128)
  - Méthode `action_generate_barcode()` - génération unique
  - Méthode `action_print_barcode_labels()` - impression étiquettes
  - Format : `LOC` + ID sur 10 chiffres
  
- **Rapports de variance de stock**
  - Nouveau modèle `stockex.stock.variance.report` (vue SQL)
  - Nouveau modèle `stockex.variance.analysis.wizard` (assistant)
  - Classification par sévérité (critique/élevé/moyen/faible)
  - Calcul écarts en quantité et valeur
  - Filtres avancés (dates, emplacements, catégories, sévérité)
  - Vues liste, graph, pivot

#### Automatisation
- **3 nouvelles actions planifiées (crons)**
  - `ir_cron_kobo_auto_sync` : Synchronisation automatique Kobo Collect (1h, désactivé par défaut)
  - `ir_cron_cycle_count_scheduler` : Génération comptages cycliques (quotidien 02:00)
  - `ir_cron_inventory_reminders` : Rappels inventaires en cours >7j (quotidien 09:00)
  
- **Méthodes cron ajoutées**
  - `stockex.kobo.config._cron_auto_sync()` : Sync auto Kobo
  - `stockex.cycle.count.scheduler.run_scheduled_cycle_counts()` : Génération comptages
  - `stockex.stock.inventory._send_inventory_reminders()` : Envoi rappels

#### Qualité & Tests
- **Suite de tests unitaires complète**
  - 10 tests couvrant toutes les nouvelles fonctionnalités
  - Classe `TestStockInventory` dans `tests/__init__.py`
  - Tests workflow, scan, photos, approbation, comparaison, etc.
  - Exécution avec `--test-enable`
  
- **Support internationalization (i18n)**
  - Template de traduction `i18n/stockex.pot`
  - Traductions FR/EN pour 100+ éléments
  - Messages d'erreur traduits
  - Labels et descriptions bilingues

#### Documentation
- **Nouvelles documentations**
  - `NOUVELLES_FONCTIONNALITES.md` : Documentation détaillée des 10 améliorations
  - `IMPLEMENTATION_SUMMARY.md` : Résumé d'implémentation technique
  - `QUICK_START.md` : Guide de démarrage rapide
  - `CHANGELOG.md` : Ce fichier
  - README.md mis à jour avec nouvelles fonctionnalités

### 🔄 Modifié

#### Modèles Existants
- **stockex.stock.inventory**
  - Ajout états `pending_approval`, `approved` dans workflow
  - Ajout champs approbation et validation
  - Méthode `action_validate()` mise à jour avec champs de validation
  
- **stockex.stock.inventory.line**
  - Ajout champs scan codes-barres
  - Ajout champs photos (3) et notes
  - Nouvelle méthode `_onchange_scanned_barcode()`
  
- **stock.location** (hérité)
  - Ajout champs `barcode` et `barcode_image`
  - Nouvelles méthodes de génération et affichage
  - Import logging et UserError

- **stockex.kobo.config**
  - Ajout méthode `_cron_auto_sync()` pour automatisation

#### Configuration
- **__manifest__.py**
  - Description mise à jour avec nouvelles fonctionnalités
  - Ajout dépendance Python `barcode`
  - Ajout fichier `data/cron_jobs.xml` dans data
  - Version bump : 18.0.1.0.0 → 18.0.2.0.0
  
- **models/__init__.py**
  - Import des 3 nouveaux modules : `cycle_count`, `inventory_comparison`, `variance_report`

### 🐛 Corrigé
- Amélioration gestion des erreurs dans scan codes-barres
- Validation robuste dans workflow d'approbation
- Optimisation requêtes SQL dans rapport variance

### 🔒 Sécurité
- Validation stricte des entrées utilisateur
- Contraintes d'unicité sur codes-barres
- Gestion sécurisée des pièces jointes

### ⚡ Performance
- Vue SQL optimisée pour rapport variance (agrégations directes en DB)
- Cache produits/emplacements dans imports (déjà existant)
- Batch processing dans crons

### 📦 Dépendances
- **Ajouté** : `python-barcode` pour génération codes-barres
- **Maintenu** : `openpyxl`, `requests` (optionnel)

---

## [18.0.1.0.0] - 2025-10-20

### ✨ Ajouté
- Module initial de gestion d'inventaire
- Import Excel/CSV
- Intégration Kobo Collect
- Dashboard interactif avec KPIs
- Analyse des écarts
- Géolocalisation GPS des entrepôts
- Export Excel/PDF
- Workflow de base (Brouillon → En cours → Validé)
- Traçabilité complète avec chatter

### 🏗️ Architecture
- Modèle principal `stockex.stock.inventory`
- Lignes `stockex.stock.inventory.line`
- Dashboard `stockex.inventory.dashboard` (vue SQL)
- Résumé `stockex.inventory.summary`
- Configuration Kobo `stockex.kobo.config`
- Extensions `stock.warehouse` et `stock.location`

### 📊 Fonctionnalités
- Calcul automatique quantités théoriques
- Différences colorées (rouge/vert)
- Top 5 catégories et entrepôts
- Valorisation en FCFA
- Multi-société
- Rapports PDF personnalisés

---

## Légende des Types de Changements

- **✨ Ajouté** : Nouvelles fonctionnalités
- **🔄 Modifié** : Changements de fonctionnalités existantes
- **⚠️ Déprécié** : Fonctionnalités bientôt supprimées
- **❌ Supprimé** : Fonctionnalités retirées
- **🐛 Corrigé** : Corrections de bugs
- **🔒 Sécurité** : Corrections de vulnérabilités
- **⚡ Performance** : Améliorations de performance
- **📦 Dépendances** : Modifications de dépendances

---

## Liens

- [Code Source](https://github.com/sorawel/stockex)
- [Documentation](https://www.sorawel.com/docs/stockex)
- [Support](mailto:contact@sorawel.com)

---

**Maintenu par [Sorawel](https://www.sorawel.com)**
