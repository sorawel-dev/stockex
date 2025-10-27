# -*- coding: utf-8 -*-

import logging
from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class CycleCountConfig(models.Model):
    """Configuration pour le comptage cyclique."""
    _name = 'stockex.cycle.count.config'
    _description = 'Configuration Comptage Cyclique'
    
    name = fields.Char(
        string='Nom',
        required=True,
        help='Nom de la configuration de comptage cyclique'
    )
    
    active = fields.Boolean(
        string='Actif',
        default=True
    )
    
    location_ids = fields.Many2many(
        comodel_name='stock.location',
        string='Emplacements',
        domain="[('usage', '=', 'internal')]",
        required=True,
        help='Emplacements inclus dans le comptage cyclique'
    )
    
    category_ids = fields.Many2many(
        comodel_name='product.category',
        string='Catégories de Produits',
        help='Catégories de produits à compter (vide = toutes)'
    )
    
    frequency = fields.Selection(
        selection=[
            ('daily', 'Quotidien'),
            ('weekly', 'Hebdomadaire'),
            ('monthly', 'Mensuel'),
            ('quarterly', 'Trimestriel'),
        ],
        string='Fréquence',
        required=True,
        default='monthly'
    )
    
    day_of_week = fields.Selection(
        selection=[
            ('0', 'Lundi'),
            ('1', 'Mardi'),
            ('2', 'Mercredi'),
            ('3', 'Jeudi'),
            ('4', 'Vendredi'),
            ('5', 'Samedi'),
            ('6', 'Dimanche'),
        ],
        string='Jour de la semaine',
        help='Pour fréquence hebdomadaire'
    )
    
    day_of_month = fields.Integer(
        string='Jour du mois',
        default=1,
        help='Pour fréquence mensuelle/trimestrielle (1-28)'
    )
    
    products_per_count = fields.Integer(
        string='Produits par comptage',
        default=50,
        help='Nombre de produits à compter à chaque cycle'
    )
    
    priority_abc = fields.Selection(
        selection=[
            ('A', 'Classe A uniquement (haute valeur)'),
            ('AB', 'Classes A et B'),
            ('ABC', 'Toutes classes (A, B, C)'),
        ],
        string='Priorité ABC',
        default='ABC',
        help='Prioriser les produits selon leur classification ABC'
    )
    
    last_run = fields.Datetime(
        string='Dernière exécution',
        readonly=True
    )
    
    next_run = fields.Datetime(
        string='Prochaine exécution',
        compute='_compute_next_run',
        store=True
    )
    
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Société',
        required=True,
        default=lambda self: self.env.company
    )
    
    @api.depends('frequency', 'last_run', 'day_of_week', 'day_of_month')
    def _compute_next_run(self):
        """Calcule la prochaine date d'exécution."""
        for config in self:
            if not config.last_run:
                config.next_run = fields.Datetime.now()
                continue
            
            last = config.last_run
            
            if config.frequency == 'daily':
                config.next_run = last + timedelta(days=1)
            elif config.frequency == 'weekly':
                config.next_run = last + timedelta(weeks=1)
            elif config.frequency == 'monthly':
                # Approximation : ajouter 30 jours
                config.next_run = last + timedelta(days=30)
            elif config.frequency == 'quarterly':
                # Approximation : ajouter 90 jours
                config.next_run = last + timedelta(days=90)
            else:
                config.next_run = False
    
    def action_generate_cycle_count(self):
        """Génère un inventaire de comptage cyclique."""
        self.ensure_one()
        
        # Sélectionner les produits à compter
        domain = [('type', '=', 'product')]
        
        if self.category_ids:
            domain.append(('categ_id', 'in', self.category_ids.ids))
        
        # Filtrer par classification ABC si configuré
        if self.priority_abc in ['A', 'AB']:
            # Ici on pourrait ajouter un champ abc_classification sur product.product
            # Pour simplifier, on prend les produits les plus chers
            pass
        
        products = self.env['product.product'].search(domain, limit=self.products_per_count)
        
        if not products:
            raise UserError("Aucun produit trouvé avec les critères configurés.")
        
        # Créer l'inventaire
        inventory = self.env['stockex.stock.inventory'].create({
            'name': f'Comptage Cyclique - {self.name} - {fields.Date.today()}',
            'date': fields.Date.today(),
            'company_id': self.company_id.id,
            'user_id': self.env.user.id,
            'state': 'draft',
            'description': f'Comptage cyclique automatique\nConfiguration: {self.name}\nFréquence: {dict(self._fields["frequency"].selection).get(self.frequency)}'
        })
        
        # Créer les lignes pour chaque emplacement et produit
        lines_vals = []
        for location in self.location_ids:
            for product in products:
                # Vérifier s'il y a du stock
                quants = self.env['stock.quant'].search([
                    ('product_id', '=', product.id),
                    ('location_id', '=', location.id),
                ])
                
                theoretical_qty = sum(quants.mapped('quantity')) - sum(quants.mapped('reserved_quantity'))
                
                # Créer une ligne même si quantité = 0 pour vérification
                lines_vals.append({
                    'inventory_id': inventory.id,
                    'product_id': product.id,
                    'location_id': location.id,
                    'product_qty': 0.0,
                    'standard_price': product.standard_price,
                })
        
        if lines_vals:
            self.env['stockex.stock.inventory.line'].create(lines_vals)
        
        # Mettre à jour la dernière exécution
        self.write({'last_run': fields.Datetime.now()})
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Comptage Cyclique Généré',
            'res_model': 'stockex.stock.inventory',
            'res_id': inventory.id,
            'view_mode': 'form',
            'target': 'current',
        }


class CycleCountScheduler(models.Model):
    """Planificateur automatique pour comptage cyclique."""
    _name = 'stockex.cycle.count.scheduler'
    _description = 'Planificateur Comptage Cyclique'
    
    def run_scheduled_cycle_counts(self):
        """Exécute les comptages cycliques planifiés (appelé par cron)."""
        configs = self.env['stockex.cycle.count.config'].search([
            ('active', '=', True),
            ('next_run', '<=', fields.Datetime.now())
        ])
        
        for config in configs:
            try:
                config.action_generate_cycle_count()
                _logger.info(f"Comptage cyclique généré avec succès : {config.name}")
            except Exception as e:
                _logger.error(f"Erreur génération comptage cyclique {config.name}: {e}")
