# 📍 Renommer les Emplacements - Guide Complet

## 🎯 Objectif

Les emplacements affichent maintenant leur **nom complet hiérarchique** au lieu de leur code.

---

## ✅ **Nouveau Format d'Affichage**

### **Avant :**
```
001/Stock
002/Stock
WH-ABJ-001/Stock
```
❌ Codes peu parlants

### **Après :**
```
Kits Comp Wse/Stock
Abidjan/Warehouse/Stock
Koumassi Wse/Warehouse/Stock
```
✅ Noms complets et descriptifs

---

## 🔍 **Comment Ça Fonctionne**

### **Le `complete_name` est Calculé Automatiquement**

Odoo calcule le nom complet en combinant :
- Le nom de l'emplacement parent
- Un séparateur `/`
- Le nom de l'emplacement enfant

**Exemple de hiérarchie :**
```
Kits Comp Wse (parent)
  └─ Stock (enfant)
     → Nom complet affiché : "Kits Comp Wse/Stock"
```

---

## 🛠️ **Étapes pour Renommer les Emplacements**

### **Étape 1 : Identifier les Emplacements à Renommer**

```
Menu → Stock → Configuration → Emplacements
```

**Vérifiez les emplacements qui ont des codes comme nom :**
- `001`, `002`, `003`, etc.
- `WH-ABJ-001`, `WH-KOU-WSE`, etc.

### **Étape 2 : Renommer l'Emplacement Parent**

**Pour chaque emplacement :**

1. **Ouvrir l'emplacement**
   ```
   Cliquer sur l'emplacement → Éditer
   ```

2. **Modifier le champ "Nom d'emplacement"**
   ```
   Ancien : 001
   Nouveau : Kits Comp Wse
   ```

3. **Enregistrer**

### **Étape 3 : Vérifier la Hiérarchie**

**Exemple de structure correcte :**

```
📁 Emplacements Physiques
  📁 Kits Comp Wse (Type: Vue)
    📦 Stock (Type: Interne)
  📁 Abidjan
    📁 Warehouse (Type: Vue)
      📦 Stock (Type: Interne)
  📁 Koumassi Wse
    📁 Warehouse (Type: Vue)
      📦 Stock (Type: Interne)
```

**Résultat des noms complets :**
```
Kits Comp Wse/Stock
Abidjan/Warehouse/Stock
Koumassi Wse/Warehouse/Stock
```

---

## 📋 **Exemples de Renommage**

### **Cas 1 : Emplacement Simple**

**Avant :**
```
Nom: 001
Parent: Emplacements Physiques
Type: Interne
→ Affichage: Emplacements Physiques/001
```

**Après renommage :**
```
Nom: Kits Comp Wse
Parent: Emplacements Physiques
Type: Interne
→ Affichage: Emplacements Physiques/Kits Comp Wse
```

### **Cas 2 : Hiérarchie à 2 Niveaux**

**Avant :**
```
Parent: WH-ABJ-001 (Type: Vue)
  Enfant: Stock (Type: Interne)
→ Affichage: WH-ABJ-001/Stock
```

**Après renommage du parent :**
```
Parent: Abidjan (Type: Vue)
  Enfant: Stock (Type: Interne)
→ Affichage: Abidjan/Stock
```

### **Cas 3 : Hiérarchie à 3 Niveaux**

**Avant :**
```
Grand-parent: WH-KOU-WSE
  Parent: Warehouse
    Enfant: Stock
→ Affichage: WH-KOU-WSE/Warehouse/Stock
```

**Après renommage du grand-parent :**
```
Grand-parent: Koumassi Wse
  Parent: Warehouse
    Enfant: Stock
→ Affichage: Koumassi Wse/Warehouse/Stock
```

---

## 🎨 **Recommandations de Nommage**

### **1. Utiliser des Noms Descriptifs**

**Bon :**
```
✅ Abidjan
✅ Koumassi Wse
✅ Kits Comp Wse
✅ Yopougon
✅ Entrepôt Central
```

**À éviter :**
```
❌ 001, 002, 003
❌ WH-ABJ-001
❌ LOC001
❌ A, B, C
```

### **2. Hiérarchie Claire**

**Structure recommandée :**
```
📁 Ville/Zone
  📁 Type d'entrepôt
    📦 Emplacement spécifique
```

**Exemple :**
```
Abidjan
  └─ Warehouse
     ├─ Stock
     ├─ Réception
     └─ Expédition
```

### **3. Noms Courts mais Parlants**

**Bon équilibre :**
```
✅ Koumassi Wse  (court, descriptif)
✅ Entrepôt Nord (clair, concis)
```

**Trop long :**
```
❌ Entrepôt de Koumassi Warehouse Section Est Zone A
```

---

## 🚀 **Renommage en Masse (Optionnel)**

### **Via SQL (Avancé)**

Si vous avez beaucoup d'emplacements à renommer, vous pouvez utiliser SQL :

```sql
-- Sauvegarder d'abord !
-- Puis renommer par exemple tous les emplacements qui commencent par WH-

UPDATE stock_location 
SET name = 
    CASE 
        WHEN name = 'WH-ABJ-001' THEN 'Abidjan'
        WHEN name = 'WH-KOU-WSE' THEN 'Koumassi Wse'
        WHEN name = 'WH-YOP-001' THEN 'Yopougon'
        ELSE name
    END
WHERE name LIKE 'WH-%';
```

**⚠️ Attention :** Faites une sauvegarde de la base avant !

### **Via Import CSV**

1. **Exporter les emplacements**
   ```
   Stock → Configuration → Emplacements
   → Sélectionner tout
   → Action → Exporter
   → Cocher : ID, Nom
   ```

2. **Modifier dans Excel**
   ```
   Colonne A: ID (ne pas modifier)
   Colonne B: Nom (modifier)
   ```

3. **Réimporter**
   ```
   Stock → Configuration → Emplacements
   → Importer
   → Charger le fichier modifié
   ```

---

## 🔄 **Impact du Renommage**

### **Où les Changements Apparaissent**

✅ **Dashboard** : Top 5 Entrepôts avec nouveaux noms
✅ **Inventaires** : Lignes d'inventaire
✅ **Imports** : Reconnaissance par nom complet
✅ **Rapports** : Tous les rapports
✅ **Recherches** : Recherche par nom descriptif

### **Pas d'Impact sur**

✅ **Données historiques** : Conservées
✅ **Références externes** : Le code-barres reste inchangé
✅ **Intégrations** : Les IDs internes ne changent pas

---

## 📊 **Vérification après Renommage**

### **Test 1 : Liste des Emplacements**

```
Stock → Configuration → Emplacements
→ Vérifier que les noms sont corrects
```

### **Test 2 : Inventaire**

```
Opérations → Inventaires → Ouvrir un inventaire
→ Vérifier l'affichage des emplacements
```

### **Test 3 : Dashboard**

```
Vue d'Ensemble → Top 5 Entrepôts
→ Vérifier les nouveaux noms
```

---

## 💡 **Astuce : Garder les Codes en Référence Interne**

Vous pouvez garder les codes dans le champ **Code-barres** pour référence :

```
Nom d'emplacement : Kits Comp Wse
Code-barres : WH-KIT-001
→ Affichage : Kits Comp Wse/Stock
→ Recherche possible par code : WH-KIT-001
```

**Avantage :** 
- Affichage descriptif
- Code conservé pour imports/exports
- Recherche possible par les deux

---

## 🎯 **Exemple Complet de Renommage**

### **Situation Initiale**

```
Emplacements:
- 001/Stock
- 002/Stock
- WH-ABJ-001/Warehouse/Stock
```

### **Actions**

1. Renommer `001` → `Kits Comp Wse`
2. Renommer `002` → `Entrepôt Central`
3. Renommer `WH-ABJ-001` → `Abidjan`

### **Résultat**

```
Emplacements:
- Kits Comp Wse/Stock
- Entrepôt Central/Stock
- Abidjan/Warehouse/Stock
```

### **Dans le Dashboard**

```
🏭 Top 5 Entrepôts
┌────────────────────────────────────┐
│ Kits Comp Wse/Stock    245,670 FCFA│
│ Abidjan/Warehouse...    89,230 FCFA│
│ Entrepôt Central...     57,890 FCFA│
└────────────────────────────────────┘
```

---

## ⚠️ **Points d'Attention**

### **1. Cohérence**

Gardez une logique de nommage cohérente :
```
✅ Abidjan, Koumassi, Yopougon
❌ Abidjan, KOU, YOP-001
```

### **2. Caractères Spéciaux**

Évitez les caractères spéciaux :
```
✅ Koumassi Wse
❌ Koumassi/Wse (/ est le séparateur)
❌ Koumassi\Wse (\ peut causer des problèmes)
```

### **3. Longueur**

Gardez des noms raisonnables :
```
✅ 10-30 caractères max
❌ Trop long → tronqué dans les tableaux
```

---

## ✅ **Checklist de Renommage**

- [ ] Identifier tous les emplacements avec codes
- [ ] Définir une nomenclature claire
- [ ] Renommer les emplacements parents en priorité
- [ ] Vérifier la hiérarchie
- [ ] Tester l'affichage dans un inventaire
- [ ] Vérifier le dashboard
- [ ] Informer les utilisateurs
- [ ] Mettre à jour la documentation interne

---

**Vos emplacements affichent maintenant des noms descriptifs et complets !** 📍✨

Pour toute question sur la structure hiérarchique ou le renommage, référez-vous à ce guide.
