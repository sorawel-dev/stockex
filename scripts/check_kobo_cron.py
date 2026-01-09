#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour vérifier l'état du CRON et tester la synchronisation
"""

import xmlrpc.client

def check_cron_status():
    """Vérifie l'état du CRON Kobo"""
    print("="*60)
    print("🔍 VÉRIFICATION DE L'ÉTAT DU CRON KOBO")
    print("="*60)
    
    try:
        # Configuration de connexion
        url = 'http://localhost:8069'
        db = 'eneo'
        username = input("Nom d'utilisateur Odoo: ")
        password = input("Mot de passe Odoo: ")
        
        print(f"\n🔗 Connexion à {url} avec la base '{db}'...")
        
        # Connexion
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        
        if not uid:
            print("❌ Échec de l'authentification")
            return False
            
        print(f"✅ Authentifié avec l'UID: {uid}")
        
        # Accès aux modèles
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        
        # Vérifier les configurations Kobo
        print("\n📊 Vérification des configurations Kobo...")
        kobo_configs = models.execute_kw(
            db, uid, password,
            'stockex.kobo.config', 'search_count',
            [[]]
        )
        print(f"   • Configurations Kobo: {kobo_configs}")
        
        if kobo_configs > 0:
            configs = models.execute_kw(
                db, uid, password,
                'stockex.kobo.config', 'search_read',
                [[]],
                {'limit': 5}
            )
            
            for config in configs:
                print(f"   • {config['name']} (Active: {config['active']})")
                print(f"     Auto-import: {config['auto_import']}")
                print(f"     CRON Actif: {config.get('cron_active', 'N/A')}")
                print(f"     Dernière sync: {config.get('last_sync', 'Jamais')}")
                
        # Vérifier le CRON système
        print("\n⏰ Vérification du CRON système...")
        cron_jobs = models.execute_kw(
            db, uid, password,
            'ir.cron', 'search_count',
            [[('name', 'ilike', 'kobo')]]
        )
        print(f"   • Jobs CRON Kobo: {cron_jobs}")
        
        if cron_jobs > 0:
            crons = models.execute_kw(
                db, uid, password,
                'ir.cron', 'search_read',
                [[('name', 'ilike', 'kobo')]]
            )
            
            for cron in crons:
                print(f"   • {cron['name']}")
                print(f"     Actif: {cron['active']}")
                print(f"     Intervalle: {cron['interval_number']} {cron['interval_type']}")
                print(f"     Prochaine exécution: {cron.get('nextcall', 'N/A')}")
                
        # Vérifier les soumissions Kobo
        print("\n📤 Vérification des soumissions Kobo...")
        submissions = models.execute_kw(
            db, uid, password,
            'stockex.kobo.submission', 'search_count',
            [[]]
        )
        print(f"   • Soumissions Kobo: {submissions}")
        
        print("\n" + "="*60)
        print("✅ VÉRIFICATION TERMINÉE")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    check_cron_status()