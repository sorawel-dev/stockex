#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'import automatique du stock initial via l'API Odoo
"""

import xmlrpc.client
import base64
import sys
import time

# Configuration
ODOO_URL = 'https://odoo-minee.kesafrica.com'
DB_NAME = 'eneo'
USERNAME = 'dev@sorawel.com'
PASSWORD = 'dev'  # À modifier si nécessaire
EXCEL_FILE = '/home/one/apps/stockex/docx/stock_initial_COMPLET.xlsx'

print("=" * 80)
print(" " * 25 + "IMPORT STOCK INITIAL")
print("=" * 80)

# Connexion à Odoo
print(f"\n🔌 Connexion à Odoo : {ODOO_URL}")
print(f"📊 Base de données : {DB_NAME}")
print(f"👤 Utilisateur : {USERNAME}")

try:
    # Authentification
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(DB_NAME, USERNAME, PASSWORD, {})
    
    if not uid:
        print("❌ Échec de l'authentification")
        sys.exit(1)
    
    print(f"✅ Connecté (UID: {uid})")
    
    # Accès aux modèles
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
    
    # Lire le fichier Excel
    print(f"\n📂 Lecture du fichier : {EXCEL_FILE}")
    with open(EXCEL_FILE, 'rb') as f:
        file_content = base64.b64encode(f.read()).decode('utf-8')
    
    print(f"✅ Fichier chargé ({len(file_content)} caractères en base64)")
    
    # Créer le wizard
    print(f"\n🔧 Création du wizard d'import...")
    wizard_vals = {
        'name': 'Stock Initial - Import Automatique',
        'date': time.strftime('%Y-%m-%d'),
        'import_file': file_content,
        'filename': 'stock_initial_COMPLET.xlsx',
        'create_products': True,
        'create_categories': True,
        'create_warehouses': True,
        'force_reset': False,  # Sécurité : pas de réinitialisation forcée
    }
    
    wizard_id = models.execute_kw(
        DB_NAME, uid, PASSWORD,
        'stockex.initial.stock.wizard', 'create',
        [wizard_vals]
    )
    
    print(f"✅ Wizard créé (ID: {wizard_id})")
    
    # Prévisualisation (optionnel)
    print(f"\n👁️  Prévisualisation des données...")
    try:
        preview_result = models.execute_kw(
            DB_NAME, uid, PASSWORD,
            'stockex.initial.stock.wizard', 'action_preview',
            [[wizard_id]]
        )
        print(f"✅ Prévisualisation générée")
        
        # Lire les infos du wizard
        wizard_data = models.execute_kw(
            DB_NAME, uid, PASSWORD,
            'stockex.initial.stock.wizard', 'read',
            [[wizard_id], ['lines_count', 'warehouses_preview', 'categories_preview']]
        )[0]
        
        print(f"\n📊 Résumé :")
        print(f"   • Lignes à importer : {wizard_data.get('lines_count', 0):,}")
        print(f"   • Entrepôts : {wizard_data.get('warehouses_preview', 'N/A')}")
        print(f"   • Catégories : {wizard_data.get('categories_preview', 'N/A')}")
        
    except Exception as e:
        print(f"⚠️  Prévisualisation ignorée : {str(e)}")
    
    # Lancer l'import
    print(f"\n🚀 Lancement de l'import...")
    print(f"⏳ Cela peut prendre plusieurs minutes...")
    
    import_result = models.execute_kw(
        DB_NAME, uid, PASSWORD,
        'stockex.initial.stock.wizard', 'action_import',
        [[wizard_id]]
    )
    
    print(f"\n✅ Import terminé avec succès !")
    
    # Vérifier le résultat
    if isinstance(import_result, dict):
        if import_result.get('type') == 'ir.actions.client':
            params = import_result.get('params', {})
            print(f"\n📬 Message : {params.get('message', 'N/A')}")
    
    # Compter les quants créés
    print(f"\n📊 Vérification des stocks créés...")
    quants_count = models.execute_kw(
        DB_NAME, uid, PASSWORD,
        'stock.quant', 'search_count',
        [[('quantity', '>', 0), ('location_id.usage', '=', 'internal')]]
    )
    
    print(f"✅ {quants_count:,} enregistrement(s) de stock créé(s)")
    
    # Compter les entrepôts
    warehouses = models.execute_kw(
        DB_NAME, uid, PASSWORD,
        'stock.warehouse', 'search_read',
        [[]],
        {'fields': ['name', 'code']}
    )
    
    print(f"\n🏢 Entrepôts ({len(warehouses)}) :")
    for wh in warehouses:
        print(f"   • {wh['name']} ({wh['code']})")
    
    print(f"\n{'=' * 80}")
    print(f"{'🎉 IMPORT TERMINÉ AVEC SUCCÈS !':^80}")
    print(f"{'=' * 80}\n")
    
except FileNotFoundError:
    print(f"\n❌ Fichier non trouvé : {EXCEL_FILE}")
    sys.exit(1)
    
except xmlrpc.client.Fault as e:
    print(f"\n❌ Erreur Odoo : {e.faultString}")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ Erreur : {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
