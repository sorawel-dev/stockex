# 📦 Fichier Stock Initial - Guide d'Utilisation

## ✅ Conversion Réussie

Le fichier [`stock_initial.xlsx`](stock_initial.xlsx) a été converti au format attendu par le module StockInv.

---

## 📁 Fichiers Disponibles

| Fichier | Description | Lignes |
|---------|-------------|--------|
| **stock_initial.xlsx** | Fichier original | 3048 lignes |
| **stock_initial_converti.xlsx** | Fichier adapté au template StockInv | 3047 produits |

---

## 📋 Structure du Fichier Converti

Le fichier `stock_initial_converti.xlsx` contient **7 colonnes** au format StockInv :

| # | Colonne | Contenu | Statut |
|---|---------|---------|--------|
| 1 | **CODE PRODUIT** | Code unique du produit | ✅ Rempli |
| 2 | **NOM PRODUIT** | Nom descriptif | ✅ Rempli |
| 3 | **CATEGORIE** | Catégorie du produit | ✅ Rempli |
| 4 | **CODE CATEGORIE** | Code de la catégorie | ✅ Rempli |
| 5 | **EMPLACEMENT** | "Stock Principal" par défaut | ✅ Rempli |
| 6 | **QUANTITE** | Quantité en stock | ⚠️ **À REMPLIR** (fond jaune) |
| 7 | **PRIX UNITAIRE** | Prix unitaire | ⚠️ **À REMPLIR** (fond jaune) |

---

## ⚠️ IMPORTANT : Colonnes à Remplir

Les colonnes **QUANTITE** et **PRIX UNITAIRE** sont à **0** avec un fond jaune.

**Vous DEVEZ les remplir** avant d'importer le fichier !

### **Exemple** :

```
CODE PRODUIT | NOM PRODUIT           | CATEGORIE      | CODE CAT    | EMPLACEMENT     | QUANTITE | PRIX
102000065    | SODER WOOD GLUE       | Fournitures... | FOURNITURES | Stock Principal | 150      | 2500
102000071    | SOUPLISSO SHEATH 6M/M | Fournitures... | FOURNITURES | Stock Principal | 200      | 1800
```

---

## 🚀 Procédure d'Import

### **Étape 1 : Remplir les Quantités et Prix**

1. **Ouvrez** : `stock_initial_converti.xlsx`

2. **Remplissez** les colonnes **F (QUANTITE)** et **G (PRIX UNITAIRE)** :
   - Quantité = nombre d'unités en stock
   - Prix unitaire = coût unitaire (FCFA ou autre devise)

3. **Sauvegardez** le fichier

---

### **Étape 2 : Mettre à Jour le Module Stockex**

**AVANT** d'importer, vous DEVEZ mettre à jour le module :

1. **Connectez-vous** à Odoo : http://localhost:8069

2. **Mode développeur** :
   - Votre nom → Paramètres → Activer le mode développeur

3. **Applications** :
   - Menu → Applications
   - Recherchez : "**stockex**"

4. **Mettez à niveau** :
   - Cliquez sur **"Mettre à niveau"**
   - Attendez 10-30 secondes

5. **Rafraîchissez** la page (F5)

---

### **Étape 3 : Importer le Fichier**

1. **Accédez au menu** :
   ```
   Gestion d'Inventaire → Import → 📦 Stock Initial
   ```

2. **Remplissez le formulaire** :
   - **Nom** : Stock Initial 2025
   - **Date** : Date de référence (ex: 01/01/2025)
   - **Emplacement** : Stock Principal
   - **Fichier** : Choisissez `stock_initial_converti.xlsx`

3. **Options** :
   - ✅ **Créer les Produits Manquants** (activé)
   - ✅ **Créer les Catégories Manquantes** (activé)

4. **Cliquez** sur **"Créer Stock Initial"**

5. **Attendez** la fin de l'import

---

### **Étape 4 : Vérifier l'Import**

1. **Vérifiez le message** :
   ```
   ✅ 3047 ligne(s) créée(s)
   📁 X catégorie(s) créée(s): ...
   ```

2. **Ouvrez l'inventaire créé** :
   - L'inventaire s'ouvre automatiquement
   - Vérifiez les lignes

3. **Validez l'inventaire** :
   - Cliquez sur **"Valider"**
   - Le stock Odoo est mis à jour

---

### **Étape 5 : Vérifier le Stock**

1. **Dashboard** :
   ```
   Gestion d'Inventaire → Vue d'Ensemble
   ```

2. **Stock par Emplacement** :
   ```
   Gestion d'Inventaire → Rapports → Stock par Emplacement
   ```

3. **Catégories créées** :
   ```
   Inventaire → Configuration → Catégories de Produits
   ```

---

## 📊 Statistiques du Fichier

### **Produits** : 3047

### **Catégories Identifiées** :

Le fichier contient les catégories suivantes (exemples) :
- `FOURNITURES` - Fournitures générales et consommables
- _(autres catégories à identifier lors de l'import)_

**Note** : Toutes les catégories seront créées automatiquement lors de l'import si l'option est activée.

---

## 🔍 Colonnes Converties

### **Mapping Ancien → Nouveau Format** :

| Ancien Format | Nouvelle Position | Nouvelle Colonne |
|---------------|-------------------|------------------|
| N° | _(supprimé)_ | - |
| CODE CATEGORIE (col 2) | Colonne 4 | CODE CATEGORIE |
| CATEGORIE (col 3) | Colonne 3 | CATEGORIE |
| CODE PRODUIT (col 4) | Colonne 1 | CODE PRODUIT |
| PRODUIT (col 5) | Colonne 2 | NOM PRODUIT |
| UDM (col 6) | _(supprimé)_ | - |
| _(nouveau)_ | Colonne 5 | EMPLACEMENT |
| _(nouveau)_ | Colonne 6 | QUANTITE ⚠️ |
| _(nouveau)_ | Colonne 7 | PRIX UNITAIRE ⚠️ |

---

## 💡 Conseils

### **1. Remplissage par Lot**

Si vous avez beaucoup de produits :
- Triez par catégorie
- Remplissez les prix par groupe de produits similaires
- Utilisez des formules Excel pour accélérer

### **2. Validation des Données**

Avant l'import, vérifiez :
- ✅ Aucune quantité négative
- ✅ Aucun prix à 0 (sauf produits gratuits)
- ✅ Tous les codes produits sont uniques

### **3. Import Progressif**

Pour tester :
1. Copiez les 10 premières lignes dans un nouveau fichier
2. Remplissez quantités et prix
3. Importez ce petit fichier de test
4. Si OK, importez le fichier complet

---

## 🆘 Problèmes Courants

### **1. Menu "Stock Initial" invisible**

**Solution** : Mettez à jour le module (voir Étape 2)

**Voir** : [`DEPANNAGE_MENU_STOCK_INITIAL.md`](../DEPANNAGE_MENU_STOCK_INITIAL.md)

---

### **2. Erreur "Quantité invalide"**

**Cause** : Colonnes QUANTITE ou PRIX vides ou négatives

**Solution** : Remplissez toutes les cellules avec des nombres positifs

---

### **3. Erreur "Code produit dupliqué"**

**Cause** : Deux produits ont le même code

**Solution** : Vérifiez les doublons dans la colonne CODE PRODUIT

---

### **4. Import trop lent**

**Cause** : 3047 produits = beaucoup de données

**Solution** :
- Soyez patient (peut prendre 2-5 minutes)
- Ou divisez en plusieurs fichiers de 500-1000 lignes

---

## 📝 Notes

- **Format accepté** : Excel (.xlsx)
- **Taille du fichier** : ~500 Ko
- **Nombre de produits** : 3047
- **Temps d'import estimé** : 2-5 minutes

---

## 🎯 Récapitulatif

1. ✅ **Fichier converti** : `stock_initial_converti.xlsx`
2. ⚠️ **Remplir** : Colonnes QUANTITE et PRIX UNITAIRE
3. ✅ **Mettre à jour** : Module stockex dans Odoo
4. ✅ **Importer** : Via menu "📦 Stock Initial"
5. ✅ **Valider** : L'inventaire créé

---

**Date de conversion** : 2025-10-28  
**Script utilisé** : [`convert_stock_initial.py`](../tools/convert_stock_initial.py)  
**Module** : StockInv (stockex) v18.0.5.0.0
