#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test d'import Kobo (simulation sans Odoo)
Ce script simule l'import de données Kobo pour valider la logique
"""

import requests
import json
from datetime import datetime
from collections import defaultdict

# Configuration
KOBO_URL = "https://kf.kobotoolbox.org"
API_TOKEN = "9f93fe1e5a6537bfabb6c935ca852264cefa30ee"
FORM_ID = "aQJVWdSP4xyzhru6Ztfo4Q"

# Mapping des champs (comme dans Odoo)
MAPPING = {
    'product_code': 'begin_group_TSW6h0mGE/material_description',
    'product_name': 'begin_group_TSW6h0mGE/nom_materiel',
    'quantity': 'begin_group_TSW6h0mGE/quantity',
    'location': 'begin_group_TSW6h0mGE/Sous_magasin',
    'brand': 'begin_group_TSW6h0mGE/marque',
    'product_type': 'begin_group_TSW6h0mGE/type_article',
    'photo': 'begin_group_TSW6h0mGE/photo',
}

def test_import():
    """Teste l'import des données Kobo"""
    print("="*100)
    print("🧪 TEST D'IMPORT KOBO COLLECT")
    print("="*100)
    
    headers = {
        'Authorization': f'Token {API_TOKEN}'
    }
    
    try:
        # Récupérer les soumissions
        print("\n📥 Récupération des soumissions depuis Kobo...")
        url = f"{KOBO_URL}/api/v2/assets/{FORM_ID}/data/"
        response = requests.get(url, headers=headers, timeout=60)
        
        if response.status_code != 200:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            return False
        
        data = response.json()
        submissions = data.get('results', [])
        
        print(f"✅ {len(submissions)} soumissions récupérées")
        
        # Simuler le traitement
        print("\n" + "="*100)
        print("📊 TRAITEMENT DES SOUMISSIONS")
        print("="*100)
        
        # Statistiques
        stats = {
            'total': len(submissions),
            'imported': 0,
            'skipped': 0,
            'products': defaultdict(int),
            'locations': defaultdict(int),
            'brands': defaultdict(int),
            'types': defaultdict(int),
            'errors': []
        }
        
        products_to_create = {}
        locations_to_create = set()
        
        for i, sub in enumerate(submissions, 1):
            try:
                # Extraire les données
                product_code = str(sub.get(MAPPING['product_code'], '')).strip()
                product_name = str(sub.get(MAPPING['product_name'], '')).strip()
                location_name = str(sub.get(MAPPING['location'], '')).strip()
                brand = str(sub.get(MAPPING['brand'], '')).strip()
                product_type = str(sub.get(MAPPING['product_type'], '')).strip()
                
                try:
                    quantity = float(sub.get(MAPPING['quantity'], 0))
                except:
                    quantity = 0.0
                
                # GPS
                geoloc = sub.get('_geolocation', [])
                gps_coords = None
                if isinstance(geoloc, list) and len(geoloc) >= 2:
                    gps_coords = f"{geoloc[0]:.6f}, {geoloc[1]:.6f}"
                
                # Validation
                if not product_code:
                    stats['skipped'] += 1
                    stats['errors'].append(f"Soumission {i}: Code produit manquant")
                    continue
                
                # Collecter les informations
                if product_code not in products_to_create:
                    products_to_create[product_code] = {
                        'name': product_name or product_code,
                        'brand': brand,
                        'type': product_type,
                    }
                
                if location_name:
                    locations_to_create.add(location_name)
                
                stats['products'][product_code] += quantity
                stats['locations'][location_name] += 1
                if brand:
                    stats['brands'][brand] += 1
                if product_type:
                    stats['types'][product_type] += 1
                
                stats['imported'] += 1
                
                # Afficher les détails pour les 5 premiers
                if i <= 5:
                    print(f"\n✅ Soumission {i}:")
                    print(f"   • Code: {product_code}")
                    print(f"   • Nom: {product_name}")
                    print(f"   • Quantité: {quantity:,.0f}")
                    print(f"   • Emplacement: {location_name}")
                    print(f"   • Marque: {brand or 'Non renseignée'}")
                    print(f"   • Type: {product_type}")
                    if gps_coords:
                        print(f"   • GPS: {gps_coords}")
                
            except Exception as e:
                stats['skipped'] += 1
                stats['errors'].append(f"Soumission {i}: {str(e)}")
        
        # Afficher les résultats
        print("\n" + "="*100)
        print("📊 RÉSULTATS DU TEST")
        print("="*100)
        
        print(f"\n📈 Statistiques générales:")
        print(f"   • Total de soumissions: {stats['total']}")
        print(f"   • ✅ Importées avec succès: {stats['imported']}")
        print(f"   • ⚠️ Ignorées: {stats['skipped']}")
        
        print(f"\n📦 Produits:")
        print(f"   • Nombre de produits uniques: {len(products_to_create)}")
        print(f"   • Quantité totale: {sum(stats['products'].values()):,.0f} unités")
        
        print(f"\n📍 Emplacements:")
        print(f"   • Nombre d'emplacements: {len(locations_to_create)}")
        for loc in sorted(locations_to_create):
            count = stats['locations'][loc]
            print(f"      - {loc}: {count} articles")
        
        print(f"\n🏷️ Marques (Top 10):")
        for brand, count in sorted(stats['brands'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   • {brand}: {count} articles")
        
        print(f"\n📦 Types d'articles:")
        for ptype, count in sorted(stats['types'].items(), key=lambda x: x[1], reverse=True):
            print(f"   • {ptype}: {count} articles")
        
        if stats['errors']:
            print(f"\n⚠️ Erreurs (premières 10):")
            for error in stats['errors'][:10]:
                print(f"   • {error}")
            if len(stats['errors']) > 10:
                print(f"   ... et {len(stats['errors']) - 10} autres erreurs")
        
        print("\n" + "="*100)
        print("✅ TEST TERMINÉ AVEC SUCCÈS!")
        print("="*100)
        
        print("\n💡 Prochaines étapes:")
        print("   1. Installer le module Stockex dans Odoo")
        print("   2. Vérifier la configuration Kobo Collect")
        print("   3. Lancer l'import depuis le menu Odoo")
        print("   4. Vérifier l'inventaire créé")
        print("   5. Valider l'inventaire après vérification")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_import()
