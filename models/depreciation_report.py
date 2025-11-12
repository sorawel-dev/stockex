# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

class StockDepreciationReport(models.Model):
    _name = 'stockex.depreciation.report'
    _description = 'Rapport de Décote du Stock'
    _auto = False
    _order = 'depreciation_rate desc, days_since_move desc'
    
    product_id = fields.Many2one('product.product', string='Produit', readonly=True)
    default_code = fields.Char(string='Référence', readonly=True)
    category_id = fields.Many2one('product.category', string='Catégorie', readonly=True)
    quantity_on_hand = fields.Float(string='Quantité en Stock', readonly=True)
    last_move_date = fields.Date(string='Dernier Mouvement', readonly=True)
    days_since_move = fields.Integer(string='Jours sans Mouvement', readonly=True)
    depreciation_rate = fields.Float(string='Taux Décote (%)', readonly=True)
    depreciation_category = fields.Char(string='Catégorie Décote', readonly=True)
    base_price = fields.Float(string='Prix Unitaire Base', readonly=True)
    depreciated_price = fields.Float(string='Prix Unitaire Décoté', readonly=True)
    base_value = fields.Float(string='Valeur Totale Base', readonly=True)
    depreciated_value = fields.Float(string='Valeur Totale Décotée', readonly=True)
    value_loss = fields.Float(string='Perte de Valeur', readonly=True)
    company_id = fields.Many2one('res.company', string='Société', readonly=True)
    
    def init(self):
        """Créer la vue SQL pour le rapport."""
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW stockex_depreciation_report AS (
                SELECT 
                    ROW_NUMBER() OVER (ORDER BY sq.product_id) as id,
                    sq.product_id as product_id,
                    pp.default_code as default_code,
                    pt.categ_id as category_id,
                    sq.quantity as quantity_on_hand,
                    sm.date::date as last_move_date,
                    CASE 
                        WHEN sm.date IS NOT NULL 
                        THEN CURRENT_DATE - sm.date::date
                        ELSE NULL
                    END as days_since_move,
                    CASE 
                        WHEN sm.date IS NULL THEN 
                            CAST((SELECT value FROM ir_config_parameter WHERE key = 'stockex.depreciation_dead_rate') AS FLOAT)
                        WHEN CURRENT_DATE - sm.date::date <= CAST((SELECT value FROM ir_config_parameter WHERE key = 'stockex.depreciation_active_days') AS INTEGER) THEN 
                            0.0
                        WHEN CURRENT_DATE - sm.date::date <= CAST((SELECT value FROM ir_config_parameter WHERE key = 'stockex.depreciation_slow_days') AS INTEGER) THEN 
                            CAST((SELECT value FROM ir_config_parameter WHERE key = 'stockex.depreciation_slow_rate') AS FLOAT)
                        ELSE 
                            CAST((SELECT value FROM ir_config_parameter WHERE key = 'stockex.depreciation_dead_rate') AS FLOAT)
                    END as depreciation_rate,
                    CASE 
                        WHEN sm.date IS NULL THEN 
                            'Stock Mort (aucun mouvement)'
                        WHEN CURRENT_DATE - sm.date::date <= CAST((SELECT value FROM ir_config_parameter WHERE key = 'stockex.depreciation_active_days') AS INTEGER) THEN 
                            'Stock Actif'
                        WHEN CURRENT_DATE - sm.date::date <= CAST((SELECT value FROM ir_config_parameter WHERE key = 'stockex.depreciation_slow_days') AS INTEGER) THEN 
                            'Rotation Lente'
                        ELSE 
                            'Stock Mort'
                    END as depreciation_category,
                    COALESCE(CAST(pp.standard_price AS NUMERIC), 0.0) as base_price,
                    COALESCE(CAST(pp.standard_price AS NUMERIC), 0.0) * (1.0 - 
                        CASE 
                            WHEN sm.date IS NULL THEN 
                                CAST((SELECT value FROM ir_config_parameter WHERE key = 'stockex.depreciation_dead_rate') AS FLOAT) / 100.0
                            WHEN CURRENT_DATE - sm.date::date <= CAST((SELECT value FROM ir_config_parameter WHERE key = 'stockex.depreciation_active_days') AS INTEGER) THEN 
                                0.0
                            WHEN CURRENT_DATE - sm.date::date <= CAST((SELECT value FROM ir_config_parameter WHERE key = 'stockex.depreciation_slow_days') AS INTEGER) THEN 
                                CAST((SELECT value FROM ir_config_parameter WHERE key = 'stockex.depreciation_slow_rate') AS FLOAT) / 100.0
                            ELSE 
                                CAST((SELECT value FROM ir_config_parameter WHERE key = 'stockex.depreciation_dead_rate') AS FLOAT) / 100.0
                        END
                    ) as depreciated_price,
                    sq.quantity * COALESCE(CAST(pp.standard_price AS NUMERIC), 0.0) as base_value,
                    sq.quantity * COALESCE(CAST(pp.standard_price AS NUMERIC), 0.0) * (1.0 - 
                        CASE 
                            WHEN sm.date IS NULL THEN 
                                CAST((SELECT value FROM ir_config_parameter WHERE key = 'stockex.depreciation_dead_rate') AS FLOAT) / 100.0
                            WHEN CURRENT_DATE - sm.date::date <= CAST((SELECT value FROM ir_config_parameter WHERE key = 'stockex.depreciation_active_days') AS INTEGER) THEN 
                                0.0
                            WHEN CURRENT_DATE - sm.date::date <= CAST((SELECT value FROM ir_config_parameter WHERE key = 'stockex.depreciation_slow_days') AS INTEGER) THEN 
                                CAST((SELECT value FROM ir_config_parameter WHERE key = 'stockex.depreciation_slow_rate') AS FLOAT) / 100.0
                            ELSE 
                                CAST((SELECT value FROM ir_config_parameter WHERE key = 'stockex.depreciation_dead_rate') AS FLOAT) / 100.0
                        END
                    ) as depreciated_value,
                    sq.quantity * COALESCE(CAST(pp.standard_price AS NUMERIC), 0.0) * 
                        CASE 
                            WHEN sm.date IS NULL THEN 
                                CAST((SELECT value FROM ir_config_parameter WHERE key = 'stockex.depreciation_dead_rate') AS FLOAT) / 100.0
                            WHEN CURRENT_DATE - sm.date::date <= CAST((SELECT value FROM ir_config_parameter WHERE key = 'stockex.depreciation_active_days') AS INTEGER) THEN 
                                0.0
                            WHEN CURRENT_DATE - sm.date::date <= CAST((SELECT value FROM ir_config_parameter WHERE key = 'stockex.depreciation_slow_days') AS INTEGER) THEN 
                                CAST((SELECT value FROM ir_config_parameter WHERE key = 'stockex.depreciation_slow_rate') AS FLOAT) / 100.0
                            ELSE 
                                CAST((SELECT value FROM ir_config_parameter WHERE key = 'stockex.depreciation_dead_rate') AS FLOAT) / 100.0
                        END as value_loss,
                    sq.company_id as company_id
                FROM stock_quant sq
                JOIN product_product pp ON pp.id = sq.product_id
                JOIN product_template pt ON pt.id = pp.product_tmpl_id
                JOIN stock_location sl ON sl.id = sq.location_id
                LEFT JOIN LATERAL (
                    SELECT date
                    FROM stock_move sm2
                    WHERE sm2.product_id = sq.product_id
                    AND sm2.state = 'done'
                    ORDER BY date DESC
                    LIMIT 1
                ) sm ON TRUE
                WHERE sq.quantity > 0
                AND sl.usage = 'internal'
            )
        """)
