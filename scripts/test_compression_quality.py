#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test de qualité de compression
Compare différents niveaux de compression et affiche les résultats
"""

import sys
from PIL import Image
from io import BytesIO
import os

def test_compression_quality(image_path, output_dir="./test_compression"):
    """
    Teste différents niveaux de compression sur une image.
    
    Args:
        image_path: Chemin vers l'image à tester
        output_dir: Répertoire de sortie pour les images de test
    """
    if not os.path.exists(image_path):
        print(f"❌ Fichier non trouvé: {image_path}")
        return
    
    # Créer le répertoire de sortie
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n" + "="*70)
    print("🧪 TEST DE QUALITÉ DE COMPRESSION D'IMAGE")
    print("="*70)
    print(f"\n📸 Image source: {image_path}")
    
    # Charger l'image
    img = Image.open(image_path)
    original_size = os.path.getsize(image_path)
    
    print(f"   Dimensions: {img.size[0]} x {img.size[1]} pixels")
    print(f"   Format: {img.format}")
    print(f"   Mode: {img.mode}")
    print(f"   Taille: {original_size / 1024:.1f} KB")
    
    # Convertir en RGB si nécessaire
    if img.mode in ('RGBA', 'LA', 'P'):
        print("   ⚠️  Conversion en RGB nécessaire")
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = background
    
    # Tester différentes configurations
    configs = [
        # (max_dimension, quality, description)
        (None, 95, "Original - Qualité 95%"),
        (1600, 90, "1600px - Qualité 90% (RECOMMANDÉ)"),
        (1600, 85, "1600px - Qualité 85%"),
        (1200, 90, "1200px - Qualité 90%"),
        (1200, 85, "1200px - Qualité 85%"),
        (1200, 75, "1200px - Qualité 75%"),
        (800, 90, "800px - Qualité 90%"),
        (800, 75, "800px - Qualité 75%"),
        (800, 65, "800px - Qualité 65%"),
    ]
    
    print("\n" + "="*70)
    print("📊 RÉSULTATS DES TESTS")
    print("="*70)
    print()
    print(f"{'Configuration':<35} {'Taille':<12} {'Gain':<12} {'Ratio'}")
    print("-" * 70)
    
    results = []
    
    for max_dim, quality, description in configs:
        # Copier l'image
        test_img = img.copy()
        
        # Redimensionner si nécessaire
        if max_dim and max(test_img.size) > max_dim:
            ratio = max_dim / max(test_img.size)
            new_size = tuple(int(dim * ratio) for dim in test_img.size)
            test_img = test_img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Compresser
        output = BytesIO()
        test_img.save(output, format='JPEG', quality=quality, optimize=True, progressive=True)
        compressed_data = output.getvalue()
        compressed_size = len(compressed_data)
        
        # Calculer les gains
        gain_kb = (original_size - compressed_size) / 1024
        gain_percent = 100 * (1 - compressed_size / original_size)
        compression_ratio = original_size / compressed_size
        
        # Sauvegarder l'image de test
        filename = f"{description.replace(' ', '_').replace('%', 'pct')}.jpg"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(compressed_data)
        
        # Afficher les résultats
        size_str = f"{compressed_size/1024:.1f} KB"
        gain_str = f"-{gain_kb:.1f} KB ({gain_percent:.1f}%)"
        ratio_str = f"{compression_ratio:.2f}:1"
        
        print(f"{description:<35} {size_str:<12} {gain_str:<12} {ratio_str}")
        
        results.append({
            'config': description,
            'size': compressed_size,
            'gain': gain_percent,
            'ratio': compression_ratio,
            'path': filepath
        })
    
    print("\n" + "="*70)
    print("💡 RECOMMANDATIONS")
    print("="*70)
    print()
    print("✅ Configuration OPTIMALE (qualité/taille):")
    print("   • Dimension max: 1600px")
    print("   • Qualité JPEG: 90%")
    print("   • Gain moyen: ~70-80%")
    print("   • Qualité visuelle: Excellente")
    print()
    print("⚖️  Configuration ÉQUILIBRÉE:")
    print("   • Dimension max: 1200px")
    print("   • Qualité JPEG: 85%")
    print("   • Gain moyen: ~80-85%")
    print("   • Qualité visuelle: Très bonne")
    print()
    print("💾 Configuration ÉCONOMIE MAXIMALE:")
    print("   • Dimension max: 800px")
    print("   • Qualité JPEG: 75%")
    print("   • Gain moyen: ~85-90%")
    print("   • Qualité visuelle: Acceptable")
    print()
    print(f"📁 Images de test sauvegardées dans: {output_dir}")
    print(f"   Comparez visuellement pour choisir la meilleure config")
    print()
    
    # Trouver la meilleure configuration (>75% de gain, ratio >4)
    best_configs = [r for r in results if r['gain'] > 75 and r['ratio'] > 4]
    if best_configs:
        best = max(best_configs, key=lambda x: x['ratio'])
        print(f"🏆 Meilleure config détectée: {best['config']}")
        print(f"   Gain: {best['gain']:.1f}% | Ratio: {best['ratio']:.2f}:1")
    
    print()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 test_compression_quality.py <chemin_image>")
        print()
        print("Exemple:")
        print("  python3 test_compression_quality.py sample_photo.jpg")
        print()
        print("Le script va:")
        print("  1. Tester différentes configurations de compression")
        print("  2. Sauvegarder les images compressées dans ./test_compression/")
        print("  3. Afficher un tableau comparatif")
        print("  4. Recommander la meilleure configuration")
        sys.exit(1)
    
    image_path = sys.argv[1]
    test_compression_quality(image_path)
