# 🛠️ Résolution de l'Erreur CRON dans Stockex

## 📋 Problème rencontré

**Erreur** : `ParseError: while parsing /mnt/extra-addons/stockex/views/kobo_config_views.xml:4`
**Message** : `Le champ "cron_interval_number" n'existe pas dans le modèle "stockex.kobo.config"`

## 🔍 Cause

Lors de la mise à jour du module Stockex, Odoo tente de charger la vue XML **avant** de créer les nouveaux champs dans la base de données. Cela arrive lorsque :

1. Les nouveaux champs sont ajoutés au modèle Python
2. La vue XML est mise à jour pour utiliser ces champs
3. Le module est mis à jour sans redémarrage préalable

## ✅ Solution appliquée

### Étape 1 : Désactivation temporaire de la section CRON
```xml
<!-- Section CRON temporairement désactivée -->
```

### Étape 2 : Redémarrage du conteneur Odoo
```bash
docker restart odoo-service
```

### Étape 3 : Réactivation de la section CRON
Script [scripts/restore_cron_section.py](file:///home/one/apps/stockex/scripts/restore_cron_section.py) exécuté avec succès

### Étape 4 : Mise à jour du module dans Odoo
**Via l'interface Odoo** :
1. Applications → Mettre à jour la liste des applications
2. Rechercher "Stockex"
3. Cliquer sur "Mettre à jour"

## 🧪 Vérification

La section CRON est maintenant active dans la vue :
```xml
<separator string="⏰ Planification Import Automatique (CRON)"/>
<group>
    <group string="Intervalle d'Exécution">
        <label for="cron_interval_number" string="Exécuter toutes les"/>
        <div class="o_row">
            <field name="cron_interval_number" class="oe_inline"/>
            <field name="cron_interval_type" class="oe_inline"/>
        </div>
        <field name="cron_active" widget="boolean_toggle"/>
    </group>
    <!-- ... -->
</group>
```

## 🎯 Fonctionnalités disponibles

### Dans Odoo : Menu **Stockex → Configuration → Configuration Kobo Collect**

**Onglet "Options"** → Section "Planification CRON" :

1. **Configurer l'intervalle** :
   - Saisir le nombre (ex: 1, 2, 4, 30)
   - Sélectionner l'unité (Minutes, Heures, Jours, etc.)

2. **Activer/Désactiver le CRON** :
   - Toggle "CRON Actif" pour démarrer/arrêter

3. **Appliquer les changements** :
   - Cliquer sur "🔄 Appliquer l'Intervalle"
   - Notification de confirmation

## 📊 Interface Utilisateur

```
┌─────────────────────────────────────────────────┐
│ ⏰ Planification Import Automatique (CRON)      │
├─────────────────────────────────────────────────┤
│                                                  │
│ Intervalle d'Exécution                          │
│ ├─ Exécuter toutes les: [1] [Heures ▼]        │
│ └─ CRON Actif: [✓]                            │
│                                                  │
│ Actions                                          │
│ └─ [🔄 Appliquer l'Intervalle]                 │
│                                                  │
├─────────────────────────────────────────────────┤
│ 💡 Recommandations d'intervalle :              │
│ • 30 minutes : Inventaires très actifs          │
│ • 1 heure : ✅ Bon compromis (par défaut)      │
│ • 4 heures : Moins fréquents                    │
│ • 1 jour : Imports quotidiens                   │
└─────────────────────────────────────────────────┘
```

## ⚠️ Prévention future

Pour éviter ce problème à l'avenir :

1. **Toujours redémarrer Odoo** après modification du code Python
2. **Mettre à jour le module** via l'interface Odoo
3. **Utiliser des scripts de migration** pour les changements de structure
4. **Tester dans un environnement de développement** avant production

## 📞 Support

Si l'erreur persiste :
1. Vérifier que le conteneur Odoo est redémarré
2. Confirmer que les champs existent dans [models/kobo_config.py](file:///home/one/apps/stockex/models/kobo_config.py)
3. Mettre à jour le module via l'interface Odoo
4. Consulter les logs Odoo : `docker logs odoo-service`

---

**Date** : 2025-11-04  
**Version** : 1.0  
**Statut** : ✅ Résolu
