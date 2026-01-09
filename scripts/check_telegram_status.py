#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour vérifier l'état des notifications Telegram
"""

import xmlrpc.client

def check_telegram_notifications():
    """Vérifie l'état des notifications Telegram"""
    print("="*60)
    print("🔍 VÉRIFICATION DES NOTIFICATIONS TELEGRAM")
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
            'stockex.kobo.config', 'search_read',
            [[]],
            {'fields': ['name', 'telegram_enabled', 'last_sync']}
        )
        
        if not kobo_configs:
            print("❌ Aucune configuration Kobo trouvée")
            return False
            
        for config in kobo_configs:
            print(f"\n📋 Configuration: {config['name']}")
            print(f"   🔔 Notifications Telegram: {'✅ Activées' if config.get('telegram_enabled', False) else '❌ Désactivées'}")
            print(f"   🕐 Dernière synchronisation: {config.get('last_sync', 'Jamais')}")
            
        # Vérifier les paramètres système Telegram
        print("\n⚙️ Vérification des paramètres système Telegram...")
        try:
            # Tenter de récupérer les paramètres de configuration
            settings = models.execute_kw(
                db, uid, password,
                'res.config.settings', 'search_read',
                [[]],
                {'limit': 1}
            )
            
            if settings:
                setting = settings[0]
                telegram_token = setting.get('telegram_bot_token', '')
                telegram_chat_id = setting.get('telegram_chat_id', '')
                
                print(f"   🤖 Token Bot: {'✅ Configuré' if telegram_token else '❌ Non configuré'}")
                print(f"   👤 Chat ID: {'✅ Configuré' if telegram_chat_id else '❌ Non configuré'}")
            else:
                print("   ℹ️ Impossible de vérifier les paramètres système")
                
        except Exception as e:
            print(f"   ℹ️ Impossible de vérifier les paramètres système: {e}")
            
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
    check_telegram_notifications()