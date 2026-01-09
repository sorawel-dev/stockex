# -*- coding: utf-8 -*-
"""
Rapport d'écart de stock et analyse de variance.
"""

import logging
from odoo import models, fields, tools

_logger = logging.getLogger(__name__)


class StockVarianceReport(models.Model):
    """Rapport d'écart de stock."""
    _name = 'stockex.stock.variance.report'
    _description = 'Rapport d\'Écart de Stock'
    _auto = False  # Vue matérialisée
    _order = 'inventory_date desc, variance_value_abs desc'
    
    # Champs de base
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Produit',
        readonly=True
    )
    product_code = fields.Char(
        string='Code Produit',
        readonly=True
    )
    product_name = fields.Char(
        string='Nom du Produit',
        readonly=True
    )
    category_id = fields.Many2one(
        comodel_name='product.category',
        string='Catégorie',
        readonly=True
    )
    category_name = fields.Char(
        string='Nom de la Catégorie',
        readonly=True
    )
    location_id = fields.Many2one(
        comodel_name='stock.location',
        string='Emplacement',
        readonly=True
    )
    location_name = fields.Char(
        string='Nom de l\'Emplacement',
        readonly=True
    )
    inventory_id = fields.Many2one(
        comodel_name='stockex.stock.inventory',
        string='Inventaire',
        readonly=True
    )
    inventory_date = fields.Date(
        string='Date Inventaire',
        readonly=True
    )
    
    # Quantités
    theoretical_qty = fields.Float(
        string='Quantité Théorique',
        readonly=True
    )
    real_qty = fields.Float(
        string='Quantité Réelle',
        readonly=True
    )
    variance_qty = fields.Float(
        string='Écart Quantité',
        readonly=True
    )
    variance_qty_percent = fields.Float(
        string='% Écart Quantité',
        readonly=True
    )
    
    # Valeurs (corrigé pour utiliser le prix du produit avec cast)
    unit_price = fields.Float(
        string='Prix Unitaire',
        readonly=True
    )
    theoretical_value = fields.Float(
        string='Valeur Théorique',
        readonly=True
    )
    real_value = fields.Float(
        string='Valeur Réelle',
        readonly=True
    )
    variance_value = fields.Float(
        string='Valeur de l\'Écart',
        readonly=True
    )
    variance_value_abs = fields.Float(
        string='Valeur Absolue',
        readonly=True
    )
    
    # Classification
    variance_type = fields.Selection(
        selection=[
            ('surplus', 'Surplus'),
            ('shortage', 'Manquant'),
            ('ok', 'Aucun écart'),
        ],
        string='Type d\'Écart',
        readonly=True
    )
    
    severity = fields.Selection(
        selection=[
            ('critical', 'Critique (>20%)'),
            ('high', 'Élevé (10-20%)'),
            ('medium', 'Moyen (5-10%)'),
            ('low', 'Faible (<5%)'),
            ('ok', 'Acceptable'),
        ],
        string='Sévérité',
        readonly=True
    )
    
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Société',
        readonly=True
    )
    
    def init(self):
        """Créer la vue SQL pour le rapport de variance."""
        tools.drop_view_if_exists(self.env.cr, self._table)
        
        query = """
            CREATE OR REPLACE VIEW stockex_stock_variance_report AS (
                SELECT
                    line.id AS id,
                    line.product_id AS product_id,
                    prod.default_code AS product_code,
                    tmpl.name AS product_name,
                    cat.id AS category_id,
                    cat.name AS category_name,
                    line.location_id AS location_id,
                    loc.complete_name AS location_name,
                    line.inventory_id AS inventory_id,
                    inv.date AS inventory_date,
                    line.theoretical_qty AS theoretical_qty,
                    line.product_qty AS real_qty,
                    line.difference AS variance_qty,
                    CASE 
                        WHEN line.theoretical_qty = 0 THEN 0
                        ELSE (line.difference / NULLIF(line.theoretical_qty, 0) * 100)
                    END AS variance_qty_percent,
                    prod.standard_price::float AS unit_price,
                    (line.theoretical_qty * prod.standard_price::float) AS theoretical_value,
                    (line.product_qty * prod.standard_price::float) AS real_value,
                    (line.difference * prod.standard_price::float) AS variance_value,
                    ABS(line.difference * prod.standard_price::float) AS variance_value_abs,
                    CASE 
                        WHEN line.difference > 0 THEN 'surplus'
                        WHEN line.difference < 0 THEN 'shortage'
                        ELSE 'ok'
                    END AS variance_type,
                    CASE 
                        WHEN line.theoretical_qty = 0 THEN 'ok'
                        WHEN ABS(line.difference / NULLIF(line.theoretical_qty, 0) * 100) > 20 THEN 'critical'
                        WHEN ABS(line.difference / NULLIF(line.theoretical_qty, 0) * 100) > 10 THEN 'high'
                        WHEN ABS(line.difference / NULLIF(line.theoretical_qty, 0) * 100) > 5 THEN 'medium'
                        WHEN ABS(line.difference / NULLIF(line.theoretical_qty, 0) * 100) > 0 THEN 'low'
                        ELSE 'ok'
                    END AS severity,
                    inv.company_id AS company_id
                FROM
                    stockex_stock_inventory_line line
                    LEFT JOIN stockex_stock_inventory inv ON inv.id = line.inventory_id
                    LEFT JOIN product_product prod ON prod.id = line.product_id
                    LEFT JOIN product_template tmpl ON tmpl.id = prod.product_tmpl_id
                    LEFT JOIN product_category cat ON cat.id = tmpl.categ_id
                    LEFT JOIN stock_location loc ON loc.id = line.location_id
                WHERE
                    inv.state = 'done'
            )
        """
        self.env.cr.execute(query)


class VarianceAnalysisWizard(models.TransientModel):
    """Assistant d'analyse de variance."""
    _name = 'stockex.variance.analysis.wizard'
    _description = 'Analyse de Variance'
    
    date_from = fields.Date(
        string='Date Début',
        required=True,
        default=lambda self: fields.Date.today().replace(day=1)
    )
    
    date_to = fields.Date(
        string='Date Fin',
        required=True,
        default=fields.Date.today
    )
    
    location_ids = fields.Many2many(
        comodel_name='stock.location',
        string='Emplacements',
        domain="[('usage', '=', 'internal')]"
    )
    
    category_ids = fields.Many2many(
        comodel_name='product.category',
        string='Catégories'
    )
    
    variance_type = fields.Selection(
        selection=[
            ('all', 'Tous les écarts'),
            ('surplus', 'Surplus uniquement'),
            ('shortage', 'Manquants uniquement'),
        ],
        string='Type d\'Écart',
        default='all',
        required=True
    )
    
    min_variance_value = fields.Float(
        string='Écart Minimum (FCFA)',
        default=0.0,
        help='Afficher uniquement les écarts supérieurs à cette valeur'
    )
    
    severity_filter = fields.Selection(
        selection=[
            ('all', 'Toutes les sévérités'),
            ('critical_only', 'Critiques uniquement'),
            ('high_critical', 'Élevés et Critiques'),
        ],
        string='Filtre Sévérité',
        default='all'
    )
    
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Société',
        default=lambda self: self.env.company
    )
    
    def action_analyze(self):
        """Lance l'analyse de variance."""
        self.ensure_one()
        
        # Construire le domaine
        domain = [
            ('inventory_date', '>=', self.date_from),
            ('inventory_date', '<=', self.date_to),
            ('company_id', '=', self.company_id.id),
        ]
        
        if self.location_ids:
            domain.append(('location_id', 'in', self.location_ids.ids))
        
        if self.category_ids:
            domain.append(('category_id', 'in', self.category_ids.ids))
        
        if self.variance_type != 'all':
            domain.append(('variance_type', '=', self.variance_type))
        
        if self.min_variance_value > 0:
            domain.append(('variance_value_abs', '>=', self.min_variance_value))
        
        if self.severity_filter == 'critical_only':
            domain.append(('severity', '=', 'critical'))
        elif self.severity_filter == 'high_critical':
            domain.append(('severity', 'in', ['critical', 'high']))
        
        # Ouvrir la vue du rapport
        return {
            'type': 'ir.actions.act_window',
            'name': 'Analyse de Variance de Stock',
            'res_model': 'stockex.stock.variance.report',
            'view_mode': 'list,graph,pivot',
            'domain': domain,
            'context': {
                'search_default_group_category': 1,
                'search_default_group_location': 1,
            },
        }