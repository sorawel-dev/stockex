# ✅ Stock Initial COMPLET - Prêt à Importer !

## 🎯 Fichier Généré

**Fichier** : [`stock_initial_COMPLET.xlsx`](stock_initial_COMPLET.xlsx)

✅ **TOUTES LES DONNÉES SONT COMPLÈTES**
- Codes produits
- Noms de produits  
- Catégories + codes
- **Emplacements réels**
- **Quantités réelles**
- **Prix unitaires réels**

---

## 📊 Statistiques

| Indicateur | Valeur |
|------------|--------|
| **Total lignes** | 3263 |
| **Produits uniques** | 3047 |
| **Produits avec stock** | 3047 (100%) |
| **Produits multi-emplacements** | 216 |

---

## 📋 Structure du Fichier

| # | Colonne | Exemple | Source |
|---|---------|---------|--------|
| 1 | CODE PRODUIT | 102000065 | stock_initial.xlsx |
| 2 | NOM PRODUIT | SODER WOOD GLUE | stock_initial.xlsx |
| 3 | CATEGORIE | Fournitures générales... | stock_initial.xlsx |
| 4 | CODE CATEGORIE | FOURNITURES | stock_initial.xlsx |
| 5 | EMPLACEMENT | Koumassi Wse | **val_stock_brut.xlsx** ✅ |
| 6 | QUANTITE | 1 | **val_stock_brut.xlsx** ✅ |
| 7 | PRIX UNITAIRE | 2600 | **val_stock_brut.xlsx** ✅ |

---

## 🔄 Fusion des Données

Le fichier a été construit en fusionnant :

### **Source 1** : `stock_initial.xlsx`
- Codes produits
- Noms de produits
- Catégories et codes de catégories

### **Source 2** : `val_stock_brut.xlsx`
- **Quantités en stock par emplacement**
- **Prix unitaires**
- **Noms des emplacements (warehouses)**

---

## ⚠️ IMPORTANT : Multi-Emplacements

**216 produits** sont présents dans **plusieurs emplacements** !

**Exemple** : Si le produit "102000065" est dans 2 entrepôts :
- Ligne 1 : Koumassi Wse, Qté: 1
- Ligne 2 : Abidjan Nord, Qté: 5

Le fichier contient **une ligne par combinaison produit/emplacement**.

---

## 🚀 Import dans Odoo

### **ÉTAPE 1 : Mettre à Jour le Module Stockex**

**OBLIGATOIRE** avant l'import :

1. Connectez-vous : http://localhost:8069
2. Mode développeur → Applications
3. Recherchez "**stockex**"
4. **Mettre à niveau**
5. Attendez 10-30 secondes
6. Rafraîchissez (F5)

---

### **ÉTAPE 2 : Vérifier le Menu**

Après mise à niveau :
```
Gestion d'Inventaire → Import → 📦 Stock Initial
```

Si absent, consultez : [`DEPANNAGE_MENU_STOCK_INITIAL.md`](../DEPANNAGE_MENU_STOCK_INITIAL.md)

---

### **ÉTAPE 3 : Importer le Fichier**

1. **Menu** : `Gestion d'Inventaire → Import → 📦 Stock Initial`

2. **Formulaire** :
   - **Nom** : "Stock Initial Complet 2025"
   - **Date** : Date de référence (ex: aujourd'hui)
   - **Emplacement** : "Stock Principal" (sera écrasé par les emplacements du fichier)
   - **Fichier** : Choisissez `stock_initial_COMPLET.xlsx`

3. **Options** :
   - ✅ **Créer les Produits Manquants** (si produits non créés)
   - ✅ **Créer les Catégories Manquantes** (si catégories non créées)

4. **Import** :
   - Cliquez sur **"Créer Stock Initial"**
   - ⏳ **Attendez 2-5 minutes** (3263 lignes)

---

### **ÉTAPE 4 : Vérifier l'Import**

**Message attendu** :
```
✅ 3263 ligne(s) créée(s)
📁 X catégorie(s) créée(s): FOURNITURES, ...
```

**Vérifications** :

1. **Inventaire créé** :
   - L'inventaire s'ouvre automatiquement
   - Vérifiez quelques lignes

2. **Nombre de lignes** :
   - Doit afficher **3263 lignes**

3. **Emplacements** :
   - Vérifiez que les emplacements sont corrects (Koumassi Wse, etc.)

4. **Quantités et prix** :
   - Vérifiez quelques produits

---

### **ÉTAPE 5 : Valider l'Inventaire**

⚠️ **ATTENTION** : Cette action met à jour le stock Odoo !

1. Dans l'inventaire, cliquez sur **"Valider"**

2. Le système crée les mouvements de stock

3. Les quantités sont ajoutées dans `stock.quant`

---

## 📊 Après Validation

### **Vérifier le Stock**

**Dashboard** :
```
Gestion d'Inventaire → Vue d'Ensemble
```

**Stock par Emplacement** :
```
Gestion d'Inventaire → Rapports → Stock par Emplacement
```

**Catégories créées** :
```
Inventaire → Configuration → Catégories de Produits
```

---

## 💡 Conseils

### **1. Test d'Abord**

Pour tester avant l'import complet :

1. Copiez les **100 premières lignes** dans un nouveau fichier
2. Importez ce fichier de test
3. Vérifiez que tout fonctionne
4. Puis importez le fichier complet

### **2. Import Progressif**

Si le fichier est trop lourd (3263 lignes) :

- Divisez en plusieurs fichiers de 500-1000 lignes
- Importez-les séparément
- Évite les timeouts

### **3. Gestion des Emplacements**

Les emplacements du fichier doivent exister dans Odoo :

**Option A** : Créer manuellement avant l'import
```
Inventaire → Configuration → Emplacements
```

**Option B** : Modifier le wizard pour créer automatiquement les emplacements
(fonctionnalité à ajouter si nécessaire)

---

## 🔍 Données Techniques

### **Emplacements Identifiés**

Le fichier contient ces emplacements (exemples) :
- Koumassi Wse
- Abidjan Nord
- _(autres selon vos données)_

### **Catégories Identifiées**

- FOURNITURES - Fournitures générales et consommables
- _(autres selon vos données)_

---

## 📁 Fichiers Générés

| Fichier | Description | Lignes |
|---------|-------------|--------|
| `stock_initial.xlsx` | Fichier original (produits) | 3047 |
| `val_stock_brut.xlsx` | Fichier original (stocks) | 3263 |
| `stock_initial_COMPLET.xlsx` | **Fichier fusionné prêt** | **3263** ✅ |
| `build_stock_initial_complet.py` | Script de fusion | - |

---

## 🆘 Problèmes Courants

### **1. Menu invisible**

**Solution** : Mettez à jour le module (voir ÉTAPE 1)

### **2. Import trop lent**

**Cause** : 3263 lignes = beaucoup de données

**Solution** : 
- Soyez patient (2-5 minutes)
- Ou divisez en plusieurs fichiers

### **3. Erreur "Emplacement non trouvé"**

**Cause** : L'emplacement du fichier n'existe pas dans Odoo

**Solution** : Créez les emplacements avant l'import
```
Inventaire → Configuration → Emplacements
```

### **4. Produits en double**

**Cause** : Même produit dans plusieurs emplacements

**Ce n'est PAS une erreur** : C'est normal ! Un produit peut être dans plusieurs emplacements.

---

## ✅ Récapitulatif

1. ✅ **Fichier prêt** : `stock_initial_COMPLET.xlsx`
2. ✅ **Toutes les données** : Quantités, prix, emplacements
3. ✅ **3263 lignes** : Incluant multi-emplacements
4. ⚠️ **Mettre à jour module** : Obligatoire avant import
5. ✅ **Importer** : Via menu "📦 Stock Initial"
6. ✅ **Valider** : Pour mettre à jour le stock Odoo

---

**Script utilisé** : [`build_stock_initial_complet.py`](../tools/build_stock_initial_complet.py)

**Date de création** : 2025-10-29

**Module** : StockInv (stockex) v18.0.5.0.0
