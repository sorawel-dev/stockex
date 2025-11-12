#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test de l'API Kobo sur kf.kesafrica.com
Vérifie la connexion et liste les formulaires disponibles
"""

import requests
import json
from datetime import datetime

# Configuration
KOBO_URL = "https://kf.kesafrica.com"
API_TOKEN = input("Entrez votre token API Kobo: ").strip()

if not API_TOKEN:
    print("❌ Token API requis")
    exit(1)

headers = {
    'Authorization': f'Token {API_TOKEN}'
}

print("\n" + "="*60)
print("🧪 TEST API KOBO - kf.kesafrica.com")
print("="*60 + "\n")

# 1. Test de connexion basique
print("1️⃣  Test de connexion basique...")
try:
    response = requests.get(f"{KOBO_URL}/api/v2/assets/", headers=headers, timeout=10)
    if response.status_code == 200:
        print("✅ Connexion réussie")
        assets = response.json()
        print(f"📊 Nombre de formulaires: {assets.get('count', 0)}")
    else:
        print(f"❌ Erreur: {response.status_code}")
        print(f"   Message: {response.text}")
        exit(1)
except Exception as e:
    print(f"❌ Erreur de connexion: {e}")
    exit(1)

# 2. Lister les formulaires disponibles
print("\n2️⃣  Formulaires disponibles:")
print("-" * 60)

results = assets.get('results', [])
if not results:
    print("⚠️  Aucun formulaire trouvé")
else:
    for i, asset in enumerate(results[:10], 1):
        asset_uid = asset.get('uid', 'N/A')
        name = asset.get('name', 'Sans nom')
        deployment_count = asset.get('deployment__submission_count', 0)
        print(f"\n{i}. {name}")
        print(f"   • UID: {asset_uid}")
        print(f"   • Soumissions: {deployment_count}")
        print(f"   • Déployé: {'✅' if asset.get('has_deployment', False) else '❌'}")

# 3. Demander quel formulaire tester
print("\n" + "="*60)
if results:
    form_choice = input(f"\n3️⃣  Entrez le numéro du formulaire à tester (1-{len(results[:10])}): ").strip()
    try:
        form_index = int(form_choice) - 1
        if 0 <= form_index < len(results[:10]):
            selected_asset = results[form_index]
            asset_uid = selected_asset.get('uid')
            asset_name = selected_asset.get('name')
            
            print(f"\n✅ Formulaire sélectionné: {asset_name}")
            print(f"   UID: {asset_uid}")
            
            # 4. Récupérer les soumissions
            print("\n4️⃣  Récupération des soumissions...")
            submissions_url = f"{KOBO_URL}/api/v2/assets/{asset_uid}/data/"
            response = requests.get(submissions_url, headers=headers, params={'limit': 5}, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                submissions = data.get('results', [])
                print(f"✅ {len(submissions)} soumissions récupérées (5 max)")
                
                if submissions:
                    print("\n📋 Première soumission (aperçu):")
                    print("-" * 60)
                    first_sub = submissions[0]
                    print(f"   • ID: {first_sub.get('_id')}")
                    print(f"   • Date: {first_sub.get('_submission_time', 'N/A')}")
                    print(f"   • GPS: {first_sub.get('_geolocation', 'N/A')}")
                    
                    # Lister quelques champs
                    print("\n   📊 Champs disponibles (10 premiers):")
                    for key in list(first_sub.keys())[:10]:
                        value = first_sub[key]
                        if isinstance(value, str) and len(value) > 50:
                            value = value[:50] + "..."
                        print(f"      - {key}: {value}")
                    
                    # Vérifier si des attachments existent
                    attachments = first_sub.get('_attachments', [])
                    if attachments:
                        print(f"\n   📸 Attachments: {len(attachments)} fichier(s)")
                        for att in attachments[:3]:
                            filename = att.get('filename', 'N/A')
                            mimetype = att.get('mimetype', 'N/A')
                            print(f"      - {filename} ({mimetype})")
                    
                    # Test de téléchargement d'un attachment
                    if attachments:
                        print("\n5️⃣  Test téléchargement d'un attachment...")
                        first_att = attachments[0]
                        att_filename = first_att.get('filename')
                        
                        # URL de téléchargement
                        download_url = first_att.get('download_url')
                        if download_url:
                            try:
                                file_response = requests.get(download_url, headers=headers, timeout=60)
                                if file_response.status_code == 200:
                                    size_kb = len(file_response.content) / 1024
                                    print(f"✅ Fichier téléchargé: {att_filename}")
                                    print(f"   Taille: {size_kb:.2f} KB")
                                else:
                                    print(f"❌ Erreur téléchargement: {file_response.status_code}")
                            except Exception as e:
                                print(f"❌ Erreur: {e}")
                
                # Configuration suggérée pour Odoo
                print("\n" + "="*60)
                print("📝 CONFIGURATION SUGGÉRÉE POUR ODOO")
                print("="*60)
                print(f"\nkobo_url: {KOBO_URL}")
                print(f"api_token: {API_TOKEN}")
                print(f"form_id: {asset_uid}")
                print(f"form_name: {asset_name}")
                
                if submissions:
                    print("\n📊 Mapping des champs (à vérifier):")
                    print("Les champs suivants ont été détectés:")
                    for key in list(first_sub.keys())[:20]:
                        if not key.startswith('_'):
                            print(f"   • {key}")
                
            else:
                print(f"❌ Erreur récupération soumissions: {response.status_code}")
                print(f"   Message: {response.text}")
        else:
            print("❌ Numéro invalide")
    except ValueError:
        print("❌ Entrée invalide")
else:
    print("⚠️  Aucun formulaire disponible pour test")

print("\n" + "="*60)
print("✅ Test terminé")
print("="*60 + "\n")
