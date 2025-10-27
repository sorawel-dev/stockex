# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    """Configuration des paramètres du module Stockex."""
    _inherit = 'res.config.settings'
    
    # Méthode d'import par défaut
    stockex_default_import_method = fields.Selection(
        selection=[
            ('excel', '📊 Fichier Excel/CSV'),
            ('kobo', '📱 Kobo Collect'),
            ('choice', '🎯 Demander à Chaque Fois'),
        ],
        string='Méthode d\'Import par Défaut',
        default='choice',
        config_parameter='stockex.default_import_method',
        help='Définit la méthode utilisée par défaut pour créer de nouveaux inventaires'
    )
    
    # Options Excel
    stockex_excel_create_products = fields.Boolean(
        string='Créer les Produits Manquants (Excel)',
        default=True,
        config_parameter='stockex.excel_create_products',
        help='Créer automatiquement les produits lors de l\'import Excel'
    )
    
    stockex_excel_create_locations = fields.Boolean(
        string='Créer les Emplacements Manquants (Excel)',
        default=True,
        config_parameter='stockex.excel_create_locations',
        help='Créer automatiquement les entrepôts lors de l\'import Excel'
    )
    
    stockex_excel_update_prices = fields.Boolean(
        string='Mettre à Jour les Prix (Excel)',
        default=True,
        config_parameter='stockex.excel_update_prices',
        help='Mettre à jour les prix des produits lors de l\'import Excel'
    )
    
    stockex_excel_import_geolocation = fields.Boolean(
        string='Importer la Géolocalisation (Excel)',
        default=True,
        config_parameter='stockex.excel_import_geolocation',
        help='Importer les coordonnées GPS lors de l\'import Excel'
    )
    
    # Options Kobo
    stockex_kobo_default_config_id = fields.Many2one(
        comodel_name='stockex.kobo.config',
        string='Configuration Kobo par Défaut',
        config_parameter='stockex.kobo_default_config_id',
        domain="[('active', '=', True)]",
        help='Configuration Kobo utilisée par défaut'
    )
    
    stockex_kobo_create_products = fields.Boolean(
        string='Créer les Produits Manquants (Kobo)',
        default=True,
        config_parameter='stockex.kobo_create_products',
        help='Créer automatiquement les produits lors de l\'import Kobo'
    )
    
    stockex_kobo_create_locations = fields.Boolean(
        string='Créer les Emplacements Manquants (Kobo)',
        default=True,
        config_parameter='stockex.kobo_create_locations',
        help='Créer automatiquement les entrepôts lors de l\'import Kobo'
    )
    
    stockex_kobo_auto_validate = fields.Boolean(
        string='Validation Automatique (Kobo)',
        default=False,
        config_parameter='stockex.kobo_auto_validate',
        help='Valider automatiquement les inventaires créés depuis Kobo'
    )
    
    # Statistiques
    stockex_inventory_count = fields.Integer(
        string='Nombre d\'Inventaires',
        compute='_compute_stockex_stats',
        readonly=True
    )
    
    stockex_last_import_date = fields.Datetime(
        string='Dernier Import',
        compute='_compute_stockex_stats',
        readonly=True
    )
    
    @api.depends('company_id')
    def _compute_stockex_stats(self):
        """Calcule les statistiques d'utilisation."""
        for config in self:
            inventories = self.env['stockex.stock.inventory'].search([
                ('company_id', '=', config.company_id.id)
            ])
            
            config.stockex_inventory_count = len(inventories)
            config.stockex_last_import_date = inventories[0].create_date if inventories else False
    
    def action_open_kobo_config(self):
        """Ouvre la configuration Kobo Collect."""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Configuration Kobo Collect',
            'res_model': 'stockex.kobo.config',
            'view_mode': 'list,form',
            'target': 'current',
        }
