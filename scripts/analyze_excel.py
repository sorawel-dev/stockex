#!/usr/bin/env python3
"""
Script pour analyser un fichier Excel d'inventaire et identifier les problèmes potentiels
Usage: python3 analyze_excel.py <fichier.xlsx>
"""

import sys
import openpyxl
from collections import defaultdict

def analyze_excel(filepath):
    """Analyse un fichier Excel et identifie les problèmes"""
    
    print(f"\n📊 Analyse du fichier: {filepath}\n")
    
    try:
        wb = openpyxl.load_workbook(filepath, data_only=True)
        sheet = wb.active
        
        # Statistiques
        total_rows = 0
        empty_rows = 0
        missing_product = 0
        missing_warehouse = 0
        missing_quantity = 0
        invalid_quantity = 0
        products = set()
        warehouses = set()
        categories = set()
        
        # Lire les données
        for i, row in enumerate(sheet.iter_rows(min_row=2, values_only=True)):
            if i >= 5000:  # Limiter à 5000 lignes
                break
                
            total_rows += 1
            
            # Vérifier si la ligne est vide
            if not any(row):
                empty_rows += 1
                continue
            
            # Extraire les colonnes (adapter selon votre format)
            product_code = row[0] if len(row) > 0 else None
            product_name = row[1] if len(row) > 1 else None
            warehouse_name = row[2] if len(row) > 2 else None
            quantity = row[3] if len(row) > 3 else None
            category = row[4] if len(row) > 4 else None
            
            # Vérifications
            if not product_code:
                missing_product += 1
            else:
                products.add(str(product_code))
            
            if not warehouse_name:
                missing_warehouse += 1
            else:
                warehouses.add(str(warehouse_name))
            
            if category:
                categories.add(str(category))
            
            if quantity is None or quantity == '':
                missing_quantity += 1
            else:
                try:
                    float(quantity)
                except (ValueError, TypeError):
                    invalid_quantity += 1
        
        # Afficher les résultats
        print("=" * 60)
        print("📈 STATISTIQUES")
        print("=" * 60)
        print(f"Total lignes (hors en-tête): {total_rows}")
        print(f"Lignes vides: {empty_rows}")
        print(f"Lignes valides potentielles: {total_rows - empty_rows}")
        print()
        
        print("=" * 60)
        print("⚠️  PROBLÈMES DÉTECTÉS")
        print("=" * 60)
        print(f"Produits manquants: {missing_product}")
        print(f"Entrepôts manquants: {missing_warehouse}")
        print(f"Quantités manquantes: {missing_quantity}")
        print(f"Quantités invalides: {invalid_quantity}")
        print()
        
        print("=" * 60)
        print("📦 DONNÉES UNIQUES")
        print("=" * 60)
        print(f"Produits uniques: {len(products)}")
        if len(products) <= 10:
            print(f"  → {', '.join(list(products)[:10])}")
        else:
            print(f"  → {', '.join(list(products)[:10])} ...")
        print()
        
        print(f"Entrepôts uniques: {len(warehouses)}")
        print(f"  → {', '.join(list(warehouses))}")
        print()
        
        print(f"Catégories uniques: {len(categories)}")
        if len(categories) <= 10:
            print(f"  → {', '.join(list(categories))}")
        else:
            print(f"  → {', '.join(list(categories)[:10])} ...")
        print()
        
        # Recommandations
        print("=" * 60)
        print("💡 RECOMMANDATIONS")
        print("=" * 60)
        
        total_issues = missing_product + missing_warehouse + missing_quantity + invalid_quantity
        if total_issues > 0:
            print(f"⚠️  {total_issues} ligne(s) seront probablement ignorées lors de l'import")
            print()
            print("Actions recommandées:")
            if missing_product > 0:
                print(f"  • Vérifier les {missing_product} ligne(s) sans code produit")
            if missing_warehouse > 0:
                print(f"  • Vérifier les {missing_warehouse} ligne(s) sans entrepôt")
            if missing_quantity > 0:
                print(f"  • Vérifier les {missing_quantity} ligne(s) sans quantité")
            if invalid_quantity > 0:
                print(f"  • Corriger les {invalid_quantity} quantité(s) invalide(s)")
        else:
            print("✅ Aucun problème majeur détecté!")
            print("   Le fichier devrait s'importer correctement.")
        
        print()
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_excel.py <fichier.xlsx>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    sys.exit(analyze_excel(filepath))
