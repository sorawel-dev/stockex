#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# Ajouter le chemin Odoo au sys.path
sys.path.append('/opt/odoo')

try:
    import pandas as pd
    print("✅ pandas disponible")
except ImportError:
    print("❌ pandas non disponible, installation requise")
    sys.exit(1)

file_path = '/home/one/apps/stockex/docx/stock_initial_COMPLET.xlsx'

print("=" * 80)
print("ANALYSE DU FICHIER EXCEL: stock_initial_COMPLET.xlsx")
print("=" * 80)

# Vérifier l'existence du fichier
if not os.path.exists(file_path):
    print(f"❌ Fichier non trouvé: {file_path}")
    sys.exit(1)

# Taille du fichier
file_size = os.path.getsize(file_path) / (1024 * 1024)
print(f"\n📦 Taille du fichier: {file_size:.2f} Mo")

# Lire le fichier Excel
try:
    xl_file = pd.ExcelFile(file_path, engine='openpyxl')
    print(f"\n📋 Nombre de feuilles: {len(xl_file.sheet_names)}")
    print(f"Feuilles: {xl_file.sheet_names}")
    
    # Analyser chaque feuille
    for sheet_name in xl_file.sheet_names:
        print(f"\n{'=' * 80}")
        print(f"FEUILLE: {sheet_name}")
        print(f"{'=' * 80}")
        
        df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
        
        print(f"\n📊 Dimensions: {df.shape[0]} lignes × {df.shape[1]} colonnes")
        print(f"\n📝 Colonnes ({len(df.columns)}):")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i}. {col}")
        
        # Afficher les premières lignes
        print(f"\n👁️  Aperçu des 5 premières lignes:")
        print(df.head().to_string())
        
        # Statistiques par colonne
        print(f"\n📈 Statistiques:")
        print(f"  - Lignes totales: {len(df)}")
        print(f"  - Lignes vides: {df.isnull().all(axis=1).sum()}")
        
        missing_info = []
        for col in df.columns:
            missing = df[col].isnull().sum()
            if missing > 0:
                missing_info.append(f"    • {col}: {missing} ({missing/len(df)*100:.1f}%)")
        
        if missing_info:
            print(f"  - Valeurs manquantes par colonne:")
            for info in missing_info:
                print(info)
        else:
            print(f"  - Aucune valeur manquante")
        
        # Valeurs uniques pour certaines colonnes clés
        key_columns = ['CATEGORIE', 'ENTREPOT', 'EMPLACEMENT', 'TYPE_PRODUIT', 'Entrepôt', 'Emplacement', 'Catégorie']
        print(f"\n🔑 Valeurs uniques pour colonnes clés:")
        for col in key_columns:
            if col in df.columns:
                unique_count = df[col].nunique()
                print(f"  • {col}: {unique_count} valeurs uniques")
                if unique_count < 50:
                    unique_vals = df[col].dropna().unique()
                    vals_str = ', '.join([str(v)[:30] for v in list(unique_vals)[:10]])
                    print(f"    Exemples: {vals_str}")
        
        # Statistiques numériques
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        if len(numeric_cols) > 0:
            print(f"\n📊 Colonnes numériques:")
            for col in numeric_cols:
                non_null = df[col].dropna()
                if len(non_null) > 0:
                    print(f"  • {col}:")
                    print(f"    - Min: {non_null.min()}")
                    print(f"    - Max: {non_null.max()}")
                    print(f"    - Moyenne: {non_null.mean():.2f}")
                    print(f"    - Total: {non_null.sum():.2f}")

except Exception as e:
    print(f"\n❌ Erreur lors de la lecture du fichier: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("FIN DE L'ANALYSE")
print("=" * 80)
