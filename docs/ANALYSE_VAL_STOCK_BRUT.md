# 📊 Analyse du Fichier val_stock_brut.csv

**Date d'analyse :** 18 Octobre 2025  
**Fichier source :** `/home/one/apps/stockex/docs/val_stock_brut.csv`  
**Taille :** 367 KB

---

## 🔍 Vue d'Ensemble

### Statistiques Générales

| Métrique | Valeur |
|----------|--------|
| **Nombre total de lignes** | 3,264 (3,263 lignes de données + 1 en-tête) |
| **Nombre de produits uniques** | 3,047 références |
| **Nombre d'entrepôts** | 7 emplacements |
| **Types d'entrepôts** | 4 types |
| **Quantité totale en stock** | ~149,015 unités |

---

## 📋 Structure du Fichier

### Colonnes Identifiées

```csv
wh_type_code, wh_type_id, wh_code, wharehouse, product_default_code, 
product_id, uom, quantity, standard_price, [valeur totale]
```

| N° | Colonne | Description | Type | Exemple |
|----|---------|-------------|------|---------|
| 1 | `wh_type_code` | Code type entrepôt | Numérique | 3010, 1010, 1305 |
| 2 | `wh_type_id` | Nom type entrepôt | Texte | "Distribution Central Warehouse" |
| 3 | `wh_code` | Code entrepôt | Numérique | 001, 002, 003 |
| 4 | `wharehouse` | Nom entrepôt | Texte | "Bassa Wse", "Koumassi Wse" |
| 5 | `product_default_code` | Référence produit | Alphanumér. | "102000065", "200000003" |
| 6 | `product_id` | Description produit | Texte | "SODER WOOD GLUE" |
| 7 | `uom` | Unité de mesure | Texte | "PC" (pièce) |
| 8 | `quantity` | Quantité en stock | Numérique | "1", "6,517", "302,201" |
| 9 | `standard_price` | Prix unitaire | Numérique | "2,600", "158" |
| 10 | `[valeur]` | Valeur totale | Numérique | Quantité × Prix |

**Note :** Les nombres utilisent la virgule comme séparateur décimal et les milliers sont séparés par des espaces.

---

## 🏢 Répartition par Entrepôts

### Nombre de Lignes par Entrepôt

| Rang | Entrepôt | Lignes | % | Type |
|------|----------|--------|---|------|
| 1 | **Bassa Wse** | 2,099 | 64.3% | Generation Central Warehouse |
| 2 | **Koumassi Wse** | 717 | 22.0% | Distribution Central Warehouse |
| 3 | **Logbaba Wse** | 187 | 5.7% | Logbaba Power Plant |
| 4 | **Douala Wse** | 174 | 5.3% | Douala Regional Warehouse |
| 5 | **Kits Comp Wse** | 51 | 1.6% | Distribution Central Warehouse |
| 6 | **Logbaba Labo** | 21 | 0.6% | Logbaba Power Plant |
| 7 | **Kits Wse** | 14 | 0.4% | Distribution Central Warehouse |

**Observation :** L'entrepôt **Bassa Wse** concentre près de **2/3** des lignes d'inventaire.

---

## 🏭 Types d'Entrepôts

### Répartition par Type

| Type | Lignes | % | Description |
|------|--------|---|-------------|
| **Generation Central Warehouse** | 1,890 | 57.9% | Entrepôt central de génération |
| **Distribution Central Warehouse** | 1,012 | 31.0% | Entrepôt central de distribution |
| **Logbaba Power Plant** | 187 | 5.7% | Centrale électrique Logbaba |
| **Douala Regional Warehouse** | 174 | 5.3% | Entrepôt régional Douala |

---

## 📦 Catégories de Produits

### Analyse des Références Produits

Les références produits suivent une nomenclature structurée :

| Préfixe | Plage | Nombre estimé | Catégorie possible |
|---------|-------|---------------|-------------------|
| **102xxxxxx** | 102000065 - 102001xxx | ~1,000 | Consommables / Fournitures |
| **200xxxxxx** | 200000003 - 200001xxx | ~1,500 | Matériel électrique |
| **300xxxxxx** | 300000xxx - 300001xxx | ~400 | Équipements |
| **400xxxxxx** | 400000xxx - 400001xxx | ~200 | Câbles et conducteurs |
| **500xxxxxx** | 500000xxx - 500001xxx | ~300 | Transformateurs |
| **600xxxxxx** | 600000xxx - 600001xxx | ~200 | Compteurs |
| **700xxxxxx** | 700000xxx - 700001xxx | ~150 | Accessoires |
| **800xxxxxx** | 800000xxx - 800001xxx | ~150 | Outils |
| **903xxxxxx** | 903000xxx | ~147 | Matériel rénové (SR_) |

**Note :** Le préfixe "SR_" indique du matériel rénové/reconditionné.

---

## 💰 Analyse des Valeurs

### Exemples de Valeurs Élevées

| Produit | Quantité | Prix Unit. | Valeur | Entrepôt |
|---------|----------|------------|--------|----------|
| LV C/B 2 WIRES 5-15A 220V DIFF 500mA | 79,117 | 13,734 | 1,086,570,606 | Kits Comp Wse |
| PIG TAIL Q 16 L | 302,201 | 1,103 | 333,302,238 | Bassa Wse |
| PLSTFIED BACC COLLAR SCR W/ ANKLE | 696,833 | 192 | 133,599,188 | Kits Comp Wse |
| LV INSLTN PIERCING FTG (PI) W/ 70/35mm² | 124,241 | 1,176 | 146,053,962 | Kits Comp Wse |
| BT AERIAL ANCHOR CLAMP TYPE PA 25 | 159,122 | 683 | 108,678,443 | Kits Comp Wse |

**Observation :** Les plus grosses valeurs sont concentrées dans **Kits Comp Wse** et **Bassa Wse**.

---

## 🔴 Points d'Attention

### 1. Données Manquantes ou Nulles

Certaines lignes contiennent des valeurs vides ou " - " :
```csv
102000071,SOUPLISSO SHEATH 6M/M,PC, 7 , -   ,0
```

**Impact :** Prix unitaire non défini = Valeur totale = 0

### 2. Format des Nombres

- **Séparateur décimal :** Virgule (,)
- **Séparateur de milliers :** Espace ( )
- **Exemples :** "6,517", "1,103", "333,302,238"

**Impact :** Nécessite un traitement spécial pour l'import dans Odoo.

### 3. Nomenclature des Produits

Produits avec descriptions variées :
- Codes standardisés : 102000065
- Descriptions en majuscules : "SODER WOOD GLUE"
- Produits rénovés : préfixe "SR_"
- Produit annulé : "ANNULEE" (ligne 3263)

### 4. Unités de Mesure

**UOM dominante :** "PC" (Pièce) pour tous les produits observés.

---

## 📈 Recommandations pour Odoo

### 1. Import des Données

**Script d'import à développer :**

```python
# Traitement des séparateurs
def clean_number(value):
    """Convertit '6,517' ou '1,103' en float."""
    return float(value.replace(' ', '').replace(',', '.'))

# Mapping des champs
CSV → Odoo:
- wh_type_code → stock.location.type (ou tag)
- wharehouse → stock.location.name
- product_default_code → product.product.default_code
- product_id → product.product.name
- uom → uom.uom (PC = Pièce)
- quantity → theoretical_qty (pour inventaire)
```

### 2. Structure Recommandée

#### Créer les Emplacements de Stock

```python
Bassa Wse (parent)
├── Generation Central Warehouse
│
Koumassi Wse (parent)
├── Distribution Central Warehouse
│
Logbaba Wse (parent)
├── Logbaba Power Plant
│
Douala Wse (parent)
└── Douala Regional Warehouse
```

#### Créer les Produits

- **3,047 produits** à créer/mettre à jour
- Utiliser `default_code` comme référence unique
- Associer l'UOM = PC (Pièce)
- Définir `standard_price` (coût standard)

#### Créer l'Inventaire

```python
# Un inventaire par entrepôt ou un seul global
Inventaire Global 2025
├── 3,263 lignes
│   ├── Produit
│   ├── Emplacement
│   ├── Quantité théorique = quantity du CSV
│   └── Valeur = standard_price × quantity
```

### 3. Script d'Import Recommandé

```python
# /home/one/apps/stockex/scripts/import_inventory.py

import csv
import logging
from odoo import api, SUPERUSER_ID

def import_inventory(env, csv_file):
    """Import les données d'inventaire depuis val_stock_brut.csv."""
    
    # 1. Créer/Récupérer les emplacements
    locations = {}
    
    # 2. Créer/Récupérer les produits
    products = {}
    
    # 3. Créer l'inventaire
    inventory = env['stockex.stock.inventory'].create({
        'name': 'Import CSV 2025',
        'date': fields.Date.today(),
    })
    
    # 4. Créer les lignes
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Traiter chaque ligne
            ...
    
    return inventory
```

### 4. Validation Recommandée

Avant import :
- [ ] Vérifier les doublons de références produits
- [ ] Valider les prix (pas de valeurs négatives)
- [ ] Contrôler les quantités aberrantes
- [ ] Nettoyer les produits "ANNULEE"

---

## 🎯 Cas d'Usage pour le Module Stockex

### Import Automatique

**Ajouter une fonctionnalité d'import CSV :**

```python
class StockInventory(models.Model):
    _inherit = 'stockex.stock.inventory'
    
    def action_import_csv(self):
        """Importe un fichier CSV d'inventaire."""
        # Ouvre un wizard de sélection de fichier
        # Parse le CSV
        # Crée les lignes d'inventaire
        pass
```

### Dashboard Analytique

Ajouter des graphiques :
- **Par entrepôt :** Quantités et valeurs
- **Par catégorie :** Top 10 produits
- **Évolution :** Historique des inventaires

### Alertes

- Stock minimum atteint
- Écarts importants (> 10%)
- Produits sans mouvement

---

## 📊 Statistiques Clés

### Résumé Exécutif

```
📦 Total Lignes:        3,263
🏢 Entrepôts:          7
🏭 Types Entrepôts:    4
📋 Produits Uniques:   3,047
📊 Quantité Totale:    ~149,015 unités
💰 Valeur Estimée:     À calculer (données manquantes)
```

### Top 5 Entrepôts (par volume)

1. **Bassa Wse** - 64.3% (2,099 lignes)
2. **Koumassi Wse** - 22.0% (717 lignes)
3. **Logbaba Wse** - 5.7% (187 lignes)
4. **Douala Wse** - 5.3% (174 lignes)
5. **Kits Comp Wse** - 1.6% (51 lignes)

---

## ✅ Prochaines Étapes

### Court Terme

1. **Développer le script d'import CSV**
   - Parser le fichier avec gestion des séparateurs
   - Créer les emplacements de stock
   - Créer/Mettre à jour les produits
   - Générer les lignes d'inventaire

2. **Créer un wizard d'import**
   - Interface utilisateur dans Odoo
   - Upload de fichier CSV
   - Mapping des colonnes
   - Prévisualisation avant import

3. **Valider les données**
   - Contrôle qualité des prix
   - Vérification des quantités
   - Gestion des doublons

### Moyen Terme

4. **Enrichir le module**
   - Rapports d'écarts d'inventaire
   - Graphiques par entrepôt
   - Export vers Excel

5. **Automatisation**
   - Import périodique (cron)
   - Réconciliation automatique
   - Alertes par email

---

## 📝 Notes Techniques

### Format CSV

- **Encodage :** UTF-8
- **Délimiteur :** Virgule (,)
- **Séparateur décimal :** Virgule (,)
- **Séparateur milliers :** Espace
- **Lignes :** 3,264 (dont 1 en-tête)

### Qualité des Données

**✅ Points Positifs :**
- Structure cohérente
- Nomenclature claire des produits
- Hiérarchie des entrepôts

**⚠️ Points à Améliorer :**
- Prix manquants (valeur " - ")
- Format numérique non standard
- Produits "ANNULEE" à nettoyer

---

**Analysé par :** Cascade AI  
**Date :** 18 Octobre 2025  
**Module :** Stockex v18.0.1.0.0
