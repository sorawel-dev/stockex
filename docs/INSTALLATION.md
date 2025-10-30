# 🚀 Guide d'Installation - Module Stockex

**Module :** Gestion d'Inventaire de Stock  
**Version :** 18.0.1.0.0  
**Odoo :** 18.0  
**Statut :** ✅ Production Ready - 100% Conforme

---

## ✅ Prérequis

- [x] Odoo 18.0 installé et configuré
- [x] Base de données créée
- [x] Modules dépendants : `base`, `mail`, `stock`, `product`
- [x] Permissions d'écriture sur `/home/one/apps/stockex`

---

## 📦 Installation

### Méthode 1 : Interface Web (Recommandée)

#### Étape 1 : Activer le Mode Développeur
1. Connectez-vous à Odoo : http://localhost:8070
2. Allez dans **Paramètres** (⚙️)
3. Scrollez en bas et cliquez sur **Activer le mode développeur**

#### Étape 2 : Mettre à Jour la Liste des Apps
1. Allez dans **Applications** (menu principal)
2. Cliquez sur **⋮** (trois points) → **Mettre à jour la liste des Apps**
3. Cliquez sur **Mettre à jour**
4. Attendez la fin du processus (quelques secondes)

#### Étape 3 : Installer le Module
1. Dans la barre de recherche des applications, tapez : `Stockinv`
2. Vous devriez voir :
   ```
   📦 Stockinv
   Module de gestion avancée des inventaires de stock
   Par: Sorawel, www.sorawel.com
   Version: 18.0.1.0.0
   ```
3. Cliquez sur **Installer** / **Install**
4. Attendez l'installation (environ 10-20 secondes)

#### Étape 4 : Vérification
✅ Un nouveau menu **"Gestion de Stock"** avec icône 📦 apparaît dans la barre latérale  
✅ Cliquez dessus → Vous voyez **"Inventaires"**  
✅ Cliquez sur **Inventaires** → La vue liste s'ouvre  
✅ Cliquez sur **Nouveau** → Le formulaire s'ouvre  

**🎉 Installation réussie !**

---

### Méthode 2 : Ligne de Commande (Développeurs)

```bash
# Arrêter Odoo (si nécessaire)
sudo systemctl stop odoo

# Installer le module
sudo -u odoo odoo-bin -c /etc/odoo/odoo.conf -d eneo -i stockex --stop-after-init

# Redémarrer Odoo
sudo systemctl start odoo

# Vérifier les logs
sudo tail -f /var/log/odoo/odoo-server.log
```

---

## 🔍 Vérification de l'Installation

### Test 1 : Menu Visible
- [ ] Le menu **"Gestion de Stock"** est visible
- [ ] L'icône 📦 (fa-boxes) s'affiche correctement
- [ ] Le sous-menu **"Inventaires"** est accessible

### Test 2 : Créer un Inventaire
1. Cliquez sur **Gestion de Stock** → **Inventaires**
2. Cliquez sur **Nouveau**
3. Remplissez :
   - Référence : (auto) ou saisir "INV-001"
   - Date : Aujourd'hui
   - Responsable : (votre utilisateur)
4. Cliquez sur **Sauvegarder**
5. Vérifiez que l'état est **"Brouillon"** (badge bleu)

### Test 3 : Ajouter des Lignes
1. Dans l'onglet **"Lignes d'inventaire"**
2. Ajoutez une ligne (cliquez dans le tableau)
3. Sélectionnez un produit
4. Saisissez une quantité réelle
5. Vérifiez que la différence se calcule automatiquement

### Test 4 : Workflow
1. Cliquez sur **Démarrer** → État passe à **"En cours"** (badge orange)
2. Cliquez sur **Valider** → État passe à **"Validé"** (badge vert)
3. Vérifiez que les boutons changent selon l'état

### Test 5 : Chatter
1. Scrollez en bas du formulaire
2. Vérifiez la présence du **Chatter**
3. Testez l'ajout d'un message
4. Testez l'ajout d'une activité

---

## 🎨 Fonctionnalités à Tester

### Vue Liste
- [x] Décorations de couleur selon état (bleu/orange/vert/gris)
- [x] Avatar utilisateur avec photo
- [x] Badge coloré pour l'état
- [x] Filtres de recherche fonctionnels

### Vue Formulaire
- [x] Boutons contextuels (visibles selon état)
- [x] Barre de statut (workflow visuel)
- [x] Champs readonly selon état
- [x] Lignes éditables en mode inline
- [x] Décorations sur lignes (rouge/orange pour différences)
- [x] Chatter complet (messages, activités, followers)

### Vue Recherche
- [x] Recherche par référence
- [x] Filtres : Brouillon, En cours, Validé
- [x] Filtre "Mes inventaires"
- [x] Filtre "Ce mois"
- [x] Groupements : État, Date, Emplacement, Responsable

---

## 🐛 Dépannage

### Problème : Module non visible dans la liste

**Solution :**
```bash
# Vérifier que le module est dans le bon dossier
ls -la /home/one/apps/stockex/__manifest__.py

# Redémarrer Odoo
sudo systemctl restart odoo

# Mettre à jour la liste des apps (interface web)
```

### Problème : Erreur à l'installation

**Vérifier les logs :**
```bash
sudo tail -100 /var/log/odoo/odoo-server.log | grep -i error
```

**Vérifier la syntaxe Python :**
```bash
python3 -m py_compile /home/one/apps/stockex/models/models.py
```

**Vérifier la syntaxe XML :**
```bash
python3 -c "import xml.etree.ElementTree as ET; ET.parse('/home/one/apps/stockex/views/stock_inventory_views.xml')"
```

### Problème : Permissions

**Corriger les permissions :**
```bash
sudo chown -R odoo:odoo /home/one/apps/stockex
sudo chmod -R 755 /home/one/apps/stockex
```

### Problème : Dépendances manquantes

**Installer les modules requis :**
1. Assurez-vous que `stock` et `mail` sont installés
2. Allez dans Applications
3. Recherchez et installez : "Inventory" et "Discuss"

---

## 📊 Après l'Installation

### Premiers Pas

1. **Créez votre premier inventaire**
   - Menu : Gestion de Stock → Inventaires → Nouveau
   - Remplissez les informations de base
   - Sauvegardez

2. **Ajoutez des lignes**
   - Onglet "Lignes d'inventaire"
   - Ajoutez vos produits
   - Saisissez les quantités

3. **Validez le workflow**
   - Démarrer → En cours
   - Valider → Validé

### Configuration Recommandée

- [ ] Créer des emplacements de stock
- [ ] Configurer les produits
- [ ] Définir les responsables
- [ ] Paramétrer les notifications email

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| `README.md` | Guide utilisateur complet |
| `NOTES_TECHNIQUES.md` | Documentation technique |
| `CHANGELOG_ODOO18.md` | Changements Odoo 18 |
| `CONFORMITE_ODOO18.md` | Rapport de conformité |
| `INSTALLATION.md` | Ce guide (installation) |

---

## 🆘 Support

### Logs Odoo
```bash
# Logs en temps réel
sudo tail -f /var/log/odoo/odoo-server.log

# Rechercher des erreurs
sudo grep -i error /var/log/odoo/odoo-server.log | tail -50
```

### Mode Debug
1. Activez le mode développeur avec assets
2. Ouvrez la console développeur du navigateur (F12)
3. Vérifiez les erreurs JavaScript

### Réinstallation Propre
```bash
# Désinstaller
# Via interface : Applications → Stockinv → Désinstaller

# Nettoyer (si nécessaire)
# Puis réinstaller via interface web
```

---

## ✅ Checklist Post-Installation

- [ ] Module installé sans erreur
- [ ] Menu "Gestion de Stock" visible
- [ ] Création d'inventaire fonctionne
- [ ] Workflow (Démarrer/Valider) opérationnel
- [ ] Lignes d'inventaire éditables
- [ ] Calcul automatique des différences
- [ ] Chatter fonctionnel
- [ ] Filtres de recherche actifs
- [ ] Décorations visuelles affichées
- [ ] Pas d'erreur dans les logs

---

## 🎉 Installation Terminée !

Votre module **Stockex** est maintenant installé et prêt à l'emploi.

**Prochaines étapes :**
1. Créez votre premier inventaire de test
2. Explorez les fonctionnalités
3. Configurez selon vos besoins
4. Formez vos utilisateurs

**Bon inventaire ! 📦**

---

**Version :** 18.0.1.0.0  
**Date :** 18 Octobre 2025  
**Auteur :** Sorawel, www.sorawel.com  
**Support :** https://www.sorawel.com
