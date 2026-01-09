#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour tester la connexion au dashboard Odoo via XML-RPC
"""

import xmlrpc.client
import json

def test_odoo_connection():
    """Teste la connexion à Odoo et récupère les données du dashboard"""
    print("="*60)
    print("🔌 TEST DE CONNEXION AU DASHBOARD ODOO")
    print("="*60)
    
    try:
        # Configuration de connexion
        url = 'http://localhost:8069'  # Remplacer par votre URL Odoo
        db = 'eneo'  # Utilisation de la base de données eneo
        username = 'admin'  # Remplacer par votre nom d'utilisateur
        password = 'admin'  # Remplacer par votre mot de passe
        
        # Connexion
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        version = common.version()
        print(f"✅ Odoo version: {version.get('server_version')}")
        
        # Authentification
        uid = common.authenticate(db, username, password, {})
        if not uid:
            print("❌ Échec de l'authentification")
            return False
            
        print(f"✅ Authentifié avec l'UID: {uid}")
        
        # Accès aux modèles
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        
        # Vérifier les inventaires
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
        
        # Vérifier les produits
        product_count = models.execute_kw(
            db, uid, password,
            'product.product', 'search_count',
            [[('type', '=', 'product')]]
        )
        print(f"🛍️ Produits stockables: {product_count}")
        
        # Vérifier le résumé d'inventaire
        try:
            summary_ids = models.execute_kw(
                db, uid, password,
                'stockex.inventory.summary', 'search',
                [[]],
                {'limit': 1}
            )
            
            if summary_ids:
                summary_data = models.execute_kw(
                    db, uid, password,
                    'stockex.inventory.summary', 'read',
                    [summary_ids],
                    {'fields': [
                        'total_inventories_done',
                        'total_products_all', 
                        'total_quantity_all',
                        'total_value_all'
                    ]}
                )
                
                if summary_data:
                    summary = summary_data[0]
                    print(f"\n📈 Dashboard - Résumé:")
                    print(f"   • Inventaires validés: {summary.get('total_inventories_done', 0)}")
                    print(f"   • Produits référencés: {summary.get('total_products_all', 0)}")
                    print(f"   • Quantité totale: {summary.get('total_quantity_all', 0):,.0f}")
                    print(f"   • Valeur totale: {summary.get('total_value_all', 0):,.0f} FCFA")
                else:
                    print("\n⚠️ Aucune donnée de résumé disponible")
            else:
                print("\n⚠️ Aucun résumé d'inventaire trouvé")
        except Exception as e:
            print(f"\n⚠️ Dashboard non disponible: {str(e)}")

        # Vérifier les quantités de stock réel
        stock_quant_count = models.execute_kw(
            db, uid, password,
            'stock.quant', 'search_count',
            [[]]
        )
        print(f"\n📊 Quantités de stock enregistrées: {stock_quant_count}")
        
        if stock_quant_count > 0:
            # Récupérer quelques quantités pour vérification
            stock_quants = models.execute_kw(
                db, uid, password,
                'stock.quant', 'search_read',
                [[]],
                {
                    'fields': ['product_id', 'quantity', 'value'],
                    'limit': 5
                }
            )
            
            print("\n📋 Exemples de quantités de stock:")
            for quant in stock_quants:
                product_name = quant['product_id'][1] if quant['product_id'] else 'N/A'
                print(f"   • {product_name}: {quant['quantity']} unités, {quant['value']:,.2f} FCFA")
                
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_odoo_connection()
