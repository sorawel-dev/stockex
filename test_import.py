#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour l'import stock initial en CLI
Usage: python test_import.py
"""

import sys
import os
import base64

# Ajouter le chemin d'Odoo
odoo_path = r"C:\Program Files\Odoo 18.0.20250428\server"
sys.path.insert(0, odoo_path)

import odoo
from odoo.api import Environment

# Configuration
DB_NAME = 'eneo'
EXCEL_FILE = r'c:\apps\stockex\docs\stock_initial_COMPLET.xlsx'
ODOO_CONF = r'C:\Program Files\Odoo 18.0.20250428\server\odoo.conf'

def test_import():
    """Test l'import complet via le wizard."""
    print("=" * 80)
    print("TEST IMPORT STOCK INITIAL VIA WIZARD")
    print("=" * 80)
    
    # Initialiser Odoo
    odoo.tools.config.parse_config(['-c', ODOO_CONF, '-d', DB_NAME])
    
    print(f"\nBase de donnees: {DB_NAME}")
    print(f"Fichier: {EXCEL_FILE}")
    
    # Vérifier que le fichier existe
    if not os.path.exists(EXCEL_FILE):
        print(f"\n❌ ERREUR: Le fichier {EXCEL_FILE} n'existe pas!")
        return
    
    file_size = os.path.getsize(EXCEL_FILE)
    print(f"✅ Fichier trouvé ({file_size:,} octets)")
    
    try:
        # Lire le fichier et l'encoder en base64
        with open(EXCEL_FILE, 'rb') as f:
            file_content = base64.b64encode(f.read())
        
        print(f"✅ Fichier encodé en base64 ({len(file_content):,} caractères)")
        
        # Connexion à Odoo
        print("\n" + "=" * 80)
        print("CONNEXION À ODOO")
        print("=" * 80)
        
        registry = odoo.registry(DB_NAME)
        
        with registry.cursor() as cr:
            env = Environment(cr, odoo.SUPERUSER_ID, {})
            
            # Vérifier le module stockex
            module = env['ir.module.module'].search([('name', '=', 'stockex')])
            if not module:
                print("\n❌ Module stockex non trouvé!")
                return
            
            print(f"\n✅ Module stockex trouvé (état: {module.state})")
            
            # Vérifier les entrepôts existants
            existing_warehouses = env['stock.warehouse'].search([])
            print(f"\n📦 Entrepôts existants: {len(existing_warehouses)}")
            for wh in existing_warehouses:
                print(f"  • {wh.name} (Code: {wh.code})")
            
            # Créer le wizard
            print("\n" + "=" * 80)
            print("CRÉATION DU WIZARD")
            print("=" * 80)
            
            company = env['res.company'].search([], limit=1)
            
            wizard_vals = {
                'name': 'Stock Initial - Test CLI',
                'date': '2025-10-29',
                'company_id': company.id,
                'create_products': True,
                'create_categories': True,
                'create_warehouses': True,
                'import_file': file_content,
                'filename': 'stock_initial_COMPLET.xlsx',
            }
            
            wizard = env['stockex.initial.stock.wizard'].create(wizard_vals)
            print(f"\n✅ Wizard créé (ID: {wizard.id})")
            
            # Tester la prévisualisation
            print("\n" + "=" * 80)
            print("🔍 PRÉVISUALISATION")
            print("=" * 80)
            
            try:
                wizard.action_preview()
                print(f"\n✅ Prévisualisation réussie")
                print(f"  • Lignes: {wizard.lines_count}")
                print(f"  • Entrepôts: {wizard.warehouses_preview}")
                print(f"  • Catégories: {wizard.categories_preview}")
            except Exception as e:
                print(f"\n⚠️ Erreur prévisualisation: {str(e)}")
            
            # Lancer l'import
            print("\n" + "=" * 80)
            print("🚀 LANCEMENT DE L'IMPORT")
            print("=" * 80)
            
            try:
                result = wizard.action_create_initial_stock()
                print(f"\n✅ Import lancé!")
                print(f"\nRésultat: {result}")
                
                # Vérifier la progression
                if wizard.progress > 0:
                    print(f"\n📊 Progression: {wizard.progress:.1f}%")
                    print(f"📝 Message: {wizard.progress_message}")
                
                # Récupérer l'inventaire créé
                if result and isinstance(result, dict) and 'res_id' in result:
                    inventory_id = result['res_id']
                    inventory = env['stockex.stock.inventory'].browse(inventory_id)
                    
                    print("\n" + "=" * 80)
                    print("📋 INVENTAIRE CRÉÉ")
                    print("=" * 80)
                    print(f"\n  • ID: {inventory.id}")
                    print(f"  • Nom: {inventory.name}")
                    print(f"  • Date: {inventory.date}")
                    print(f"  • État: {inventory.state}")
                    print(f"  • Nombre de lignes: {len(inventory.line_ids)}")
                    
                    # Afficher les premières lignes
                    print("\n  📝 Premières lignes (max 10):")
                    for line in inventory.line_ids[:10]:
                        product_name = line.product_id.name if line.product_id else 'N/A'
                        location_name = line.location_id.complete_name if line.location_id else 'N/A'
                        print(f"    - {product_name[:40]:<40} | {location_name[:30]:<30} | Qty: {line.counted_quantity:>8.0f}")
                    
                    if len(inventory.line_ids) > 10:
                        print(f"    ... et {len(inventory.line_ids) - 10} autre(s) ligne(s)")
                    
                    # Statistiques par entrepôt
                    print("\n  🏭 Statistiques par entrepôt:")
                    locations = {}
                    for line in inventory.line_ids:
                        loc = line.location_id.complete_name if line.location_id else 'N/A'
                        if loc not in locations:
                            locations[loc] = {'count': 0, 'qty': 0}
                        locations[loc]['count'] += 1
                        locations[loc]['qty'] += line.counted_quantity
                    
                    for loc, stats in sorted(locations.items()):
                        print(f"    - {loc[:40]:<40} | Lignes: {stats['count']:>5} | Qty totale: {stats['qty']:>10,.0f}")
                
                # Vérifier les nouveaux entrepôts
                new_warehouses = env['stock.warehouse'].search([])
                print("\n" + "=" * 80)
                print(f"🏭 ENTREPÔTS APRÈS IMPORT ({len(new_warehouses)})")
                print("=" * 80)
                for wh in new_warehouses:
                    print(f"  • {wh.name} (Code: {wh.code})")
                
                print("\n" + "=" * 80)
                print("✅ IMPORT TERMINÉ AVEC SUCCÈS")
                print("=" * 80)
                
            except Exception as e:
                print(f"\n❌ ERREUR lors de l'import: {str(e)}")
                import traceback
                traceback.print_exc()
                
                # Afficher les logs du wizard si disponibles
                if wizard.progress_message:
                    print(f"\n📝 Dernier message: {wizard.progress_message}")
                    print(f"📊 Progression: {wizard.progress:.1f}%")
            
            # Ne pas committer (test uniquement)
            cr.rollback()
            print("\n⚠️  Transaction annulée (mode test)")
            
    except Exception as e:
        print(f"\n❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_import()
