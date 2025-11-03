# 🔧 Dépannage : Menu "Stock Initial" Invisible

## 🎯 Problème

Le menu **"📦 Stock Initial"** n'apparaît pas dans :
```
Gestion d'Inventaire → Import → ???
```

---

## ✅ Solutions (Essayez dans l'ordre)

### **Solution 1 : Mise à Jour du Module (RECOMMANDÉE)**

1. **Connectez-vous à Odoo** : http://localhost:8069

2. **Activez le mode développeur** :
   - Cliquez sur votre nom (en haut à droite)
   - **Paramètres** → **Activer le mode développeur**

3. **Allez dans Applications** :
   - Menu principal → **Applications**
   - Supprimez le filtre "Applications" dans la barre de recherche

4. **Recherchez le module** :
   - Tapez : **"stockex"** ou **"StockInv"**

5. **Mettez à niveau** :
   - Cliquez sur le bouton **"Mettre à niveau"** (icône flèche circulaire)
   - Attendez 10-30 secondes

6. **Rafraîchissez** :
   - Appuyez sur **F5** pour rafraîchir la page

7. **Vérifiez** :
   - `Gestion d'Inventaire → Import → 📦 Stock Initial`

---

### **Solution 2 : Redémarrage du Service**

#### **Via Services Windows** :

1. **Win + R** → tapez `services.msc` → **Entrée**

2. Trouvez **"odoo-server-18.0"**

3. **Clic droit** → **Redémarrer**

4. Attendez 10-15 secondes

5. Puis appliquez **Solution 1** (mise à niveau du module)

---

#### **Via Script Automatique** :

**Exécutez** (en tant qu'administrateur) :
```
c:\apps\stockex\force_update.ps1
```

OU

```
c:\apps\stockex\force_update.bat
```

---

### **Solution 3 : Accès Direct via URL**

Si le menu n'apparaît toujours pas, essayez d'accéder directement :

```
http://localhost:8069/web#action=stockex.action_initial_stock_wizard_menu
```

Si cela fonctionne, c'est un problème de droits ou de cache.

---

### **Solution 4 : Vérification des Droits**

1. **Allez dans** : Paramètres → Utilisateurs & Sociétés → Utilisateurs

2. **Ouvrez votre utilisateur**

3. **Vérifiez les groupes** :
   - ✅ **Administration / Paramètres** (pour voir tous les menus)
   - ✅ **Inventaire / Administrateur**
   - ✅ **Inventaire / Utilisateur**

4. **Sauvegardez** et **reconnectez-vous**

---

### **Solution 5 : Réinstallation Complète du Module**

⚠️ **ATTENTION** : Cette méthode supprime toutes les données du module !

1. **Sauvegardez vos données** avant de continuer

2. **Allez dans** : Applications

3. **Recherchez** : "stockex"

4. **Désinstallez** le module :
   - Menu (⋮) → **Désinstaller**
   - Confirmez

5. **Attendez** la désinstallation complète

6. **Réinstallez** le module :
   - Recherchez "stockex"
   - Cliquez sur **Installer**

7. **Vérifiez** le menu

---

## 🔍 Diagnostic Avancé

### **Vérifier si l'action existe** :

1. **Mode développeur** activé

2. **Allez dans** : Paramètres → Technique → Actions → Actions de fenêtre

3. **Recherchez** : "Stock Initial"

4. **Vérifiez** :
   - ✅ Nom : "Stock Initial"
   - ✅ Modèle : `stockex.initial.stock.wizard`
   - ✅ Type de vue : `form`
   - ✅ Mode cible : `new`

5. Si l'action **n'existe pas** → Le module n'est pas correctement chargé → **Solution 1**

---

### **Vérifier si le menu existe** :

1. **Mode développeur** activé

2. **Allez dans** : Paramètres → Technique → Interface utilisateur → Éléments de menu

3. **Recherchez** : "Stock Initial"

4. **Vérifiez** :
   - ✅ Nom : "📦 Stock Initial"
   - ✅ Parent : "Import"
   - ✅ Action : "Stock Initial"
   - ✅ Séquence : 1

5. Si le menu **existe** mais n'apparaît pas → Problème de droits → **Solution 4**

---

### **Vérifier les logs Odoo** :

1. **Localisez les logs** (généralement) :
   ```
   C:\Program Files\Odoo 18.0.20250428\server\odoo.log
   ```

2. **Recherchez** des erreurs liées à :
   - `stockex`
   - `action_initial_stock_wizard`
   - `menu_initial_stock_wizard`

3. Si vous trouvez des erreurs de type :
   - `External ID not found` → Ordre de chargement incorrect
   - `Access Denied` → Problème de droits
   - `ParseError` → Erreur XML

---

## 📊 Vérification de l'Ordre de Chargement

Le fichier `__manifest__.py` doit avoir cet ordre :

```python
'data': [
    # ... security, data ...
    
    # Wizards AVANT menus.xml
    'wizards/initial_stock_wizard_views.xml',  # ← Définit action_initial_stock_wizard
    
    # ... autres vues ...
    
    # Menus APRÈS les wizards
    'views/menus.xml',  # ← Utilise action_initial_stock_wizard_menu
],
```

---

## 🆘 Support

Si aucune solution ne fonctionne :

1. **Vérifiez** que vous avez bien :
   - ✅ Mis à jour le module
   - ✅ Rafraîchi la page (F5)
   - ✅ Mode développeur activé
   - ✅ Droits administrateur

2. **Essayez** l'accès direct (Solution 3)

3. **Consultez** les logs Odoo pour voir les erreurs exactes

4. **Dernier recours** : Réinstallation complète (Solution 5)

---

## 📝 Notes

- Le menu devrait apparaître sous : `Gestion d'Inventaire → Import`
- Séquence : 1 (donc en **premier** dans la liste Import)
- Icône : 📦
- Action : Ouvre un wizard modal (popup)

---

**Dernière mise à jour** : 2025-10-28  
**Module** : StockInv (stockex)  
**Version** : 18.0.5.0.0
