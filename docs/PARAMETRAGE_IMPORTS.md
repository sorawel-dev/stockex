# ⚙️ Guide de Paramétrage des Imports

## 📍 Accès aux Paramètres

**Menu** : `Gestion d'Inventaire → Configuration → Paramètres`

Ou depuis les **Settings Odoo** généraux → Section `Gestion d'Inventaire`

---

## 🎯 Méthode d'Import par Défaut

### **Configuration**

Choisissez la méthode utilisée par défaut lors de la création d'un nouvel inventaire :

| Option | Comportement |
|--------|--------------|
| **📊 Fichier Excel/CSV** | Ouvre directement le wizard Excel/CSV |
| **📱 Kobo Collect** | Ouvre directement le wizard Kobo Collect |
| **🎯 Demander à Chaque Fois** | Affiche l'écran de choix (par défaut) |

### **Utilisation**

**Scénario 1 : Bureau uniquement**
```
Méthode par défaut : 📊 Fichier Excel/CSV
→ Gain de temps : 1 clic en moins à chaque import
```

**Scénario 2 : Terrain uniquement**
```
Méthode par défaut : 📱 Kobo Collect
→ Les agents terrain accèdent directement à Kobo
```

**Scénario 3 : Hybride**
```
Méthode par défaut : 🎯 Demander à Chaque Fois
→ Flexibilité totale selon le besoin
```

---

## 📊 Options Import Excel/CSV

### **Création Automatique**

#### **Créer les Produits Manquants**
- ✅ **Activé** (recommandé) : Les produits sont créés automatiquement
- ❌ **Désactivé** : Import échoue si produit manquant

**Exemple :**
```
Fichier contient : Code produit "ABC123"
Base Odoo : Produit inexistant

✅ Activé → Produit "ABC123" créé automatiquement
❌ Désactivé → Ligne ignorée avec erreur
```

#### **Créer les Emplacements Manquants**
- ✅ **Activé** (recommandé) : Les entrepôts sont créés automatiquement
- ❌ **Désactivé** : Import échoue si entrepôt manquant

**Exemple :**
```
Fichier contient : Entrepôt "Koumassi Wse"
Base Odoo : Entrepôt inexistant

✅ Activé → Entrepôt créé avec hiérarchie et GPS
❌ Désactivé → Ligne ignorée avec erreur
```

### **Mises à Jour**

#### **Mettre à Jour les Prix**
- ✅ **Activé** : Prix des produits existants mis à jour
- ❌ **Désactivé** (recommandé) : Prix conservés

**Attention** : Si activé, tous les prix seront écrasés !

**Exemple :**
```
Fichier : Produit "ABC123" à 10.50€
Base : Produit "ABC123" à 8.00€

✅ Activé → Prix devient 10.50€
❌ Désactivé → Prix reste 8.00€
```

#### **Importer la Géolocalisation**
- ✅ **Activé** (recommandé) : GPS importé si présent
- ❌ **Désactivé** : GPS ignoré

**Colonnes concernées :**
- LATITUDE, LONGITUDE
- VILLE, ADRESSE
- TELEPHONE, EMAIL

---

## 📱 Options Kobo Collect

### **Configuration Kobo par Défaut**

Sélectionnez la configuration Kobo utilisée par défaut :
- Liste des configurations actives
- Bouton **Gérer les Configurations** pour créer/modifier

**Utilité :**
```
Plusieurs projets/formulaires Kobo
→ Définir celui utilisé par défaut
→ Gain de temps à chaque import
```

### **Création Automatique**

#### **Créer les Produits Manquants (Kobo)**
- ✅ **Activé** (recommandé) : Produits créés depuis terrain
- ❌ **Désactivé** : Seuls les produits existants acceptés

**Cas d'usage :**
```
Agent terrain découvre nouveau produit
→ Le saisit dans Kobo Collect
→ Produit créé automatiquement dans Odoo
```

#### **Créer les Emplacements Manquants (Kobo)**
- ✅ **Activé** (recommandé) : Entrepôts créés depuis terrain
- ❌ **Désactivé** : Seuls les entrepôts existants acceptés

### **Validation Automatique**

#### **⚠️ Option Critique**

- ✅ **Activé** : Inventaire validé automatiquement après import
- ❌ **Désactivé** (recommandé) : Validation manuelle requise

**Avantages Activé :**
- ✅ Gain de temps
- ✅ Stocks mis à jour immédiatement
- ✅ Pas d'intervention manuelle

**Inconvénients Activé :**
- ⚠️ Pas de vérification humaine
- ⚠️ Erreurs directement dans les stocks
- ⚠️ Corrections plus complexes

**Recommandation :**
```
Déploiement initial : ❌ DÉSACTIVÉ
→ Vérifier manuellement chaque import
→ S'assurer de la qualité des données

Production stable : ✅ ACTIVÉ (optionnel)
→ Si confiance totale dans les données
→ Si processus de contrôle terrain robuste
```

---

## 📊 Statistiques

### **Affichées dans les Paramètres :**

1. **Nombre d'Inventaires** : Total créés
2. **Dernier Import** : Date/heure du dernier import

**Utilité :**
- Suivre l'utilisation du module
- Vérifier l'activité récente
- Diagnostic rapide

---

## 🔧 Configuration Recommandée

### **Démarrage (Première Utilisation)**

```yaml
Méthode par défaut: Demander à Chaque Fois
Excel - Créer produits: ✅ Activé
Excel - Créer emplacements: ✅ Activé
Excel - Mettre à jour prix: ❌ Désactivé
Excel - Géolocalisation: ✅ Activé
Kobo - Créer produits: ✅ Activé
Kobo - Créer emplacements: ✅ Activé
Kobo - Validation auto: ❌ Désactivé
```

### **Production Bureau Uniquement**

```yaml
Méthode par défaut: Fichier Excel/CSV
Excel - Créer produits: ✅ Activé
Excel - Créer emplacements: ✅ Activé
Excel - Mettre à jour prix: ❌ Désactivé
Excel - Géolocalisation: ✅ Activé
```

### **Production Terrain Uniquement**

```yaml
Méthode par défaut: Kobo Collect
Kobo - Config défaut: [Votre config]
Kobo - Créer produits: ✅ Activé
Kobo - Créer emplacements: ✅ Activé
Kobo - Validation auto: ❌ Désactivé (ou ✅ si contrôle terrain robuste)
```

### **Production Hybride**

```yaml
Méthode par défaut: Demander à Chaque Fois
Excel - Créer produits: ✅ Activé
Excel - Créer emplacements: ✅ Activé
Excel - Mettre à jour prix: ❌ Désactivé
Excel - Géolocalisation: ✅ Activé
Kobo - Config défaut: [Votre config]
Kobo - Créer produits: ✅ Activé
Kobo - Créer emplacements: ✅ Activé
Kobo - Validation auto: ❌ Désactivé
```

---

## 🎯 Exemples de Workflows

### **Workflow 1 : Import Initial Base de Données**

**Configuration :**
```
Méthode : Excel/CSV (direct)
Créer produits : ✅ Activé
Créer emplacements : ✅ Activé
Mettre à jour prix : ✅ Activé (exception!)
```

**Résultat :**
- Import massif de 2000+ produits
- Création complète de la base
- Prix initiaux définis

### **Workflow 2 : Inventaire Terrain Régulier**

**Configuration :**
```
Méthode : Kobo Collect (direct)
Config Kobo : Production
Créer produits : ✅ Activé (nouveaux produits terrain)
Validation auto : ❌ Désactivé (vérification bureau)
```

**Processus :**
1. Agents terrain → Collecte Kobo
2. Synchronisation automatique
3. Bureau → Vérification
4. Bureau → Validation manuelle
5. Stocks mis à jour

### **Workflow 3 : Contrôle Qualité Strict**

**Configuration :**
```
Méthode : Demander (choix manuel)
Créer produits : ❌ Désactivé
Créer emplacements : ❌ Désactivé
Validation auto : ❌ Désactivé
```

**Processus :**
1. Seules données validées acceptées
2. Produits/entrepôts créés manuellement avant
3. Import vérifie la conformité
4. Validation manuelle après contrôle

---

## 💡 Bonnes Pratiques

### **1. Tester Avant Production**

```
1. Configurer en mode TEST
2. Importer petit fichier échantillon
3. Vérifier résultats
4. Ajuster paramètres
5. Passer en PRODUCTION
```

### **2. Sauvegarder Avant Changement**

```
Avant de changer "Mettre à jour prix" :
→ Exporter les prix actuels
→ Backup base de données
```

### **3. Former les Utilisateurs**

```
Chaque utilisateur doit comprendre :
- Quelle méthode utiliser
- Quand créer vs utiliser existant
- Impact de la validation auto
```

### **4. Documenter Vos Choix**

```
Créer un document interne :
"Pourquoi validation auto = Désactivé"
"Pourquoi Excel par défaut"
etc.
```

---

## 🔍 Dépannage

### **Problème : Imports trop lents**

**Solution :**
```
✅ Activer créations automatiques
→ Évite erreurs et ré-imports
→ Traitement plus fluide
```

### **Problème : Trop de doublons**

**Solution :**
```
❌ Désactiver créations automatiques
→ Force utilisation données existantes
→ Nettoyer la base d'abord
```

### **Problème : Prix incorrects**

**Solution :**
```
1. Vérifier "Mettre à jour prix"
2. Si activé → Désactiver
3. Restaurer prix depuis backup
4. Réimporter avec option désactivée
```

### **Problème : Kobo ne synchronise pas**

**Solution :**
```
1. Configuration → Paramètres
2. Vérifier "Configuration Kobo par défaut"
3. Cliquer "Gérer les Configurations"
4. Tester la connexion
```

---

## ✅ Checklist de Configuration

### **À Faire au Démarrage :**

- [ ] Accéder aux Paramètres
- [ ] Définir méthode par défaut
- [ ] Configurer options Excel
- [ ] Configurer Kobo (si utilisé)
- [ ] Tester avec échantillon
- [ ] Former les utilisateurs
- [ ] Documenter les choix

### **À Revoir Régulièrement :**

- [ ] Statistiques d'utilisation
- [ ] Pertinence méthode par défaut
- [ ] Qualité des données importées
- [ ] Besoin validation automatique
- [ ] Performance des imports

---

## 🚀 Accès Rapide

**Modifier les Paramètres :**
```
Menu → Gestion d'Inventaire → Configuration → Paramètres
```

**Droits Requis :**
```
Groupe : Gestionnaire Gestion d'Inventaire
(stockex.group_stockex_manager)
```

---

**Les paramètres vous permettent d'adapter le module à vos besoins spécifiques !** ⚙️
