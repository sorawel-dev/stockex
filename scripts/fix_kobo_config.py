#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour résoudre le problème de configuration Kobo Collect.
Ce script désactive automatiquement la configuration "Configuration Kobo - Magasin Douala"
pour permettre l'activation d'une autre configuration.
"""

import sys
import os

# Ajouter le chemin du projet
sys.path.append('/home/one/apps/stockex')

def fix_kobo_configuration():
    """
    Désactive la configuration Kobo active pour permettre l'activation d'une autre.
    """
    try:
        # Importer Odoo
        import odoo
        from odoo import api, SUPERUSER_ID
        
        # Initialiser Odoo
        odoo.tools.config.parse_config(['-c', '/etc/odoo/odoo.conf'])
        odoo.service.server.start(preload=['eneo'], stop=True)
        
        with api.Environment.manage():
            with odoo.registry('eneo').cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                
                # Trouver la configuration "Configuration Kobo - Magasin Douala"
                KoboConfig = env['stockex.kobo.config']
                config_to_deactivate = KoboConfig.search([('name', '=', 'Configuration Kobo - Magasin Douala')])
                
                if config_to_deactivate:
                    # Désactiver la configuration
                    config_to_deactivate.write({'active': False})
                    print(f"✅ Configuration '{config_to_deactivate.name}' désactivée avec succès.")
                    
                    # Trouver d'autres configurations actives
                    other_active_configs = KoboConfig.search([
                        ('id', '!=', config_to_deactivate.id),
                        ('active', '=', True)
                    ])
                    
                    if other_active_configs:
                        print("Autres configurations actives :")
                        for config in other_active_configs:
                            print(f"  - {config.name}")
                    else:
                        print("_aucune autre configuration active.")
                else:
                    print("❌ Configuration 'Configuration Kobo - Magasin Douala' non trouvée.")
                    
                # Afficher toutes les configurations
                all_configs = KoboConfig.search([])
                print("\n📋 Toutes les configurations Kobo :")
                for config in all_configs:
                    status = "✅ Actif" if config.active else "❌ Inactif"
                    print(f"  {status} - {config.name}")
                    
    except Exception as e:
        print(f"❌ Erreur : {e}")
        sys.exit(1)

if __name__ == "__main__":
    fix_kobo_configuration()