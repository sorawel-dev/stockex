# 📊 Module de Gestion d'Inventaire - Odoo 18

## 🎯 Description

Module complet de gestion d'inventaire pour Odoo 18 avec **import Excel/CSV**, **collecte mobile Kobo**, **dashboard interactif** et **analyses avancées**. 

Gérez vos inventaires de A à Z avec traçabilité complète, calcul automatique des écarts et valorisation en FCFA.

## 🆕 Version 18.0.3.0.0 - Gestion Comptable Intégrée !

### 💰 3 Nouvelles Fonctionnalités Comptables

1. 📚 **Génération Automatique d'Écritures Comptables** - Plus de saisie manuelle !
2. 🆕 **Assistant de Stock Initial** - Pour bases de données vides
3. ⚙️ **Configuration Guidée des Catégories** - Avec aide contextuelle

**👉 Voir [GESTION_COMPTABLE.md](GESTION_COMPTABLE.md) pour le guide complet**

## 🆕 Version 18.0.2.0.0 - Nouvelles Fonctionnalités !

### ✨ 10 Améliorations Majeures

1. 📱 **Scan de Codes-Barres Mobile** - Saisie 5x plus rapide
2. 📷 **Pièces Jointes Photo** - Documentation visuelle (3 photos/ligne)
3. ✅ **Workflow d'Approbation Multi-niveaux** - Contrôle qualité renforcé
4. 📊 **Comparaison d'Inventaires** - Analyse d'évolution entre périodes
5. 🔄 **Comptage Cyclique Automatisé** - Planning intelligent
6. 🏷️ **Génération Codes-Barres Emplacements** - Traçabilité physique
7. ⏰ **Actions Planifiées (Crons)** - Automatisation complète
8. 📈 **Rapports de Variance Avancés** - Analytics détaillés
9. 🧪 **Tests Unitaires Complets** - Qualité garantie (10 tests)
10. 🌐 **Support i18n Amélioré** - Traductions FR/EN

**👉 Voir [NOUVELLES_FONCTIONNALITES.md](NOUVELLES_FONCTIONNALITES.md) pour les détails complets**

**🚀 Démarrage rapide : [QUICK_START.md](QUICK_START.md)**

## ✨ Fonctionnalités Principales

### 📊 Dashboard Interactif
- **Vue d'Ensemble** : Page d'accueil avec KPIs temps réel
  - 📋 Nombre d'inventaires validés
  - 📦 Total produits inventoriés  
  - 📊 Quantité totale en stock
  - 💰 Valeur globale en FCFA
- **Analyse des Écarts** : Visualisation des différences
  - Écarts totaux (positifs + négatifs)
  - Surplus identifiés (écarts positifs)
  - Manquants détectés (écarts négatifs)
- **Top 5** : Classements dynamiques
  - Top 5 Catégories par valeur
  - Top 5 Entrepôts par valeur
- **Dernier Inventaire** : Résumé du dernier inventaire validé

### 📥 Import Multi-Format
- **Import Excel** (.xlsx)
  - Mapping automatique des colonnes
  - Création auto entrepôts/produits
  - Validation et rapport d'erreurs
- **Import CSV** (.csv)
  - Support séparateurs multiples
  - Import en masse rapide
- **Import Kobo Collect**
  - Collecte terrain sur mobile/tablette
  - Synchronisation API automatique
  - Géolocalisation des données

### 📋 Gestion des Inventaires
- **Workflow complet** : Brouillon → En cours → Validé
- **Calcul automatique**
  - Quantités théoriques vs réelles
  - Écarts en quantité et valeur
  - Valorisation en FCFA
- **Traçabilité complète**
  - Chatter intégré
  - Suivi des modifications
  - Historique des validations

### 📈 Rapports et Analyses
- **Analyses personnalisées**
  - Vue Graphique (évolution temporelle)
  - Vue Pivot (tableau croisé dynamique)
  - Vue Liste (export Excel)
- **Rapports Stock Odoo**
  - Stock par emplacement
  - Mouvements de stock
  - Analyse produits

### 🗺️ Géolocalisation
- **Entrepôts géolocalisés**
  - Coordonnées GPS (Latitude/Longitude)
  - Lien Google Maps intégré
  - Adresse complète et contact
- **Emplacements hiérarchiques**
  - Arborescence multi-niveaux
  - Noms complets descriptifs
  - Code-barres optionnel

## 🔧 Installation

### Prérequis
- **Odoo 18.0 ou 19.0** (✅ **Compatible avec les deux versions**)
- Python 3.10+
- Bibliothèque openpyxl (pour import Excel)
- Bibliothèque python-barcode (pour génération codes-barres)

**👉 Voir [COMPATIBILITE_ODOO_18_19.md](COMPATIBILITE_ODOO_18_19.md) pour les détails de compatibilité**

### Étapes

```bash
# 1. Copier le module
cp -r stockex /path/to/odoo/addons/

# 2. Mettre à jour Odoo
odoo -d your_database -u stockex

# Ou via l'interface
# Apps → Mettre à jour la liste → Rechercher "Stockinv" → Installer
```

## 🔧 Dépendances

### Modules Odoo
- `base` - Module de base Odoo
- `mail` - Messagerie et activités
- `stock` - Gestion des stocks
- `product` - Gestion des produits

### Bibliothèques Python
- `openpyxl` - Lecture/écriture fichiers Excel

## 🚀 Démarrage Rapide

### 1. Accéder au Module

```
Menu Principal → 📊 Gestion d'Inventaire
→ Vue d'Ensemble s'ouvre automatiquement
```

### 2. Créer Votre Premier Inventaire

#### Option A : Import Excel (Recommandé)

```
1. Préparer votre fichier Excel avec colonnes :
   - CODE ENTREPOT / ENTREPOT
   - CODE ART / CODE ARTICLE  
   - DESIGN / DESIGNATION
   - QTE / QUANTITE

2. Import → Nouvel Inventaire → Import Excel
3. Charger le fichier
4. Vérifier l'import
5. Valider l'inventaire
```

#### Option B : Saisie Manuelle

```
1. Opérations → Inventaires de Stock → Créer
2. Remplir : Date, Responsable
3. Ajouter lignes : Produit, Emplacement, Qté réelle
4. Démarrer l'inventaire
5. Valider
```

### 3. Consulter le Dashboard

```
Vue d'Ensemble
→ Voir KPIs, Écarts, Top 5
→ Actions rapides disponibles
```

### 4. Analyser

```
Rapports → Analyse Détaillée
→ Graphiques, Pivot, Export Excel
```

## 📖 Documentation

### Guides Utilisateur

- **[Guide Utilisateur](docs/GUIDE_UTILISATEUR.md)** - Guide complet avec illustrations
- **[Guide Acquisition Données](docs/GUIDE_ACQUISITION_DONNEES.md)** - Import et Kobo Collect  
- **[Rapports Stock Odoo](docs/RAPPORTS_STOCK_ODOO.md)** - Analyses avancées
- **[Affichage Emplacements](docs/AFFICHAGE_EMPLACEMENTS.md)** - Configuration emplacements
- **[Page d'Accueil](docs/PAGE_ACCUEIL.md)** - Dashboard et KPIs

## Structure technique

### Modèles

#### stockex.stock.inventory
Modèle principal pour les inventaires de stock
- Hérite de : mail.thread, mail.activity.mixin
- Champs principaux : name, date, state, location_id, company_id, user_id, line_ids

#### stockex.stock.inventory.line
Lignes détaillées d'inventaire
- Champs principaux : product_id, theoretical_qty, product_qty, difference, location_id

### Vues

- **Tree View** : Liste des inventaires
- **Form View** : Formulaire détaillé avec header, sheet et chatter
- **Search View** : Recherche avec filtres et groupements

### Sécurité

Droits d'accès configurés pour :
- stockex.stock.inventory
- stockex.stock.inventory.line

## 🏗️ Architecture Technique

### Modèles Principaux

```python
stockex.stock.inventory          # Inventaires
stockex.stock.inventory.line     # Lignes d'inventaire  
stockex.inventory.summary        # Dashboard KPIs
stockex.kobo.config             # Configuration Kobo
stock.location                   # Emplacements (hérité)
stock.warehouse                  # Entrepôts (hérité)
```

### Wizards d'Import

```python
stockex.import.method.wizard     # Choix méthode
stockex.import.inventory.wizard  # Import CSV
stockex.import.excel.wizard     # Import Excel
stockex.import.kobo.wizard      # Import Kobo
stockex.fix.locations.wizard    # Correction emplacements
```

### Vues

- **Dashboard** : Vue d'ensemble avec cartes KPIs
- **Tree/Form** : Liste et détail inventaires
- **Pivot/Graph** : Analyses multi-dimensionnelles
- **Kanban** : Vue mosaïque (dashboard)

### Standards Odoo 18

✅ **Balise `<list>` au lieu de `<tree>`**
✅ **Attributs directs** (pas de `attrs`)
✅ **Champs computed** avec `@api.depends`
✅ **mail.thread et mail.activity.mixin**
✅ **Tracking sur champs importants**
✅ **Widgets modernes** (badge, many2one_avatar_user)

## 🎨 Captures d'Écran (Illustrations Textuelles)

Voir le [Guide Utilisateur](docs/GUIDE_UTILISATEUR.md) pour des illustrations détaillées de :
- Dashboard avec KPIs
- Import Excel étape par étape
- Détail d'un inventaire
- Rapports et analyses

## 🤝 Support

### Contact
- **Développeur** : Sorawel
- **Site Web** : [www.sorawel.com](https://www.sorawel.com)
- **Email** : contact@sorawel.com

### Contributions

Les contributions sont bienvenues ! 

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit (`git commit -m 'Ajout fonctionnalité'`)
4. Push (`git push origin feature/amelioration`)
5. Créer une Pull Request

## 📄 Licence

**LGPL-3** - Voir fichier [LICENSE](LICENSE) pour détails

## 👤 Auteur

**Sorawel**  
Développement et solutions Odoo

## 📌 Version

**18.0.1.0.0** - Octobre 2025

### Changelog

#### v18.0.1.0.0 (2025-10-20)
- ✨ Dashboard interactif avec KPIs
- ✨ Import Excel/CSV/Kobo
- ✨ Analyse des écarts
- ✨ Géolocalisation entrepôts
- ✨ Rapports Stock Odoo intégrés
- ✨ Affichage emplacements hiérarchiques
- ✨ Valorisation FCFA
- 📖 Documentation complète

---

**⭐ Si vous aimez ce module, n'hésitez pas à le partager !**
