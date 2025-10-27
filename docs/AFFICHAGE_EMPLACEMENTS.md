# 📍 Affichage des Emplacements - Format Amélioré

## 🎯 Objectif

Les emplacements s'affichent maintenant avec un format plus complet et lisible : **[CODE] Nom Complet**

---

## ✅ **Nouveau Format d'Affichage**

### **Avant :**
```
WH/Stock
```
❌ Peu parlant, difficile à identifier

### **Après :**
```
[WH-ABJ-001] Abidjan / Warehouse / Stock
```
✅ Code ET nom complet visibles immédiatement

---

## 📊 **Exemples Concrets**

### **Cas 1 : Avec Code (Barcode)**

**Données :**
- Code (barcode) : `WH-KOU-WSE`
- Nom complet : `Koumassi Wse / Warehouse / Stock`

**Affichage :**
```
[WH-KOU-WSE] Koumassi Wse / Warehouse / Stock
```

### **Cas 2 : Sans Code**

**Données :**
- Pas de code
- Nom complet : `Yopougon / Warehouse / Stock`

**Affichage :**
```
Yopougon / Warehouse / Stock
```
(Standard Odoo si pas de code)

---

## 🔍 **Où S'applique Cette Modification**

### **1. Lignes d'Inventaire**

Lors de la sélection d'un emplacement :
```
┌────────────────────────────────────────────┐
│ Emplacement: ▼                             │
│ [WH-ABJ-001] Abidjan / Warehouse / Stock   │
│ [WH-KOU-WSE] Koumassi Wse / Warehouse...   │
│ [WH-YOP-001] Yopougon / Warehouse / Stock  │
└────────────────────────────────────────────┘
```

### **2. Formulaire d'Inventaire**

Dans le détail d'un inventaire :
```
Produit              | Emplacement                              | Qté
------------------------------------------------------------------
ABC123 Frigo LG      | [WH-ABJ-001] Abidjan / Warehouse / Stock | 50
XYZ456 Clim Samsung  | [WH-KOU-WSE] Koumassi Wse / Warehouse... | 30
```

### **3. Import Excel/CSV**

Lors de l'import, le code est utilisé pour matcher :
```
Fichier Excel:
CODE ENTREPOT    | ENTREPOT
---------------------------------
WH-ABJ-001       | Abidjan Warehouse

Résultat Odoo:
[WH-ABJ-001] Abidjan / Warehouse / Stock
```

### **4. Dashboard**

Dans le Top 5 Entrepôts :
```
┌────────────────────────────────────────┐
│ 🏭 Top 5 Entrepôts                     │
├────────────────────────────────────────┤
│ [WH-ABJ-001] Abidjan...    245,670 €   │
│ [WH-KOU-WSE] Koumassi...    89,230 €   │
│ [WH-YOP-001] Yopougon...    57,890 €   │
└────────────────────────────────────────┘
```

### **5. Rapports et Listes**

Toutes les vues où les emplacements apparaissent.

---

## 🛠️ **Comment Ça Fonctionne**

### **Code Technique**

Le champ `display_name` est maintenant calculé automatiquement :

```python
@api.depends('name', 'barcode', 'complete_name')
def _compute_display_name(self):
    for record in self:
        if record.barcode:
            # Avec code: [CODE] Nom Complet
            record.display_name = f"[{record.barcode}] {record.complete_name or record.name}"
        else:
            # Sans code: Nom Complet standard
            record.display_name = record.complete_name or record.name
```

### **Champs Utilisés**

- **barcode** : Code de l'emplacement (ex: WH-ABJ-001)
- **complete_name** : Chemin complet (ex: Abidjan / Warehouse / Stock)
- **name** : Nom simple (ex: Stock)

---

## 📋 **Avantages**

### **1. ✅ Identification Rapide**

```
❌ Avant: "Stock"
   → De quel entrepôt ? Quelle ville ?

✅ Après: "[WH-ABJ-001] Abidjan / Warehouse / Stock"
   → Information complète en un coup d'œil
```

### **2. ✅ Cohérence avec les Imports**

Les codes utilisés dans vos fichiers Excel correspondent exactement :

```
Excel:           WH-ABJ-001
Odoo affiche:    [WH-ABJ-001] Abidjan / Warehouse / Stock
→ Matching immédiat !
```

### **3. ✅ Traçabilité**

Chaque emplacement est unique et identifiable :

```
[WH-ABJ-001] → Code unique
Abidjan / Warehouse / Stock → Chemin hiérarchique complet
```

### **4. ✅ Compatibilité Kobo**

Pour la collecte terrain, le code est envoyé et reconnu :

```
Kobo envoie:     WH-ABJ-001
Odoo trouve:     [WH-ABJ-001] Abidjan / Warehouse / Stock
→ Import automatique réussi !
```

---

## 🔄 **Mise à Jour Automatique**

Les emplacements existants sont automatiquement mis à jour :
- Pas besoin de modifier les données
- Le calcul se fait en temps réel
- S'applique à tous les emplacements

---

## 📝 **Recommandations**

### **1. Utiliser des Codes Clairs**

**Bonne pratique :**
```
WH-ABJ-001  → Entrepôt Abidjan, Stock 1
WH-KOU-WSE  → Entrepôt Koumassi, Warehouse
WH-YOP-001  → Entrepôt Yopougon, Stock 1
```

**Structure recommandée :**
```
[Type]-[Ville]-[Numéro]
WH : Warehouse (Entrepôt)
ABJ : Abidjan
001 : Numéro séquentiel
```

### **2. Définir les Codes dès la Création**

Lors de la création d'un emplacement :
```
1. Nom: Stock
2. Parent: Abidjan / Warehouse
3. ⭐ Code-barres: WH-ABJ-001
```

Sans code, seul le nom complet s'affiche.

### **3. Standardiser la Nomenclature**

Créer un document de référence :
```
┌───────┬───────────┬──────────────────────┐
│ Code  │ Ville     │ Nom Complet          │
├───────┼───────────┼──────────────────────┤
│ WH-ABJ│ Abidjan   │ Abidjan / Warehouse  │
│ WH-KOU│ Koumassi  │ Koumassi Wse         │
│ WH-YOP│ Yopougon  │ Yopougon / Warehouse │
└───────┴───────────┴──────────────────────┘
```

---

## 🔧 **Personnalisation**

### **Changer le Format d'Affichage**

Si vous voulez un format différent, modifiez :
```
/home/one/apps/stockex/models/stock_location.py
```

**Exemples de formats possibles :**

```python
# Format 1: [CODE] - Nom
record.display_name = f"[{record.barcode}] - {record.name}"

# Format 2: CODE | Nom Complet
record.display_name = f"{record.barcode} | {record.complete_name}"

# Format 3: CODE (Nom)
record.display_name = f"{record.barcode} ({record.complete_name})"
```

Puis :
```bash
odoo -d eneo --addons-path=/home/one/apps --stop-after-init -u stockex
```

---

## ✅ **Vérification**

### **Test 1 : Liste d'Emplacements**

```
Stock → Configuration → Emplacements
→ Vérifier le format [CODE] Nom
```

### **Test 2 : Ligne d'Inventaire**

```
Opérations → Inventaires → Ouvrir un inventaire
→ Voir les emplacements avec codes
```

### **Test 3 : Import Excel**

```
Import un fichier avec codes d'entrepôts
→ Vérifier que les codes matchent
```

---

## 🎯 **Résultat Final**

### **Avant la Modification**

```
Inventaire INV/2025/001
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Produit          | Emplacement  | Qté
----------------------------------------
Frigo LG         | Stock        | 50
Clim Samsung     | Stock        | 30
```
❌ Impossible de savoir quel "Stock"

### **Après la Modification**

```
Inventaire INV/2025/001
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Produit          | Emplacement                               | Qté
--------------------------------------------------------------------
Frigo LG         | [WH-ABJ-001] Abidjan / Warehouse / Stock  | 50
Clim Samsung     | [WH-KOU-WSE] Koumassi Wse / Warehouse...  | 30
```
✅ Information complète et claire !

---

## 📊 **Impact**

### **Lisibilité**
⭐⭐⭐⭐⭐ (5/5) - Information complète

### **Traçabilité**
⭐⭐⭐⭐⭐ (5/5) - Code unique visible

### **Efficacité**
⭐⭐⭐⭐⭐ (5/5) - Identification immédiate

### **Compatibilité**
⭐⭐⭐⭐⭐ (5/5) - Fonctionne partout

---

**Vos emplacements s'affichent maintenant de manière claire et complète dans tout le module !** 📍✨
