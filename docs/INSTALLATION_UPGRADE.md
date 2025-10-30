# 📦 Guide d'Installation et de Mise à Jour - Stockex v18.0.2.0.0

## 🎯 Objectif

Ce guide vous accompagne dans :
- ✅ **Installation fraîche** du module Stockex v18.0.2.0.0
- ✅ **Mise à jour** depuis v18.0.1.0.0 vers v18.0.2.0.0
- ✅ **Vérification** et tests post-installation

---

## 📋 Prérequis

### Système
- ✅ **Odoo 18.0** installé et fonctionnel
- ✅ **PostgreSQL 12+** comme base de données
- ✅ **Python 3.10+**
- ✅ Droits d'administration sur Odoo

### Modules Odoo
Le module Stockex nécessite :
- `base` (inclus par défaut)
- `mail` (inclus par défaut)
- `stock` (module standard Odoo)
- `product` (module standard Odoo)

---

## 🆕 Installation Fraîche (Nouveau Déploiement)

### Étape 1 : Copier le Module

```bash
# Copier le dossier stockex dans addons
cp -r /chemin/vers/stockex /chemin/vers/odoo/addons/

# Vérifier les permissions
chmod -R 755 /chemin/vers/odoo/addons/stockex
chown -R odoo:odoo /chemin/vers/odoo/addons/stockex
```

### Étape 2 : Installer les Dépendances Python

```bash
# Activer l'environnement virtuel Odoo (si utilisé)
source /chemin/vers/odoo-venv/bin/activate

# Installer les dépendances
pip install openpyxl       # Import Excel (obligatoire)
pip install python-barcode # Codes-barres (obligatoire)
pip install requests       # Kobo API (optionnel)

# Vérifier l'installation
pip list | grep -E "openpyxl|barcode|requests"
```

### Étape 3 : Mettre à Jour la Liste des Applications

**Via Interface Odoo** :
```
1. Se connecter en tant qu'administrateur
2. Apps → Mettre à jour la liste des applications
3. Rechercher "Stockinv"
4. Cliquer sur "Installer"
```

**Via Ligne de Commande** :
```bash
odoo-bin -c /etc/odoo/odoo.conf -d your_database -i stockex --stop-after-init
```

### Étape 4 : Vérifier l'Installation

```bash
# Exécuter les tests unitaires
odoo-bin -d your_database -i stockex --test-enable --stop-after-init

# Vérifier les logs
tail -f /var/log/odoo/odoo.log | grep stockex
```

**Résultat attendu** :
```
10 tests passed, 0 failed
```

### Étape 5 : Configuration Initiale

1. **Activer les crons**
   ```
   Paramètres → Technique → Automatisation → Actions planifiées
   ```
   - Activer "Planificateur Comptage Cyclique"
   - Activer "Rappels Inventaires En Cours"

2. **Générer codes-barres pour emplacements principaux**
   ```
   Inventaire → Configuration → Emplacements → Générer Code-barres
   ```

3. **Créer une configuration de comptage cyclique** (optionnel)
   ```
   Inventaires → Configuration → Comptage Cyclique → Créer
   ```

---

## 🔄 Mise à Jour (Depuis v18.0.1.0.0)

### ⚠️ IMPORTANT : Sauvegarde

**Toujours sauvegarder avant mise à jour !**

```bash
# Arrêter Odoo
sudo systemctl stop odoo

# Sauvegarder la base de données
pg_dump -U odoo your_database > backup_$(date +%Y%m%d_%H%M%S).sql

# Sauvegarder le filestore (attachments)
tar -czf filestore_backup_$(date +%Y%m%d_%H%M%S).tar.gz /var/lib/odoo/filestore/your_database

# Sauvegarder le module actuel
cp -r /chemin/vers/odoo/addons/stockex /chemin/vers/backup/stockex_v18.0.1.0.0
```

### Étape 1 : Installer Nouvelles Dépendances

```bash
# Activer l'environnement virtuel
source /chemin/vers/odoo-venv/bin/activate

# Installer python-barcode (NOUVELLE dépendance)
pip install python-barcode

# Vérifier
python -c "import barcode; print('✅ barcode OK')"
```

### Étape 2 : Remplacer les Fichiers du Module

```bash
# Supprimer l'ancienne version
rm -rf /chemin/vers/odoo/addons/stockex

# Copier la nouvelle version
cp -r /chemin/vers/stockex_v18.0.2.0.0 /chemin/vers/odoo/addons/stockex

# Vérifier les permissions
chmod -R 755 /chemin/vers/odoo/addons/stockex
chown -R odoo:odoo /chemin/vers/odoo/addons/stockex
```

### Étape 3 : Mettre à Jour le Module

```bash
# Mettre à jour le module
odoo-bin -c /etc/odoo/odoo.conf -d your_database -u stockex --stop-after-init

# Ou via interface :
# Apps → Stockinv → Mettre à jour
```

### Étape 4 : Vérifier la Migration

#### A. Tests Automatiques

```bash
# Exécuter les tests
odoo-bin -d your_database -u stockex --test-enable --stop-after-init
```

**Vérifier** : 10 tests doivent passer

#### B. Vérifications Manuelles

```sql
-- Vérifier les nouveaux champs (psql)
\c your_database
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'stockex_stock_inventory_line' 
AND column_name IN ('scanned_barcode', 'image_1', 'image_2', 'image_3', 'note');

-- Résultat attendu : 5 lignes

SELECT column_name FROM information_schema.columns 
WHERE table_name = 'stockex_stock_inventory' 
AND column_name IN ('approver_id', 'approval_date', 'validator_id', 'validation_date');

-- Résultat attendu : 4 lignes
```

#### C. Vérifier les Nouveaux Modèles

```
Paramètres → Technique → Modèles de Données
Rechercher : "stockex"
```

**Nouveaux modèles attendus** :
- stockex.cycle.count.config
- stockex.cycle.count.scheduler
- stockex.inventory.comparison
- stockex.inventory.comparison.result
- stockex.stock.variance.report
- stockex.variance.analysis.wizard

#### D. Vérifier les Crons

```
Paramètres → Technique → Automatisation → Actions planifiées
Rechercher : "Stockex"
```

**3 crons attendus** :
- Stockex: Synchronisation Auto Kobo Collect
- Stockex: Planificateur Comptage Cyclique
- Stockex: Rappels Inventaires En Cours

### Étape 5 : Configuration Post-Migration

1. **Générer codes-barres emplacements existants**
   ```
   Pour chaque emplacement important :
   Inventaire → Configuration → Emplacements → Ouvrir → Générer Code-barres
   ```

2. **Tester le workflow d'approbation**
   ```
   Créer un inventaire test → Démarrer → Demander Approbation → Vérifier
   ```

3. **Tester le scan codes-barres**
   ```
   Créer ligne inventaire → Scanner un code-barres → Vérifier auto-remplissage
   ```

### Étape 6 : Redémarrer Odoo

```bash
# Redémarrer le service
sudo systemctl start odoo

# Vérifier le statut
sudo systemctl status odoo

# Surveiller les logs
tail -f /var/log/odoo/odoo.log
```

---

## ✅ Checklist Post-Installation/Migration

### Installation/Migration Technique
- [ ] Module installé/mis à jour sans erreur
- [ ] Tests unitaires passés (10/10)
- [ ] Nouveaux modèles créés (6 modèles)
- [ ] Nouveaux champs ajoutés (vérification SQL)
- [ ] Crons créés et visibles (3 crons)
- [ ] Pas d'erreurs dans logs Odoo
- [ ] Dépendances Python installées

### Configuration Fonctionnelle
- [ ] Crons activés (au moins 2/3)
- [ ] Codes-barres générés pour emplacements principaux
- [ ] Configuration comptage cyclique créée (optionnel)
- [ ] Workflow approbation testé
- [ ] Scan codes-barres testé
- [ ] Upload photo testé

### Tests Utilisateur
- [ ] Créer un inventaire avec scan codes-barres
- [ ] Ajouter des photos à une ligne
- [ ] Workflow approbation complet
- [ ] Générer un comptage cyclique
- [ ] Comparer deux inventaires
- [ ] Analyser variance de stock

---

## 🐛 Résolution de Problèmes

### Problème 1 : Module ne s'installe pas

**Symptôme** : Erreur lors de l'installation

**Solutions** :
1. Vérifier les dépendances Python
   ```bash
   pip install openpyxl python-barcode requests
   ```

2. Vérifier les permissions
   ```bash
   chmod -R 755 /chemin/vers/odoo/addons/stockex
   chown -R odoo:odoo /chemin/vers/odoo/addons/stockex
   ```

3. Vérifier les logs
   ```bash
   tail -f /var/log/odoo/odoo.log
   ```

### Problème 2 : Erreur "Module barcode not found"

**Solution** :
```bash
pip install python-barcode
sudo systemctl restart odoo
```

### Problème 3 : Nouveaux champs non visibles

**Solution** :
```bash
# Forcer la mise à jour
odoo-bin -d your_database -u stockex --stop-after-init

# Vider le cache navigateur
# Ctrl+Shift+R (Chrome/Firefox)
```

### Problème 4 : Tests échouent

**Diagnostic** :
```bash
odoo-bin -d your_database -u stockex --test-enable --stop-after-init --log-level=test
```

**Causes fréquentes** :
- Données de test manquantes (UdM, catégories)
- Droits d'accès insuffisants
- Séquence non créée

**Solution** :
```bash
# Réinstaller complètement
odoo-bin -d your_database -i stockex --test-enable --stop-after-init
```

### Problème 5 : Crons ne s'exécutent pas

**Vérifications** :
```sql
-- Vérifier l'état des crons
SELECT name, active, nextcall, numbercall 
FROM ir_cron 
WHERE name LIKE '%Stockex%';
```

**Solutions** :
1. Activer manuellement via interface
2. Vérifier la date de prochaine exécution
3. Vérifier les logs : `grep CRON /var/log/odoo/odoo.log`

### Problème 6 : Photos ne se chargent pas

**Vérifications** :
- Taille fichier (<5MB recommandé)
- Format supporté (JPEG, PNG)
- Permissions filestore : `/var/lib/odoo/filestore/your_database`

**Solution** :
```bash
chmod -R 755 /var/lib/odoo/filestore/your_database
chown -R odoo:odoo /var/lib/odoo/filestore/your_database
```

---

## 🔙 Rollback (Retour Arrière)

### Si Problème Majeur Après Mise à Jour

**Étape 1 : Arrêter Odoo**
```bash
sudo systemctl stop odoo
```

**Étape 2 : Restaurer la Base de Données**
```bash
# Supprimer la DB actuelle
dropdb -U odoo your_database

# Restaurer le backup
psql -U odoo -d postgres -c "CREATE DATABASE your_database OWNER odoo"
psql -U odoo your_database < backup_YYYYMMDD_HHMMSS.sql
```

**Étape 3 : Restaurer le Filestore**
```bash
rm -rf /var/lib/odoo/filestore/your_database
tar -xzf filestore_backup_YYYYMMDD_HHMMSS.tar.gz -C /
```

**Étape 4 : Restaurer l'Ancien Module**
```bash
rm -rf /chemin/vers/odoo/addons/stockex
cp -r /chemin/vers/backup/stockex_v18.0.1.0.0 /chemin/vers/odoo/addons/stockex
```

**Étape 5 : Redémarrer**
```bash
sudo systemctl start odoo
```

---

## 📊 Tableau de Compatibilité

| Stockex Version | Odoo Version | Python Version | PostgreSQL Version |
|----------------|--------------|----------------|-------------------|
| 18.0.2.0.0     | 18.0         | 3.10+          | 12+               |
| 18.0.1.0.0     | 18.0         | 3.10+          | 12+               |

---

## 📞 Support

### Avant de Contacter le Support

Préparer :
1. **Version Odoo** : `odoo-bin --version`
2. **Version Module** : Vérifier dans `__manifest__.py`
3. **Logs d'erreur** : Dernières 100 lignes
4. **Étapes de reproduction** du problème
5. **Screenshots** si applicable

### Contact

**Email** : contact@sorawel.com  
**Site Web** : [www.sorawel.com](https://www.sorawel.com)  
**Documentation** : Voir fichiers `.md` du module

---

## 📚 Documentation Complémentaire

- **[QUICK_START.md](QUICK_START.md)** - Guide de démarrage rapide
- **[NOUVELLES_FONCTIONNALITES.md](NOUVELLES_FONCTIONNALITES.md)** - Détails des nouvelles fonctionnalités
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Résumé technique
- **[CHANGELOG.md](CHANGELOG.md)** - Historique des versions
- **[README.md](README.md)** - Vue d'ensemble du module

---

**✅ Installation/Migration réussie ? Consultez le [QUICK_START.md](QUICK_START.md) pour commencer !**
