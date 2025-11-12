#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour vérifier l'état des inventaires dans Odoo
"""

import sys
import os

# Ajouter le chemin du module Odoo
sys.path.append('/usr/lib/python3/dist-packages')

try:
    import odoo
    from odoo import api, SUPERUSER_ID
    from datetime import datetime
    
    def check_inventory_status():
        """Vérifie l'état des inventaires dans Odoo"""
        print("="*60)
        print("🔍 VÉRIFICATION DE L'ÉTAT DES INVENTAIRES DANS ODOO")
        print("="*60)
        
        try:
            # Initialiser l'environnement Odoo
            config = odoo.tools.config
            config['db_name'] = 'eneo'  # Utilisation de la base de données eneo
            
            # Se connecter à la base de données
            registry = odoo.registry(config['db_name'])
            with api.Environment.manage():
                with registry.cursor() as cr:
                    env = api.Environment(cr, SUPERUSER_ID, {})
                    
                    # Vérifier les inventaires
                    inventories = env['stockex.stock.inventory'].search([])
                    print(f"📦 Inventaires trouvés: {len(inventories)}")
                    
                    # Compter par état
                    states = {}
                    for inv in inventories:
                        states[inv.state] = states.get(inv.state, 0) + 1
                    
                    print("\n📊 Répartition par état:")
                    for state, count in states.items():
                        state_label = dict(env['stockex.stock.inventory']._fields['state'].selection).get(state, state)
                        print(f"   • {state_label}: {count}")
                    
                    # Vérifier les inventaires validés
                    done_inventories = inventories.filtered(lambda i: i.state == 'done')
                    print(f"\n✅ Inventaires validés: {len(done_inventories)}")
                    
                    if done_inventories:
                        # Afficher les 5 derniers
                        print("\n📋 5 derniers inventaires validés:")
                        for inv in done_inventories[:5]:
                            value = sum(line.product_qty * line.standard_price for line in inv.line_ids)
                            print(f"   • {inv.name} ({inv.date}): {len(inv.line_ids)} produits, {value:,.0f} FCFA")
                    
                    # Vérifier les quantités de stock
                    products = env['product.product'].search([('type', '=', 'product')])
                    print(f"\n🛍️ Produits stockables: {len(products)}")
                    
                    # Calculer la quantité totale en stock
                    total_qty = 0
                    total_value = 0
                    for product in products:
                        qty = product.qty_available
                        price = product.standard_price
                        total_qty += qty
                        total_value += qty * price
                    
                    print(f"📊 Quantité totale en stock: {total_qty:,.0f} unités")
                    print(f"💰 Valeur totale du stock: {total_value:,.0f} FCFA")
                    
                    # Vérifier le résumé d'inventaire
                    summary = env['stockex.inventory.summary'].search([], limit=1)
                    if summary:
                        print(f"\n📈 Dashboard - Résumé:")
                        print(f"   • Inventaires validés: {summary.total_inventories_done}")
                        print(f"   • Produits référencés: {summary.total_products_all}")
                        print(f"   • Quantité totale: {summary.total_quantity_all:,.0f}")
                        print(f"   • Valeur totale: {summary.total_value_all:,.0f} FCFA")
                    else:
                        print("\n⚠️ Aucun résumé d'inventaire trouvé")
                        
                    return True
                    
        except Exception as e:
            print(f"❌ Erreur lors de la vérification: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    if __name__ == '__main__':
        check_inventory_status()
        
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("💡 Assurez-vous qu'Odoo est installé et accessible")
except Exception as e:
    print(f"❌ Erreur générale: {e}")
    import traceback
    traceback.print_exc()
