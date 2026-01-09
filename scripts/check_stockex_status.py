#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour vérifier l'état du module Stockex et des données
"""

import xmlrpc.client

def check_stockex_status():
    """Vérifie l'état du module Stockex et des données"""
    print("="*60)
    print("🔍 VÉRIFICATION DE L'ÉTAT DU MODULE STOCKEX")
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
        
        # Vérifier le module Stockex
        print("\n📦 Vérification du module Stockex...")
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
                {'fields': ['name', 'state', 'latest_version']}
            )
            
            if module_data:
                module = module_data[0]
                print(f"   • Nom: {module['name']}")
                print(f"   • État: {module['state']}")
                print(f"   • Version: {module.get('latest_version', 'N/A')}")
                
                if module['state'] != 'installed':
                    print("⚠️ Le module n'est pas installé correctement")
                    return False
            else:
                print("❌ Impossible de lire les données du module")
                return False
        else:
            print("❌ Module Stockex non trouvé")
            return False
            
        # Vérifier les configurations Kobo
        print("\n📡 Vérification des configurations Kobo...")
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
                {'limit': 3}
            )
            
            for config in configs:
                print(f"   • {config['name']} (Active: {config['active']})")
                
        # Vérifier les inventaires
        print("\n📋 Vérification des inventaires...")
        inventory_count = models.execute_kw(
            db, uid, password,
            'stockex.stock.inventory', 'search_count',
            [[]]
        )
        print(f"   • Inventaires totaux: {inventory_count}")
        
        # Compter par état
        states = ['draft', 'in_progress', 'done', 'cancel']
        for state in states:
            count = models.execute_kw(
                db, uid, password,
                'stockex.stock.inventory', 'search_count',
                [[('state', '=', state)]]
            )
            state_label = dict([
                ('draft', 'Brouillon'),
                ('in_progress', 'En cours'),
                ('done', 'Validé'),
                ('cancel', 'Annulé')
            ]).get(state, state)
            print(f"   • {state_label}: {count}")
            
        # Vérifier les lignes d'inventaire
        if inventory_count > 0:
            line_count = models.execute_kw(
                db, uid, password,
                'stockex.stock.inventory.line', 'search_count',
                [[]]
            )
            print(f"   • Lignes d'inventaire: {line_count}")
            
            if line_count > 0:
                # Calculer la quantité totale
                total_qty = models.execute_kw(
                    db, uid, password,
                    'stockex.stock.inventory.line', 'read_group',
                    [[], ['product_qty:sum']],
                    {}
                )
                print(f"   • Quantité totale: {total_qty[0]['product_qty'] if total_qty else 0}")
                
        # Vérifier les produits
        print("\n🛍️ Vérification des produits...")
        product_count = models.execute_kw(
            db, uid, password,
            'product.product', 'search_count',
            [[('type', '=', 'product')]]
        )
        print(f"   • Produits stockables: {product_count}")
        
        # Vérifier le résumé d'inventaire
        print("\n📈 Vérification du dashboard...")
        try:
            summary_count = models.execute_kw(
                db, uid, password,
                'stockex.inventory.summary', 'search_count',
                [[]]
            )
            print(f"   • Résumés d'inventaire: {summary_count}")
            
            if summary_count > 0:
                summary = models.execute_kw(
                    db, uid, password,
                    'stockex.inventory.summary', 'search_read',
                    [[]],
                    {'limit': 1}
                )
                
                if summary:
                    s = summary[0]
                    print(f"   • Inventaires validés: {s.get('total_inventories_done', 0)}")
                    print(f"   • Produits référencés: {s.get('total_products_all', 0)}")
                    print(f"   • Quantité totale: {s.get('total_quantity_all', 0)}")
                    print(f"   • Valeur totale: {s.get('total_value_all', 0)}")
        except Exception as e:
            print(f"   ⚠️ Dashboard non disponible: {str(e)}")
            
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
    check_stockex_status()
