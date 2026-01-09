# 📚 Guide Utilisateur - Gestion d'Inventaire

**Version 18.0 | Module Stockinv**

---

## 📋 Table des Matières

1. [Vue d'Ensemble](#vue-densemble)
2. [Accès au Module](#accès-au-module)
3. [Tableau de Bord](#tableau-de-bord)
4. [Créer un Inventaire](#créer-un-inventaire)
5. [Importer des Données](#importer-des-données)
6. [Gérer les Inventaires](#gérer-les-inventaires)
7. [💰 Valorisation du Stock](#-valorisation-du-stock) **(NOUVEAU)**
8. [Rapports et Analyses](#rapports-et-analyses)
9. [Configuration](#configuration)

---

## 🎯 Vue d'Ensemble

### Qu'est-ce que ce module ?

Le module **Gestion d'Inventaire** vous permet de :
- ✅ Créer et gérer des inventaires de stock
- ✅ Importer des données depuis Excel, CSV ou Kobo Collect
- ✅ Comparer les quantités théoriques et réelles
- ✅ Calculer automatiquement les écarts
- ✅ **Valoriser les stocks avec 4 méthodes (Standard, AVCO, FIFO, Économique)**
- ✅ Suivre la valorisation des stocks en temps réel
- ✅ Générer des rapports et analyses

---

## 🚀 Accès au Module

### Depuis le Menu Principal

```
┌─────────────────────────────────────────┐
│ 📊 Gestion d'Inventaire                 │  ← Cliquer ici
│                                         │
│ 📅 Calendrier                           │
│ 💬 Conversations                        │
│ ...                                     │
└─────────────────────────────────────────┘
```

**Icône du module** : Carton violet avec grille (symbolisant l'inventaire)

**Position** : Menu principal (barre latérale gauche)

---

## 📊 Tableau de Bord

### Page d'Accueil

Dès l'ouverture, vous accédez à la **Vue d'Ensemble** :

```
┌──────────────────────────────────────────────────────────────┐
│ 📊 VUE D'ENSEMBLE - GESTION D'INVENTAIRE                     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────────────┐   │
│  │  📋 5   │  │ 📦 2,277│  │📊 6,308k│  │💰 392,108    │   │
│  │Inventair│  │ Produits│  │ Quantité│  │ FCFA         │   │
│  │  validés│  │         │  │         │  │              │   │
│  └─────────┘  └─────────┘  └─────────┘  └──────────────┘   │
│                                                              │
│  🚀 ACTIONS RAPIDES                                          │
│  [📦 Nouvel Inventaire] [📋 Voir Inventaires] [📈 Analyse]  │
│                                                              │
│  📊 VALEUR DES ÉCARTS D'INVENTAIRE                           │
│  ┌──────────────┬──────────────────┬─────────────────────┐  │
│  │ Écarts Totaux│ ➕ Écarts Positifs│ ➖ Écarts Négatifs │  │
│  │  12,500 FCFA │   15,000 FCFA    │   -2,500 FCFA      │  │
│  └──────────────┴──────────────────┴─────────────────────┘  │
│                                                              │
│  🔄 Dernier      📊 Top 5         🏭 Top 5                   │
│  Inventaire      Catégories       Entrepôts                 │
│  ───────────     ──────────       ─────────                 │
│  INV/2025/005    FRIGO  125k      Abidjan  245k             │
│  20/10/2025      CLIMAV  98k      Koumassi  89k             │
│  2,277 produits  BUREAU  67k      Yopougon  57k             │
│  392,108 FCFA    ...              ...                       │
└──────────────────────────────────────────────────────────────┘
```

### Cartes KPIs

**1. Inventaires Validés** (Bleu)
- Nombre total d'inventaires terminés

**2. Produits** (Vert)
- Nombre de références uniques

**3. Quantité** (Cyan)
- Somme totale des quantités

**4. Valeur Totale** (Jaune)
- Valeur globale en FCFA

### Section Écarts

Visualisation des différences entre stock théorique et réel :
- **Écarts Totaux** : Impact global
- **Positifs (Vert)** : Surplus trouvés
- **Négatifs (Rouge)** : Produits manquants

---

## 📦 Créer un Inventaire

### Méthode 1 : Depuis le Dashboard

```
Vue d'Ensemble → [📦 Nouvel Inventaire]
```

### Méthode 2 : Depuis le Menu

```
Gestion d'Inventaire → Import → Nouvel Inventaire
```

### Assistant de Choix de Méthode

```
┌────────────────────────────────────────────────┐
│ Choisir une Méthode d'Import                   │
├────────────────────────────────────────────────┤
│                                                │
│  ⚪ Import CSV                                 │
│     Fichier texte avec colonnes séparées       │
│                                                │
│  ⚪ Import Excel                               │
│     Fichier .xlsx avec mise en forme           │
│                                                │
│  ⚪ Import Kobo Collect                        │
│     Données collectées sur mobile              │
│                                                │
│           [Annuler]  [Suivant ➜]               │
└────────────────────────────────────────────────┘
```

**Sélectionnez la méthode** puis cliquez **Suivant**.

---

## 📥 Importer des Données

### Import Excel (Recommandé)

#### Étape 1 : Préparer le Fichier

**Format attendu :**

```
┌─────────────┬────────────┬────────────┬────────┬──────┐
│ CODE ENTREPOT│ ENTREPOT  │ CODE ART   │ DESIGN │ QTE  │
├─────────────┼────────────┼────────────┼────────┼──────┤
│ WH-ABJ-001  │ Abidjan    │ FRG-001    │ Frigo  │ 50   │
│ WH-KOU-WSE  │ Koumassi   │ CLI-002    │ Clim   │ 30   │
│ WH-YOP-001  │ Yopougon   │ BUR-003    │ Bureau │ 18   │
└─────────────┴────────────┴────────────┴────────┴──────┘
```

**Colonnes obligatoires :**
- `CODE ENTREPOT` ou `ENTREPOT` : Identifiant de l'emplacement
- `CODE ART` ou `CODE ARTICLE` : Référence produit
- `QTE` ou `QUANTITE` : Quantité comptée

#### Étape 2 : Charger le Fichier

```
┌────────────────────────────────────────────────┐
│ Import Excel                                    │
├────────────────────────────────────────────────┤
│                                                │
│  Fichier Excel :  [Parcourir...]               │
│                                                │
│  📄 inventaire_octobre_2025.xlsx               │
│                                                │
│  ✅ Créer entrepôts manquants                  │
│  ✅ Créer produits manquants                   │
│  ⚠️  Ignorer lignes invalides                  │
│                                                │
│           [Annuler]  [Importer]                │
└────────────────────────────────────────────────┘
```

**Options :**
- **Créer entrepôts** : Ajoute automatiquement les nouveaux emplacements
- **Créer produits** : Ajoute les nouveaux produits
- **Ignorer invalides** : Continue malgré les erreurs

#### Étape 3 : Vérifier l'Import

```
┌────────────────────────────────────────────────┐
│ ✅ Import Réussi \!                             │
├────────────────────────────────────────────────┤
│                                                │
│  Inventaire créé : INV/2025/006                │
│                                                │
│  📊 Statistiques :                             │
│  • 2,277 lignes importées                      │
│  • 3 entrepôts                                 │
│  • 2,277 produits                              │
│  • Valeur totale : 392,108 FCFA                │
│                                                │
│  [Voir l'Inventaire]  [Fermer]                 │
└────────────────────────────────────────────────┘
```

### Import CSV

Même procédure que Excel, mais avec fichier `.csv`

**Format CSV :**
```
CODE ENTREPOT,ENTREPOT,CODE ART,DESIGN,QTE
WH-ABJ-001,Abidjan,FRG-001,Frigo LG,50
WH-KOU-WSE,Koumassi,CLI-002,Clim Samsung,30
```

**Séparateur** : Virgule (`,`) ou point-virgule (`;`)

### Import Kobo Collect

Pour la collecte terrain sur mobile/tablette.

**Configuration requise :**
1. Projet Kobo créé
2. Formulaire configuré
3. API Token obtenu

**Voir :** [Guide Acquisition Données](GUIDE_ACQUISITION_DONNEES.md)

---

## 📋 Gérer les Inventaires

### Liste des Inventaires

```
Gestion d'Inventaire → Opérations → Inventaires de Stock
```

**Affichage :**

```
┌──────────────────────────────────────────────────────────────┐
│ Inventaires de Stock                                         │
├─────────────┬────────────┬──────────┬────────┬──────────────┤
│ Référence   │ Date       │ Produits │ Valeur │ État         │
├─────────────┼────────────┼──────────┼────────┼──────────────┤
│ INV/2025/006│ 20/10/2025 │ 2,277    │ 392k   │ 🟢 Validé    │
│ INV/2025/005│ 15/10/2025 │ 2,180    │ 385k   │ 🟢 Validé    │
│ INV/2025/004│ 10/10/2025 │ 2,100    │ 378k   │ 🟡 En cours  │
│ INV/2025/003│ 05/10/2025 │ 2,050    │ 370k   │ ⚪ Brouillon │
└─────────────┴────────────┴──────────┴────────┴──────────────┘
```

**États possibles :**
- 🟢 **Validé** : Inventaire terminé et approuvé
- 🟡 **En cours** : En cours de comptage
- ⚪ **Brouillon** : Créé mais pas commencé

### Détail d'un Inventaire

Cliquer sur un inventaire pour voir le détail :

```
┌──────────────────────────────────────────────────────────────┐
│ INV/2025/006 - Inventaire du 20/10/2025           🟢 Validé  │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  📅 Date : 20/10/2025          👤 Responsable : Admin        │
│  📦 Produits : 2,277           💰 Valeur : 392,108 FCFA      │
│  📊 Écarts : +12,500 FCFA      🏢 Société : Sorawel          │
│                                                              │
│  ━━━ Lignes d'Inventaire ━━━                                │
│                                                              │
│  [+ Ajouter une ligne]                         🔍 Rechercher │
│                                                              │
│ ┌────────────┬─────────────┬─────┬──────┬──────┬──────────┐ │
│ │ Produit    │ Emplacement │ Théo│ Réel │ Écart│ Valeur   │ │
│ ├────────────┼─────────────┼─────┼──────┼──────┼──────────┤ │
│ │ Frigo LG   │ Abidjan/... │  45 │  50  │  +5  │ +2,500   │ │
│ │ Clim Sam.. │ Koumassi/.. │  28 │  30  │  +2  │ +1,600   │ │
│ │ Bureau Del │ Yopougon/.. │  20 │  18  │  -2  │ -2,000   │ │
│ │ ...        │ ...         │ ... │  ... │  ... │  ...     │ │
│ └────────────┴─────────────┴─────┴──────┴──────┴──────────┘ │
│                                                              │
│  [🔄 Recalculer] [📊 Analyser] [💾 Valider l'Inventaire]    │
└──────────────────────────────────────────────────────────────┘
```

**Colonnes importantes :**
- **Théo** : Quantité théorique (dans le système)
- **Réel** : Quantité réelle comptée
- **Écart** : Différence (Réel - Théo)
- **Valeur** : Valeur de l'écart (Écart × Prix)

**Codes couleur :**
- 🟢 Vert : Écart positif (surplus)
- 🔴 Rouge : Écart négatif (manquant)
- ⚪ Blanc : Pas d'écart

### Workflow d'un Inventaire

```
1. Brouillon
   ↓
   [Démarrer l'Inventaire]
   ↓
2. En cours
   ↓
   • Compter physiquement
   • Saisir les quantités réelles
   • Vérifier les écarts
   ↓
   [Valider l'Inventaire]
   ↓
3. Validé
   ↓
   • Stocks mis à jour
   • Inventaire figé
   • Rapport disponible
```

---

## 💰 Valorisation du Stock

### Qu'est-ce que la Valorisation ?

La **valorisation du stock** est le calcul de la valeur monétaire de vos articles en stock. Le module propose **4 méthodes de valorisation** pour s'adapter à vos besoins :

```
┌─────────────────┬───────────────────────┬────────────────────────────┐
│ Méthode         │ Base de Calcul        │ Cas d'Usage                │
├─────────────────┼───────────────────────┼────────────────────────────┤
│ 📌 Standard     │ Prix fixe manuel      │ Prix stable, peu de        │
│                 │                       │ variation                  │
├─────────────────┼───────────────────────┼────────────────────────────┤
│ ⚖️ AVCO         │ Moyenne pondérée      │ Prix fluctuants,           │
│                 │ de tous les achats    │ lissage des variations     │
├─────────────────┼───────────────────────┼────────────────────────────┤
│ 🔄 FIFO         │ Premier entré,        │ Produits périssables,      │
│                 │ premier sorti         │ rotation obligatoire       │
├─────────────────┼───────────────────────┼────────────────────────────┤
│ 💰 Économique   │ Dernier prix d'achat  │ Évaluation réaliste,       │
│                 │ réel                  │ prix variables             │
└─────────────────┴───────────────────────┴────────────────────────────┘
```

### Méthode 1 : Coût Standard 📌

**Principe** : Utilise le prix fixe défini manuellement sur chaque produit.

**Configuration** :
```
Produit → Onglet Achats → Coût : 5 000 FCFA
```

**Avantages** :
- ✅ Simple à comprendre
- ✅ Stabilité des rapports
- ✅ Aucune configuration complexe

**Inconvénients** :
- ❌ Nécessite mise à jour manuelle
- ❌ Peut devenir obsolète
- ❌ Ne reflète pas les variations

### Méthode 2 : Coût Moyen (AVCO) ⚖️

**Principe** : Calcule la moyenne pondérée de tous les achats.

**Exemple** :
```
Achat 1 : 100 unités à 1 000 FCFA = 100 000 FCFA
Achat 2 : 50 unités à 1 200 FCFA  =  60 000 FCFA
──────────────────────────────────────────────
Total   : 150 unités               = 160 000 FCFA
Coût moyen = 160 000 / 150 = 1 067 FCFA/unité
```

**Avantages** :
- ✅ Lisse les variations de prix
- ✅ Calcul automatique
- ✅ Adapté aux prix fluctuants

**Inconvénients** :
- ❌ Complexe à expliquer
- ❌ Peut masquer des tendances

### Méthode 3 : FIFO (Premier Entré, Premier Sorti) 🔄

**Principe** : Valorise d'abord les articles les plus anciens.

**Exemple** :
```
Stock :
  • 50 unités achetées à 1 000 FCFA (Janvier)
  • 30 unités achetées à 1 200 FCFA (Mars)

Sortie de 60 unités :
  • 50 unités × 1 000 FCFA = 50 000 FCFA (Janvier)
  • 10 unités × 1 200 FCFA = 12 000 FCFA (Mars)
  ─────────────────────────────────────────
  Total : 62 000 FCFA
```

**Avantages** :
- ✅ Gestion rotation obligatoire
- ✅ Adapté produits périssables
- ✅ Conforme à certaines normes

**Inconvénients** :
- ❌ Complexité de calcul
- ❌ Nécessite traçabilité stricte

### Méthode 4 : Coût Économique Réel 💰 (Recommandé)

**Principe** : Utilise le **dernier prix d'achat réel** enregistré dans Odoo.

**Comment ça marche ?**

1. **Source des données** : `stock.valuation.layer` (couches de valorisation Odoo)
2. **Récupération** : Dernier mouvement d'achat enregistré
3. **Fallback** : Si aucun achat, utilise le coût standard

**Exemple concret** :
```
Produit : Câble Électrique 10mm²

Historique des achats :
  • Janvier 2024 : 5 000 FCFA
  • Mars 2024   : 5 500 FCFA
  • Juin 2024   : 6 200 FCFA  ← Dernier achat

Coût Standard (manuel) : 5 000 FCFA (non mis à jour)

VALORISATION :
  ❌ Avec Coût Standard   : 5 000 FCFA
     → Sous-évaluation de 1 200 FCFA/unité
     
  ✅ Avec Coût Économique : 6 200 FCFA
     → Reflète la réalité du marché
```

**Avantages** :
- ✅ **Réaliste** : Reflète les prix actuels du marché
- ✅ **Automatique** : Mise à jour à chaque achat
- ✅ **Précis** : Basé sur transactions réelles
- ✅ **Simple** : Pas de calcul complexe

**Cas d'usage idéaux** :
- Prix des matériaux fluctuants (cuivre, acier, etc.)
- Secteur électrique (transformateurs, câbles)
- Import/export avec variations de change
- Inflation importante

### Configuration de la Valorisation

#### Étape 1 : Accéder aux Paramètres

```
Paramètres → Inventaire → Section StockEx
→ Bloc "💰 Règle de valorisation"
```

#### Étape 2 : Choisir la Méthode

```
┌────────────────────────────────────────────────┐
│ 💰 Règle de valorisation                       │
├────────────────────────────────────────────────┤
│                                                │
│  Méthode de valorisation :                     │
│  ⚪ 📌 Coût Standard                           │
│  ⚪ ⚖️ Coût Moyen (AVCO)                       │
│  ⚪ 🔄 Premier Entré Premier Sorti (FIFO)     │
│  🔘 💰 Coût économique réel                   │
│                                                │
│  💡 Explication :                              │
│  Standard : Prix fixe défini manuellement      │
│  AVCO : Moyenne pondérée des achats            │
│  FIFO : Premier entré, premier sorti           │
│  Économique : Dernier prix d'achat réel        │
│                                                │
│  ⚠️ Attention : Toutes les catégories de       │
│     produits seront automatiquement mises      │
│     à jour avec la méthode sélectionnée        │
│                                                │
│           [Annuler]  [Enregistrer]             │
└────────────────────────────────────────────────┘
```

#### Étape 3 : Configurer la Décote (Optionnel)

Pour ajuster la valorisation selon l'âge du stock :

```
┌────────────────────────────────────────────────┐
│ Décote selon Rotation                           │
├────────────────────────────────────────────────┤
│                                                │
│  ☑ Appliquer la décote selon rotation         │
│                                                │
│  💡 Principe :                                 │
│  Stock actif (0%) • Rotation lente (40%)       │
│  • Stock mort (100%)                           │
│                                                │
│  ━━━ Paramètres de Décote ━━━                 │
│                                                │
│  Période stock actif (jours) : [  365  ]       │
│  → Décote 0%                                   │
│                                                │
│  Période rotation lente (jours) : [ 1095 ]     │
│  → Au-delà = stock mort                        │
│                                                │
│  Taux décote rotation lente (%) : [ 40 ]       │
│  → Généralement 40%                            │
│                                                │
│  Taux décote stock mort (%) : [ 100 ]          │
│  → Généralement 100%                           │
│                                                │
│           [Annuler]  [Enregistrer]             │
└────────────────────────────────────────────────┘
```

**Exemple de calcul avec décote** :
```
Produit : Transformateur 50kVA
Coût économique : 2 500 000 FCFA
Dernière sortie : Il y a 850 jours (rotation lente)

Configuration :
  • Stock actif (< 365j)    : 0% décote
  • Rotation lente (365-1095j) : 40% décote  ← Applicable
  • Stock mort (> 1095j)    : 100% décote

Calcul :
  Prix de base : 2 500 000 FCFA
  Coefficient  : 0.6 (100% - 40%)
  Prix final   : 1 500 000 FCFA
  
💡 Impact : Valorisation réaliste tenant compte
           de l'obsolescence du stock
```

### Visualisation dans le Dashboard

#### Badge Indicateur

Le dashboard affiche la méthode active :

```
┌────────────────────────────────────────────────┐
│ 📊 DASHBOARD INVENTAIRE                        │
├────────────────────────────────────────────────┤
│                                                │
│  [💰 Coût Économique]  ← Badge vert si actif   │
│  ou                                            │
│  [📌 Coût Standard]    ← Badge bleu si standard│
│                                                │
│  Valeur Totale : 392 108 000 FCFA              │
│  (calculée avec la méthode active)             │
└────────────────────────────────────────────────┘
```

#### Statistiques Affectées

Toutes ces valeurs utilisent la méthode configurée :

- ✅ Valeur totale du stock inventorié
- ✅ Valeur des différences (positives/négatives)
- ✅ Valeur du stock initial
- ✅ Valorisation par entrepôt
- ✅ Valorisation par catégorie de produits
- ✅ Exports Excel/PDF
- ✅ Rapports d'analyse

### Vérification de la Configuration

#### 1. Vérifier la Méthode Active

```
Dashboard → Badge en haut à droite
→ Doit afficher "💰 Coût Économique" si configuré
```

#### 2. Vérifier les Couches de Valorisation

Pour que le coût économique fonctionne, vos produits doivent avoir des mouvements enregistrés :

```
Inventaire → Rapports → Valorisation du stock
→ Sélectionner un produit
→ Vérifier la présence de mouvements valorisés
```

**Si vide** : 
- Les futurs achats créeront les couches
- En attendant, le système utilise le coût standard

#### 3. Comparer les Méthodes

Test simple pour voir la différence :

```
1. Noter la valeur totale avec méthode actuelle
2. Changer la méthode de valorisation
3. Actualiser le dashboard (F5)
4. Comparer les valeurs
5. Revenir à la méthode souhaitée
```

### Export de Valorisation

#### Export Excel Détaillé

```
Dashboard → Actions → Export Valorisation
```

**Contenu du fichier** :
```
┌──────────────┬─────────┬──────────┬──────────┬───────────┐
│ Produit      │ Quantité│ Prix Unit│ Valeur   │ Méthode   │
├──────────────┼─────────┼──────────┼──────────┼───────────┤
│ Câble 10mm²  │ 1 200   │ 6 200    │ 7 440 000│ Économique│
│ Transfo 50kVA│ 15      │1 500 000 │22 500 000│ Économique│
│ Compteur 3P  │ 450     │ 25 000   │11 250 000│ Économique│
└──────────────┴─────────┴──────────┴──────────┴───────────┘
```

Options disponibles :
- ☑ Inclure VSD (Valeur avec Décote)
- ☑ Inclure les écarts
- ☑ Grouper par entrepôt
- ☑ Grouper par catégorie

### Questions Fréquentes - Valorisation

#### Quelle méthode choisir ?

**Coût Économique** si :
- ✅ Vos prix d'achat varient régulièrement
- ✅ Vous voulez une valorisation réaliste
- ✅ Vous effectuez des achats fréquents

**Coût Standard** si :
- ✅ Vos prix sont stables
- ✅ Vous préférez la simplicité
- ✅ Peu d'achats enregistrés dans Odoo

#### Comment passe-t-on d'une méthode à l'autre ?

```
1. Paramètres → Inventaire → StockEx
2. Changer la méthode de valorisation
3. Enregistrer
4. Actualiser le dashboard
```

⚠️ **Attention** : Le changement est immédiat sur tous les calculs futurs.

#### Les valeurs passées changent-elles ?

**Non**, les inventaires validés restent figés avec leurs valeurs d'origine.

Seuls les **nouveaux calculs** utilisent la méthode modifiée.

#### Comment fonctionne le fallback ?

Si un produit n'a pas de couche de valorisation (aucun achat enregistré) :

```
1. Système cherche dans stock.valuation.layer
2. Si aucune couche trouvée
3. → Utilise product.standard_price (coût standard)
4. → Valeur garantie même sans historique
```

#### La décote est-elle obligatoire ?

**Non**, la décote est optionnelle.

Elle est recommandée pour :
- Stock avec rotation lente
- Produits sujets à obsolescence
- Secteur avec évolution technologique rapide

#### Puis-je avoir des méthodes différentes par produit ?

**Non**, la méthode s'applique à **toutes les catégories de produits**.

C'est une contrainte Odoo pour garantir la cohérence comptable.

### Impact Comptable

La valorisation affecte directement :

```
📊 Bilan Comptable
├─ Actif
│  └─ Stock (valorisation × quantité)
│
💰 Compte de Résultat  
├─ Variation de Stock
│  └─ (Stock final - Stock initial)
│
📈 Ratios Financiers
├─ Rotation des stocks
├─ Taux de marge
└─ Rentabilité
```

⚠️ **Important** : Consultez votre comptable avant de modifier la méthode de valorisation.

↩ Retour à [Configuration](#configuration)

---

## 📊 Rapports et Analyses

### Analyse Détaillée

```
Gestion d'Inventaire → Rapports → Analyse Détaillée
```

**Vue Graphique :**

```
┌──────────────────────────────────────────────────┐
│ Analyse des Inventaires                          │
├──────────────────────────────────────────────────┤
│                                                  │
│  [Graphique] [Pivot] [Liste]                     │
│                                                  │
│  📊 Évolution de la Valeur des Stocks            │
│                                                  │
│      400k ┤                              ●       │
│      350k ┤                        ●             │
│      300k ┤                  ●                   │
│      250k ┤            ●                         │
│      200k ┤      ●                               │
│           └──────────────────────────────────    │
│            Jan   Fév   Mar   Avr   Mai   Oct    │
│                                                  │
│  📈 Grouper par : [Catégorie ▼] [Entrepôt ▼]    │
└──────────────────────────────────────────────────┘
```

**Vue Pivot :**

Table croisée dynamique pour analyses personnalisées

```
┌──────────────────────────────────────────────────┐
│                    │  Jan  │  Fév  │  Mar  │     │
│────────────────────┼───────┼───────┼───────┼─────│
│ FRIGO              │ 125k  │ 130k  │ 135k  │     │
│ CLIMAVENIR         │  98k  │ 100k  │ 102k  │     │
│ BUREAUX            │  67k  │  70k  │  72k  │     │
│────────────────────┼───────┼───────┼───────┼─────│
│ Total              │ 290k  │ 300k  │ 309k  │     │
└──────────────────────────────────────────────────┘
```

### Rapports Stock Odoo

Trois rapports supplémentaires disponibles :

**1. Analyse Stock/Emplacement**
```
Rapports → Analyse Stock/Emplacement
→ Vue complète produits + stock par emplacement
```

**2. Stock par Emplacement**
```
Rapports → Stock par Emplacement
→ Quantités détaillées par emplacement
```

**3. Mouvements de Stock**
```
Rapports → Mouvements de Stock
→ Historique complet des mouvements
```

---

## ⚙️ Configuration

### Entrepôts et Emplacements

```
Configuration → Entrepôts
```

**Créer un Entrepôt :**

```
┌────────────────────────────────────────────────┐
│ Nouvel Entrepôt                                 │
├────────────────────────────────────────────────┤
│                                                │
│  Nom : Abidjan                                 │
│  Code : ABJ                                    │
│                                                │
│  ━━━ Géolocalisation ━━━                       │
│  Latitude  : 5.3599517                         │
│  Longitude : -4.0082563                        │
│  Ville     : Abidjan                           │
│  Adresse   : Zone Industrielle                 │
│  Téléphone : +237 XX XX XX XX XX               │
│                                                │
│           [Annuler]  [Enregistrer]             │
└────────────────────────────────────────────────┘
```

**Renommer les Emplacements :**

Pour afficher des noms lisibles :

```
Avant : WH-ABJ-001/Stock
Après : Abidjan/Warehouse/Stock
```

**Procédure :**
1. Ouvrir l'emplacement
2. Modifier le champ "Nom"
3. Le nom complet se calcule automatiquement

### Paramètres du Module

```
Configuration → Paramètres
```

#### Liens rapides
- Aller à [💰 Valorisation du Stock](#-valorisation-du-stock)
- Aller à [Décote selon Rotation](#étape-3--configurer-la-décote-optionnel)
- Aller à [Configuration Kobo](#configuration-kobo)

**Options disponibles :**
- Méthode de valorisation des stocks (📌 Standard, ⚖️ AVCO, 🔄 FIFO, 💰 Économique)
- Activer la décote selon rotation (optionnelle)
- Paramètres de décote (jours actifs, jours rotation lente, taux lente, taux stock mort)
- Autoriser création auto produits
- Autoriser création auto emplacements
- Configurer modèles d'import
- Gérer les séquences

**Méthode de valorisation :**
```
Paramètres → Inventaire → StockEx → Règle de valorisation
→ Sélectionner la méthode souhaitée
→ Enregistrer
```

#### Pas-à-pas: Changer de méthode
1. Ouvrir Paramètres → Inventaire → StockEx
2. Dans « Règle de valorisation », choisir la méthode (📌/⚖️/🔄/💰)
3. Cliquer [Enregistrer]
4. Actualiser le Dashboard (F5)
5. Vérifier le badge « 💰 Coût Économique » si applicable

💡 Remarque : Le changement de méthode met à jour automatiquement les catégories de produits (cohérence comptable).

⚠️ Attention (impact comptable):
- La méthode choisie affecte la valorisation et les rapports (Bilan, Variation de stock, marges).
- La mise à jour des catégories est immédiate et s'applique aux calculs futurs.
- Avant de modifier la méthode, consultez votre comptable et validez le paramétrage.
- Voir détails : [Impact Comptable](#impact-comptable)

**Décote selon rotation (optionnelle) :**
```
Paramètres → Inventaire → StockEx → Décote selon Rotation
→ Cocher "Appliquer la décote"
→ Définir les seuils et taux
→ Enregistrer
```

Recommandations par défaut :
- Stock actif (< 365 jours) : Décote 0%
- Rotation lente (365–1095 jours) : Décote 40%
- Stock mort (> 1095 jours) : Décote 100%

#### FAQ Configuration

- Changer la méthode modifie-t-il l’historique ?
  → Non. Les inventaires déjà validés restent figés. Le changement s’applique aux calculs futurs.
- Que se passe-t-il si un produit n'a pas d’achats ?
  → Fallback automatique sur le coût standard (`standard_price`).
- Peut-on définir une méthode différente par produit ?
  → Non. La méthode s’applique au niveau des catégories (cohérence comptable).
- La décote est-elle obligatoire ?
  → Non. Elle est optionnelle et recommandée pour la rotation lente/stock mort.
- Comment vérifier que la configuration est active ?
  → Le dashboard affiche un badge “💰 Coût Économique” lorsque la méthode est active.

### Configuration Kobo

```
Configuration → 📱 Kobo Collect
```

Pour connecter vos collectes terrain mobile.

**Champs requis :**
- Nom de la configuration
- URL serveur Kobo
- API Token
- Mapping des champs

---

## 🎯 Cas d'Usage Courants

### Cas 1 : Inventaire Mensuel Simple

```
1. Import → Nouvel Inventaire
2. Choisir "Import Excel"
3. Charger le fichier Excel
4. Vérifier les lignes importées
5. Cliquer "Valider l'Inventaire"
6. Consulter le rapport
```

### Cas 2 : Corriger un Écart

```
1. Ouvrir l'inventaire
2. Rechercher la ligne avec écart
3. Cliquer sur "Mouvements de Stock"
4. Analyser l'historique
5. Justifier l'écart
6. Valider ou ajuster
```

### Cas 3 : Comparer Deux Inventaires

```
1. Rapports → Analyse Détaillée
2. Vue Pivot
3. Lignes : Produit
4. Colonnes : Inventaire
5. Mesure : Valeur
6. Comparer les écarts
```

---

## 💡 Conseils et Bonnes Pratiques

### Import de Données

✅ **Préparez bien votre fichier Excel**
- Vérifier les en-têtes de colonnes
- Supprimer les lignes vides
- Utiliser des codes cohérents

✅ **Vérifiez avant d'importer**
- Tester avec un petit fichier
- Valider les codes entrepôts
- Contrôler les références produits

### Gestion des Inventaires

✅ **Inventaire régulier**
- Minimum mensuel recommandé
- Même jour du mois
- Même équipe si possible

✅ **Traitement des écarts**
- Analyser systématiquement
- Documenter les causes
- Actions correctives

✅ **Validation**
- Vérifier les totaux
- Contrôler les écarts importants
- Approuver en connaissance

### Rapports

✅ **Export Excel**
- Archivage mensuel
- Partage avec direction
- Analyse hors-ligne

✅ **Graphiques**
- Présentation claire
- Tendances visibles
- Décisions rapides

---

## ❓ Questions Fréquentes

### Comment importer un inventaire ?

```
Menu → Import → Nouvel Inventaire
→ Choisir méthode (Excel recommandé)
→ Charger fichier
→ Vérifier import
```

### Les écarts sont normaux ?

Oui, des petits écarts sont normaux :
- Erreurs de comptage
- Vols/pertes mineurs
- Transactions non enregistrées

**Écarts > 5%** : Investigation requise

### Comment exporter un rapport ?

```
1. Ouvrir le rapport
2. Cliquer ⚙️ (Actions)
3. Choisir "Exporter"
4. Sélectionner colonnes
5. Format Excel
```

### Puis-je modifier un inventaire validé ?

**Non**, un inventaire validé est figé.

**Solution** : Créer un nouvel inventaire de correction

### Comment renommer les emplacements ?

```
1. Configuration → Emplacements
2. Ouvrir l'emplacement
3. Modifier le champ "Nom"
4. Enregistrer
```

L'affichage se met à jour automatiquement.

---

## 📞 Support

### Documentation Complète

Consultez les guides détaillés :
- [Guide Acquisition Données](GUIDE_ACQUISITION_DONNEES.md)
- [Affichage Emplacements](AFFICHAGE_EMPLACEMENTS.md)
- [Rapports Stock Odoo](RAPPORTS_STOCK_ODOO.md)

### Contact

**Développeur** : Sorawel  
**Site** : www.sorawel.com  
**Email** : contact@sorawel.com

---

## 🎓 Résumé Rapide

### Créer un Inventaire
```
Import → Nouvel Inventaire → Excel → Charger → Importer
```

### Voir les Inventaires
```
Opérations → Inventaires de Stock
```

### Consulter le Dashboard
```
Gestion d'Inventaire (ouvre directement la vue d'ensemble)
```

### Analyser
```
Rapports → Analyse Détaillée → Graphique/Pivot
```

---

**Version 1.1 - Novembre 2025**

*Guide créé pour le module Stockinv - Gestion d'Inventaire Odoo 18/19*

**Dernière mise à jour** : Ajout de la section complète sur la valorisation du stock avec 4 méthodes (Standard, AVCO, FIFO, Économique)
