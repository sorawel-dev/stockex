# -*- coding: utf-8 -*-

def migrate(cr, version):
    """Ajouter le champ color aux modèles utilisant le widget badge."""
    
    # Liste des tables qui ont besoin du champ color
    tables = [
        'stockex_stock_inventory',
        'stockex_stock_inventory_line',
        'stockex_inventory_lot_line',
        'stockex_warehouse_valuation_export_wizard',
    ]
    
    for table in tables:
        # Vérifier si la colonne existe déjà
        cr.execute(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='{table}' AND column_name='color'
        """)
        
        if not cr.fetchone():
            # Ajouter la colonne si elle n'existe pas
            cr.execute(f"ALTER TABLE {table} ADD COLUMN color INTEGER DEFAULT 0")
            print(f"✅ Colonne 'color' ajoutée à {table}")
        else:
            print(f"ℹ️  Colonne 'color' déjà présente dans {table}")
