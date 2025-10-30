# Configuration des Comptes Comptables OHADA pour les Stocks

## Vue d'ensemble

Le module **StockInv** configure automatiquement les comptes comptables selon le référentiel **OHADA** (Organisation pour l'Harmonisation en Afrique du Droit des Affaires) pour la gestion des stocks.

---

## 📊 Structure des Comptes OHADA

### CLASSE 3 : COMPTES DE STOCKS (Actif)

| Code | Nom | Type | Usage |
|------|-----|------|-------|
| **31** | Marchandises | Actif circulant | Stock de marchandises achetées pour revente |
| **311** | Marchandises A | Actif circulant | Subdivision des marchandises |
| **32** | Matières premières et fournitures | Actif circulant | Matières utilisées pour production |
| **321** | Matières A | Actif circulant | Subdivision des matières |
| **33** | Autres approvisionnements | Actif circulant | Fournitures et consommables |
| **35** | Stocks de produits | Actif circulant | Produits finis fabriqués |
| **351** | Produits finis | Actif circulant | Subdivision des produits finis |

### CLASSE 6 : COMPTES DE CHARGES

| Code | Nom | Type | Usage |
|------|-----|------|-------|
| **603** | Variation des stocks de marchandises | Charge | Contrepartie des mouvements de marchandises |
| **6031** | Variation des stocks de matières premières | Charge | Contrepartie des mouvements de matières |
| **6032** | Variation des autres approvisionnements | Charge | Contrepartie des mouvements de fournitures |

### CLASSE 7 : COMPTES DE PRODUITS

| Code | Nom | Type | Usage |
|------|-----|------|-------|
| **713** | Variation des stocks de produits | Produit | Contrepartie des mouvements de produits finis |
| **7131** | Variation des stocks de produits finis | Produit | Subdivision des variations de produits |

---

## 🏷️ Configuration par Catégorie de Produits

### 1. Marchandises

**Méthode de coût :** FIFO (Premier Entré, Premier Sorti)  
**Valorisation :** Temps réel (real_time)

| Propriété | Compte OHADA |
|-----------|--------------|
| Compte de valorisation | **311** - Marchandises A |
| Compte d'entrée | **603** - Variation des stocks de marchandises |
| Compte de sortie | **603** - Variation des stocks de marchandises |

**Écritures comptables automatiques :**
```
Entrée de marchandises (100 unités à 10 XOF) :
  Débit  311 - Marchandises A          1,000 XOF
  Crédit 603 - Variation des stocks    1,000 XOF

Sortie de marchandises (50 unités à 10 XOF) :
  Débit  603 - Variation des stocks      500 XOF
  Crédit 311 - Marchandises A            500 XOF
```

---

### 2. Matières Premières

**Méthode de coût :** FIFO  
**Valorisation :** Temps réel

| Propriété | Compte OHADA |
|-----------|--------------|
| Compte de valorisation | **321** - Matières A |
| Compte d'entrée | **6031** - Variation des stocks de matières |
| Compte de sortie | **6031** - Variation des stocks de matières |

**Écritures comptables automatiques :**
```
Entrée de matières (200 kg à 5 XOF) :
  Débit  321 - Matières A              1,000 XOF
  Crédit 6031 - Variation des stocks   1,000 XOF

Sortie de matières (100 kg à 5 XOF) :
  Débit  6031 - Variation des stocks     500 XOF
  Crédit 321 - Matières A                500 XOF
```

---

### 3. Fournitures

**Méthode de coût :** Coût Moyen Pondéré  
**Valorisation :** Temps réel

| Propriété | Compte OHADA |
|-----------|--------------|
| Compte de valorisation | **33** - Autres approvisionnements |
| Compte d'entrée | **6032** - Variation des autres approvision. |
| Compte de sortie | **6032** - Variation des autres approvision. |

---

### 4. Produits Finis

**Méthode de coût :** FIFO  
**Valorisation :** Temps réel

| Propriété | Compte OHADA |
|-----------|--------------|
| Compte de valorisation | **351** - Produits finis |
| Compte d'entrée | **7131** - Variation des stocks de produits |
| Compte de sortie | **7131** - Variation des stocks de produits |

**Écritures comptables automatiques :**
```
Production de produits finis (50 unités à 20 XOF) :
  Débit  351 - Produits finis          1,000 XOF
  Crédit 7131 - Variation des stocks   1,000 XOF

Vente de produits finis (30 unités à 20 XOF) :
  Débit  7131 - Variation des stocks     600 XOF
  Crédit 351 - Produits finis            600 XOF
```

---

### 5. Consommables

**Méthode de coût :** Coût Standard  
**Valorisation :** Manuelle périodique (manual_periodic)

> ⚠️ **Note :** Les consommables n'ont pas de comptes automatiques. Les écritures sont enregistrées manuellement en fin de période.

---

## 🔄 Flux des Écritures Comptables

### Valorisation en Temps Réel (real_time)

```
┌─────────────────────┐
│  Mouvement Stock    │
│  (Entrée/Sortie)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Calcul Valorisation│
│  (Qty × Prix)       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Écriture Comptable  │
│ Automatique         │
└─────────────────────┘
```

### Validation d'Inventaire

```
Stock Initial → Validation → Ajustements Comptables

Exemple :
  Quantité théorique : 0
  Quantité réelle    : 100
  Différence         : +100 (excédent)

Écriture :
  Débit  311 - Marchandises A        1,000 XOF
  Crédit 603 - Variation des stocks  1,000 XOF
```

---

## ⚙️ Configuration Manuelle

Si vous souhaitez modifier les comptes par défaut :

1. **Allez dans** : Inventaire → Configuration → Catégories de Produits
2. **Sélectionnez** une catégorie (ex: Marchandises)
3. **Onglet** "Propriétés comptables"
4. **Modifiez** :
   - Compte de valorisation du stock
   - Compte de contrepartie des entrées
   - Compte de contrepartie des sorties

---

## 📝 Exemple Complet : Cycle d'Achat et Vente

### 1. Achat de marchandises

```
Facture fournisseur : 10,000 XOF (100 unités à 100 XOF)

Écriture comptable :
  Débit  601 - Achats de marchandises  10,000 XOF
  Crédit 401 - Fournisseurs            10,000 XOF
```

### 2. Réception en stock

```
Écriture automatique (real_time) :
  Débit  311 - Marchandises A          10,000 XOF
  Crédit 603 - Variation des stocks    10,000 XOF
```

### 3. Vente de marchandises

```
Facture client : 15,000 XOF (70 unités à 214.29 XOF)

Écriture vente :
  Débit  411 - Clients                 15,000 XOF
  Crédit 701 - Ventes de marchandises  15,000 XOF

Écriture sortie stock automatique :
  Débit  603 - Variation des stocks     7,000 XOF
  Crédit 311 - Marchandises A           7,000 XOF
```

### 4. Stock restant

```
Stock initial  : 100 unités (10,000 XOF)
Stock vendu    : 70 unités  (7,000 XOF)
Stock final    : 30 unités  (3,000 XOF)

Solde compte 311 : 3,000 XOF ✅
```

---

## 🚀 Avantages de la Configuration OHADA

✅ **Conformité légale** : Respect du référentiel OHADA  
✅ **Écritures automatiques** : Gain de temps comptable  
✅ **Traçabilité** : Suivi précis des mouvements de stock  
✅ **Valorisation temps réel** : Valeur instantanée du stock  
✅ **Rapports financiers** : États financiers automatiques  

---

## 📚 Références

- **OHADA** : Acte uniforme relatif au droit comptable
- **Plan Comptable OHADA** : Classes 1 à 9
- **Odoo Documentation** : Stock Valuation

---

## 💡 Support

Pour toute question sur la configuration comptable :
- 📧 Email : support@sorawel.com
- 🌐 Web : https://www.sorawel.com

---

**Version du module :** 18.0.7.4.0  
**Date de mise à jour :** 2025-10-30
