# 🚨 HOTFIX - Page Blanche sur odoo-minee.kesafrica.com

## Diagnostic

**Symptômes** :
- Page blanche à la connexion
- Console affiche `ERR_CONNECTION_RESET` 
- Assets CSS/JS ne se chargent pas (`/web/assets/...` en pending/timeout)
- Erreur SVG `Expected number` 
- TypeError `Failed to fetch at odoo.reloadMenus`

**Cause Racine** : Les assets compilés d'Odoo ne sont pas régénérés après le dernier commit (554ce6e).

---

## Solution Immédiate (À exécuter sur le serveur)

### 1. Se connecter au serveur

```bash
ssh user@odoo-minee.kesafrica.com
```

### 2. Identifier le container Odoo

```bash
docker ps | grep odoo
# Notez le nom du container (ex: odoo19, odoo-web, etc.)
```

### 3. Régénérer les assets

```bash
# Méthode 1: Redémarrage avec update (RECOMMANDÉ)
docker exec -it <container_name> odoo-bin -d <database_name> -u stockex --stop-after-init

# Méthode 2: Nettoyage cache + redémarrage
docker exec -it <container_name> rm -rf /var/lib/odoo/.local/share/Odoo/filestore/<database_name>/assets/*
docker restart <container_name>
```

### 4. Vérifier la résolution

```bash
# Attendre 30 secondes puis tester
curl -I https://odoo-minee.kesafrica.com/web/login
# Doit retourner 200 OK
```

---

## Solution Alternative (Si la première échoue)

### Rollback au commit précédent stable

```bash
# Sur le serveur, aller dans le répertoire du module
cd /path/to/odoo/addons/stockex

# Revenir au commit avant les nouvelles cartes
git checkout bf9c503

# Redémarrer Odoo
docker restart <container_name>
```

---

## Solution Permanente

### Après avoir testé le rollback, mettre à jour proprement

```bash
# Revenir sur main
git checkout main
git pull origin main

# Update avec regénération complète
docker exec -it <container_name> odoo-bin \
  -d <database_name> \
  -u stockex \
  --stop-after-init \
  --log-level=debug

# Vérifier les logs
docker logs <container_name> --tail 100 | grep -i "error\|exception\|asset"
```

---

## Détails Techniques

### Commit Problématique
- **Hash**: 554ce6e
- **Message**: "🚨 Ajout 2 cartes intelligentes au dashboard + redesign"
- **Fichiers modifiés**:
  - `models/inventory_dashboard.py` (+212 lignes)
  - `static/src/js/inventory_dashboard.js` (+70 lignes)  
  - `static/src/xml/inventory_dashboard.xml` (+197 lignes)

### Assets Affectés
- `web.assets_backend`:
  - `stockex/static/src/css/inventory_dashboard.css`
  - `stockex/static/src/js/inventory_dashboard.js`
  - `stockex/static/src/xml/inventory_dashboard.xml`

### Validation XML Locale
```bash
# Tous les fichiers sont valides localement
python3 -c "import xml.etree.ElementTree as ET; ET.parse('static/src/xml/inventory_dashboard.xml'); print('✅ OK')"
# Output: ✅ XML valide
```

---

## Checklist de Dépannage

- [ ] Vérifier que le serveur est accessible (`ping odoo-minee.kesafrica.com`)
- [ ] Vérifier que le container Odoo tourne (`docker ps`)
- [ ] Consulter les logs Odoo (`docker logs <container>`)
- [ ] Vérifier l'espace disque (`df -h`)
- [ ] Vérifier les permissions des fichiers statiques (`ls -la /path/to/stockex/static/`)
- [ ] Tenter regénération assets (voir Solution 3 ci-dessus)
- [ ] Si échec, rollback au commit bf9c503
- [ ] Après stabilisation, update proprement avec `-u stockex`

---

## Commits Stables de Référence

| Hash | Description | Date |
|------|-------------|------|
| **bf9c503** | ✅ ✨ Dashboard améliorations UI + sécurité | Stable |
| 3da2ed0 | ✅ feat: Dashboard inventaire optimisé avec cache | Stable |
| 554ce6e | ⚠️ 🚨 Ajout 2 cartes + redesign | **PROBLÉMATIQUE** |

---

## Contact

Si le problème persiste après ces étapes, vérifier :
1. Version d'Odoo sur le serveur (doit être 19.0)
2. Modules dépendants (`base`, `mail`, `stock`, `stock_account`)
3. Logs PostgreSQL (`docker logs <postgres_container>`)

---

---

## 🆕 Problème Chart.js (15/01/2026 09:34)

**Symptôme** : `AssetsLoadingError: The loading of /web/static/lib/Chart/Chart.js failed`

**Solution Appliquée** :
1. ✅ Nettoyage assets web via API XML-RPC
2. ✅ Upgrade module `web` pour régénérer Chart.js
3. ✅ Purge complète cache assets

**État** : Serveur instable après upgrades multiples

**Action Requise sur Serveur** :
```bash
# Se connecter au serveur
ssh -p 9209 root@odoo-minee.kesafrica.com

# Redémarrer le container Odoo
docker ps | grep odoo
docker restart <container_name>

# Attendre 30 secondes
sleep 30

# Vérifier que le service répond
curl -I http://localhost:8069/web/login

# Si timeout persistant, vérifier les logs
docker logs <container_name> --tail 50
```

**Validation** : Après redémarrage, accéder au dashboard Inventaire pour vérifier que Chart.js se charge sans erreur.

---

**Date**: 2026-01-15  
**Environnement**: odoo-minee.kesafrica.com  
**Module**: stockex v19.0.10.0.0  
**Port SSH**: 9209
