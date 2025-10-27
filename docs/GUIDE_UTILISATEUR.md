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
7. [Rapports et Analyses](#rapports-et-analyses)
8. [Configuration](#configuration)

---

## 🎯 Vue d'Ensemble

### Qu'est-ce que ce module ?

Le module **Gestion d'Inventaire** vous permet de :
- ✅ Créer et gérer des inventaires de stock
- ✅ Importer des données depuis Excel, CSV ou Kobo Collect
- ✅ Comparer les quantités théoriques et réelles
- ✅ Calculer automatiquement les écarts
- ✅ Suivre la valorisation des stocks
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

**Options disponibles :**
- Autoriser création auto produits
- Autoriser création auto emplacements
- Configurer modèles d'import
- Gérer les séquences

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

**Version 1.0 - Octobre 2025**

*Guide créé pour le module Stockinv - Gestion d'Inventaire Odoo 18*
