#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test de connexion à l'API Kobo
"""

import requests
import json
from datetime import datetime

# Configuration
KOBO_URL = "https://kf.kobotoolbox.org"
API_TOKEN = "9f93fe1e5a6537bfabb6c935ca852264cefa30ee"
FORM_ID = "aQJVWdSP4xyzhru6Ztfo4Q"  # Extrait du fichier Excel

def test_connection():
    """Teste la connexion de base à l'API Kobo"""
    print("="*80)
    print("🔌 TEST DE CONNEXION À L'API KOBO")
    print("="*80)
    
    headers = {
        'Authorization': f'Token {API_TOKEN}'
    }
    
    try:
        # Test 1: Récupérer les informations du formulaire
        print("\n📋 Test 1: Récupération des informations du formulaire...")
        url = f"{KOBO_URL}/api/v2/assets/{FORM_ID}/"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Connexion réussie!")
            print(f"   - Nom du formulaire: {data.get('name')}")
            print(f"   - UID: {data.get('uid')}")
            print(f"   - Nombre de soumissions: {data.get('deployment__submission_count', 0)}")
            print(f"   - Date de création: {data.get('date_created')}")
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            return False
        
        # Test 2: Récupérer les soumissions
        print("\n📊 Test 2: Récupération des soumissions...")
        url = f"{KOBO_URL}/api/v2/assets/{FORM_ID}/data/"
        params = {
            'limit': 5  # Limiter à 5 pour le test
        }
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            print(f"✅ {len(results)} soumissions récupérées (sur {data.get('count', 0)} total)")
            
            if results:
                print("\n📝 Exemple de la première soumission:")
                first = results[0]
                print(f"   - ID: {first.get('_id')}")
                print(f"   - Date: {first.get('_submission_time')}")
                print(f"   - Magasin: {first.get('MAGASIN')}")
                code_article = first.get('Code d' + chr(39) + 'article', first.get('Code article'))
                print(f"   - Code article: {code_article}")
                print(f"   - Nom: {first.get('Nom du Materiel')}")
                quantite = first.get('Quantité', first.get('Quantite'))
                print(f"   - Quantité: {quantite}")
                print(f"   - Emplacement: {first.get('EMPLACEMENT')}")
                
                print("\n🗂️ Champs disponibles dans la soumission:")
                for key in sorted(first.keys()):
                    if not key.startswith('_') and not key.startswith('formhub'):
                        print(f"   - {key}")
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            return False
        
        # Test 3: Statistiques
        print("\n📈 Test 3: Statistiques des soumissions...")
        url = f"{KOBO_URL}/api/v2/assets/{FORM_ID}/data/"
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            all_results = data.get('results', [])
            
            print(f"✅ Total de soumissions: {len(all_results)}")
            
            # Compter par magasin
            magasins = {}
            for sub in all_results:
                mag = sub.get('MAGASIN', 'Non défini')
                magasins[mag] = magasins.get(mag, 0) + 1
            
            print("\n📍 Répartition par magasin:")
            for mag, count in sorted(magasins.items(), key=lambda x: x[1], reverse=True):
                print(f"   - {mag}: {count} soumissions")
            
            # Compter par type d'article
            types = {}
            for sub in all_results:
                type_key = 'Type d' + chr(39) + 'article'
                typ = sub.get(type_key, sub.get('Type article', 'Non défini'))
                types[typ] = types.get(typ, 0) + 1
            
            print("\n📦 Répartition par type:")
            for typ, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
                print(f"   - {typ}: {count} articles")
            
            # Calcul des quantités
            total_qty = 0
            for sub in all_results:
                qty = sub.get('Quantité', sub.get('Quantite', 0))
                try:
                    total_qty += float(qty)
                except:
                    pass
            print(f"\n📊 Quantité totale en stock: {total_qty:,.0f} unités")
        
        print("\n" + "="*80)
        print("✅ TOUS LES TESTS SONT RÉUSSIS!")
        print("="*80)
        print("\n💡 Configuration Odoo suggérée:")
        print(f"   - URL Kobo: {KOBO_URL}")
        print(f"   - Token API: {API_TOKEN}")
        print(f"   - ID Formulaire: {FORM_ID}")
        print(f"   - Nom Formulaire: {data.get('name', 'Non disponible')}")
        print("\n📋 Mapping des champs:")
        print("   - Code produit: 'Code d'article'")
        print("   - Nom produit: 'Nom du Materiel'")
        print("   - Quantité: 'Quantité'")
        print("   - Magasin: 'MAGASIN'")
        print("   - Emplacement: 'EMPLACEMENT'")
        print("   - Marque: 'Marque'")
        print("   - Type: 'Type d'article'")
        print("   - GPS Latitude: '_Coordonnées géographiques_latitude'")
        print("   - GPS Longitude: '_Coordonnées géographiques_longitude'")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_connection()
