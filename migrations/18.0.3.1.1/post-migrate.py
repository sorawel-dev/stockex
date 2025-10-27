# -*- coding: utf-8 -*-

import logging

_logger = logging.getLogger(__name__)


def _generate_warehouse_code(name):
    """
    Génère un diminutif intelligent du nom de l'entrepôt.
    
    Args:
        name (str): Nom de l'entrepôt
        
    Returns:
        str: Code diminutif (max 5 caractères)
    """
    if not name:
        return 'WH'
    
    name = name.strip()
    words = name.split()
    
    if len(words) == 1:
        # Un seul mot : prendre les 5 premiers caractères
        code = name[:5].upper()
    else:
        # Plusieurs mots : prendre la première lettre de chaque mot (max 5)
        code = ''.join([word[0].upper() for word in words[:5] if word])
        # Si le code est trop court, compléter avec les premières lettres du premier mot
        if len(code) < 3 and words:
            code = (words[0][:3] + code).upper()[:5]
    
    return code


def migrate(cr, version):
    """
    Migration pour recalculer les codes (diminutifs) des entrepôts existants.
    
    Le code devient un vrai diminutif du nom, pas juste un identifiant technique.
    Les warehouse_code conservent les anciennes valeurs.
    """
    _logger.info("="*70)
    _logger.info("Migration: Recalcul des codes entrepôts comme diminutifs du nom")
    _logger.info("="*70)
    
    # Récupérer tous les entrepôts
    cr.execute("""
        SELECT id, name, code, warehouse_code
        FROM stock_warehouse
        WHERE name IS NOT NULL
        ORDER BY id
    """)
    
    warehouses = cr.fetchall()
    
    if not warehouses:
        _logger.info("Aucun entrepôt à migrer")
        return
    
    _logger.info(f"Traitement de {len(warehouses)} entrepôts...")
    _logger.info("-"*70)
    
    updated_count = 0
    
    for wh_id, name, old_code, warehouse_code in warehouses:
        # Générer le nouveau code (diminutif)
        new_code = _generate_warehouse_code(name)
        
        # Mettre à jour uniquement si le code change
        if new_code != old_code:
            cr.execute("""
                UPDATE stock_warehouse
                SET code = %s
                WHERE id = %s
            """, (new_code, wh_id))
            
            _logger.info(f"  ID {wh_id}: '{name}'")
            _logger.info(f"    Ancien code: {old_code} → Nouveau: {new_code}")
            if warehouse_code:
                _logger.info(f"    Code entrepôt conservé: {warehouse_code}")
            updated_count += 1
        else:
            _logger.debug(f"  ID {wh_id}: '{name}' - Code déjà correct: {old_code}")
    
    _logger.info("-"*70)
    _logger.info(f"✅ {updated_count} entrepôts mis à jour sur {len(warehouses)} traités")
    _logger.info("="*70)
    _logger.info("Migration terminée avec succès")
    _logger.info("Les codes sont maintenant des diminutifs intelligents du nom")
    _logger.info("="*70)
