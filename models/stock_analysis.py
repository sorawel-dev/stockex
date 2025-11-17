# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class StockAnalysis(models.Model):
    _name = 'stockex.stock.analysis'
    _description = 'Analyse Complète des Stocks'
    _auto = False
    _rec_name = 'product_id'
    _order = 'date desc, product_id'

    # Dimensions d'analyse
    date = fields.Date(string='Date', readonly=True)
    product_id = fields.Many2one('product.product', string='Produit', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', string='Modèle Produit', readonly=True)
    categ_id = fields.Many2one('product.category', string='Catégorie', readonly=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Entrepôt', readonly=True)
    location_id = fields.Many2one('stock.location', string='Emplacement', readonly=True)
    company_id = fields.Many2one('res.company', string='Société', readonly=True)
    
    # Informations produit
    default_code = fields.Char(string='Référence Interne', readonly=True)
    barcode = fields.Char(string='Code-Barres', readonly=True)
    product_type = fields.Selection([
        ('product', 'Article Stockable'),
        ('consu', 'Consommable'),
        ('service', 'Service')
    ], string='Type de Produit', readonly=True)
    
    # Métriques de quantité
    quantity_on_hand = fields.Float(string='Qté en Main', readonly=True, digits='Product Unit of Measure')
    quantity_available = fields.Float(string='Qté Disponible', readonly=True, digits='Product Unit of Measure')
    quantity_reserved = fields.Float(string='Qté Réservée', readonly=True, digits='Product Unit of Measure')
    quantity_incoming = fields.Float(string='Qté Entrante', readonly=True, digits='Product Unit of Measure')
    quantity_outgoing = fields.Float(string='Qté Sortante', readonly=True, digits='Product Unit of Measure')
    
    # Métriques de valorisation
    standard_price = fields.Float(string='Coût Standard', readonly=True, digits='Product Price')
    economic_price = fields.Float(string='Coût Économique', readonly=True, digits='Product Price')
    value_on_hand = fields.Float(string='Valeur en Main', readonly=True, digits='Product Price')
    value_available = fields.Float(string='Valeur Disponible', readonly=True, digits='Product Price')
    value_reserved = fields.Float(string='Valeur Réservée', readonly=True, digits='Product Price')
    
    # Décote et rotation
    last_move_date = fields.Date(string='Dernier Mouvement', readonly=True)
    days_since_last_move = fields.Integer(string='Jours sans Mouvement', readonly=True)
    rotation_status = fields.Selection([
        ('active', 'Stock Actif'),
        ('slow', 'Rotation Lente'),
        ('dead', 'Stock Mort')
    ], string='Statut Rotation', readonly=True)
    depreciation_rate = fields.Float(string='Taux Décote (%)', readonly=True)
    depreciated_value = fields.Float(string='Valeur Décotée (VSD)', readonly=True, digits='Product Price')
    
    # Inventaire
    inventory_id = fields.Many2one('stockex.stock.inventory', string='Inventaire', readonly=True)
    inventory_date = fields.Date(string='Date Inventaire', readonly=True)
    inventory_qty = fields.Float(string='Qté Inventoriée', readonly=True, digits='Product Unit of Measure')
    inventory_value = fields.Float(string='Valeur Inventoriée', readonly=True, digits='Product Price')
    inventory_difference = fields.Float(string='Écart Inventaire', readonly=True, digits='Product Unit of Measure')
    inventory_difference_value = fields.Float(string='Écart Valeur', readonly=True, digits='Product Price')
    
    # Indicateurs de performance
    stock_coverage_days = fields.Integer(string='Couverture Stock (jours)', readonly=True)
    turnover_rate = fields.Float(string='Taux de Rotation', readonly=True)
    abc_classification = fields.Selection([
        ('A', 'Classe A (80% valeur)'),
        ('B', 'Classe B (15% valeur)'),
        ('C', 'Classe C (5% valeur)')
    ], string='Classification ABC', readonly=True)
    
    # Alertes
    is_stockout = fields.Boolean(string='Rupture de Stock', readonly=True)
    is_overstock = fields.Boolean(string='Surstock', readonly=True)
    has_negative_stock = fields.Boolean(string='Stock Négatif', readonly=True)
    needs_recount = fields.Boolean(string='Recompte Nécessaire', readonly=True)

    def init(self):
        """Créer la vue SQL pour l'analyse."""
        # Vérifier la présence des tables nécessaires (module Stock installé)
        self.env.cr.execute("SELECT to_regclass('stock_valuation_layer'), to_regclass('stock_move')")
        svl_reg, sm_reg = self.env.cr.fetchone()
        svl_present = bool(svl_reg)
        if not sm_reg:
            _logger.warning("Stock non installé ou tables manquantes (stock_move). Vue %s non créée.", self._table)
            tools.drop_view_if_exists(self.env.cr, self._table)
            return
        tools.drop_view_if_exists(self.env.cr, self._table)
        
        if svl_present:
            query = """
        CREATE OR REPLACE VIEW %s AS (
            SELECT 
                ROW_NUMBER() OVER (ORDER BY sq.id, inv.id) as id,
                
                -- Dimensions temporelles
                COALESCE(inv.date, CURRENT_DATE) as date,
                
                -- Dimensions produit
                sq.product_id,
                pp.product_tmpl_id,
                pt.categ_id,
                sl.warehouse_id,
                sq.location_id,
                sq.company_id,
                
                -- Informations produit
                pp.default_code,
                pp.barcode,
                pt.type as product_type,
                
                -- Quantités
                COALESCE(sq.quantity, 0.0) as quantity_on_hand,
                COALESCE(sq.quantity, 0.0) - COALESCE(sq.reserved_quantity, 0.0) as quantity_available,
                COALESCE(sq.reserved_quantity, 0.0) as quantity_reserved,
                0.0 as quantity_incoming,
                0.0 as quantity_outgoing,
                
                -- Valorisation (via SVL)
                COALESCE((SELECT unit_cost FROM stock_valuation_layer svl WHERE svl.product_id = sq.product_id ORDER BY create_date DESC LIMIT 1), 0.0) as standard_price,
                COALESCE((SELECT unit_cost FROM stock_valuation_layer svl WHERE svl.product_id = sq.product_id ORDER BY create_date DESC LIMIT 1), 0.0) as economic_price,
                COALESCE(sq.quantity, 0.0) * COALESCE((SELECT unit_cost FROM stock_valuation_layer svl WHERE svl.product_id = sq.product_id ORDER BY create_date DESC LIMIT 1), 0.0) as value_on_hand,
                (COALESCE(sq.quantity, 0.0) - COALESCE(sq.reserved_quantity, 0.0)) * COALESCE((SELECT unit_cost FROM stock_valuation_layer svl WHERE svl.product_id = sq.product_id ORDER BY create_date DESC LIMIT 1), 0.0) as value_available,
                COALESCE(sq.reserved_quantity, 0.0) * COALESCE((SELECT unit_cost FROM stock_valuation_layer svl WHERE svl.product_id = sq.product_id ORDER BY create_date DESC LIMIT 1), 0.0) as value_reserved,
                
                -- Rotation et décote
                (SELECT MAX(sm.date) FROM stock_move sm WHERE sm.product_id = sq.product_id AND sm.state = 'done') as last_move_date,
                COALESCE(CURRENT_DATE - (SELECT MAX(sm.date)::date FROM stock_move sm WHERE sm.product_id = sq.product_id AND sm.state = 'done'), 9999) as days_since_last_move,
                CASE WHEN COALESCE(CURRENT_DATE - (SELECT MAX(sm.date)::date FROM stock_move sm WHERE sm.product_id = sq.product_id AND sm.state = 'done'), 9999) < 365 THEN 'active'
                     WHEN COALESCE(CURRENT_DATE - (SELECT MAX(sm.date)::date FROM stock_move sm WHERE sm.product_id = sq.product_id AND sm.state = 'done'), 9999) BETWEEN 365 AND 1095 THEN 'slow'
                     ELSE 'dead' END as rotation_status,
                CASE WHEN COALESCE(CURRENT_DATE - (SELECT MAX(sm.date)::date FROM stock_move sm WHERE sm.product_id = sq.product_id AND sm.state = 'done'), 9999) < 365 THEN 0.0
                     WHEN COALESCE(CURRENT_DATE - (SELECT MAX(sm.date)::date FROM stock_move sm WHERE sm.product_id = sq.product_id AND sm.state = 'done'), 9999) BETWEEN 365 AND 1095 THEN 40.0
                     ELSE 100.0 END as depreciation_rate,
                COALESCE(sq.quantity, 0.0) * COALESCE((SELECT unit_cost FROM stock_valuation_layer svl WHERE svl.product_id = sq.product_id ORDER BY create_date DESC LIMIT 1), 0.0) * (1 - (CASE WHEN COALESCE(CURRENT_DATE - (SELECT MAX(sm.date)::date FROM stock_move sm WHERE sm.product_id = sq.product_id AND sm.state = 'done'), 9999) < 365 THEN 0.0 WHEN COALESCE(CURRENT_DATE - (SELECT MAX(sm.date)::date FROM stock_move sm WHERE sm.product_id = sq.product_id AND sm.state = 'done'), 9999) BETWEEN 365 AND 1095 THEN 0.4 ELSE 1.0 END)) as depreciated_value,
                
                -- Inventaire
                inv.id as inventory_id,
                inv.date as inventory_date,
                invl.product_qty as inventory_qty,
                invl.product_qty * COALESCE((SELECT unit_cost FROM stock_valuation_layer svl WHERE svl.product_id = sq.product_id ORDER BY create_date DESC LIMIT 1), 0.0) as inventory_value,
                COALESCE(invl.difference, 0.0) as inventory_difference,
                COALESCE(invl.difference, 0.0) * COALESCE((SELECT unit_cost FROM stock_valuation_layer svl WHERE svl.product_id = sq.product_id ORDER BY create_date DESC LIMIT 1), 0.0) as inventory_difference_value,
                
                -- Indicateurs
                30 as stock_coverage_days,
                0.0 as turnover_rate,
                'B' as abc_classification,
                
                -- Alertes
                CASE WHEN COALESCE(sq.quantity, 0.0) <= 0 THEN TRUE ELSE FALSE END as is_stockout,
                FALSE as is_overstock,
                CASE WHEN COALESCE(sq.quantity, 0.0) < 0 THEN TRUE ELSE FALSE END as has_negative_stock,
                CASE WHEN ABS(COALESCE(invl.difference, 0.0)) > COALESCE(sq.quantity, 0.0) * 0.1 THEN TRUE ELSE FALSE END as needs_recount
                
            FROM stock_quant sq
            JOIN product_product pp ON pp.id = sq.product_id
            JOIN product_template pt ON pt.id = pp.product_tmpl_id
            LEFT JOIN stock_location sl ON sl.id = sq.location_id
            LEFT JOIN stockex_stock_inventory_line invl ON invl.product_id = sq.product_id AND invl.location_id = sq.location_id
            LEFT JOIN stockex_stock_inventory inv ON inv.id = invl.inventory_id
            WHERE sl.usage = 'internal'
              AND pt.type = 'product'
        )
        """ % (self._table,)
        else:
            # Fallback sans SVL: utiliser le coût standard du template
            query = """
        CREATE OR REPLACE VIEW %s AS (
            SELECT 
                ROW_NUMBER() OVER (ORDER BY sq.id, inv.id) as id,
                
                COALESCE(inv.date, CURRENT_DATE) as date,
                sq.product_id,
                pp.product_tmpl_id,
                pt.categ_id,
                sl.warehouse_id,
                sq.location_id,
                sq.company_id,
                pp.default_code,
                pp.barcode,
                pt.type as product_type,
                COALESCE(sq.quantity, 0.0) as quantity_on_hand,
                COALESCE(sq.quantity, 0.0) - COALESCE(sq.reserved_quantity, 0.0) as quantity_available,
                COALESCE(sq.reserved_quantity, 0.0) as quantity_reserved,
                0.0 as quantity_incoming,
                0.0 as quantity_outgoing,
                
                -- Valorisation (fallback)
                COALESCE((pp.standard_price)::numeric, 0.0) as standard_price,
                COALESCE((pp.standard_price)::numeric, 0.0) as economic_price,
                COALESCE(sq.quantity, 0.0) * COALESCE((pp.standard_price)::numeric, 0.0) as value_on_hand,
                (COALESCE(sq.quantity, 0.0) - COALESCE(sq.reserved_quantity, 0.0)) * COALESCE((pp.standard_price)::numeric, 0.0) as value_available,
                COALESCE(sq.reserved_quantity, 0.0) * COALESCE((pp.standard_price)::numeric, 0.0) as value_reserved,
                
                (SELECT MAX(sm.date) FROM stock_move sm WHERE sm.product_id = sq.product_id AND sm.state = 'done') as last_move_date,
                COALESCE(CURRENT_DATE - (SELECT MAX(sm.date)::date FROM stock_move sm WHERE sm.product_id = sq.product_id AND sm.state = 'done'), 9999) as days_since_last_move,
                CASE WHEN COALESCE(CURRENT_DATE - (SELECT MAX(sm.date)::date FROM stock_move sm WHERE sm.product_id = sq.product_id AND sm.state = 'done'), 9999) < 365 THEN 'active'
                     WHEN COALESCE(CURRENT_DATE - (SELECT MAX(sm.date)::date FROM stock_move sm WHERE sm.product_id = sq.product_id AND sm.state = 'done'), 9999) BETWEEN 365 AND 1095 THEN 'slow'
                     ELSE 'dead' END as rotation_status,
                CASE WHEN COALESCE(CURRENT_DATE - (SELECT MAX(sm.date)::date FROM stock_move sm WHERE sm.product_id = sq.product_id AND sm.state = 'done'), 9999) < 365 THEN 0.0
                     WHEN COALESCE(CURRENT_DATE - (SELECT MAX(sm.date)::date FROM stock_move sm WHERE sm.product_id = sq.product_id AND sm.state = 'done'), 9999) BETWEEN 365 AND 1095 THEN 40.0
                     ELSE 100.0 END as depreciation_rate,
                COALESCE(sq.quantity, 0.0) * COALESCE((pp.standard_price)::numeric, 0.0) * (1 - (CASE WHEN COALESCE(CURRENT_DATE - (SELECT MAX(sm.date)::date FROM stock_move sm WHERE sm.product_id = sq.product_id AND sm.state = 'done'), 9999) < 365 THEN 0.0 WHEN COALESCE(CURRENT_DATE - (SELECT MAX(sm.date)::date FROM stock_move sm WHERE sm.product_id = sq.product_id AND sm.state = 'done'), 9999) BETWEEN 365 AND 1095 THEN 0.4 ELSE 1.0 END)) as depreciated_value,
                
                inv.id as inventory_id,
                inv.date as inventory_date,
                invl.product_qty as inventory_qty,
                invl.product_qty * COALESCE((pp.standard_price)::numeric, 0.0) as inventory_value,
                COALESCE(invl.difference, 0.0) as inventory_difference,
                COALESCE(invl.difference, 0.0) * COALESCE((pp.standard_price)::numeric, 0.0) as inventory_difference_value,
                
                30 as stock_coverage_days,
                0.0 as turnover_rate,
                'B' as abc_classification,
                CASE WHEN COALESCE(sq.quantity, 0.0) <= 0 THEN TRUE ELSE FALSE END as is_stockout,
                FALSE as is_overstock,
                CASE WHEN COALESCE(sq.quantity, 0.0) < 0 THEN TRUE ELSE FALSE END as has_negative_stock,
                CASE WHEN ABS(COALESCE(invl.difference, 0.0)) > COALESCE(sq.quantity, 0.0) * 0.1 THEN TRUE ELSE FALSE END as needs_recount
                
            FROM stock_quant sq
            JOIN product_product pp ON pp.id = sq.product_id
            JOIN product_template pt ON pt.id = pp.product_tmpl_id
            LEFT JOIN stock_location sl ON sl.id = sq.location_id
            LEFT JOIN stockex_stock_inventory_line invl ON invl.product_id = sq.product_id AND invl.location_id = sq.location_id
            LEFT JOIN stockex_stock_inventory inv ON inv.id = invl.inventory_id
            WHERE sl.usage = 'internal'
              AND pt.type = 'product'
        )
        """ % (self._table,)
        
        self.env.cr.execute(query)                

    @api.model
    def action_open_analysis(self):
        """Ouvrir l'analyse complète des stocks."""
        return {
            'name': 'Analyse Complète des Stocks',
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'pivot,graph,list,form',
            'views': [
                (False, 'pivot'),
                (False, 'graph'),
                (False, 'list'),
                (False, 'form'),
            ],
            'context': {
                'search_default_group_by_warehouse': 1,
                'search_default_group_by_category': 1,
                'pivot_measures': ['quantity_on_hand', 'quantity_available', 'quantity_reserved', 'inventory_qty', 'inventory_difference', 'value_on_hand', 'depreciated_value', 'inventory_difference_value'],
                'graph_type': 'bar',
            },
            'target': 'current',
        }
