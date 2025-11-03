# 📝 Changements : Gestion des Catégories de Produits

## 🎯 Objectif

Permettre la création automatique des catégories de produits lors de l'import du stock initial, avec possibilité de renseigner des codes de catégories.

---

## ✅ Modifications Effectuées

### 1. **Wizard Stock Initial** (`wizards/initial_stock_wizard.py`)

#### Nouveau champ ajouté :
```python
create_categories = fields.Boolean(
    string='Créer les Catégories Manquantes',
    default=True,
    help='Si coché, crée automatiquement les catégories de produits non trouvées'
)
```

#### Nouvelle méthode :
```python
def _get_or_create_category(self, category_name, category_code=None):
    """Recherche ou crée une catégorie de produit."""
```

**Fonctionnalités** :
- ✅ Recherche la catégorie par nom
- ✅ Crée la catégorie si elle n'existe pas (si option activée)
- ✅ Attribue un code de catégorie si fourni
- ✅ Log les catégories créées

#### Méthode `_create_inventory_lines()` modifiée :
- ✅ Gère les colonnes **CATEGORIE** et **CODE CATEGORIE**
- ✅ Crée automatiquement les catégories manquantes
- ✅ Associe les produits à leur catégorie
- ✅ Affiche un récapitulatif des catégories créées

---

### 2. **Vue du Wizard** (`wizards/initial_stock_wizard_views.xml`)

#### Nouveau champ dans le formulaire :
```xml
<field name="create_categories"/>
```

#### Instructions mises à jour :
```
Colonnes requises : CODE PRODUIT, NOM PRODUIT, QUANTITE, PRIX UNITAIRE
Colonnes optionnelles : CATEGORIE, CODE CATEGORIE, EMPLACEMENT
```

---

### 3. **Template Excel** (`tools/create_template.py`)

#### Nouvelle colonne ajoutée :
```python
headers = ['CODE PRODUIT', 'NOM PRODUIT', 'CATEGORIE', 'CODE CATEGORIE', 'EMPLACEMENT', 'QUANTITE', 'PRIX UNITAIRE']
```

#### Exemples mis à jour :
```python
['ASP001', 'Aspirine 500mg', 'Médicaments', 'MED001', 'Stock Principal', 1000, 500]
['PAR001', 'Paracétamol 1g', 'Médicaments', 'MED001', 'Stock Principal', 850, 450]
['AMX001', 'Amoxicilline 500mg', 'Antibiotiques', 'ATB001', 'Stock Principal', 500, 1200]
```

**Résultat** : Fichier Excel avec **7 colonnes** au lieu de 6

---

### 4. **Guide Utilisateur** (`GUIDE_STOCK_INITIAL.md`)

#### Nouvelle colonne documentée :
| # | Colonne | Description | Exemple | Obligatoire |
|---|---------|-------------|---------|-------------|
| 4 | **CODE CATEGORIE** | Code de la catégorie | MED001 | ❌ Optionnel |

#### Note ajoutée :
> 🔑 **Note sur les catégories** :
> - Si **CATEGORIE** n'existe pas, elle sera créée automatiquement (si l'option est activée)
> - **CODE CATEGORIE** permet d'attribuer un code à la catégorie (utile pour la comptabilité)

---

## 📊 Exemple d'Utilisation

### **Avant** (sans catégories) :

| CODE PRODUIT | NOM PRODUIT | QUANTITE | PRIX UNITAIRE |
|--------------|-------------|----------|---------------|
| ASP001 | Aspirine 500mg | 1000 | 500 |

❌ Catégorie = "All" (catégorie par défaut)

---

### **Après** (avec catégories) :

| CODE PRODUIT | NOM PRODUIT | CATEGORIE | CODE CATEGORIE | QUANTITE | PRIX UNITAIRE |
|--------------|-------------|-----------|----------------|----------|---------------|
| ASP001 | Aspirine 500mg | Médicaments | MED001 | 1000 | 500 |

✅ Catégorie créée automatiquement : "Médicaments" (Code: MED001)

---

## 🎬 Workflow Complet

1. **Préparer Excel** avec colonnes CATEGORIE et CODE CATEGORIE
2. **Import via wizard** → Options activées :
   - ✅ Créer les Produits Manquants
   - ✅ Créer les Catégories Manquantes
3. **Résultat** :
   ```
   ✅ 50 ligne(s) créée(s)
   📁 5 catégorie(s) créée(s): Médicaments, Antibiotiques, Vitamines, Anti-inflammatoires, Consommables
   ```

---

## 🔍 Vérification

### Via l'interface Odoo :

```
Inventaire → Configuration → Catégories de Produits
```

Toutes les catégories créées doivent apparaître avec :
- ✅ Nom de la catégorie
- ✅ Code dans le nom complet : `[MED001] Médicaments`

---

## 🚀 Prochaines Étapes

1. **Redémarrer Odoo** ou **mettre à jour le module** via :
   ```
   Odoo → Applications → StockInv → Mettre à niveau
   ```

2. **Tester l'import** :
   - Ouvrir : `Gestion d'Inventaire → Import → 📦 Stock Initial`
   - Vérifier que la checkbox "Créer les Catégories Manquantes" est présente
   - Importer un fichier avec catégories

3. **Vérifier le résultat** :
   - Les catégories doivent être créées automatiquement
   - Les produits doivent être associés à leur catégorie
   - Le message de succès doit afficher le nombre de catégories créées

---

## 📦 Fichiers Modifiés

1. ✅ `wizards/initial_stock_wizard.py` - Logique de création des catégories
2. ✅ `wizards/initial_stock_wizard_views.xml` - Interface utilisateur
3. ✅ `tools/create_template.py` - Template Excel avec nouvelle colonne
4. ✅ `GUIDE_STOCK_INITIAL.md` - Documentation mise à jour
5. ✅ `template_stock_initial.xlsx` - Nouveau template généré

---

## 🎯 Bénéfices

- ✅ **Gain de temps** : Plus besoin de créer manuellement les catégories
- ✅ **Organisation** : Produits automatiquement classés
- ✅ **Traçabilité** : Codes de catégories pour la comptabilité
- ✅ **Simplicité** : Tout se fait en une seule opération

---

**Date** : 2025-10-28  
**Version** : 1.0  
**Module** : StockInv (stockex)
