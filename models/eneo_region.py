# -*- coding: utf-8 -*-
"""
Régions Électriques ENEO (Cameroun)
====================================
Gestion des 9 régions électriques de ENEO (Société Nationale d'Électricité du Cameroun)
et leur liaison avec les régions administratives du Cameroun.
"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class EneoRegion(models.Model):
    """Régions électriques ENEO (Société Nationale d'Électricité du Cameroun)."""
    _name = 'stockex.eneo.region'
    _description = 'Région Électrique ENEO'
    _order = 'code'
    
    name = fields.Char(
        string='Nom de la Région Électrique',
        required=True,
        help='Nom complet de la région électrique ENEO (ex: Région Électrique de Douala)'
    )
    
    code = fields.Char(
        string='Code',
        size=3,
        required=True,
        help='Code à 3 caractères de la région électrique (ex: DRD, DRY)',
        index=True
    )
    
    administrative_region = fields.Selection(
        selection=[
            ('adamaoua', 'Adamaoua'),
            ('centre', 'Centre'),
            ('est', 'Est'),
            ('extreme_nord', 'Extrême-Nord'),
            ('littoral', 'Littoral'),
            ('nord', 'Nord'),
            ('nord_ouest', 'Nord-Ouest'),
            ('ouest', 'Ouest'),
            ('sud', 'Sud'),
            ('sud_ouest', 'Sud-Ouest'),
        ],
        string='Région Administrative',
        required=True,
        help='Région administrative du Cameroun à laquelle appartient cette région électrique'
    )
    
    network = fields.Selection(
        selection=[
            ('south', 'Sud'),
            ('north', 'Nord'),
        ],
        string='Réseau Interconnecté',
        required=True,
        index=True,
        help="Réseau interconnecté auquel appartient cette région (Sud ou Nord)"
    )
    
    warehouse_ids = fields.One2many(
        'stock.warehouse',
        'eneo_region_id',
        string='Entrepôts',
        help='Entrepôts rattachés à cette région électrique'
    )
    
    warehouse_count = fields.Integer(
        string='Nombre d\'Entrepôts',
        compute='_compute_warehouse_count',
        store=True
    )
    
    color = fields.Integer(
        string='Couleur',
        default=0,
        help='Couleur pour l\'affichage dans les vues kanban'
    )
    
    active = fields.Boolean(
        string='Actif',
        default=True,
        help='Décocher pour archiver cette région électrique'
    )
    
    notes = fields.Text(
        string='Notes',
        help='Notes sur cette région électrique'
    )
    
    @api.constrains('code')
    def _check_code_unique(self):
        for region in self:
            if region.code and self.search([('code', '=', region.code), ('id', '!=', region.id)], limit=1):
                raise ValidationError("Le code de la région électrique doit être unique.")

    @api.constrains('name')
    def _check_name_unique(self):
        for region in self:
            if region.name and self.search([('name', '=', region.name), ('id', '!=', region.id)], limit=1):
                raise ValidationError("Le nom de la région électrique doit être unique.")
    
    @api.depends('warehouse_ids')
    def _compute_warehouse_count(self):
        """Calcule le nombre d'entrepôts rattachés."""
        for region in self:
            region.warehouse_count = len(region.warehouse_ids)
    
    @api.constrains('code')
    def _check_code_format(self):
        """Vérifie que le code respecte le format à 3 caractères."""
        for region in self:
            if region.code:
                if len(region.code) != 3:
                    raise ValidationError(
                        "Le code de la région électrique doit contenir exactement 3 caractères."
                    )
                if not region.code.isupper():
                    raise ValidationError(
                        "Le code de la région électrique doit être en MAJUSCULES."
                    )
    
    def action_view_warehouses(self):
        """Affiche les entrepôts de cette région électrique."""
        self.ensure_one()
        return {
            'name': f'Entrepôts - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.warehouse',
            'view_mode': 'list,form,kanban',
            'domain': [('eneo_region_id', '=', self.id)],
            'context': {'default_eneo_region_id': self.id},
        }
    
    @api.model
    def create_default_eneo_regions(self):
        """
        Crée les 9 régions électriques ENEO par défaut.
        Méthode utilitaire pour initialiser les données.
        """
        default_regions = [
            {
                'name': 'Région Électrique de Douala',
                'code': 'DRD',
                'administrative_region': 'littoral',
            },
            {
                'name': 'Région Électrique de Yaoundé',
                'code': 'DRY',
                'administrative_region': 'centre',
            },
            {
                'name': 'Région Électrique de l\'Ouest',
                'code': 'DRO',
                'administrative_region': 'ouest',
            },
            {
                'name': 'Région Électrique du Nord',
                'code': 'DRN',
                'administrative_region': 'nord',
            },
            {
                'name': 'Région Électrique de l\'Est',
                'code': 'DRE',
                'administrative_region': 'est',
            },
            {
                'name': 'Région Électrique du Sud',
                'code': 'DRS',
                'administrative_region': 'sud',
            },
            {
                'name': 'Région Électrique du Littoral',
                'code': 'DRL',
                'administrative_region': 'littoral',
            },
            {
                'name': 'Région Électrique de l\'Extrême-Nord',
                'code': 'DREN',
                'administrative_region': 'extreme_nord',
            },
            {
                'name': 'Région Électrique du Nord-Ouest',
                'code': 'DRNO',
                'administrative_region': 'nord_ouest',
            },
        ]
        
        created_regions = []
        for region_data in default_regions:
            # Vérifie si la région existe déjà
            existing = self.search([('code', '=', region_data['code'])], limit=1)
            if not existing:
                region = self.create(region_data)
                created_regions.append(region)
                _logger.info(f"Région électrique créée: {region.name} ({region.code})")
        
        return created_regions
