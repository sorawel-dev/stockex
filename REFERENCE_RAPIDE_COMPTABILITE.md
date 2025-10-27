# 📋 Référence Rapide - Gestion Comptable Stockex

## ⚡ Démarrage Rapide (5 Minutes)

### 1. Installer stock_account
```bash
odoo-bin -d your_database -i stock_account
```

### 2. Configurer une Catégorie
```
Menu → Inventaire → Configuration → Catégories de Produits
→ Matières Premières
   ├── Méthode : FIFO
   ├── Valorisation : Temps Réel
   ├── Compte Stock : 31000
   ├── Compte Entrée : 60300
   └── Compte Sortie : 71300
```

### 3. Créer Stock Initial
```
Menu → Inventaire → Configuration → Stock Initial
→ Import fichier Excel ou saisie manuelle
→ Valider
```

### 4. Activer Écritures sur Inventaire
```
Inventaire → ☑️ Générer Écritures Comptables → Valider
```

---

## 📖 Commandes Principales

### Assistant Stock Initial
```
Menu: Inventaire → Configuration → Stock Initial

Format Excel:
CODE PRODUIT | PRODUIT | QUANTITE | PRIX UNITAIRE

Résultat:
✅ Inventaire créé
✅ Stock enregistré
✅ Écritures générées
```

### Inventaire avec Comptabilité
```
1. Créer inventaire
2. ☑️ Générer Écritures Comptables
3. Ajouter lignes
4. Valider
→ Écritures créées automatiquement !
```

### Configuration Catégories
```
Menu: Inventaire → Configuration → Catégories de Produits

Par catégorie:
- Méthode de Coût (Standard/FIFO/AVCO)
- Valorisation (Manuel/Temps Réel)
- 3 Comptes comptables
```

---

## 🔍 Vérifications Rapides

### Vérifier si stock_account est installé
```sql
SELECT name, state 
FROM ir_module_module 
WHERE name = 'stock_account';
-- Résultat attendu: state = 'installed'
```

### Vérifier Comptes Comptables
```
Menu → Comptabilité → Configuration → Plan Comptable
Rechercher: 31000, 60300, 71300
```

### Vérifier Stock Existant
```sql
SELECT COUNT(*) 
FROM stock_quant 
WHERE quantity > 0 AND location_usage = 'internal';
-- Si > 0 : NE PAS utiliser Assistant Stock Initial
```

---

## 🎯 Cas d'Usage

| Situation | Solution |
|-----------|----------|
| **Nouvelle installation** | Assistant Stock Initial |
| **Migration depuis autre système** | Assistant Stock Initial (par lots) |
| **Inventaire mensuel** | Inventaire normal + comptabilité activée |
| **Correction de stock** | Inventaire normal + comptabilité activée |
| **Stock existant** | NE PAS utiliser Assistant Stock Initial |

---

## ⚠️ Erreurs Fréquentes

### "Module stock_account not found"
```bash
Solution: odoo-bin -d DB -i stock_account
```

### "Comptes comptables non configurés"
```
Solution: Configurer les 3 comptes sur la catégorie
Menu → Inventaire → Configuration → Catégories
```

### "Stock déjà existant"
```
Solution: Ne pas utiliser Assistant Stock Initial
→ Utiliser inventaire normal
```

### "Aucune écriture générée"
```
Vérifier:
☑️ "Générer Écritures Comptables" coché ?
☑️ stock_account installé ?
☑️ Comptes configurés sur catégorie ?
```

---

## 📊 Écritures Comptables Générées

### Surplus (+)
```
Qté théorique: 100
Qté réelle:    120
Écart:         +20 × 50 FCFA = +1,000 FCFA

┌────────────────┬───────┬────────┐
│ Compte         │ Débit │ Crédit │
├────────────────┼───────┼────────┤
│ 31000 Stock    │ 1,000 │        │
│ 60300 Variation│       │  1,000 │
└────────────────┴───────┴────────┘
```

### Manquant (-)
```
Qté théorique: 100
Qté réelle:    80
Écart:         -20 × 50 FCFA = -1,000 FCFA

┌────────────────┬───────┬────────┐
│ Compte         │ Débit │ Crédit │
├────────────────┼───────┼────────┤
│ 60300 Variation│ 1,000 │        │
│ 31000 Stock    │       │  1,000 │
└────────────────┴───────┴────────┘
```

---

## 🔢 Plan Comptable Standard

```
31000 - Stocks de marchandises (Actif)
31100 - Stocks de matières premières (Actif)
31200 - Stocks de produits finis (Actif)

60300 - Variation de stocks (Charge)
60310 - Variation stocks matières premières
60320 - Variation stocks produits finis

71300 - Production stockée (Produit)
71310 - Production stockée MP
71320 - Production stockée PF
```

---

## 🎓 Bonnes Pratiques

### 1. Configuration Initiale
```
✅ Installer stock_account AVANT premier inventaire
✅ Configurer TOUTES les catégories
✅ Tester sur environnement de test
```

### 2. Stock Initial
```
✅ Préparer fichier Excel complet
✅ Vérifier prix unitaires
✅ Sauvegarder avant import
```

### 3. Inventaires Mensuels
```
✅ Toujours activer comptabilité
✅ Vérifier écritures générées
✅ Pointer avec comptabilité générale
```

### 4. Catégories
```
Matières Premières → FIFO + Temps Réel
Produits Finis     → Standard + Temps Réel
Fournitures        → AVCO + Manuel
Marchandises       → FIFO + Temps Réel
```

---

## 📞 Support Rapide

**Email**: contact@sorawel.com  
**Documentation Complète**: [GESTION_COMPTABLE.md](GESTION_COMPTABLE.md)  
**Version**: 18.0.3.0.0

---

**Développé par Sorawel - www.sorawel.com**
