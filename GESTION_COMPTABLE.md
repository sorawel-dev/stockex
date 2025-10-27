# 💰 Guide de Gestion Comptable - Stockex v18.0.3.0.0

## 🎯 Vue d'Ensemble

Cette version ajoute **3 fonctionnalités comptables majeures** :

1. ✅ **Génération automatique d'écritures comptables** lors des inventaires
2. ✅ **Assistant de stock initial** pour bases de données vides
3. ✅ **Configuration guidée** des catégories de produits

---

## 📊 1. Génération Automatique d'Écritures Comptables

### Activation

**Prérequis** :
```bash
# Installer le module stock_account (si pas déjà fait)
odoo-bin -d your_database -i stock_account
```

### Configuration par Inventaire

1. **Créer/Ouvrir un inventaire**
   ```
   Menu → Inventaires → Inventaires de Stock → Créer
   ```

2. **Activer la comptabilité**
   ```
   ☑️ Cocher "Générer Écritures Comptables"
   ```

3. **Valider l'inventaire**
   ```
   Les écritures comptables seront générées automatiquement !
   ```

### Fonctionnement

#### Pour les Surplus (Écarts Positifs)
```
Exemple : Quantité théorique = 100, Quantité réelle = 120
Écart = +20 unités × 50 FCFA = +1,000 FCFA

Écriture Comptable :
┌─────────────────────────────┬────────┬────────┐
│ Compte                      │ Débit  │ Crédit │
├─────────────────────────────┼────────┼────────┤
│ 31000 - Stock               │ 1,000  │        │
│ 60300 - Variation de stock  │        │ 1,000  │
└─────────────────────────────┴────────┴────────┘
```

#### Pour les Manquants (Écarts Négatifs)
```
Exemple : Quantité théorique = 100, Quantité réelle = 80
Écart = -20 unités × 50 FCFA = -1,000 FCFA

Écriture Comptable :
┌─────────────────────────────┬────────┬────────┐
│ Compte                      │ Débit  │ Crédit │
├─────────────────────────────┼────────┼────────┤
│ 60300 - Variation de stock  │ 1,000  │        │
│ 31000 - Stock               │        │ 1,000  │
└─────────────────────────────┴────────┴────────┘
```

### Consultation des Écritures

**Après validation de l'inventaire** :
```
Inventaire → Onglet "Écritures Comptables"
→ Liste des écritures générées
→ Lien vers chaque écriture dans la comptabilité
```

### Configuration des Comptes

**Par Catégorie de Produit** :
```
Menu → Inventaire → Configuration → Catégories de Produits
→ Sélectionner une catégorie
→ Onglet "Valorisation du Stock"

Comptes requis :
├── Compte de Stock (Actif)        : Ex: 31000
├── Compte Entrée de Stock         : Ex: 60300
└── Compte Sortie de Stock         : Ex: 71300
```

---

## 🆕 2. Assistant de Stock Initial

### Quand Utiliser ?

✅ **OUI** - Pour :
- Nouvelle installation Odoo
- Migration depuis autre système
- Base de données vide (stock = 0)
- Premier enregistrement de stock

❌ **NON** - Pour :
- Base avec stock existant
- Mise à jour de stock
- Corrections d'inventaire

### Procédure Complète

#### Étape 1 : Préparer le Fichier Excel (Optionnel)

**Format requis** :
```
┌──────────────┬──────────┬──────────┬────────────────┐
│ CODE PRODUIT │ PRODUIT  │ QUANTITE │ PRIX UNITAIRE  │
├──────────────┼──────────┼──────────┼────────────────┤
│ PROD001      │ Bureau   │ 50       │ 150.00         │
│ PROD002      │ Chaise   │ 200      │ 45.00          │
│ PROD003      │ Table    │ 75       │ 120.00         │
└──────────────┴──────────┴──────────┴────────────────┘
```

**Télécharger le modèle** : [template_stock_initial.xlsx]

#### Étape 2 : Lancer l'Assistant

```
Menu → Inventaire → Configuration → Stock Initial
```

#### Étape 3 : Remplir le Formulaire

```
┌─────────────────────────────────────────────────┐
│ 📝 Assistant Stock Initial                      │
├─────────────────────────────────────────────────┤
│ Nom de l'Inventaire Initial : Stock Initial     │
│ Date du Stock Initial       : 01/01/2025        │
│ Emplacement Principal       : [Sélectionner]    │
│ Société                     : Ma Société        │
│                                                 │
│ ☑️ Créer les Produits Manquants                │
│                                                 │
│ 📎 Fichier d'Import (Excel) : [Parcourir...]   │
│                                                 │
│ ⚠️ ATTENTION : Pour bases VIDES uniquement     │
│                                                 │
│ [Créer Stock Initial] [Annuler]                │
└─────────────────────────────────────────────────┘
```

#### Étape 4 : Résultat

L'assistant crée automatiquement :
- ✅ Un inventaire nommé "Stock Initial"
- ✅ Toutes les lignes avec quantité théorique = 0
- ✅ Quantités réelles = vos données Excel
- ✅ Produits créés si manquants

#### Étape 5 : Valider l'Inventaire

```
1. Vérifier les lignes créées
2. Ajuster si nécessaire
3. Cliquer "Démarrer"
4. Cliquer "Valider"
```

**Résultat final** :
- ✅ Stock enregistré dans Odoo
- ✅ Écritures comptables générées (si activé)
- ✅ Base prête pour utilisation

### Saisie Manuelle (Sans Excel)

Si pas de fichier Excel :

1. **Créer l'inventaire initial** via l'assistant (sans fichier)
2. **Ajouter les lignes** manuellement :
   ```
   Pour chaque produit :
   - Cliquer "Ajouter une ligne"
   - Sélectionner le produit
   - Quantité réelle = quantité initiale
   - Prix unitaire = coût standard
   ```
3. **Valider** l'inventaire

---

## ⚙️ 3. Configuration Guidée des Catégories

### Pourquoi Configurer les Catégories ?

Les catégories déterminent :
- 💰 **Méthode de valorisation** (Standard, FIFO, AVCO)
- 📊 **Type de comptabilisation** (Manuel ou Temps Réel)
- 📚 **Comptes comptables** utilisés

### Guide de Configuration

#### Étape 1 : Accéder aux Catégories

```
Menu → Inventaire → Configuration → Catégories de Produits
```

#### Étape 2 : Créer/Modifier une Catégorie

**Exemple : Matières Premières**

```
┌─────────────────────────────────────────────────┐
│ Catégorie : Matières Premières                  │
├─────────────────────────────────────────────────┤
│ Onglet "Valorisation du Stock" :                │
│                                                 │
│ Méthode de Coût           : ⦿ FIFO             │
│                             ○ Standard          │
│                             ○ Coût Moyen (AVCO) │
│                                                 │
│ Valorisation des Stocks   : ⦿ Temps Réel       │
│                             ○ Manuel/Périodique │
│                                                 │
│ Compte de Stock           : 31100 - MP Stock    │
│ Compte Entrée de Stock    : 60310 - Var. MP     │
│ Compte Sortie de Stock    : 71310 - Prod. MP    │
└─────────────────────────────────────────────────┘
```

#### Étape 3 : Utiliser le Guide Intégré

L'onglet **"Guide de Configuration"** contient :

✅ **Explications des méthodes de coût**
```
Standard : Prix fixe défini manuellement
FIFO     : Premier Entré, Premier Sorti
AVCO     : Coût Moyen Pondéré
```

✅ **Types de valorisation**
```
Manuel       : Mise à jour via inventaires uniquement
Temps Réel   : Écritures automatiques à chaque mouvement
```

✅ **Exemples par type de produit**
```
┌────────────────────┬─────────────┬──────────────┐
│ Type               │ Méthode     │ Valorisation │
├────────────────────┼─────────────┼──────────────┤
│ Matières Premières │ FIFO        │ Temps Réel   │
│ Produits Finis     │ Standard    │ Temps Réel   │
│ Fournitures        │ AVCO        │ Manuel       │
│ Marchandises       │ FIFO        │ Temps Réel   │
└────────────────────┴─────────────┴──────────────┘
```

### Catégories Préconfigurées

Le module installe **4 catégories par défaut** :

1. **Matières Premières**
   - Méthode : Standard
   - Valorisation : Manuel

2. **Produits Finis**
   - Méthode : FIFO
   - Valorisation : Temps Réel

3. **Fournitures**
   - Méthode : AVCO
   - Valorisation : Manuel

4. **Marchandises**
   - Méthode : FIFO
   - Valorisation : Temps Réel

**Note** : Vous devez configurer les comptes comptables manuellement.

---

## 🔧 Configuration Complète - Checklist

### Pour Nouvelle Installation

- [ ] **1. Installer stock_account**
  ```bash
  odoo-bin -d your_database -i stock_account
  ```

- [ ] **2. Configurer les Catégories de Produits**
  ```
  Menu → Inventaire → Configuration → Catégories de Produits
  → Configurer méthode de coût + comptes pour chaque catégorie
  ```

- [ ] **3. Vérifier le Plan Comptable**
  ```
  Comptes requis :
  - 31000 : Stocks
  - 60300 : Variation de stock (entrée)
  - 71300 : Production stockée (sortie)
  ```

- [ ] **4. Créer le Stock Initial**
  ```
  Menu → Inventaire → Configuration → Stock Initial
  → Importer le fichier Excel ou saisir manuellement
  ```

- [ ] **5. Activer la Comptabilité sur Inventaire**
  ```
  Lors de la validation, cocher "Générer Écritures Comptables"
  ```

- [ ] **6. Valider et Vérifier**
  ```
  Vérifier que les écritures comptables sont correctes
  ```

---

## 📊 Exemples Pratiques

### Cas 1 : Nouvelle Entreprise avec Stock Initial

**Situation** : Entreprise qui démarre, 150 produits à enregistrer

**Solution** :
1. Préparer fichier Excel avec 150 produits
2. Lancer assistant Stock Initial
3. Importer le fichier
4. Vérifier les lignes
5. Valider l'inventaire
6. Les écritures comptables sont générées automatiquement

**Temps estimé** : 30 minutes

---

### Cas 2 : Migration depuis Autre Système

**Situation** : Migration depuis ancien système, 5,000 produits

**Solution** :
1. Exporter les stocks de l'ancien système en Excel
2. Adapter au format Stockex (CODE PRODUIT, QUANTITE, PRIX)
3. Diviser en lots de 1,000 produits
4. Lancer assistant 5 fois (1 par lot)
5. Valider les 5 inventaires

**Temps estimé** : 2-3 heures

---

### Cas 3 : Inventaire Mensuel avec Écritures

**Situation** : Inventaire mensuel avec génération comptable

**Solution** :
1. Créer inventaire normal
2. Cocher "Générer Écritures Comptables"
3. Compter les produits
4. Valider
5. Les écritures d'écarts sont automatiquement créées

**Avantage** : Pas de saisie comptable manuelle !

---

## ⚠️ Points d'Attention

### 1. Stock_Account Requis

Pour les écritures comptables :
```
✅ Module stock_account DOIT être installé
✅ Comptes comptables DOIVENT être configurés
❌ Sans cela → Erreur à la validation
```

### 2. Assistant Stock Initial = BD Vide Uniquement

```
✅ OK pour : Base nouvelle, aucun mouvement de stock
❌ ERREUR si : Stock existant déjà enregistré
→ L'assistant bloque avec message d'avertissement
```

### 3. Configuration Catégories Obligatoire

```
Sans configuration :
❌ Pas d'écritures comptables
❌ Erreur à la validation si comptabilité activée
```

### 4. Vérification Plan Comptable

```
Avant activation :
✅ Vérifier que les comptes existent
✅ Vérifier les numéros de compte
✅ Tester sur environnement de test
```

---

## 📞 Support

**Email** : contact@sorawel.com  
**Site** : www.sorawel.com  
**Version** : 18.0.3.0.0

---

**Développé avec ❤️ par Sorawel**
