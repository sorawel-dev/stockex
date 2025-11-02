# Comptes Comptables OHADA pour la Gestion des Stocks
## Recommandations Expert Comptable

---

## 📊 Vue d'Ensemble

Ce document présente les comptes comptables OHADA appropriés pour la gestion automatisée des stocks dans Odoo, conformément au Plan Comptable OHADA révisé.

---

## 🎯 Les 4 Types de Comptes Requis

### 1️⃣ **Compte d'Entrée en Stock** (Stock Input Account)
**Rôle**: Enregistre la contrepartie lors de l'entrée de marchandises/matières en stock

| Type de Stock | Compte | Libellé |
|---------------|--------|---------|
| **Marchandises** | **603** | Variation des stocks de marchandises |
| Matières premières | 6031 | Variation des stocks de matières premières |
| Fournitures | 6032 | Variation des autres approvisionnements |

**Écriture type (Entrée en stock)**:
```
Débit  31  Marchandises                    10 000
Crédit 603 Variation stocks marchandises           10 000
```

---

### 2️⃣ **Compte de Sortie de Stock** (Stock Output Account)
**Rôle**: Enregistre la contrepartie lors de la sortie de marchandises/produits du stock

| Type de Stock | Compte | Libellé |
|---------------|--------|---------|
| **Marchandises** | **603** | Variation des stocks de marchandises (même compte) |
| Produits finis | 713 | Variation des stocks de produits |

**Écriture type (Sortie de stock)**:
```
Débit  603 Variation stocks marchandises    8 000
Crédit 31  Marchandises                            8 000
```

---

### 3️⃣ **Compte de Valorisation des Stocks** (Stock Valuation Account)
**Rôle**: Compte de bilan qui représente la valeur des stocks détenus

| Type de Stock | Compte | Libellé | Classe |
|---------------|--------|---------|--------|
| **Marchandises** | **31** | Marchandises | Actif Circulant |
| Matières premières | 32 | Matières premières et fournitures liées | Actif Circulant |
| Fournitures | 33 | Autres approvisionnements | Actif Circulant |
| Produits finis | 35 | Stocks de produits | Actif Circulant |

**Principe**: Ce compte figure au bilan et représente la valeur totale du stock à la date de clôture.

---

### 4️⃣ **Compte d'Écart de Prix** (Price Difference Account)
**Rôle**: Enregistre les différences entre prix standard et prix réel d'achat

#### **Méthode 1: Comptes d'Écarts Détaillés (Recommandée)**

| Compte | Libellé | Type d'Écart |
|--------|---------|--------------|
| **381** | Écarts de prix sur achats (Mali) | Écart défavorable (perte) |
| **382** | Écarts de prix sur achats (Boni) | Écart favorable (gain) |

**Écriture type (Prix réel > Prix standard)**:
```
Débit  31  Marchandises (prix standard)     10 000
Débit  381 Écart de prix (Mali)                500
Crédit 401 Fournisseurs                            10 500
```

#### **Méthode 2: Compte Simplifié (Alternative)**

| Compte | Libellé | Usage |
|--------|---------|-------|
| **658** | Charges diverses de gestion courante | Tous les écarts en charges |

**Écriture type (Prix réel > Prix standard)**:
```
Débit  31  Marchandises (prix standard)     10 000
Débit  658 Charges diverses                     500
Crédit 401 Fournisseurs                            10 500
```

---

## ✅ Configuration Par Défaut Recommandée

### **Pour les MARCHANDISES** (cas le plus courant)

```
┌─────────────────────────────────────────────────────┐
│ Catégorie: Marchandises                            │
├─────────────────────────────────────────────────────┤
│ 1. Compte d'Entrée:      603                        │
│ 2. Compte de Sortie:     603                        │
│ 3. Compte de Valorisation: 31                       │
│ 4. Compte d'Écart:       381 (ou 658)               │
└─────────────────────────────────────────────────────┘
```

### **Pour les MATIÈRES PREMIÈRES**

```
┌─────────────────────────────────────────────────────┐
│ Catégorie: Matières Premières                      │
├─────────────────────────────────────────────────────┤
│ 1. Compte d'Entrée:      6031                       │
│ 2. Compte de Sortie:     6031                       │
│ 3. Compte de Valorisation: 32                       │
│ 4. Compte d'Écart:       381 (ou 658)               │
└─────────────────────────────────────────────────────┘
```

### **Pour les PRODUITS FINIS**

```
┌─────────────────────────────────────────────────────┐
│ Catégorie: Produits Finis                          │
├─────────────────────────────────────────────────────┤
│ 1. Compte d'Entrée:      713                        │
│ 2. Compte de Sortie:     713                        │
│ 3. Compte de Valorisation: 35                       │
│ 4. Compte d'Écart:       381 (ou 658)               │
└─────────────────────────────────────────────────────┘
```

---

## 📚 Principes Comptables OHADA

### **Principe de Base**

1. **Comptes de Classe 3** (Actif Circulant)
   - Enregistrent la **VALEUR** des stocks au bilan
   - Mouvements: Débit = Entrée, Crédit = Sortie

2. **Comptes de Classe 6** (Charges)
   - Enregistrent les **VARIATIONS** de stocks d'achats
   - Comptes 603x pour marchandises et matières

3. **Comptes de Classe 7** (Produits)
   - Enregistrent les **VARIATIONS** de stocks de production
   - Compte 713 pour produits finis

### **Méthode de l'Inventaire Permanent**

Dans Odoo avec valorisation automatique:
- Chaque mouvement de stock génère une écriture comptable
- Le compte 31 (ou 32, 33, 35) reflète en temps réel la valeur du stock
- Les comptes 603/713 enregistrent les variations

---

## 🔄 Flux Comptable Complet

### **Exemple: Achat de Marchandises**

**Étape 1: Réception (Entrée en stock)**
```
Date: 01/10/2025
Débit  31  Marchandises                    10 000
Crédit 603 Variation stocks marchandises           10 000
```

**Étape 2: Vente (Sortie de stock)**
```
Date: 15/10/2025
Débit  603 Variation stocks marchandises    8 000
Crédit 31  Marchandises                            8 000
```

**Résultat au 31/10/2025**:
- Compte 31 (Bilan): 2 000 (stock restant)
- Compte 603 (Résultat): Crédit 2 000 (variation positive)

---

## ⚠️ Points d'Attention

### **1. Même Compte pour Entrée/Sortie**
Pour les marchandises et matières, le compte 603x est utilisé:
- En **CRÉDIT** lors des entrées (augmentation stock)
- En **DÉBIT** lors des sorties (diminution stock)

### **2. Écarts de Prix**
Deux approches possibles:
- **Détaillée** (381/382): Permet un suivi précis des écarts
- **Simplifiée** (658): Plus simple, écarts en charges diverses

### **3. Inventaire Physique**
Lors de l'inventaire annuel, ajuster le compte 31 (ou 32, 33, 35) pour refléter la valeur réelle du stock physique.

---

## 📋 Tableau Récapitulatif

| Type Stock | Valorisation | Entrée | Sortie | Écart Prix |
|------------|--------------|--------|--------|------------|
| Marchandises | 31 | 603 | 603 | 381/658 |
| Matières 1ères | 32 | 6031 | 6031 | 381/658 |
| Fournitures | 33 | 6032 | 6032 | 381/658 |
| Produits Finis | 35 | 713 | 713 | 381/658 |

---

## 🎓 Références OHADA

- **Plan Comptable OHADA** - Système Comptable OHADA Révisé
- **Classe 3**: Comptes de Stocks et En-cours
- **Classe 6**: Comptes de Charges
- **Classe 7**: Comptes de Produits

---

## 💡 Conseil Expert

**Pour une PME commerciale classique**, la configuration recommandée est:

```yaml
Catégorie par défaut: "Toutes catégories / All"
  - Stock Input Account: 603
  - Stock Output Account: 603
  - Stock Valuation Account: 31
  - Price Difference Account: 658 (simplifié)
```

Cette configuration couvre 80% des besoins et respecte strictement le plan OHADA.

---

**Document préparé par**: Expert Comptable OHADA  
**Date**: Octobre 2025  
**Version**: 1.0
