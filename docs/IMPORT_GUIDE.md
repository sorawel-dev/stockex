# 📋 Guide d'Import Excel - Module Stockex

## 🎯 Création Automatique des Données

L'import Excel crée automatiquement **TOUTES** les données nécessaires :

### ✅ 1. Catégories de Produits
- **Colonnes utilisées** : `CODE CATEGORIE`, `CATEGORIE`
- **Création automatique** : Si la catégorie n'existe pas
- **Exemples** :
  - Code: `FOURNITURES` → Nom: `Fournitures générales et consommables`
  - Code: `AUTRES` → Nom: `Autres matériels`

### ✅ 2. Entrepôts (stock.warehouse)
- **Colonnes utilisées** : `CODE ENTREPOT`, `ENTREPOT`
- **Hiérarchie** : `CODE ENTREPOT PARENT`, `ENTREPOT PARENT`
- **Géolocalisation** : `LATITUDE`, `LONGITUDE`, `VILLE`, `ADRESSE`
- **Création automatique** : Entrepôts et leurs parents
- **Exemples** :
  - Parent: `3010 - Distribution Central Warehouse`
  - Enfant: `002 - Koumassi Wse` (parent: 3010)
  - Enfant: `001 - Bassa Wse` (parent: 3010)

### ✅ 3. Produits (product.product)
- **Colonnes utilisées** : `CODE PRODUIT`, `PRODUIT`, `UDM`
- **Prix** : `COUT UNITAIRE`
- **Catégorie** : Assignée automatiquement
- **Création automatique** : Avec tous les attributs
- **Exemples** :
  - Code: `102000065` → Nom: `SODER WOOD GLUE` → UdM: `PC` → Prix: `2.60`

### ✅ 4. Unités de Mesure (UdM)
- **Reconnaissance automatique** : PC, KG, L, M, etc.
- **Fallback** : Si non trouvée, utilise "Unité(s)"

### ✅ 5. Lignes d'Inventaire
- **Quantités** : Format anglais supporté (`6,308,788` = 6308788)
- **Prix unitaires** : Format anglais supporté (`2.600` = 2.6)
- **Emplacement** : Pointe vers `lot_stock_id` de l'entrepôt

---

## 📊 Structure du Fichier Excel Requis

### Colonnes Obligatoires :
1. **CODE PRODUIT** - Code du produit
2. **PRODUIT** - Nom du produit
3. **CODE ENTREPOT** - Code de l'entrepôt
4. **ENTREPOT** - Nom de l'entrepôt
5. **QUANTITE** - Quantité en stock
6. **COUT UNITAIRE** - Prix unitaire

### Colonnes Optionnelles :
7. **CODE CATEGORIE** - Code de la catégorie
8. **CATEGORIE** - Nom de la catégorie
9. **CODE ENTREPOT PARENT** - Code de l'entrepôt parent
10. **ENTREPOT PARENT** - Nom de l'entrepôt parent
11. **UDM** - Unité de mesure (PC, KG, etc.)
12. **LATITUDE** - Coordonnée GPS
13. **LONGITUDE** - Coordonnée GPS
14. **VILLE** - Ville de l'entrepôt
15. **ADRESSE** - Adresse complète
16. **TELEPHONE** - Téléphone
17. **EMAIL** - Email de contact

---

## 🚀 Procédure d'Import

### Étape 1 : Préparer le Fichier
✅ Vérifier que toutes les colonnes obligatoires sont présentes  
✅ Les codes produits doivent être uniques  
✅ Format des nombres : virgule = milliers, point = décimales

### Étape 2 : Lancer l'Import
1. **Menu** : `Import → Import Excel`
2. **Nom** : Donner un nom à votre inventaire
3. **Date** : Sélectionner la date
4. **Fichier** : Charger votre fichier Excel
5. **Options** :
   - ☑️ **Créer les produits manquants**
   - ☑️ **Créer les emplacements manquants**
   - ☑️ **Mettre à jour les prix produits**
   - ☑️ **Importer la géolocalisation** (si colonnes GPS présentes)

### Étape 3 : Vérifier
- Aperçu du nombre de lignes
- Validation automatique des données
- Cliquer sur **"Importer"**

### Étape 4 : Valider
- L'inventaire s'ouvre automatiquement
- Vérifier les lignes
- Cliquer sur **"Valider"**
- Les stocks Odoo sont mis à jour automatiquement !

---

## 📈 Exemple de Résultat

### Fichier `inventaire_analyse_complete.xlsx` :
- **2,277 produits** importés
- **3 catégories** créées automatiquement
- **10+ entrepôts** créés avec hiérarchie
- **6,308,788 unités** en stock
- **392,107.91** de valeur totale

### Données créées automatiquement :
```
📦 Catégories de Produits :
  ├── FOURNITURES - Fournitures générales et consommables
  ├── AUTRES - Autres matériels
  └── ...

🏢 Entrepôts (Hiérarchie) :
  ├── 3010 - Distribution Central Warehouse (Parent)
  │   ├── 001 - Bassa Wse
  │   ├── 002 - Koumassi Wse
  │   └── ...
  └── ...

📦 Produits :
  ├── 102000065 - SODER WOOD GLUE (PC) - 2.60
  ├── ...
  └── Total : 2,277 produits

📊 Inventaire :
  └── 2,277 lignes avec quantités et prix
```

---

## ✅ Checklist de Validation

Après l'import, vérifier :

- [ ] **Catégories** : `Configuration → Produits → Catégories`
- [ ] **Entrepôts** : `Configuration → Entrepôts`
- [ ] **Produits** : `Configuration → Produits`
- [ ] **Inventaire** : `Inventaires → Inventaires`
- [ ] **Stocks** : `Inventaire → Rapports → Quantités en Stock`

---

## 💡 Conseils

1. **Test** : Commencer avec un petit fichier de test (10-20 lignes)
2. **Backup** : Faire une sauvegarde de la base avant un gros import
3. **Logs** : Consulter les logs Odoo en cas d'erreur
4. **Performance** : Commit automatique tous les 500 enregistrements

---

## 🐛 Dépannage

### Problème : Quantités = 0
**Solution** : Vérifier le format des nombres dans Excel (virgule = milliers)

### Problème : Erreur de création d'entrepôt
**Solution** : Le code entrepôt doit faire max 5 caractères

### Problème : Produits sans catégorie
**Solution** : Vérifier les colonnes CODE CATEGORIE et CATEGORIE

---

## 📞 Support

Pour toute question, consulter les logs Odoo :
```bash
tail -f /var/log/odoo/odoo-server.log | grep "stockex"
```
