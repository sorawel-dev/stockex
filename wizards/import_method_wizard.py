# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class ImportMethodWizard(models.TransientModel):
    """Wizard pour choisir la méthode d'import des données d'inventaire."""
    _name = 'stockex.import.method.wizard'
    _description = 'Choix de la Méthode d\'Import'
    
    @api.model
    def default_get(self, fields_list):
        """Bypass le wizard si une méthode par défaut est configurée."""
        res = super().default_get(fields_list)
        
        # Vérifier si une méthode par défaut est configurée
        default_method = self.env['ir.config_parameter'].sudo().get_param('stockex.default_import_method', 'choice')
        
        # Si pas de choix manuel, rediriger directement
        if default_method != 'choice' and self.env.context.get('auto_redirect', True):
            res['import_method'] = default_method
        
        return res
    
    import_method = fields.Selection(
        selection=[
            ('excel', '📊 Fichier Excel/CSV'),
            ('kobo', '📱 Kobo Collect'),
        ],
        string='Méthode d\'Import',
        required=True,
        default=lambda self: self._get_default_import_method(),
        help='Choisissez comment vous souhaitez importer vos données d\'inventaire'
    )
    
    def _get_default_import_method(self):
        """Récupère la méthode d'import par défaut depuis les paramètres."""
        default_method = self.env['ir.config_parameter'].sudo().get_param('stockex.default_import_method', 'choice')
        
        if default_method == 'choice':
            return 'excel'  # Par défaut si choix manuel
        return default_method
    
    name = fields.Char(
        string='Nom de l\'Inventaire',
        required=True,
        default=lambda self: f"Inventaire {fields.Date.today()}"
    )
    
    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.today
    )
    
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Société',
        required=True,
        default=lambda self: self.env.company
    )
    
    # Statistiques
    excel_import_count = fields.Integer(
        string='Imports Excel',
        compute='_compute_stats'
    )
    
    kobo_import_count = fields.Integer(
        string='Imports Kobo',
        compute='_compute_stats'
    )
    
    kobo_config_exists = fields.Boolean(
        string='Kobo Configuré',
        compute='_compute_kobo_config'
    )
    
    kobo_submissions_available = fields.Integer(
        string='Soumissions Disponibles',
        compute='_compute_kobo_config'
    )
    
    @api.depends('company_id')
    def _compute_stats(self):
        """Calcule les statistiques d'import."""
        for wizard in self:
            wizard.excel_import_count = 0  # À implémenter
            wizard.kobo_import_count = 0  # À implémenter
    
    @api.depends('company_id')
    def _compute_kobo_config(self):
        """Vérifie si Kobo Collect est configuré."""
        for wizard in self:
            config = self.env['stockex.kobo.config'].search([
                ('active', '=', True),
                ('company_id', '=', wizard.company_id.id)
            ], limit=1)
            
            wizard.kobo_config_exists = bool(config)
            wizard.kobo_submissions_available = config.submissions_count if config else 0
    
    def action_continue(self):
        """Redirige vers le wizard approprié."""
        self.ensure_one()
        
        if self.import_method == 'excel':
            return {
                'type': 'ir.actions.act_window',
                'name': 'Import Excel/CSV',
                'res_model': 'stockex.import.excel.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_name': self.name,
                    'default_date': self.date,
                    'default_company_id': self.company_id.id,
                },
            }
        
        elif self.import_method == 'kobo':
            return {
                'type': 'ir.actions.act_window',
                'name': 'Import Kobo Collect',
                'res_model': 'stockex.import.kobo.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_name': self.name,
                    'default_date': self.date,
                    'default_company_id': self.company_id.id,
                },
            }
    
    def action_configure_kobo(self):
        """Ouvre la configuration Kobo."""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Configuration Kobo Collect',
            'res_model': 'stockex.kobo.config',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_company_id': self.company_id.id,
            },
        }
