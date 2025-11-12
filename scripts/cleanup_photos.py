#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de nettoyage des photos Odoo
Supprime les attachments images orphelins et compresse les anciennes photos
"""

import os
import sys

# Ajouter le chemin Odoo au PYTHONPATH si nécessaire
# sys.path.append('/path/to/odoo')

def cleanup_photos(dry_run=True):
    """
    Nettoie les photos dans Odoo:
    1. Supprime les attachments orphelins (lignes d'inventaire supprimées)
    2. Compresse les grandes images (>1MB)
    3. Affiche les statistiques d'espace libéré
    
    Args:
        dry_run: Si True, affiche ce qui serait fait sans modifier
    """
    import odoo
    from odoo import api, SUPERUSER_ID
    
    # Connexion à la base de données
    db_name = input("Nom de la base de données Odoo: ").strip()
    if not db_name:
        print("❌ Nom de base requis")
        return
    
    odoo.tools.config.parse_config([])
    odoo.tools.config['db_name'] = db_name
    
    registry = odoo.registry(db_name)
    
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        
        print("\n" + "="*60)
        print("🧹 NETTOYAGE DES PHOTOS ODOO")
        print("="*60)
        print(f"Mode: {'SIMULATION' if dry_run else 'RÉEL'}")
        print()
        
        # 1. Trouver les attachments orphelins
        print("1️⃣  Recherche des attachments orphelins...")
        orphan_attachments = env['ir.attachment'].search([
            ('res_model', '=', 'stockex.stock.inventory.line'),
            ('mimetype', 'like', 'image/%'),
        ])
        
        orphans_to_delete = []
        for att in orphan_attachments:
            # Vérifier si la ligne existe encore
            if not env['stockex.stock.inventory.line'].browse(att.res_id).exists():
                orphans_to_delete.append(att)
        
        if orphans_to_delete:
            total_size = sum(len(att.datas or b'') for att in orphans_to_delete) / (1024*1024)
            print(f"   ✅ {len(orphans_to_delete)} attachments orphelins trouvés ({total_size:.2f} MB)")
            
            if not dry_run:
                orphans_to_delete.unlink()
                print(f"   ✅ Supprimés")
        else:
            print("   ✅ Aucun attachment orphelin")
        
        # 2. Compresser les grandes images
        print("\n2️⃣  Recherche des grandes images à compresser...")
        all_images = env['ir.attachment'].search([
            ('res_model', '=', 'stockex.stock.inventory.line'),
            ('mimetype', 'like', 'image/%'),
        ])
        
        large_images = []
        for att in all_images:
            if att.datas:
                size_mb = len(att.datas) / (1024*1024)
                if size_mb > 1.0:  # Plus de 1MB
                    large_images.append((att, size_mb))
        
        if large_images:
            print(f"   ✅ {len(large_images)} grandes images trouvées")
            
            if not dry_run:
                try:
                    from PIL import Image
                    from io import BytesIO
                    import base64
                    
                    compressed_count = 0
                    total_saved = 0
                    
                    for att, original_size in large_images:
                        try:
                            # Décoder l'image
                            img_data = base64.b64decode(att.datas)
                            img = Image.open(BytesIO(img_data))
                            
                            # Convertir en RGB
                            if img.mode in ('RGBA', 'LA', 'P'):
                                background = Image.new('RGB', img.size, (255, 255, 255))
                                if img.mode == 'P':
                                    img = img.convert('RGBA')
                                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                                img = background
                            
                            # Redimensionner si trop grand
                            if max(img.size) > 1200:
                                ratio = 1200 / max(img.size)
                                new_size = tuple(int(dim * ratio) for dim in img.size)
                                img = img.resize(new_size, Image.Resampling.LANCZOS)
                            
                            # Compresser
                            output = BytesIO()
                            img.save(output, format='JPEG', quality=85, optimize=True)
                            compressed_data = output.getvalue()
                            
                            new_size = len(compressed_data) / (1024*1024)
                            saved = original_size - new_size
                            
                            if saved > 0.1:  # Au moins 100KB économisés
                                att.write({
                                    'datas': base64.b64encode(compressed_data),
                                    'mimetype': 'image/jpeg'
                                })
                                compressed_count += 1
                                total_saved += saved
                                print(f"      ✅ {att.name}: {original_size:.2f}MB → {new_size:.2f}MB (gain: {saved:.2f}MB)")
                        
                        except Exception as e:
                            print(f"      ⚠️  Erreur compression {att.name}: {e}")
                    
                    print(f"\n   ✅ {compressed_count} images compressées")
                    print(f"   💾 Espace libéré: {total_saved:.2f} MB")
                    
                except ImportError:
                    print("   ⚠️  Pillow non installé, compression impossible")
                    print("      Installez avec: pip3 install Pillow")
        else:
            print("   ✅ Aucune grande image à compresser")
        
        # 3. Statistiques finales
        print("\n" + "="*60)
        print("📊 STATISTIQUES")
        print("="*60)
        
        total_attachments = env['ir.attachment'].search_count([
            ('res_model', '=', 'stockex.stock.inventory.line'),
            ('mimetype', 'like', 'image/%'),
        ])
        
        total_size = 0
        for att in env['ir.attachment'].search([
            ('res_model', '=', 'stockex.stock.inventory.line'),
            ('mimetype', 'like', 'image/%'),
        ]):
            if att.datas:
                total_size += len(att.datas)
        
        print(f"Total attachments: {total_attachments}")
        print(f"Espace total: {total_size/(1024*1024):.2f} MB")
        print()
        
        if not dry_run:
            cr.commit()
            print("✅ Modifications enregistrées")
        else:
            print("ℹ️  Mode simulation - Aucune modification appliquée")
            print("   Relancez avec --execute pour appliquer les changements")


if __name__ == '__main__':
    dry_run = '--execute' not in sys.argv
    cleanup_photos(dry_run=dry_run)
