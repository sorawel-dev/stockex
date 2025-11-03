# 📦 Guide : Initialisation du Stock

## 🎯 Objectif

Ce guide explique comment **initialiser votre stock** dans Stockex lorsque vous démarrez avec une base de données vide.

---

## 📁 Fichier Template

**Fichier fourni** : [`template_stock_initial.xlsx`](template_stock_initial.xlsx)

Ce fichier Excel contient :
- ✅ En-têtes formatés
- ✅ 5 exemples de produits
- ✅ 100 lignes vides prêtes à remplir
- ✅ Instructions intégrées

---

## 📋 Structure du Fichier

### Colonnes requises

| # | Colonne | Description | Exemple | Obligatoire |
|---|---------|-------------|---------|-------------|
| 1 | **CODE PRODUIT** | Code unique du produit | ASP001 | ✅ Oui |
| 2 | **NOM PRODUIT** | Nom descriptif | Aspirine 500mg | ✅ Oui |
| 3 | **CATEGORIE** | Catégorie du produit | Médicaments | ⚠️ Recommandé |
| 4 | **CODE CATEGORIE** | Code de la catégorie | MED001 | ❌ Optionnel |
| 5 | **EMPLACEMENT** | Nom de l'emplacement | Stock Principal | ✅ Oui |
| 6 | **QUANTITE** | Quantité initiale | 1000 | ✅ Oui |
| 7 | **PRIX UNITAIRE** | Coût unitaire (FCFA) | 500 | ✅ Oui |

**🔑 Note sur les catégories** :
- Si **CATEGORIE** n'existe pas, elle sera créée automatiquement (si l'option est activée)
- **CODE CATEGORIE** permet d'attribuer un code à la catégorie (utile pour la comptabilité)

---

## 🚀 Procédure d'Import

### **Étape 1 : Préparer le fichier**

1. Ouvre `template_stock_initial.xlsx`
2. Supprime les exemples (lignes 10-14) si nécessaire
3. Remplis tes données à partir de la ligne 17
4. Sauvegarde le fichier

**Exemple de données** :

```
CODE PRODUIT | NOM PRODUIT          | CATEGORIE          | CODE CATEGORIE | EMPLACEMENT      | QUANTITE | PRIX UNITAIRE
-------------|----------------------|-------------------|----------------|------------------|----------|---------------
ASP001       | Aspirine 500mg       | Médicaments       | MED001         | Stock Principal  | 1000     | 500
PAR001       | Paracétamol 1g       | Médicaments       | MED001         | Stock Principal  | 850      | 450
AMX001       | Amoxicilline 500mg   | Antibiotiques     | ATB001         | Stock Principal  | 500      | 1200
```

---

### **Étape 2 : Accéder au menu**

Dans Odoo :

```
Gestion d'Inventaire → Import → 📦 Stock Initial
```

---

### **Étape 3 : Configurer l'import**

Remplis le formulaire :

1. **Nom de l'Inventaire Initial** : `Stock Initial [DATE]`
2. **Date du Stock Initial** : Date de démarrage (ex: 01/01/2025)
3. **Emplacement Principal** : Sélectionne ton emplacement principal
4. **Fichier d'Import** : Choisis `template_stock_initial.xlsx`

**Options recommandées** :

- ✅ **Créer les Produits Manquants** : Activé
  - Les produits inexistants seront créés automatiquement
- ✅ **Créer les Catégories Manquantes** : Activé
  - Les catégories non trouvées seront créées avec leur code

---

### **Étape 4 : Lancer l'import**

1. Clique sur **"Créer Stock Initial"**
2. ⏳ Attends la fin de l'import
3. ✅ Un inventaire est créé automatiquement

---

### **Étape 5 : Vérifier**

1. Va dans : `Gestion d'Inventaire → Opérations → Inventaires de Stock`
2. Ouvre l'inventaire créé
3. Vérifie que toutes les lignes sont présentes
4. Vérifie les quantités et prix

---

### **Étape 6 : Valider**

1. Dans l'inventaire, clique sur **"Valider"**
2. ✅ Le stock Odoo est maintenant initialisé !
3. Les quantités sont mises à jour dans `stock.quant`

---

## 🔍 Vérification du Stock

### **Option 1 : Via Dashboard**

```
Gestion d'Inventaire → Vue d'Ensemble
```

Tu verras :
- 📊 Nombre total de produits
- 💰 Valeur totale du stock
- 📦 Emplacements couverts

---

### **Option 2 : Via Stock Odoo**

```
Inventaire (Odoo) → Rapports → Stock par Emplacement
```

Tous tes produits doivent apparaître avec les bonnes quantités.

---

## ⚠️ Points d'Attention

### **1. CODE PRODUIT unique**

❌ **Erreur** : Deux produits avec le même code
```
ASP001 | Aspirine 500mg
ASP001 | Aspirine 1000mg  ← ERREUR
```

✅ **Correct** : Codes uniques
```
ASP001 | Aspirine 500mg
ASP002 | Aspirine 1000mg  ← OK
```

---

### **2. Format des nombres**

❌ **Erreur** : Texte au lieu de nombre
```
QUANTITE: "mille"  ← ERREUR
PRIX: "500 FCFA"   ← ERREUR
```

✅ **Correct** : Nombres uniquement
```
QUANTITE: 1000  ← OK
PRIX: 500       ← OK
```

---

### **3. Emplacements**

Si l'option "Créer les emplacements manquants" est **désactivée** :
- Les emplacements doivent exister dans Odoo
- Utilise exactement le même nom

Si **activée** :
- Les emplacements sont créés automatiquement
- Type : "Emplacement interne"

---

## 📊 Exemple Complet

**Fichier `template_stock_initial.xlsx`** :

| CODE PRODUIT | NOM PRODUIT | CATEGORIE | CODE CATEGORIE | EMPLACEMENT | QUANTITE | PRIX UNITAIRE |
|--------------|-------------|-----------|----------------|-------------|----------|---------------|
| MED001 | Paracétamol 500mg | Médicaments | MED | Pharmacie Centrale | 5000 | 50 |
| MED002 | Aspirine 100mg | Médicaments | MED | Pharmacie Centrale | 3000 | 75 |
| MED003 | Amoxicilline 500mg | Antibiotiques | ATB | Pharmacie Centrale | 1200 | 250 |
| MED004 | Doliprane 1000mg | Médicaments | MED | Pharmacie Nord | 2500 | 120 |
| VIT001 | Vitamine C 1000mg | Vitamines | VIT | Dépôt Vitamines | 8000 | 45 |

**Résultat après import et validation** :

```
✅ 5 produits créés
✅ 3 emplacements créés (Pharmacie Centrale, Pharmacie Nord, Dépôt Vitamines)
✅ 3 catégories créées (Médicaments, Antibiotiques, Vitamines)
✅ Stock Odoo mis à jour :
   - Pharmacie Centrale : 9200 unités
   - Pharmacie Nord : 2500 unités
   - Dépôt Vitamines : 8000 unités
💰 Valeur totale : 1 495 000 FCFA
```

---

## 🆘 Résolution de Problèmes

### **Problème 1 : "Produit [CODE] non trouvé"**

**Cause** : Option "Créer les produits manquants" désactivée

**Solution** :
1. Active l'option dans le formulaire
2. OU crée les produits manuellement d'abord

---

### **Problème 2 : "Emplacement [NOM] non trouvé"**

**Cause** : Emplacement inexistant

**Solution** :
1. Crée l'emplacement dans : `Inventaire → Configuration → Emplacements`
2. OU active "Créer les emplacements manquants"

---

### **Problème 3 : Erreur de format Excel**

**Cause** : Fichier corrompu ou mauvais format

**Solution** :
1. Utilise le template fourni
2. Sauvegarde en `.xlsx` (pas `.xls` ou `.csv`)
3. Vérifie que les en-têtes sont en ligne 9

---

## 🎓 Bonnes Pratiques

### ✅ **DO (À faire)**

1. **Utilise le template fourni**
2. **Garde une copie de ton fichier** avant import
3. **Vérifie les données** avant validation
4. **Utilise des codes produits cohérents** (ex: MED001, MED002...)
5. **Regroupe par catégorie** pour faciliter la gestion

### ❌ **DON'T (À éviter)**

1. ❌ Ne modifie pas les en-têtes du template
2. ❌ N'utilise pas de codes avec caractères spéciaux
3. ❌ Ne mélange pas les formats de nombres
4. ❌ Ne valide pas l'inventaire avant vérification
5. ❌ N'importe pas le même fichier deux fois

---

## 📞 Support

**Besoin d'aide ?**

1. Consulte la documentation : `README.md`
2. Vérifie les logs : `Gestion d'Inventaire → Configuration → Paramètres`
3. Contacte le support : dev@sorawel.com

---

## 📚 Ressources

- [`template_stock_initial.xlsx`](template_stock_initial.xlsx) - Template Excel
- [`wizards/initial_stock_wizard.py`](wizards/initial_stock_wizard.py) - Code source
- [`README.md`](README.md) - Documentation générale

---

**Créé avec ❤️ par Sorawel - www.sorawel.com**
