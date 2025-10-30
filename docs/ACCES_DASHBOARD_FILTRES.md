# 🔍 Comment Accéder au Dashboard avec Filtres

## ✅ Problème Résolu

Les filtres sont maintenant visibles et fonctionnels sur le dashboard !

---

## 📍 **Comment Accéder au Dashboard**

### **Méthode 1 : Via le Menu Principal**

```
Stock → Dashboard → Vue d'Ensemble
```

**OU**

```
Stock → Dashboard Inventaire
```

---

### **Méthode 2 : Via le Menu Accueil**

1. Cliquer sur le logo Odoo (en haut à gauche)
2. Dans les applications, chercher **"Stockex"**
3. Cliquer sur l'application
4. Vous arrivez sur le dashboard

---

## 🔍 **Ce que Vous Devez Voir**

Une fois sur le dashboard, vous devriez voir :

```
┌─────────────────────────────────────────────────┐
│ 📊 Dashboard Inventaire                         │
│ Filtrez et analysez vos inventaires en temps réel│
├─────────────────────────────────────────────────┤
│ 🔍 Filtres                                      │
│                                                 │
│ Période: [Toute la période ▼]                  │
│ Valeur: [Toutes valeurs ▼]                     │
│ Écarts: [Tous les écarts ▼]                    │
│                                                 │
│ Catégories: [+ Ajouter]                        │
│ Entrepôts: [+ Ajouter]                         │
│ Emplacements: [+ Ajouter]                      │
│                                                 │
│ [🔍 Appliquer] [🔄 Réinitialiser] [📋 Voir]    │
│                                                 │
│ 🚀 Filtres Rapides:                            │
│ [📅 Ce Mois] [💎 Haute Valeur] [⚠️ Écarts]    │
├─────────────────────────────────────────────────┤
│ 📈 Vue d'Ensemble | 💰 Valeurs                 │
│ ...                                            │
└─────────────────────────────────────────────────┘
```

---

## 🎯 **Test Rapide**

### Étape 1 : Vider le Cache

1. **Ctrl + Shift + R** (ou **Cmd + Shift + R** sur Mac)
2. Cela force le rechargement complet de la page

### Étape 2 : Accéder au Dashboard

1. Menu **Stock**
2. Cliquer sur **Dashboard** ou **Vue d'Ensemble**

### Étape 3 : Vérifier les Filtres

Vous devriez voir :
- ✅ Section "🔍 Filtres" en haut
- ✅ Champs de sélection modifiables
- ✅ Boutons "Appliquer" et "Réinitialiser"
- ✅ Filtres rapides (3 boutons)

---

## 🧪 **Test des Filtres**

### Test 1 : Filtre de Période

```
1. Dans "Période", sélectionner "Ce Mois"
2. Cliquer "🔍 Appliquer Filtres"
3. Observer : Une notification verte apparaît
4. Les stats se mettent à jour
```

### Test 2 : Filtre Rapide

```
1. Cliquer directement sur "📅 Ce Mois"
2. Observer : Application instantanée
3. Bannière verte : "✅ Filtres actifs: Ce Mois"
```

### Test 3 : Filtre par Catégorie

```
1. Dans "Catégories", cliquer sur le champ
2. Sélectionner une ou plusieurs catégories
3. Cliquer "🔍 Appliquer Filtres"
4. Observer : Stats filtrées par catégorie
```

---

## 🛠️ **Si les Filtres Ne Sont Toujours Pas Visibles**

### Solution 1 : Vider le Cache Navigateur

**Chrome/Edge:**
```
1. Ctrl + Shift + Delete
2. Cocher "Images et fichiers en cache"
3. Cliquer "Effacer les données"
4. Actualiser la page (F5)
```

**Firefox:**
```
1. Ctrl + Shift + Delete
2. Cocher "Cache"
3. Cliquer "Effacer maintenant"
4. Actualiser la page (F5)
```

### Solution 2 : Mode Navigation Privée

1. Ouvrir une fenêtre de navigation privée
2. Se connecter à Odoo
3. Accéder au dashboard
4. Les filtres devraient être visibles

### Solution 3 : Forcer la Mise à Jour des Vues

En ligne de commande :

```bash
odoo -d eneo --addons-path=/home/one/apps --stop-after-init -u stockex
sudo systemctl restart odoo
```

### Solution 4 : Mode Debug

1. Activer le mode debug :
   - URL : Ajouter `?debug=1` à la fin
   - Ex: `http://localhost:8069/web?debug=1`

2. Aller dans le dashboard

3. Les filtres devraient être visibles en mode debug

---

## 📸 **Capture d'Écran Attendue**

Voici ce que vous devriez voir :

```
┌──────────────────────────────────────────────────────────────┐
│ 📊 Dashboard Inventaire                                      │
│ Filtrez et analysez vos inventaires en temps réel           │
├──────────────────────────────────────────────────────────────┤
│ 🔍 Filtres ▼                                                 │
│ ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│ │ Période     │ Valeur      │ Écarts      │             │  │
│ │ [▼ Menu]    │ [▼ Menu]    │ [▼ Menu]    │             │  │
│ └─────────────┴─────────────┴─────────────┴─────────────┘  │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Catégories:    [+ Ajouter une catégorie]               │ │
│ │ Entrepôts:     [+ Ajouter un entrepôt]                 │ │
│ │ Emplacements:  [+ Ajouter un emplacement]              │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                              │
│ [🔍 Appliquer Filtres]  [🔄 Réinitialiser]  [📋 Voir...]   │
│                                                              │
│ 🚀 Filtres Rapides:                                         │
│ [📅 Ce Mois]  [💎 Haute Valeur]  [⚠️ Écarts Importants]    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ 📈 Vue d'Ensemble              💰 Valeurs                   │
│ ┌──────────────┐              ┌──────────────┐             │
│ │ ...          │              │ ...          │             │
```

---

## ❓ **Questions Fréquentes**

### Q1 : Je vois le dashboard mais pas les filtres

**R :** 
1. Vider le cache (Ctrl + Shift + R)
2. Vérifier que vous êtes bien sur "Dashboard Inventaire"
3. Essayer en mode navigation privée

### Q2 : Les champs de filtres sont grisés

**R :** C'est normal au départ. Cliquez dans un champ pour le modifier.

### Q3 : Le bouton "Appliquer" ne fait rien

**R :** 
1. Vérifier qu'un filtre est bien sélectionné
2. Regarder en haut à droite : une notification devrait apparaître
3. Les stats se mettent à jour automatiquement

### Q4 : Comment retirer tous les filtres ?

**R :** Cliquer sur le bouton "🔄 Réinitialiser"

### Q5 : Les filtres rapides fonctionnent ?

**R :** Oui ! Cliquez sur "📅 Ce Mois" pour tester. Une notification verte devrait apparaître.

---

## 🔧 **Modifications Techniques Appliquées**

1. ✅ Vue formulaire : Passage en mode édition
2. ✅ Action dashboard : Context `'edit'` au lieu de `'readonly'`
3. ✅ Champs filtres : Tous modifiables (required="0")
4. ✅ Layout optimisé : Grid 4 colonnes
5. ✅ Module mis à jour : v18.0.3.2.0
6. ✅ Odoo redémarré : Service actif

---

## 📞 **Support**

Si les filtres ne sont toujours pas visibles après avoir suivi ce guide :

1. **Envoyer une capture d'écran** de votre dashboard actuel
2. **Vérifier la version** : Doit être v18.0.3.2.0
3. **Vérifier les logs Odoo** :
   ```bash
   sudo tail -f /var/log/odoo/odoo-server.log
   ```

---

## ✅ **Checklist de Vérification**

Avant de signaler un problème, vérifier :

- [ ] Cache navigateur vidé (Ctrl + Shift + R)
- [ ] Module stockex à jour (v18.0.3.2.0)
- [ ] Odoo redémarré
- [ ] Accès via le bon menu (Stock → Dashboard)
- [ ] Mode navigation privée testé
- [ ] Mode debug activé (`?debug=1`)

---

**Si tout est coché et que les filtres ne sont toujours pas visibles, contactez le support technique.**

---

**Document créé le 25 octobre 2025**  
**Version Stockex : 18.0.3.2.0**  
**Problème : Filtres non visibles - RÉSOLU ✅**
