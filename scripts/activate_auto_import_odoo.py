#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour activer l'import automatique Kobo → Odoo toutes les 30 minutes
Usage: python3 activate_auto_import_odoo.py
"""

import sys
import os

# Chemin vers Odoo
ODOO_PATH = '/home/one/odoo'
sys.path.insert(0, ODOO_PATH)

# Configuration
DB_NAME = 'odoo'  # ⚠️ Remplacer par le nom de votre base de données Odoo
ADMIN_PASSWORD = 'admin'  # ⚠️ Remplacer par le mot de passe admin

try:
    import odoo
    from odoo import api, SUPERUSER_ID
    
    print("\n" + "="*70)
    print("🔧 ACTIVATION IMPORT AUTOMATIQUE KOBO → ODOO")
    print("="*70)
    print()
    
    # Initialiser Odoo
    odoo.tools.config.parse_config([])
    odoo.tools.config['db_name'] = DB_NAME
    
    registry = odoo.registry(DB_NAME)
    
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        
        print("📋 ÉTAPE 1/3: Recherche du CRON...")
        
        # Trouver le CRON
        cron = env.ref('stockex.ir_cron_kobo_auto_sync', raise_if_not_found=False)
        
        if not cron:
            print("❌ CRON 'ir_cron_kobo_auto_sync' non trouvé")
            print("   Vérifiez que le module stockex est bien installé")
            sys.exit(1)
        
        print(f"✅ CRON trouvé: {cron.name}")
        print(f"   État actuel: {'Actif' if cron.active else 'Inactif'}")
        print(f"   Intervalle actuel: {cron.interval_number} {cron.interval_type}")
        print()
        
        print("📋 ÉTAPE 2/3: Configuration du CRON...")
        
        # Configurer le CRON pour 30 minutes
        cron.write({
            'active': True,
            'interval_number': 30,
            'interval_type': 'minutes',
        })
        
        print("✅ CRON configuré:")
        print("   • Actif: Oui")
        print("   • Intervalle: 30 minutes")
        print(f"   • Prochaine exécution: {cron.nextcall}")
        print()
        
        print("📋 ÉTAPE 3/3: Activation import automatique dans la configuration...")
        
        # Trouver les configurations Kobo actives
        configs = env['stockex.kobo.config'].search([('active', '=', True)])
        
        if not configs:
            print("⚠️  Aucune configuration Kobo active trouvée")
            print("   Créez d'abord une configuration dans Odoo")
            print("   (Inventaire → Configuration → Kobo Collect)")
            sys.exit(1)
        
        print(f"✅ {len(configs)} configuration(s) active(s) trouvée(s):")
        print()
        
        for config in configs:
            print(f"   📝 {config.name}")
            print(f"      • Import auto: {'Oui' if config.auto_import else 'Non'}")
            print(f"      • Validation auto: {'Oui' if config.auto_validate else 'Non'}")
            
            # Activer l'import automatique
            config.write({
                'auto_import': True,
                'cron_interval_number': 30,
                'cron_interval_type': 'minutes',
            })
            
            print(f"      ✅ Import automatique ACTIVÉ (30 minutes)")
            print()
        
        cr.commit()
        
        print("="*70)
        print("✅ CONFIGURATION TERMINÉE !")
        print("="*70)
        print()
        print("📊 Résumé:")
        print(f"   • CRON actif: Oui")
        print(f"   • Intervalle: 30 minutes")
        print(f"   • Configurations activées: {len(configs)}")
        print(f"   • Prochaine synchronisation: {cron.nextcall}")
        print()
        print("🔄 Le système va maintenant synchroniser automatiquement")
        print("   les soumissions Kobo vers Odoo toutes les 30 minutes.")
        print()
        print("💡 Pour vérifier les logs:")
        print("   • Odoo: Paramètres → Technique → Tâches planifiées")
        print("   • Logs: docker logs -f <container_odoo> | grep Kobo")
        print()
        print("="*70)
        print()
        
except ImportError as e:
    print(f"❌ Erreur d'import Odoo: {e}")
    print(f"   Vérifiez que le chemin Odoo est correct: {ODOO_PATH}")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour activer l'import automatique Kobo → Odoo toutes les 30 minutes
Usage: python3 activate_auto_import_odoo.py
"""

import sys
import os

# Chemin vers Odoo
ODOO_PATH = '/home/one/odoo'
sys.path.insert(0, ODOO_PATH)

# Configuration
DB_NAME = 'odoo'  # ⚠️ Remplacer par le nom de votre base de données Odoo
ADMIN_PASSWORD = 'admin'  # ⚠️ Remplacer par le mot de passe admin

try:
    import odoo
    from odoo import api, SUPERUSER_ID
    
    print("\n" + "="*70)
    print("🔧 ACTIVATION IMPORT AUTOMATIQUE KOBO → ODOO")
    print("="*70)
    print()
    
    # Initialiser Odoo
    odoo.tools.config.parse_config([])
    odoo.tools.config['db_name'] = DB_NAME
    
    registry = odoo.registry(DB_NAME)
    
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        
        print("📋 ÉTAPE 1/3: Recherche du CRON...")
        
        # Trouver le CRON
        cron = env.ref('stockex.ir_cron_kobo_auto_sync', raise_if_not_found=False)
        
        if not cron:
            print("❌ CRON 'ir_cron_kobo_auto_sync' non trouvé")
            print("   Vérifiez que le module stockex est bien installé")
            sys.exit(1)
        
        print(f"✅ CRON trouvé: {cron.name}")
        print(f"   État actuel: {'Actif' if cron.active else 'Inactif'}")
        print(f"   Intervalle actuel: {cron.interval_number} {cron.interval_type}")
        print()
        
        print("📋 ÉTAPE 2/3: Configuration du CRON...")
        
        # Configurer le CRON pour 30 minutes
        cron.write({
            'active': True,
            'interval_number': 30,
            'interval_type': 'minutes',
        })
        
        print("✅ CRON configuré:")
        print("   • Actif: Oui")
        print("   • Intervalle: 30 minutes")
        print(f"   • Prochaine exécution: {cron.nextcall}")
        print()
        
        print("📋 ÉTAPE 3/3: Activation import automatique dans la configuration...")
        
        # Trouver les configurations Kobo actives
        configs = env['stockex.kobo.config'].search([('active', '=', True)])
        
        if not configs:
            print("⚠️  Aucune configuration Kobo active trouvée")
            print("   Créez d'abord une configuration dans Odoo")
            print("   (Inventaire → Configuration → Kobo Collect)")
            sys.exit(1)
        
        print(f"✅ {len(configs)} configuration(s) active(s) trouvée(s):")
        print()
        
        for config in configs:
            print(f"   📝 {config.name}")
            print(f"      • Import auto: {'Oui' if config.auto_import else 'Non'}")
            print(f"      • Validation auto: {'Oui' if config.auto_validate else 'Non'}")
            
            # Activer l'import automatique
            config.write({
                'auto_import': True,
                'cron_interval_number': 30,
                'cron_interval_type': 'minutes',
            })
            
            print(f"      ✅ Import automatique ACTIVÉ (30 minutes)")
            print()
        
        cr.commit()
        
        print("="*70)
        print("✅ CONFIGURATION TERMINÉE !")
        print("="*70)
        print()
        print("📊 Résumé:")
        print(f"   • CRON actif: Oui")
        print(f"   • Intervalle: 30 minutes")
        print(f"   • Configurations activées: {len(configs)}")
        print(f"   • Prochaine synchronisation: {cron.nextcall}")
        print()
        print("🔄 Le système va maintenant synchroniser automatiquement")
        print("   les soumissions Kobo vers Odoo toutes les 30 minutes.")
        print()
        print("💡 Pour vérifier les logs:")
        print("   • Odoo: Paramètres → Technique → Tâches planifiées")
        print("   • Logs: docker logs -f <container_odoo> | grep Kobo")
        print()
        print("="*70)
        print()
        
except ImportError as e:
    print(f"❌ Erreur d'import Odoo: {e}")
    print(f"   Vérifiez que le chemin Odoo est correct: {ODOO_PATH}")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
