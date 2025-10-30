# ✅ Corrections Appliquées : Menu Stock Initial

## 🎯 Problème Initial

Le menu **"📦 Stock Initial"** n'apparaissait pas dans l'interface Odoo malgré plusieurs tentatives de correction.

---

## 🔍 Causes Identifiées

### **1. Ordre de Chargement Incorrect**
- ❌ `menus.xml` était chargé **AVANT** `initial_stock_wizard_views.xml`
- ❌ Le menu référençait une action qui n'existait pas encore

### **2. Règle de Sécurité Manquante**
- ❌ Le modèle `stockex.initial.stock.wizard` n'avait **aucune règle d'accès**
- ❌ Même avec le menu visible, les utilisateurs n'auraient pas pu y accéder

### **3. Référence d'Action Ambiguë**
- ❌ L'action était définie dans un fichier, référencée dans un autre
- ❌ Risque de conflit d'External ID

---

## ✅ Solutions Appliquées

### **Solution 1 : Ordre de Chargement Corrigé**

**Fichier** : `__manifest__.py`

**Avant** :
```python
'data': [
    # ...
    'views/menus.xml',  # ← Chargé en PREMIER
    'wizards/initial_stock_wizard_views.xml',  # ← Chargé APRÈS
]
```

**Après** :
```python
'data': [
    # Wizards (définissent les actions)
    'wizards/initial_stock_wizard_views.xml',  # ← Chargé en PREMIER
    # ...
    # Menus (utilisent les actions)
    'views/menus.xml',  # ← Chargé APRÈS
]
```

**Résultat** : L'action est définie **avant** d'être référencée ✅

---

### **Solution 2 : Action Définie Localement**

**Fichier** : `views/menus.xml`

**Ajout** :
```xml
<!-- Action Stock Initial (définie ici pour éviter les problèmes de référence) -->
<record id="action_initial_stock_wizard_menu" model="ir.actions.act_window">
    <field name="name">Stock Initial</field>
    <field name="res_model">stockex.initial.stock.wizard</field>
    <field name="view_mode">form</field>
    <field name="target">new</field>
</record>

<menuitem id="menu_initial_stock_wizard"
          name="📦 Stock Initial"
          parent="menu_stockex_import"
          action="action_initial_stock_wizard_menu"  ← Action locale
          sequence="1"
          groups="base.group_user"/>
```

**Avantage** : L'action et le menu sont dans le même fichier, évitant les problèmes de dépendance ✅

---

### **Solution 3 : Règle de Sécurité Ajoutée**

**Fichier** : `security/ir.model.access.csv`

**Ajout** :
```csv
access_stockex_initial_stock_wizard_user,Access Initial Stock Wizard - User,model_stockex_initial_stock_wizard,stockex.group_stockex_user,1,1,1,1
```

**Résultat** : Les utilisateurs du groupe `stockex_user` ont maintenant accès au wizard ✅

---

## 📋 Modifications Détaillées

### **1. `__manifest__.py` (ligne 65)**
```python
# AVANT
'wizards/import_kobo_wizard_views.xml',
'wizards/fix_locations_wizard_views.xml',
# Vues de base (utilisent les actions wizards)

# APRÈS
'wizards/import_kobo_wizard_views.xml',
'wizards/fix_locations_wizard_views.xml',
'wizards/initial_stock_wizard_views.xml',  # ← AJOUTÉ ICI
# Vues de base (utilisent les actions wizards)
```

Et **supprimé** de la ligne 78 :
```python
# SUPPRIMÉ
'wizards/initial_stock_wizard_views.xml',
```

---

### **2. `views/menus.xml` (lignes 33-52)**
```xml
<!-- AJOUTÉ -->
<!-- Action Stock Initial (définie ici pour éviter les problèmes de référence) -->
<record id="action_initial_stock_wizard_menu" model="ir.actions.act_window">
    <field name="name">Stock Initial</field>
    <field name="res_model">stockex.initial.stock.wizard</field>
    <field name="view_mode">form</field>
    <field name="target">new</field>
</record>

<!-- MODIFIÉ : action="action_initial_stock_wizard" → action="action_initial_stock_wizard_menu" -->
<menuitem id="menu_initial_stock_wizard"
          name="📦 Stock Initial"
          parent="menu_stockex_import"
          action="action_initial_stock_wizard_menu"
          sequence="1"
          groups="base.group_user"/>
```

---

### **3. `security/ir.model.access.csv` (ligne 10)**
```csv
# AJOUTÉ
access_stockex_initial_stock_wizard_user,Access Initial Stock Wizard - User,model_stockex_initial_stock_wizard,stockex.group_stockex_user,1,1,1,1
```

---

## 🚀 Instructions de Mise à Jour

### **IMPORTANT** : Vous DEVEZ mettre à jour le module pour que les changements prennent effet !

### **Méthode 1 : Via l'Interface Odoo (RECOMMANDÉE)**

1. **Connectez-vous** : http://localhost:8069

2. **Mode développeur** :
   - Cliquez sur votre nom → Paramètres → **Activer le mode développeur**

3. **Applications** :
   - Menu principal → **Applications**
   - Supprimez le filtre "Applications"

4. **Recherchez** : "**stockex**" ou "**StockInv**"

5. **Mettez à niveau** :
   - Cliquez sur **"Mettre à niveau"** (icône flèche circulaire)
   - Attendez 10-30 secondes

6. **Rafraîchissez** : Appuyez sur **F5**

7. **Vérifiez** :
   ```
   Gestion d'Inventaire → Import → 📦 Stock Initial
   ```

---

### **Méthode 2 : Script Automatique**

**Exécutez en tant qu'administrateur** :

#### **PowerShell** :
```powershell
c:\apps\stockex\force_update.ps1
```

#### **Batch** :
```cmd
c:\apps\stockex\force_update.bat
```

**Puis** : Méthode 1 (mise à niveau via l'interface)

---

## ✅ Vérification Finale

Après la mise à jour, vous devriez voir :

```
Gestion d'Inventaire
  └─ Import
      ├─ 📦 Stock Initial          ← ICI (séquence 1)
      ├─ 📦 Nouvel Inventaire       (séquence 5)
      ├─ Import CSV (Direct)        (séquence 10)
      └─ Import Excel (Direct)      (séquence 20)
```

### **Test du Menu** :

1. Cliquez sur **"📦 Stock Initial"**

2. Un popup doit s'ouvrir avec :
   - ✅ Champ "Nom de l'Inventaire Initial"
   - ✅ Champ "Date du Stock Initial"
   - ✅ Champ "Emplacement Principal"
   - ✅ Champ "Fichier d'Import (Excel)"
   - ✅ Checkbox "Créer les Produits Manquants"
   - ✅ Checkbox "Créer les Catégories Manquantes" ← NOUVEAU

3. Boutons :
   - ✅ "Créer Stock Initial" (bleu)
   - ✅ "Annuler" (gris)

---

## 📦 Fichiers Modifiés

| Fichier | Modification | Ligne |
|---------|-------------|-------|
| `__manifest__.py` | Ordre de chargement | 65 |
| `views/menus.xml` | Action locale + menu | 33-52 |
| `security/ir.model.access.csv` | Règle d'accès | 10 |
| `wizards/initial_stock_wizard.py` | Gestion catégories | 144-253 |
| `wizards/initial_stock_wizard_views.xml` | Nouveau champ | 18 |
| `tools/create_template.py` | Colonne CODE CATEGORIE | 30, 51-56 |
| `GUIDE_STOCK_INITIAL.md` | Documentation | Toutes |

---

## 📝 Scripts Créés

| Script | Description |
|--------|-------------|
| `force_update.ps1` | Redémarrage service PowerShell |
| `force_update.bat` | Redémarrage service Batch |
| `DEPANNAGE_MENU_STOCK_INITIAL.md` | Guide dépannage complet |
| `CHANGELOG_CATEGORIES.md` | Changements catégories |
| `CORRECTIONS_MENU_STOCK_INITIAL.md` | Ce fichier |

---

## 🆘 Si le Menu N'Apparaît Toujours Pas

1. **Vérifiez** que vous avez bien **mis à niveau le module** (Méthode 1)

2. **Consultez** : `DEPANNAGE_MENU_STOCK_INITIAL.md`

3. **Essayez l'accès direct** :
   ```
   http://localhost:8069/web#action=stockex.action_initial_stock_wizard_menu
   ```

4. **Vérifiez vos droits** : Vous devez être dans le groupe `stockex_user` ou `stockex_manager`

5. **Dernier recours** : Réinstallez le module (voir guide dépannage)

---

**Date** : 2025-10-28  
**Version** : 18.0.5.0.0  
**Module** : StockInv (stockex)

---

## ✨ Bonus : Fonctionnalités du Stock Initial

Une fois le menu accessible, vous pourrez :

- ✅ Importer un fichier Excel avec stock initial
- ✅ Créer automatiquement les produits manquants
- ✅ Créer automatiquement les catégories avec codes
- ✅ Initialiser les quantités en stock
- ✅ Définir les prix unitaires
- ✅ Générer un inventaire Odoo validé

**Template fourni** : `template_stock_initial.xlsx` (7 colonnes)
