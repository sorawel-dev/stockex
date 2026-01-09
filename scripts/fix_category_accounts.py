#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour diagnostiquer et corriger les comptes comptables des catégories de produits.
Usage: python3 fix_category_accounts.py
"""

import xmlrpc.client
import sys

# Configuration Odoo
ODOO_URL = "http://localhost:8069"
ODOO_DB = "eneo"  # Remplacer par le nom de votre base de données
ODOO_USERNAME = "admin"  # Remplacer par votre nom d'utilisateur
ODOO_PASSWORD = "admin"  # Remplacer par votre mot de passe

def connect_odoo():
    """Connexion à Odoo via XML-RPC."""
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    
    if not uid:
        print("❌ Échec de l'authentification")
        sys.exit(1)
    
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
    return uid, models

def get_default_accounts(uid, models):
    """Récupère les comptes par défaut (31/603)."""
    # Chercher le compte 31
    account_31 = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
        'account.account', 'search_read',
        [[['code', '=', '31']]],
        {'fields': ['id', 'code', 'name'], 'limit': 1})
    
    # Chercher le compte 603
    account_603 = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
        'account.account', 'search_read',
        [[['code', '=', '603']]],
        {'fields': ['id', 'code', 'name'], 'limit': 1})
    
    if not account_31 or not account_603:
        print("⚠️ Comptes 31 ou 603 non trouvés. Recherche des alternatives...")
        
        # Chercher 311
        if not account_31:
            account_31 = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
                'account.account', 'search_read',
                [[['code', '=', '311']]],
                {'fields': ['id', 'code', 'name'], 'limit': 1})
        
        # Chercher 6030
        if not account_603:
            account_603 = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
                'account.account', 'search_read',
                [[['code', '=', '6030']]],
                {'fields': ['id', 'code', 'name'], 'limit': 1})
    
    return account_31[0] if account_31 else None, account_603[0] if account_603 else None

def diagnose_and_fix_categories(uid, models):
    """Diagnostique et corrige toutes les catégories."""
    print("\n" + "="*60)
    print("🔍 DIAGNOSTIC DES CATÉGORIES DE PRODUITS")
    print("="*60 + "\n")
    
    # Récupérer les comptes par défaut
    account_31, account_603 = get_default_accounts(uid, models)
    
    if not account_31 or not account_603:
        print("❌ Impossible de trouver les comptes par défaut (31/311 ou 603/6030)")
        print("Veuillez créer ces comptes dans votre plan comptable.")
        return
    
    print(f"✅ Comptes par défaut trouvés:")
    print(f"   - Valorisation: {account_31['code']} - {account_31['name']}")
    print(f"   - Variation: {account_603['code']} - {account_603['name']}\n")
    
    # Récupérer toutes les catégories
    categories = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
        'product.category', 'search_read',
        [[]],
        {'fields': ['id', 'name', 'parent_id', 
                    'property_stock_valuation_account_id',
                    'property_stock_account_input_categ_id',
                    'property_stock_account_output_categ_id']})
    
    print(f"📊 {len(categories)} catégorie(s) trouvée(s)\n")
    
    configured_count = 0
    fixed_count = 0
    
    for category in categories:
        cat_name = category['name']
        has_valuation = bool(category['property_stock_valuation_account_id'])
        has_input = bool(category['property_stock_account_input_categ_id'])
        has_output = bool(category['property_stock_account_output_categ_id'])
        
        is_configured = has_valuation and has_input and has_output
        
        if is_configured:
            configured_count += 1
            print(f"✅ {cat_name} - Déjà configurée")
        else:
            print(f"❌ {cat_name} - NON configurée")
            
            # Déterminer les comptes à utiliser
            valuation_id = None
            input_id = None
            output_id = None
            source = None
            
            # Si la catégorie a un parent configuré
            if category['parent_id']:
                parent_id = category['parent_id'][0]
                parent = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
                    'product.category', 'read',
                    [parent_id],
                    {'fields': ['property_stock_valuation_account_id',
                                'property_stock_account_input_categ_id',
                                'property_stock_account_output_categ_id']})
                
                if parent and parent[0]['property_stock_valuation_account_id']:
                    valuation_id = parent[0]['property_stock_valuation_account_id'][0]
                    input_id = parent[0]['property_stock_account_input_categ_id'][0]
                    output_id = parent[0]['property_stock_account_output_categ_id'][0]
                    source = f"parent ({category['parent_id'][1]})"
            
            # Sinon, utiliser les comptes par défaut
            if not valuation_id:
                valuation_id = account_31['id']
                input_id = account_603['id']
                output_id = account_603['id']
                source = "défaut"
            
            # Appliquer la configuration
            try:
                models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
                    'product.category', 'write',
                    [[category['id']], {
                        'property_stock_valuation_account_id': valuation_id,
                        'property_stock_account_input_categ_id': input_id,
                        'property_stock_account_output_categ_id': output_id,
                    }])
                fixed_count += 1
                print(f"   → ✅ Corrigée avec comptes {source}")
            except Exception as e:
                print(f"   → ❌ Erreur: {str(e)}")
    
    print("\n" + "="*60)
    print("📊 RÉSUMÉ")
    print("="*60)
    print(f"✅ Catégories déjà configurées: {configured_count}")
    print(f"🔧 Catégories corrigées: {fixed_count}")
    print(f"📦 Total: {len(categories)}")
    print("="*60 + "\n")
    
    if fixed_count > 0:
        print("✅ Toutes les catégories sont maintenant configurées !")
        print("Vous pouvez maintenant valider votre inventaire.")
    else:
        print("ℹ️ Aucune correction nécessaire.")

if __name__ == "__main__":
    print("\n🚀 Démarrage du script de correction des comptes comptables...\n")
    
    try:
        uid, models = connect_odoo()
        diagnose_and_fix_categories(uid, models)
    except Exception as e:
        print(f"\n❌ Erreur: {str(e)}")
        sys.exit(1)
    
    print("\n✅ Script terminé avec succès !\n")
