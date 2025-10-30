# 📁 Catégories de Produits dans Configuration

## ✅ Accès aux Catégories de Produits

### Navigation

Pour accéder à la configuration des catégories de produits :

```
Stock → Configuration → Catégories de Produits
```

**Chemin complet :**
1. Ouvrir le menu **Stock** (icône 📦)
2. Aller dans **Configuration**
3. Cliquer sur **Catégories de Produits**

---

## 🎯 Objectif

Centraliser la gestion des catégories de produits avec leurs paramètres de coût et de valorisation depuis le menu Configuration du module Stock.

---

## 📋 Fonctionnalités

### Vue Liste

Affiche toutes les catégories de produits avec :
- Nom de la catégorie
- Catégorie parente (si hiérarchie)
- Méthode de coût
- Type de valorisation
- Comptes comptables (si configurés)

### Vue Formulaire

Permet de configurer pour chaque catégorie :

#### 1. **Informations de Base**
- Nom de la catégorie
- Catégorie parente (pour hiérarchie)

#### 2. **Méthode de Coût**

Choisir parmi :
- **Standard** : Prix fixe défini sur le produit
- **FIFO** (Premier Entré, Premier Sorti) : Coût basé sur l'ordre d'entrée
- **AVCO** (Average Cost) : Coût moyen pondéré

#### 3. **Valorisation du Stock**

Deux options :
- **Manuel/Périodique** : Mise à jour manuelle via inventaires
- **Automatique (Temps Réel)** : Écritures comptables automatiques à chaque mouvement

#### 4. **Comptes Comptables** (si Valorisation Temps Réel)

- Compte de Stock (Actif)
- Compte d'Entrée de Stock
- Compte de Sortie de Stock

---

## 💡 Exemples de Configuration par Type

### Matières Premières
```
Nom : Matières Premières
Méthode : Standard ou FIFO
Valorisation : Temps Réel
Comptes : À configurer selon plan comptable
```

### Produits Finis
```
Nom : Produits Finis
Méthode : FIFO ou Standard
Valorisation : Temps Réel
Comptes : À configurer selon plan comptable
```

### Fournitures
```
Nom : Fournitures
Méthode : Standard ou AVCO
Valorisation : Manuel/Périodique
Comptes : Non requis (valorisation manuelle)
```

### Marchandises
```
Nom : Marchandises
Méthode : FIFO
Valorisation : Temps Réel
Comptes : À configurer selon plan comptable
```

---

## 🔧 Configuration Technique

### Menu Odoo

**Fichier :** `/home/one/apps/stockex/views/product_category_config_views.xml`

```xml
<menuitem 
    id="menu_configure_product_categories"
    name="Catégories de Produits"
    parent="stock.menu_stock_config_settings"
    action="action_configure_product_categories"
    sequence="10"
    groups="stock.group_stock_manager"/>
```

**Caractéristiques :**
- Parent : `stock.menu_stock_config_settings` (Menu Configuration de Stock)
- Action : Ouvre la liste des catégories de produits
- Groupes : Accessible aux gestionnaires de stock (`stock.group_stock_manager`)
- Séquence : 10 (apparaît en premier dans la section Configuration)

### Action Window

```xml
<record id="action_configure_product_categories" model="ir.actions.act_window">
    <field name="name">Catégories de Produits</field>
    <field name="res_model">product.category</field>
    <field name="view_mode">list,form</field>
    ...
</record>
```

---

## 📊 Utilisation

### Créer une Nouvelle Catégorie

1. Aller dans **Stock → Configuration → Catégories de Produits**
2. Cliquer sur **Créer**
3. Remplir les champs :
   - Nom de la catégorie
   - Catégorie parente (optionnel)
   - Méthode de coût
   - Type de valorisation
4. Si "Temps Réel" : Configurer les comptes comptables
5. Enregistrer

### Modifier une Catégorie Existante

1. Aller dans **Stock → Configuration → Catégories de Produits**
2. Sélectionner la catégorie à modifier
3. Modifier les paramètres souhaités
4. Enregistrer

**⚠️ Attention :** La modification d'une catégorie affectera tous les produits qui l'utilisent.

### Hiérarchie de Catégories

Vous pouvez créer une hiérarchie en définissant une **Catégorie Parente** :

```
Produits (Parent)
  ├── Matières Premières
  ├── Produits Finis
  └── Fournitures
```

---

## 🔐 Permissions

### Groupes Requis

Pour accéder au menu, l'utilisateur doit appartenir au groupe :
- **Gestionnaire de Stock** (`stock.group_stock_manager`)

### Vérification des Permissions

Pour vérifier si un utilisateur a accès :
1. Aller dans **Paramètres → Utilisateurs**
2. Ouvrir la fiche utilisateur
3. Vérifier l'onglet **Droits d'accès**
4. S'assurer que **Stock / Gestionnaire** est coché

---

## 📚 Comptes Comptables pour Valorisation Temps Réel

### Compte de Stock (Actif)

**Exemple :** `31000 - Stocks de marchandises`
- Enregistre la valeur totale du stock
- Type : Actif circulant

### Compte d'Entrée de Stock

**Exemple :** `60300 - Variation de stock`
- Utilisé lors des réceptions/achats
- Débité lors de l'entrée en stock

### Compte de Sortie de Stock

**Exemple :** `71300 - Production stockée`
- Utilisé lors des livraisons/ventes
- Crédité lors de la sortie du stock

**Note :** Ces comptes doivent exister dans votre plan comptable avant configuration.

---

## ⚙️ Catégories Préconfigurées

Le module stockex crée automatiquement 4 catégories de base :

### 1. Matières Premières
```
Méthode : Standard
Valorisation : Manuel/Périodique
```

### 2. Produits Finis
```
Méthode : FIFO
Valorisation : Manuel/Périodique
```

### 3. Fournitures
```
Méthode : Average (AVCO)
Valorisation : Manuel/Périodique
```

### 4. Marchandises
```
Méthode : FIFO
Valorisation : Manuel/Périodique
```

**Fichier :** `/home/one/apps/stockex/data/product_categories_config.xml`

**Note :** Ces catégories sont créées avec `noupdate="1"`, ce qui signifie qu'elles ne seront pas écrasées lors des mises à jour du module.

---

## 🔄 Workflow Recommandé

### Étape 1 : Configurer le Plan Comptable

Avant d'activer la valorisation en temps réel :
1. Créer les comptes comptables nécessaires
2. Vérifier qu'ils sont de type approprié (Actif, Charge, etc.)

### Étape 2 : Configurer les Catégories

1. Accéder à **Stock → Configuration → Catégories de Produits**
2. Pour chaque catégorie :
   - Définir la méthode de coût selon le type de produit
   - Choisir le type de valorisation
   - Si temps réel : Associer les comptes comptables

### Étape 3 : Assigner les Produits

1. Aller dans **Stock → Produits**
2. Pour chaque produit, sélectionner la catégorie appropriée
3. Les paramètres de coût et valorisation seront hérités de la catégorie

### Étape 4 : Tester

1. Créer un mouvement de stock test
2. Vérifier les écritures comptables (si valorisation temps réel)
3. Ajuster si nécessaire

---

## ❓ Questions Fréquentes

### Q1 : Puis-je changer la méthode de coût après avoir créé des produits ?

**R :** Oui, mais cela affectera tous les produits de cette catégorie. Il est recommandé de le faire avant la mise en production.

### Q2 : Quelle est la différence entre FIFO et AVCO ?

**R :**
- **FIFO** : Le coût du produit vendu est celui du lot le plus ancien
- **AVCO** : Le coût est la moyenne pondérée de tous les lots en stock

### Q3 : Dois-je obligatoirement configurer les comptes comptables ?

**R :** Uniquement si vous utilisez la valorisation en **Temps Réel**. Pour la valorisation **Manuel/Périodique**, les comptes ne sont pas requis.

### Q4 : Comment savoir quelle méthode choisir ?

**R :** Cela dépend de votre secteur d'activité :
- **FIFO** : Produits périssables, mode, électronique
- **Standard** : Production stable, coûts prévisibles
- **AVCO** : Matières premières, produits interchangeables

### Q5 : Les catégories existantes seront-elles modifiées ?

**R :** Non, les catégories préconfigurées par stockex sont créées uniquement si elles n'existent pas déjà (grâce à `noupdate="1"`).

---

## 🔍 Débogage

### Le menu n'apparaît pas

**Vérifications :**
1. L'utilisateur a-t-il le groupe "Gestionnaire de Stock" ?
2. Le module stockex est-il bien installé et mis à jour ?
3. Vider le cache du navigateur (Ctrl+F5)

**Commande de vérification :**
```bash
odoo -d eneo --addons-path=/home/one/apps --stop-after-init -u stockex
```

### Erreur lors de la modification d'une catégorie

**Si erreur sur les comptes :**
- Vérifier que les comptes existent dans le plan comptable
- S'assurer que les comptes sont du bon type

**Si erreur de valorisation temps réel :**
- Message : "Les comptes de stock doivent être définis"
- Solution : Définir les 3 comptes comptables requis

---

## 📁 Fichiers Associés

```
stockex/
├── views/
│   └── product_category_config_views.xml  # Vue et menu
├── data/
│   └── product_categories_config.xml      # Catégories préconfigurées
└── docs/
    └── CATEGORIES_PRODUITS_CONFIGURATION.md  # Cette documentation
```

---

## 🚀 Version

**Module :** Stockex v18.0.3.1.2  
**Fonctionnalité ajoutée :** Version 18.0.3.1.2  
**Date :** 25 octobre 2025

---

## 📞 Support

Pour toute question ou problème :
- **Email** : contact@sorawel.com
- **Site** : www.sorawel.com

---

**Documentation créée le 25 octobre 2025**  
*Module Stockex - Gestion d'Inventaire - Odoo 18*
