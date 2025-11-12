#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse de la structure réelle des données Kobo
"""

import requests
import json

# Configuration
KOBO_URL = "https://kf.kobotoolbox.org"
API_TOKEN = "9f93fe1e5a6537bfabb6c935ca852264cefa30ee"
FORM_ID = "aQJVWdSP4xyzhru6Ztfo4Q"

headers = {
    'Authorization': f'Token {API_TOKEN}'
}

# Récupérer toutes les soumissions
print("Récupération de toutes les soumissions...")
url = f"{KOBO_URL}/api/v2/assets/{FORM_ID}/data/"
response = requests.get(url, headers=headers, timeout=60)

if response.status_code == 200:
    data = response.json()
    submissions = data.get('results', [])
    
    print(f"Total: {len(submissions)} soumissions\n")
    print("="*100)
    print("STRUCTURE DES DONNÉES - PREMIÈRE SOUMISSION COMPLÈTE")
    print("="*100)
    
    if submissions:
        first = submissions[0]
        print(json.dumps(first, indent=2, ensure_ascii=False))
        
        print("\n" + "="*100)
        print("TOUS LES CHAMPS DISPONIBLES")
        print("="*100)
        for key in sorted(first.keys()):
            value = first[key]
            value_type = type(value).__name__
            if isinstance(value, (str, int, float)) and value != '':
                print(f"{key:70s} = {str(value)[:50]} ({value_type})")
            else:
                print(f"{key:70s} ({value_type})")
        
        print("\n" + "="*100)
        print("MAPPING SUGGÉRÉ")
        print("="*100)
        
        # Rechercher les champs pertinents
        for key in first.keys():
            lower_key = key.lower()
            if 'code' in lower_key or 'article' in lower_key:
                print(f"Code produit → {key} = {first[key]}")
            elif 'nom' in lower_key and 'materiel' in lower_key:
                print(f"Nom produit → {key} = {first[key]}")
            elif 'quantity' in lower_key or 'quantit' in lower_key:
                print(f"Quantité → {key} = {first[key]}")
            elif 'magasin' in lower_key and 'sous' not in lower_key:
                print(f"Magasin → {key} = {first[key]}")
            elif 'emplacement' in lower_key or 'location' in lower_key:
                print(f"Emplacement → {key} = {first[key]}")
            elif 'marque' in lower_key or 'brand' in lower_key:
                print(f"Marque → {key} = {first[key]}")
            elif 'type' in lower_key and 'article' in lower_key:
                print(f"Type article → {key} = {first[key]}")
            elif 'gps' in lower_key or 'geopoint' in lower_key or ('latitude' in lower_key and 'longitude' not in key):
                print(f"GPS → {key} = {first[key]}")
else:
    print(f"Erreur {response.status_code}: {response.text}")
