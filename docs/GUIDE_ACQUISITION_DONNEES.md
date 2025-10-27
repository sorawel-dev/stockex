# 📦 Guide d'Acquisition des Données d'Inventaire

## 🎯 Vue d'Ensemble

Le module **Gestion d'Inventaire** offre **deux méthodes** pour acquérir vos données d'inventaire :

### 1. 📊 **Fichier Excel/CSV**
- Import bureau depuis un fichier
- Idéal pour consolidation et imports massifs

### 2. 📱 **Kobo Collect**
- Collecte terrain sur mobile/tablette
- Idéal pour inventaires physiques sur le terrain

---

## 🚀 Démarrage Rapide

### **Créer un Nouvel Inventaire**

1. **Menu** : `Gestion d'Inventaire → Import → 📦 Nouvel Inventaire`
2. **Choisir la méthode** :
   - 📊 Fichier Excel/CSV
   - 📱 Kobo Collect
3. **Suivre le wizard** approprié

---

## 📊 Méthode 1 : Fichier Excel/CSV

### **Avantages**
- ✅ Import de masse (milliers de lignes)
- ✅ Fichiers Excel (.xlsx) ou CSV
- ✅ Création automatique de produits/entrepôts/catégories
- ✅ Structure flexible
- ✅ Géolocalisation supportée
- ✅ Pas de configuration requise

### **Quand Utiliser ?**
- Import initial de données existantes
- Consolidation de plusieurs sources
- Mise à jour massive
- Travail de bureau

### **Procédure**

1. **Préparer le Fichier Excel**

Colonnes obligatoires :
- `CODE PRODUIT` : Code unique du produit
- `PRODUIT` : Nom du produit
- `CODE ENTREPOT` : Code de l'entrepôt
- `ENTREPOT` : Nom de l'entrepôt
- `QUANTITE` : Quantité en stock
- `COUT UNITAIRE` : Prix unitaire

Colonnes optionnelles :
- `CODE CATEGORIE` : Code de la catégorie
- `CATEGORIE` : Nom de la catégorie
- `CODE ENTREPOT PARENT` : Pour hiérarchie
- `ENTREPOT PARENT` : Nom du parent
- `UDM` : Unité de mesure (PC, KG, L...)
- `LATITUDE`, `LONGITUDE` : Coordonnées GPS
- `VILLE`, `ADRESSE`, `TELEPHONE`, `EMAIL`

2. **Lancer l'Import**
   - Menu : `Import → 📦 Nouvel Inventaire`
   - Choisir : `📊 Fichier Excel/CSV`
   - Remplir le formulaire
   - Charger le fichier
   - Cocher les options
   - Cliquer sur `Importer`

3. **Valider l'Inventaire**
   - Vérifier les lignes
   - Cliquer sur `Valider`
   - Les stocks Odoo sont mis à jour automatiquement

### **Options Disponibles**
- ☑️ Créer les produits manquants
- ☑️ Créer les emplacements manquants
- ☑️ Mettre à jour les prix produits
- ☑️ Importer la géolocalisation

---

## 📱 Méthode 2 : Kobo Collect

### **Avantages**
- ✅ Collecte terrain sur mobile/tablette
- ✅ Mode hors ligne
- ✅ Synchronisation automatique
- ✅ Géolocalisation GPS automatique
- ✅ Validation en temps réel
- ✅ Photos et codes-barres supportés

### **Quand Utiliser ?**
- Inventaires physiques sur le terrain
- Comptages dans les entrepôts
- Collecte distribuée (plusieurs agents)
- Zones sans connexion internet

### **Configuration Initiale**

#### **1. Créer un Compte Kobo**
1. Allez sur https://www.kobotoolbox.org
2. Créez un compte gratuit
3. Ou utilisez https://kobo.humanitarianresponse.info (compte humanitaire)

#### **2. Créer un Formulaire Kobo**

**Exemple de formulaire d'inventaire :**

```
Question                Type            Nom du Champ
----------------------------------------------------
Code Produit           Text            product_code
Nom du Produit         Text            product_name
Catégorie              Select One      category
Entrepôt               Select One      warehouse
Quantité               Integer         quantity
Prix Unitaire          Decimal         unit_price
Position GPS           Geopoint        gps_location
```

**Déployez le formulaire** sur Kobo.

#### **3. Obtenir le Token API**
1. Dans Kobo : `Paramètres → Sécurité`
2. Créez ou copiez votre **Token API**
3. Conservez-le précieusement

#### **4. Configurer dans Odoo**

1. **Menu** : `Configuration → 📱 Kobo Collect`
2. **Créer** une nouvelle configuration
3. **Remplir** :
   - Nom : `Configuration Production`
   - URL Kobo : `https://kf.kobotoolbox.org`
   - Token API : Collez votre token
   - ID du Formulaire : Ex: `aXYZ123456` (trouvé dans l'URL)

4. **Mapping des Champs** :
   - Champ Code Produit : `product_code`
   - Champ Quantité : `quantity`
   - Champ Emplacement : `warehouse`
   - Champ Nom Produit : `product_name`
   - Champ Catégorie : `category`
   - Champ Prix : `unit_price`
   - Champ GPS : `gps_location`

5. **Tester** : Cliquez sur `🔌 Tester la Connexion`

### **Collecte des Données**

#### **1. Installation Mobile**
1. Téléchargez **KoboCollect** depuis Play Store / App Store
2. Ouvrez l'application
3. `⚙️ Paramètres → Serveur`
4. URL : `https://kf.kobotoolbox.org`
5. Nom d'utilisateur : Votre email Kobo
6. Mot de passe : Votre mot de passe Kobo

#### **2. Télécharger le Formulaire**
1. Menu : `Obtenir un formulaire vide`
2. Sélectionnez votre formulaire d'inventaire
3. Téléchargez-le

#### **3. Collecter les Données**
1. Menu : `Remplir un nouveau formulaire`
2. Sélectionnez votre formulaire
3. Remplissez les informations :
   - Scannez le code-barres (si configuré)
   - Entrez la quantité
   - GPS automatique
   - Photos si nécessaire
4. Sauvegardez

#### **4. Synchroniser**
- Si en ligne : `Envoyer les formulaires finalisés`
- Si hors ligne : Attendez d'avoir une connexion
- Les données sont envoyées vers Kobo

### **Import dans Odoo**

1. **Menu** : `Import → 📦 Nouvel Inventaire`
2. **Choisir** : `📱 Kobo Collect`
3. **Sélectionner** la configuration Kobo
4. **Mode d'Import** :
   - `Nouvelles Soumissions` : Importe uniquement les nouvelles
   - `Toutes les Soumissions` : Importe tout
   - `Plage de Dates` : Période spécifique
5. **Options** :
   - Créer produits/emplacements manquants
   - Mettre à jour les prix
   - Importer géolocalisation
   - Valider automatiquement
6. **Synchroniser** : Récupère les données
7. **Importer** : Crée l'inventaire
8. **Valider** : Met à jour les stocks

---

## 🔄 Comparaison des Méthodes

| Critère | Excel/CSV | Kobo Collect |
|---------|-----------|--------------|
| **Configuration** | Aucune | Configuration initiale requise |
| **Connexion Internet** | Non requise | Requise pour sync (pas pour collecte) |
| **Équipement** | Ordinateur | Mobile/Tablette |
| **Volume** | Illimité | Dépend du terrain |
| **Géolocalisation** | Manuelle | Automatique GPS |
| **Validation** | Post-import | En temps réel |
| **Photos** | Non | Oui |
| **Codes-barres** | Non | Oui (scanner) |
| **Hors ligne** | Oui | Oui |
| **Collecte distribuée** | Non | Oui (plusieurs agents) |

---

## 💡 Recommandations

### **Utiliser Excel/CSV si :**
- ✅ Vous avez déjà des données structurées
- ✅ Import initial ou mise à jour massive
- ✅ Travail de bureau/consolidation
- ✅ Pas de besoin de collecte terrain

### **Utiliser Kobo Collect si :**
- ✅ Inventaire physique sur le terrain
- ✅ Plusieurs agents de collecte
- ✅ Besoin de géolocalisation automatique
- ✅ Zones sans connexion internet stable
- ✅ Validation en temps réel nécessaire

### **Utiliser les Deux (Hybride) :**
- 📊 **Excel** : Import initial des données de base
- 📱 **Kobo** : Collecte terrain et mises à jour régulières

---

## 🛠️ Dépannage

### **Problème : Kobo non configuré**
**Solution** : `Configuration → 📱 Kobo Collect` → Créer une configuration

### **Problème : Erreur de connexion Kobo**
**Solutions** :
1. Vérifiez le Token API
2. Vérifiez l'URL Kobo
3. Vérifiez l'ID du formulaire
4. Testez la connexion

### **Problème : Mapping incorrect**
**Solution** : Vérifiez les noms exacts des champs dans votre formulaire Kobo

### **Problème : Emplacements non 'internal'**
**Solution** : Utilisez l'assistant `Action → Corriger les Emplacements`

---

## 📚 Ressources

### **Documentation Kobo Collect**
- https://www.kobotoolbox.org/
- https://support.kobotoolbox.org/

### **Module Python Requis**
```bash
pip3 install requests
```

### **Formats de Fichiers Supportés**
- **.xlsx** : Excel 2007+
- **.csv** : Comma-separated values

---

## 🎯 Workflow Recommandé

### **Configuration Initiale :**
1. Import Excel → Créer base de données produits
2. Configurer Kobo Collect
3. Former les agents terrain

### **Opérations Courantes :**
1. Agents terrain → Kobo Collect
2. Sync automatique → Odoo
3. Validation → Stocks mis à jour

### **Consolidation :**
1. Export depuis Kobo
2. Traitement Excel
3. Réimport dans Odoo

---

## ✅ Checklist de Déploiement

### **Pour Excel/CSV :**
- [ ] Préparer le modèle de fichier
- [ ] Former les utilisateurs
- [ ] Tester avec un petit fichier
- [ ] Valider les résultats

### **Pour Kobo Collect :**
- [ ] Créer compte Kobo
- [ ] Créer formulaire
- [ ] Obtenir Token API
- [ ] Configurer dans Odoo
- [ ] Tester la connexion
- [ ] Installer KoboCollect sur mobiles
- [ ] Configurer les mobiles
- [ ] Former les agents terrain
- [ ] Test terrain avec validation
- [ ] Déploiement complet

---

**Le système est maintenant prêt à recevoir vos données d'inventaire, que ce soit depuis le bureau ou le terrain !** 🎉
