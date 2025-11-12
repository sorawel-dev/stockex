#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de configuration automatique de l'interconnexion Kobo → Odoo
Crée une configuration complète prête à l'emploi
"""

import requests
import json

print("\n" + "="*70)
print("🔧 CONFIGURATION INTERCONNEXION KOBO → ODOO")
print("="*70)
print()

# Étape 1: Token API
print("📋 ÉTAPE 1/5: Token API Kobo")
print("-" * 70)
print()
print("Option 1: Récupérer via l'interface web")
print("  → Ouvrez https://kf.kesafrica.com")
print("  → Account Settings → Security → Copier 'API Token'")
print()
print("Option 2: Récupérer via identifiants")
print()

choice = input("Choisissez (1 ou 2): ").strip()

if choice == "1":
    api_token = input("\nEntrez le token API: ").strip()
else:
    username = input("\nUsername Kobo: ").strip()
    password = input("Password Kobo: ").strip()
    
    print("\n🔄 Récupération du token...")
    try:
        response = requests.post(
            "https://kf.kesafrica.com/token/",
            json={"username": username, "password": password},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            api_token = data.get('token')
            print(f"✅ Token récupéré: {api_token[:10]}...")
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            exit(1)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        exit(1)

# Étape 2: Tester la connexion et lister les formulaires
print("\n" + "="*70)
print("📋 ÉTAPE 2/5: Liste des formulaires disponibles")
print("-" * 70)
print()

headers = {'Authorization': f'Token {api_token}'}

try:
    response = requests.get(
        "https://kf.kesafrica.com/api/v2/assets/",
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        assets = data.get('results', [])
        
        if not assets:
            print("⚠️  Aucun formulaire trouvé")
            exit(1)
        
        print(f"✅ {len(assets)} formulaire(s) trouvé(s)\n")
        
        for i, asset in enumerate(assets, 1):
            uid = asset.get('uid')
            name = asset.get('name', 'Sans nom')
            submissions = asset.get('deployment__submission_count', 0)
            deployed = '✅' if asset.get('has_deployment') else '❌'
            
            print(f"{i}. {name}")
            print(f"   UID: {uid}")
            print(f"   Soumissions: {submissions}")
            print(f"   Déployé: {deployed}")
            print()
        
        # Sélectionner le formulaire
        form_num = input(f"Choisissez le formulaire à utiliser (1-{len(assets)}): ").strip()
        try:
            form_index = int(form_num) - 1
            selected_asset = assets[form_index]
            form_id = selected_asset['uid']
            form_name = selected_asset['name']
            
            print(f"\n✅ Formulaire sélectionné: {form_name}")
            print(f"   UID: {form_id}")
        except:
            print("❌ Sélection invalide")
            exit(1)
    else:
        print(f"❌ Erreur {response.status_code}: {response.text}")
        exit(1)

except Exception as e:
    print(f"❌ Erreur: {e}")
    exit(1)

# Étape 3: Analyser la structure d'une soumission
print("\n" + "="*70)
print("📋 ÉTAPE 3/5: Analyse de la structure des données")
print("-" * 70)
print()

try:
    response = requests.get(
        f"https://kf.kesafrica.com/api/v2/assets/{form_id}/data/",
        headers=headers,
        params={'limit': 1},
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        submissions = data.get('results', [])
        
        if submissions:
            sample = submissions[0]
            print("✅ Échantillon récupéré")
            print(f"   Soumission ID: {sample.get('_id')}")
            print(f"   Date: {sample.get('_submission_time')}")
            
            # Détecter les champs importants
            print("\n📊 Champs détectés:")
            
            fields_detected = {
                'product_code': None,
                'product_name': None,
                'quantity': None,
                'location': None,
                'gps': None
            }
            
            # Rechercher les champs par patterns
            for key in sample.keys():
                key_lower = key.lower()
                
                if any(x in key_lower for x in ['code', 'material', 'article']):
                    if not fields_detected['product_code']:
                        fields_detected['product_code'] = key
                        print(f"   • Code produit: {key}")
                
                if any(x in key_lower for x in ['nom', 'name', 'materiel', 'product']):
                    if not fields_detected['product_name'] and 'code' not in key_lower:
                        fields_detected['product_name'] = key
                        print(f"   • Nom produit: {key}")
                
                if any(x in key_lower for x in ['quantity', 'quantite', 'qty']):
                    fields_detected['quantity'] = key
                    print(f"   • Quantité: {key}")
                
                if any(x in key_lower for x in ['location', 'magasin', 'warehouse', 'emplacement']):
                    if not fields_detected['location']:
                        fields_detected['location'] = key
                        print(f"   • Emplacement: {key}")
                
                if 'geolocation' in key_lower or '_gps' in key_lower:
                    fields_detected['gps'] = key
                    print(f"   • GPS: {key}")
        else:
            print("⚠️  Aucune soumission disponible pour analyse")
            print("   Utilisation des valeurs par défaut")
            fields_detected = {
                'product_code': 'material_description',
                'product_name': 'nom_materiel',
                'quantity': 'quantity',
                'location': 'Sous_magasin',
                'gps': '_geolocation'
            }
    
except Exception as e:
    print(f"⚠️  Erreur d'analyse: {e}")
    print("   Utilisation des valeurs par défaut")
    fields_detected = {
        'product_code': 'material_description',
        'product_name': 'nom_materiel',
        'quantity': 'quantity',
        'location': 'Sous_magasin',
        'gps': '_geolocation'
    }

# Étape 4: Générer la configuration SQL
print("\n" + "="*70)
print("📋 ÉTAPE 4/5: Génération de la configuration")
print("-" * 70)
print()

config_sql = f"""
-- Configuration Kobo pour Odoo
-- Serveur: https://kf.kesafrica.com
-- Formulaire: {form_name}
-- UID: {form_id}

-- Cette requête doit être exécutée dans Odoo via le shell Python

-- Connexion à Odoo
import odoo
from odoo import api, SUPERUSER_ID

# Nom de votre base de données
db_name = 'votre_base_odoo'

odoo.tools.config.parse_config([])
odoo.tools.config['db_name'] = db_name

registry = odoo.registry(db_name)

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {{}})
    
    # Créer la configuration Kobo
    config = env['stockex.kobo.config'].create({{
        'name': 'Configuration Kobo - {form_name}',
        'active': True,
        'kobo_url': 'https://kf.kesafrica.com',
        'api_token': '{api_token}',
        'form_id': '{form_id}',
        'form_name': '{form_name}',
        
        # Mapping des champs
        'mapping_product_code': '{fields_detected.get("product_code", "material_description")}',
        'mapping_product_name': '{fields_detected.get("product_name", "nom_materiel")}',
        'mapping_quantity': '{fields_detected.get("quantity", "quantity")}',
        'mapping_location': '{fields_detected.get("location", "Sous_magasin")}',
        'mapping_warehouse': '{fields_detected.get("location", "Sous_magasin")}',
        'mapping_gps_lat': '_geolocation[0]',
        'mapping_gps_lon': '_geolocation[1]',
        
        # Options de gestion des photos (HAUTE QUALITÉ)
        'download_photos': True,
        'compress_photos': True,
        'photo_max_size': 1600,
        'photo_quality': 90,
        
        # Options de création automatique
        'create_missing_products': True,
        'create_missing_locations': True,
        
        # Import automatique
        'auto_import': False,
        'auto_validate': False,
    }})
    
    cr.commit()
    
    print(f"✅ Configuration créée: {{config.id}}")
    print(f"   Nom: {{config.name}}")
    print(f"   URL: {{config.kobo_url}}")
    print(f"   Formulaire: {{config.form_name}}")
"""

# Sauvegarder la configuration
config_file = '/home/one/apps/stockex/scripts/create_kobo_config.py'
with open(config_file, 'w') as f:
    f.write(config_sql)

print(f"✅ Configuration générée: {config_file}")

# Étape 5: Instructions
print("\n" + "="*70)
print("📋 ÉTAPE 5/5: Instructions d'installation")
print("="*70)
print()
print("🎯 Pour activer la configuration dans Odoo:")
print()
print("Option A - Via l'interface Odoo:")
print("  1. Ouvrez Odoo")
print("  2. Allez dans: Inventaire → Configuration → Kobo Collect")
print("  3. Cliquez sur 'Créer'")
print("  4. Remplissez les champs:")
print(f"     • URL Kobo: https://kf.kesafrica.com")
print(f"     • Token API: {api_token[:20]}...")
print(f"     • Form ID: {form_id}")
print(f"     • Nom: {form_name}")
print("  5. Configurez le mapping des champs")
print("  6. Activez les options de photos (1600px, 90%)")
print("  7. Sauvegardez")
print()
print("Option B - Via script Python:")
print(f"  1. Éditez le fichier: {config_file}")
print("  2. Remplacez 'votre_base_odoo' par le nom de votre BDD")
print("  3. Exécutez: python3 create_kobo_config.py")
print()
print("="*70)
print("✅ CONFIGURATION TERMINÉE")
print("="*70)
print()
print("📊 Résumé:")
print(f"   • Serveur: https://kf.kesafrica.com")
print(f"   • Formulaire: {form_name}")
print(f"   • UID: {form_id}")
print(f"   • Token: {api_token[:10]}...{api_token[-5:]}")
print(f"   • Champs détectés: {len([v for v in fields_detected.values() if v])}/5")
print()
print("🔄 Prochaines étapes:")
print("   1. Créer la configuration dans Odoo (Option A ou B)")
print("   2. Tester la connexion (bouton 'Test Connexion')")
print("   3. Lancer un import test")
print("   4. Vérifier l'inventaire créé")
print()
