# -*- coding: utf-8 -*-

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """
    Migration post-installation pour transférer les valeurs du champ 'code' 
    vers le nouveau champ 'warehouse_code'.
    
    Après cette migration :
    - Les anciennes valeurs de 'code' (ex: WH-ABJ-001) sont copiées dans 'warehouse_code'
    - Le champ 'code' sera recalculé automatiquement comme diminutif du nom
    """
    _logger.info("="*70)
    _logger.info("Début migration: Transfert code → warehouse_code pour stock.warehouse")
    _logger.info("="*70)
    
    # Vérifier si le champ warehouse_code existe
    cr.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='stock_warehouse' 
        AND column_name='warehouse_code'
    """)
    
    if not cr.fetchone():
        _logger.warning("Le champ warehouse_code n'existe pas encore, migration ignorée")
        return
    
    # Copier les valeurs de code vers warehouse_code pour les entrepôts qui ont un code
    cr.execute("""
        UPDATE stock_warehouse
        SET warehouse_code = code
        WHERE code IS NOT NULL 
        AND code != ''
        AND warehouse_code IS NULL
    """)
    
    affected_rows = cr.rowcount
    _logger.info(f"✅ {affected_rows} entrepôts mis à jour: code → warehouse_code")
    
    # Lister les entrepôts migrés
    cr.execute("""
        SELECT id, name, warehouse_code
        FROM stock_warehouse
        WHERE warehouse_code IS NOT NULL
        ORDER BY id
    """)
    
    warehouses = cr.fetchall()
    if warehouses:
        _logger.info("-"*70)
        _logger.info("Entrepôts migrés:")
        for wh_id, name, wh_code in warehouses:
            _logger.info(f"  ID {wh_id}: {name} → Code: {wh_code}")
        _logger.info("-"*70)
    
    _logger.info("="*70)
    _logger.info("Migration terminée avec succès")
    _logger.info("Les champs 'code' seront recalculés automatiquement au prochain démarrage")
    _logger.info("="*70)
