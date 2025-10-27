# 🚀 Guide Rapide de Démarrage - Nouvelles Fonctionnalités

## 📋 Prérequis

1. **Installation des dépendances Python**
```bash
pip install python-barcode
```

2. **Mise à jour du module**
```bash
odoo-bin -d your_database -u stockex
```

---

## ⚡ Démarrage en 5 Minutes

### 1️⃣ Activer les Crons (30 secondes)

```
Menu → Paramètres → Technique → Automatisation → Actions planifiées
```

Activer :
- ✅ **Planificateur Comptage Cyclique** (quotidien 02:00)
- ✅ **Rappels Inventaires En Cours** (quotidien 09:00)
- ⚠️ **Synchronisation Auto Kobo** (désactivé par défaut, activer si besoin)

---

### 2️⃣ Générer Codes-Barres Emplacements (2 minutes)

```
Menu → Inventaire → Configuration → Emplacements
```

1. Ouvrir un emplacement
2. Cliquer sur **"Générer Code-barres"**
3. Le code-barres apparaît (ex: `LOC0000000001`)
4. Imprimer l'étiquette si nécessaire

**💡 Astuce** : Faire pour tous les emplacements principaux

---

### 3️⃣ Créer une Configuration de Comptage Cyclique (1 minute)

```
Menu → Inventaires → Configuration → Comptage Cyclique → Créer
```

**Exemple de configuration** :
- **Nom** : "Comptage Mensuel Entrepôt Principal"
- **Emplacements** : Sélectionner votre/vos emplacements
- **Fréquence** : Mensuel
- **Jour du mois** : 1
- **Produits par comptage** : 50
- **Priorité ABC** : Toutes classes

👉 **Sauvegarder** et le système générera automatiquement les inventaires !

---

### 4️⃣ Tester le Scan de Codes-Barres (1 minute)

```
Menu → Inventaires → Inventaires de Stock → Créer
```

1. Créer un nouvel inventaire
2. Ajouter une ligne
3. Dans **"Code-barres scanné"**, saisir le code-barres d'un produit
4. ✨ Le produit se remplit automatiquement !

**💡 Astuce** : Fonctionne avec scanner USB ou saisie manuelle

---

### 5️⃣ Tester le Workflow d'Approbation (30 secondes)

Sur un inventaire avec lignes :

1. **Démarrer** l'inventaire
2. Cliquer **"Demander Approbation"**
3. État passe à "En attente d'approbation"
4. ✉️ Une activité est créée pour votre manager
5. Le manager peut **Approuver** ou **Rejeter**

---

## 🎯 Fonctionnalités Avancées

### 📷 Ajouter des Photos à une Ligne

1. Dans une ligne d'inventaire, aller dans l'onglet **Photos** (si vue formulaire)
2. Uploader jusqu'à 3 photos
3. Ajouter des remarques dans **"Notes"**

---

### 📊 Comparer Deux Inventaires

```
Menu → Inventaires → Rapports → Comparaison d'Inventaires
```

1. Sélectionner **Inventaire 1** (plus ancien)
2. Sélectionner **Inventaire 2** (plus récent)
3. Choisir le type de comparaison
4. **Lancer la comparaison**
5. Voir les résultats détaillés !

---

### 📈 Analyser la Variance de Stock

```
Menu → Inventaires → Rapports → Analyse de Variance
```

1. Définir la **plage de dates**
2. Filtrer par **emplacements/catégories** (optionnel)
3. Choisir les **types d'écarts** à afficher
4. **Analyser** → Résultats en liste/graph/pivot

**Filtres utiles** :
- Écarts critiques uniquement (>20%)
- Valeur minimum (ex: >10,000 FCFA)
- Surplus ou manquants uniquement

---

### 🔄 Générer un Comptage Cyclique Manuellement

```
Menu → Inventaires → Configuration → Comptage Cyclique
```

1. Ouvrir une configuration
2. Cliquer **"Générer Comptage Cyclique"**
3. Un inventaire est créé automatiquement avec les produits sélectionnés !

---

## 🎓 Cas d'Usage Pratiques

### Cas 1 : Inventaire Physique Rapide avec Scanner

**Objectif** : Inventaire de 500 produits en 2 heures

1. Créer un inventaire
2. **Équiper avec scanner USB**
3. Scanner chaque code-barres produit
4. Saisir quantité réelle
5. Photo si anomalie
6. Démarrer → Demander approbation → Manager approuve → Valider

**Gain de temps** : 80% vs saisie manuelle !

---

### Cas 2 : Comptage Cyclique Automatisé

**Objectif** : Compter 50 produits par semaine automatiquement

1. Créer configuration comptage cyclique
   - Fréquence : Hebdomadaire
   - Jour : Lundi
   - Produits : 50
   - Priorité : Classe A (haute valeur)

2. Chaque lundi à 02:00, un inventaire est généré
3. Équipe reçoit la liste et compte
4. Workflow approbation si écarts >10,000 FCFA

**Résultat** : Planning automatique, aucun oubli !

---

### Cas 3 : Analyse Mensuelle des Écarts

**Objectif** : Identifier les produits problématiques

1. Fin du mois → Analyse de variance
2. Filtrer : Écarts critiques (>20%)
3. Vue Pivot : Par catégorie + emplacement
4. Identifier tendances
5. Actions correctives :
   - Formation équipe si erreurs répétées
   - Amélioration stockage si détérioration
   - Ajuster seuils de réapprovisionnement

---

## 🛠️ Configuration Recommandée

### Pour Petite Entreprise (<100 produits)

**Comptage Cyclique** :
- Fréquence : Mensuel
- Tous les produits à chaque fois
- Pas de priorité ABC

**Approbation** :
- Tous les inventaires
- Approbateur : Responsable stock

**Crons** :
- Comptage cyclique : Activé
- Rappels : Activé
- Kobo sync : Selon besoin

---

### Pour Moyenne Entreprise (100-1000 produits)

**Comptage Cyclique** :
- Fréquence : Hebdomadaire
- 50-100 produits par cycle
- Priorité ABC : Classe A hebdo, B mensuel, C trimestriel

**Approbation** :
- Si écart >10,000 FCFA ou >10%
- Approbateur : Manager inventaire

**Crons** :
- Tous activés
- Surveillance logs quotidienne

---

### Pour Grande Entreprise (>1000 produits)

**Comptage Cyclique** :
- Fréquence : Quotidien
- 100-200 produits par jour
- Priorité ABC stricte :
  - A (20% produits, 80% valeur) : Quotidien
  - B (30% produits, 15% valeur) : Hebdomadaire
  - C (50% produits, 5% valeur) : Mensuel

**Approbation** :
- Workflow à 2 niveaux :
  - Niveau 1 : Chef d'équipe (tous)
  - Niveau 2 : Directeur (>50,000 FCFA)

**Crons** :
- Tous activés
- Monitoring automatisé
- Alertes email si échecs

---

## 📊 KPIs à Suivre

### Quotidiens
- [ ] Nombre d'inventaires en cours
- [ ] Écarts critiques détectés
- [ ] Photos manquantes

### Hebdomadaires
- [ ] Taux de validation inventaires (objectif >95%)
- [ ] Délai moyen approbation (objectif <24h)
- [ ] Écarts par catégorie

### Mensuels
- [ ] Tendance écarts globaux (objectif décroissant)
- [ ] Efficacité comptage cyclique (couverture %)
- [ ] Valeur écarts vs valeur stock (objectif <2%)

---

## ⚠️ Erreurs Courantes et Solutions

### Erreur : "Module barcode not found"
**Solution** :
```bash
pip install python-barcode
service odoo restart
```

### Erreur : "Aucun produit trouvé avec le code-barres"
**Solution** :
- Vérifier que les produits ont des codes-barres configurés
- Menu → Inventaire → Produits → Modifier → Onglet Ventes → Code-barres

### Cron ne s'exécute pas
**Solution** :
- Vérifier que le cron est "Actif"
- Vérifier la "Prochaine exécution"
- Vérifier les logs Odoo : `grep CRON odoo.log`

### Photos trop volumineuses
**Solution** :
- Redimensionner avant upload (<1MB recommandé)
- Utiliser compression JPEG qualité 80%
- Nettoyer anciennes photos périodiquement

---

## 🎯 Checklist de Démarrage

### Jour 1 : Installation
- [ ] Dépendances Python installées
- [ ] Module mis à jour
- [ ] Tests unitaires exécutés
- [ ] Crons activés

### Semaine 1 : Configuration
- [ ] Codes-barres emplacements générés
- [ ] 1-2 configurations comptage cyclique créées
- [ ] Workflow approbation testé
- [ ] Formation utilisateurs scan codes-barres

### Mois 1 : Optimisation
- [ ] Analyser premiers rapports variance
- [ ] Ajuster fréquences comptage cyclique
- [ ] Optimiser workflow approbation
- [ ] Comparer 2 inventaires mensuels

---

## 📞 Besoin d'Aide ?

**Documentation complète** : Voir `NOUVELLES_FONCTIONNALITES.md`

**Support** :
- Email : contact@sorawel.com
- Site : www.sorawel.com

**Logs Odoo** :
```bash
tail -f /var/log/odoo/odoo.log | grep stockex
```

---

**🎉 Félicitations ! Vous êtes prêt à utiliser toutes les nouvelles fonctionnalités !**
