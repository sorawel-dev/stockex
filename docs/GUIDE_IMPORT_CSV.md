# 📥 Guide d'Import CSV - Module Stockex

**Version :** 18.0.1.0.0  
**Date :** 18 Octobre 2025  
**Fonctionnalité :** Import d'Inventaire depuis Fichier CSV

---

## 🎯 Vue d'Ensemble

Le wizard d'import CSV permet d'importer automatiquement des données d'inventaire depuis un fichier CSV structuré. Il est particulièrement adapté pour le fichier `val_stock_brut.csv` (3,263 lignes).

### Fonctionnalités

✅ **Import automatique** de milliers de lignes d'inventaire  
✅ **Prévisualisation** avant import réel  
✅ **Création automatique** des produits et emplacements manquants  
✅ **Mise à jour** des prix standards (optionnel)  
✅ **Gestion des erreurs** avec log détaillé  
✅ **Support multi-formats** (séparateurs configurables)

---

## 📋 Prérequis

### Structure du Fichier CSV Attendue

Le fichier CSV doit contenir ces colonnes (ordre flexible) :

| Colonne | Description | Obligatoire | Exemple |
|---------|-------------|-------------|---------|
| `product_default_code` | Référence produit unique | ✅ Oui | 102000065 |
| `product_id` | Nom/description du produit | ⚠️ Recommandé | SODER WOOD GLUE |
| `wharehouse` | Nom de l'emplacement de stock | ✅ Oui | Bassa Wse |
| `quantity` | Quantité théorique en stock | ✅ Oui | 1 ou 6,517 |
| `standard_price` | Prix unitaire standard | ⚪ Optionnel | 2,600 |
| `uom` | Unité de mesure | ⚪ Optionnel | PC (Pièce) |

**Autres colonnes** (ignorées) : `wh_type_code`, `wh_type_id`, `wh_code`

### Format des Nombres Supportés

| Format | Exemple | Configuration Wizard |
|--------|---------|---------------------|
| **Virgule décimale + Espace milliers** | 1 234,56 | Décimal: Virgule |
| **Point décimal + Virgule milliers** | 1,234.56 | Décimal: Point |
| **Sans séparateur milliers** | 1234.56 | Point ou Virgule |

---

## 🚀 Guide d'Utilisation

### Étape 1 : Accéder au Wizard

**Méthode 1 - Depuis la Liste des Inventaires :**
1. Menu : **Gestion de Stock** → **Inventaires**
2. Cliquez sur **"Importer CSV"** (bouton bleu avec icône 📤)

**Méthode 2 - Depuis le Menu Actions (si configuré) :**
1. Menu **Action** → **Importer un Inventaire CSV**

---

### Étape 2 : Remplir le Formulaire

#### Section 1 : Informations de l'Inventaire

```
┌──────────────────────────────────────────┐
│ Nom de l'inventaire:  Import CSV 2025   │
│ Date:                 18/10/2025         │
└──────────────────────────────────────────┘
```

- **Nom** : Donnez un nom descriptif (ex: "Inventaire Annuel 2025")
- **Date** : Date de l'inventaire (par défaut: aujourd'hui)

#### Section 2 : Fichier

```
┌──────────────────────────────────────────┐
│ Fichier CSV:  [Choisir un fichier...]   │
└──────────────────────────────────────────┘
```

- Cliquez sur **"Choisir un fichier"**
- Sélectionnez votre fichier CSV (ex: `val_stock_brut.csv`)

#### Section 3 : Paramètres d'Import

```
┌──────────────────────────────────────────┐
│ ── Paramètres d'Import ──────────────── │
│                                          │
│ Séparateur:          [ Virgule (,)    ▼]│
│ Séparateur décimal:  [ Virgule (,)    ▼]│
│                                          │
│ ☑ Créer les produits manquants          │
│ ☑ Créer les emplacements manquants      │
│ ☐ Mettre à jour les prix produits       │
└──────────────────────────────────────────┘
```

**Séparateur CSV :**
- Virgule (,) → Pour fichiers standards
- Point-virgule (;) → Pour fichiers européens
- Tabulation → Pour fichiers TSV

**Séparateur Décimal :**
- Virgule (,) → Format européen : 1,50
- Point (.) → Format anglais : 1.50

**Options de Création :**

| Option | Description | Recommandation |
|--------|-------------|----------------|
| **Créer les produits manquants** | Crée automatiquement les produits non trouvés | ✅ Activé (si 1er import) |
| **Créer les emplacements manquants** | Crée les emplacements de stock manquants | ✅ Activé (si 1er import) |
| **Mettre à jour les prix produits** | Écrase les prix existants avec ceux du CSV | ⚠️  Activer avec précaution |

---

### Étape 3 : Prévisualiser l'Import

1. Cliquez sur le bouton **"Prévisualiser"** (🔍)
2. Le wizard analyse le fichier sans créer de données
3. Un onglet **"Résultats de Prévisualisation"** apparaît

#### Écran de Prévisualisation

```
┌────────────────────────────────────────────────┐
│ ── Résultats de Prévisualisation ────────────  │
│                                                │
│ Nombre total de lignes:   3,263               │
│ Lignes valides:           3,100               │
│ Lignes avec erreurs:      163                 │
│                                                │
│ ── Log d'Analyse ──────────────────────────── │
│ === PRÉVISUALISATION DE L'IMPORT ===          │
│ Fichier : val_stock_brut.csv                  │
│ Total lignes : 3263                            │
│                                                │
│ Colonnes détectées : wh_type_code, ...        │
│                                                │
│ === RÉSULTATS ===                              │
│ ✅ Lignes valides : 95/100 (échantillon)      │
│ ❌ Lignes avec erreurs : 5/100                 │
│                                                │
│ ⚠️  Estimation sur fichier complet :          │
│    Lignes valides estimées : ~3100            │
│    Lignes erreurs estimées : ~163             │
└────────────────────────────────────────────────┘
```

**Interprétation :**
- ✅ **Lignes valides** : Données complètes et correctes
- ❌ **Lignes erreurs** : Données manquantes ou format incorrect
- 📊 **Échantillon** : Analyse sur 100 premières lignes pour rapidité

---

### Étape 4 : Lancer l'Import

1. Vérifiez les statistiques de prévisualisation
2. Si tout est OK, cliquez sur **"Importer"** (bouton bleu)
3. **Patience !** L'import peut prendre quelques minutes pour gros fichiers

#### Écran de Progression

```
⏳ Import en cours...
   Création des emplacements...
   Création des produits...
   Création des lignes d'inventaire...
   
   Progress: 1500 / 3263 lignes
```

#### Résultat de l'Import

```
┌────────────────────────────────────────────────┐
│ ✅ Import terminé avec succès !                │
│                                                │
│ ✅ Lignes importées : 3,100                    │
│ ⚠️  Lignes ignorées : 163                      │
│                                                │
│ Premières erreurs :                            │
│ - Ligne 15: Emplacement non trouvé            │
│ - Ligne 47: Produit non trouvé                │
│ - Ligne 102: Quantité = 0                     │
└────────────────────────────────────────────────┘
```

---

### Étape 5 : Vérifier l'Inventaire Créé

Vous êtes automatiquement redirigé vers l'inventaire créé :

```
┌────────────────────────────────────────────────┐
│ Inventaire : Import CSV 2025                   │
│ État : 🔵 Brouillon                            │
├────────────────────────────────────────────────┤
│ Date : 18/10/2025                              │
│ Responsable : John Doe                         │
│                                                │
│ ── Lignes d'inventaire (3,100) ────────────   │
│ Produit         │ Empl.   │ Théo.  │ Réel.   │
│ SODER WOOD GLUE │ Bassa   │ 1      │ 1       │
│ SOUPLISSO 6M/M  │ Bassa   │ 7      │ 7       │
│ ...                                            │
└────────────────────────────────────────────────┘
```

**Actions disponibles :**
1. **Vérifier les données** importées
2. **Modifier** les quantités réelles si nécessaire
3. **Démarrer** l'inventaire pour passer en mode "En cours"
4. **Valider** l'inventaire une fois terminé

---

## ⚠️ Résolution de Problèmes

### Erreur : "Emplacement non trouvé"

**Cause :** L'emplacement n'existe pas dans Odoo

**Solution 1 :** Activer "Créer les emplacements manquants"  
**Solution 2 :** Créer manuellement l'emplacement :
1. Inventory → Configuration → Emplacements
2. Créer un nouvel emplacement
3. Relancer l'import

### Erreur : "Produit non trouvé"

**Cause :** Le `product_default_code` n'existe pas

**Solution 1 :** Activer "Créer les produits manquants"  
**Solution 2 :** Importer d'abord les produits (module Product)

### Erreur : "Colonne manquante"

**Cause :** Structure CSV incorrecte

**Solution :**
1. Vérifier les noms de colonnes (exact match)
2. Vérifier l'encodage du fichier (UTF-8)
3. Vérifier le séparateur (virgule, point-virgule, tab)

### Erreur : "Format de nombre invalide"

**Cause :** Séparateur décimal incorrect

**Solution :**
- Si nombres comme "1,234.56" → Séparateur décimal: Point (.)
- Si nombres comme "1 234,56" → Séparateur décimal: Virgule (,)

### Import Très Lent

**Cause :** Gros fichier (> 5000 lignes)

**Solution :**
1. Désactiver le mode debug
2. Relancer Odoo en mode production
3. Découper le fichier en plusieurs parties

---

## 💡 Bonnes Pratiques

### Avant l'Import

- [ ] **Sauvegarder** la base de données
- [ ] **Vérifier** la structure du CSV (colonnes obligatoires)
- [ ] **Nettoyer** les données (supprimer lignes vides, "ANNULEE")
- [ ] **Tester** sur échantillon (100 lignes)
- [ ] **Activer** le mode développeur pour logs détaillés

### Pendant l'Import

- [ ] **Toujours** faire une prévisualisation d'abord
- [ ] **Noter** le nombre de lignes attendues
- [ ] **Ne pas fermer** le navigateur pendant l'import
- [ ] **Surveiller** les logs Odoo (si accès serveur)

### Après l'Import

- [ ] **Vérifier** le nombre de lignes créées
- [ ] **Contrôler** un échantillon de produits
- [ ] **Comparer** avec le fichier source
- [ ] **Corriger** les erreurs manuellement si peu nombreuses
- [ ] **Valider** l'inventaire si tout est correct

---

## 📊 Cas d'Usage Typiques

### Cas 1 : Import Initial (1ère fois)

```
Configuration recommandée :
✅ Créer les produits manquants
✅ Créer les emplacements manquants
✅ Mettre à jour les prix produits

Résultat attendu :
- Création de ~3,047 produits
- Création de 7 emplacements
- Création de 3,263 lignes d'inventaire
```

### Cas 2 : Mise à Jour d'Inventaire

```
Configuration recommandée :
❌ Créer les produits manquants (déjà créés)
❌ Créer les emplacements manquants (déjà créés)
❌ Mettre à jour les prix produits (optionnel)

Résultat attendu :
- 0 nouveau produit
- 0 nouvel emplacement
- Création d'un nouvel inventaire avec produits existants
```

### Cas 3 : Import Partiel (par Entrepôt)

```
Préparation :
1. Filtrer le CSV par entrepôt (ex: Bassa Wse)
2. Garder seulement les lignes concernées

Configuration :
❌ Créer les produits manquants
✅ Créer les emplacements manquants
❌ Mettre à jour les prix produits

Nom inventaire : "Inventaire Bassa Wse - Oct 2025"
```

---

## 🔧 Configuration Avancée

### Modification du Format CSV

Si votre fichier a une structure différente, modifiez le code :

**Fichier :** `wizards/import_inventory_wizard.py`

```python
# Ligne ~100 : Extraction des données
product_code = line.get('votre_colonne_produit', '').strip()
warehouse_name = line.get('votre_colonne_entrepot', '').strip()
```

### Ajout de Validation Personnalisée

```python
# Ligne ~120 : Avant création de ligne
if quantity < 0:
    raise UserError("Quantité négative non autorisée")
```

### Import Programmé (CRON)

Pour automatiser l'import quotidien :

1. Créer un CRON dans Odoo
2. Appeler `wizard.with_context(auto=True).action_import()`
3. Placer le fichier CSV dans un répertoire surveillé

---

## 📈 Statistiques d'Import

### Performance Estimée

| Nombre de Lignes | Temps d'Import | Mémoire |
|------------------|----------------|---------|
| 100 lignes | ~5 secondes | 50 MB |
| 1,000 lignes | ~30 secondes | 100 MB |
| 3,000 lignes | ~2 minutes | 200 MB |
| 10,000 lignes | ~10 minutes | 500 MB |

**Note :** Temps estimés sur serveur standard. Varie selon CPU/RAM.

### Optimisation

Pour gros fichiers (> 10,000 lignes) :
1. Augmenter la RAM Odoo
2. Désactiver le tracking sur les champs
3. Utiliser `create_multi` au lieu de `create`
4. Découper en batches de 1000 lignes

---

## 🆘 Support

### Logs Odoo

Pour voir les détails de l'import :

```bash
# En temps réel
sudo tail -f /var/log/odoo/odoo-server.log | grep "Import"

# Rechercher erreurs
sudo grep -i "ERROR.*import" /var/log/odoo/odoo-server.log
```

### Mode Debug

Activer le mode développeur :
1. Paramètres → Activer le mode développeur
2. Relancer l'import
3. Consulter les logs dans le chatter de l'inventaire

### Réinitialiser un Import Raté

Si l'import échoue en cours :
1. Supprimer l'inventaire partiellement créé
2. Corriger le fichier CSV
3. Relancer l'import

---

## ✅ Checklist Finale

Avant de valider un import :

- [ ] Nombre de lignes importées = Nombre attendu
- [ ] Échantillon de 10 produits vérifiés manuellement
- [ ] Emplacements correctement assignés
- [ ] Quantités cohérentes
- [ ] Prix standards corrects (si mis à jour)
- [ ] Aucune erreur dans les logs
- [ ] Description de l'inventaire remplie
- [ ] Responsable assigné

---

**Version du guide :** 1.0  
**Dernière mise à jour :** 18 Octobre 2025  
**Auteur :** Sorawel  
**Module :** Stockex v18.0.1.0.0
