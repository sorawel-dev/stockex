#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple pour vérifier l'état de la base de données eneo
"""

import xmlrpc.client
import json

def test_eneo_database():
    """Teste la connexion à la base de données eneo"""
    print("="*60)
    print("🔌 TEST DE CONNEXION À LA BASE DE DONNÉES ENEO")
    print("="*60)
    
    try:
        # Configuration de connexion
        url = 'http://localhost:8069'
        db = 'eneo'
        username = 'admin'
        password = 'admin'  # À adapter selon votre configuration
        
        print(f"🔗 Tentative de connexion à {url} avec la base '{db}'...")
        
        # Connexion
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        
        # Vérifier la version
        try:
            version = common.version()
            print(f"✅ Serveur Odoo accessible - Version: {version.get('server_version', 'Inconnue')}")
        except Exception as e:
            print(f"⚠️ Impossible de récupérer la version: {e}")
        
        # Authentification
        uid = common.authenticate(db, username, password, {})
        if not uid:
            print("❌ Échec de l'authentification - Vérifiez vos identifiants")
            print("💡 Essayez avec les identifiants de votre interface Odoo")
            return False
            
        print(f"✅ Authentifié avec l'UID: {uid}")
        
        # Accès aux modèles
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        
        # Vérifier si le module stockex est installé
        try:
            module_ids = models.execute_kw(
                db, uid, password,
                'ir.module.module', 'search',
                [[('name', '=', 'stockex')]]
            )
            
            if module_ids:
                module_data = models.execute_kw(
                    db, uid, password,
                    'ir.module.module', 'read',
                    [module_ids],
                    {'fields': ['name', 'state']}
                )
                
                if module_data:
                    module = module_data[0]
                    state = module['state']
                    print(f"📦 Module Stockex: {state}")
                    if state != 'installed':
                        print("⚠️ Le module Stockex n'est pas installé")
                        print("💡 Allez dans Applications et installez le module Stockex")
                else:
                    print("⚠️ Module Stockex non trouvé")
            else:
                print("❌ Module Stockex non trouvé dans la base")
                
        except Exception as e:
            print(f"⚠️ Impossible de vérifier le module: {e}")
        
        # Vérifier les inventaires
        try:
            inventory_count = models.execute_kw(
                db, uid, password,
                'stockex.stock.inventory', 'search_count',
                [[]]
            )
            print(f"📦 Nombre total d'inventaires: {inventory_count}")
            
            # Vérifier les inventaires validés
            done_inventory_count = models.execute_kw(
                db, uid, password,
                'stockex.stock.inventory', 'search_count',
                [[('state', '=', 'done')]]
            )
            print(f"✅ Inventaires validés: {done_inventory_count}")
            
        except Exception as e:
            print(f"⚠️ Impossible de vérifier les inventaires: {e}")
            print("💡 Le module Stockex n'est probablement pas installé")
            
        # Vérifier les produits
        try:
            product_count = models.execute_kw(
                db, uid, password,
                'product.product', 'search_count',
                [[('type', '=', 'product')]]
            )
            print(f"🛍️ Produits stockables: {product_count}")
        except Exception as e:
            print(f"⚠️ Impossible de vérifier les produits: {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        print("\n💡 Solutions possibles:")
        print("   1. Vérifiez que le serveur Odoo est démarré (http://localhost:8069)")
        print("   2. Vérifiez vos identifiants de connexion")
        print("   3. Assurez-vous que la base 'eneo' existe")
        print("   4. Installez le module Stockex si ce n'est pas fait")
        return False

if __name__ == '__main__':
    test_eneo_database()
