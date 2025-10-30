# -*- coding: utf-8 -*-
"""
Gestion des Lots et Traçabilité
================================
Extension du module Stockex pour la gestion complète des lots/séries
avec traçabilité réglementaire (pharma, alimentaire, cosmétique).

Features:
- Inventaire par lot/série
- Gestion dates d'expiration
- Alertes FEFO (First Expired First Out)
- Traçabilité complète
- Rappels produits
- Conformité réglementaire
"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date, timedelta
import logging

_logger = logging.getLogger(__name__)


class StockInventoryLine(models.Model):
    """Extension des lignes d'inventaire pour support lots."""
    _inherit = 'stockex.stock.inventory.line'
    
    # Tracking du produit
    tracking = fields.Selection(
        related='product_id.tracking',
        string='Type de Suivi',
        store=True,
        help='none = Pas de suivi, lot = Par lot, serial = Par numéro de série'
    )
    
    # Support lots/séries
    lot_ids = fields.Many2many(
        'stock.lot',
        string='Lots/Séries',
        help='Lots ou numéros de série associés à cette ligne'
    )
    
    # Lignes détaillées par lot
    lot_line_ids = fields.One2many(
        'stockex.inventory.lot.line',
        'inventory_line_id',
        string='Détail par Lot',
        help='Détail des quantités par lot/série'
    )
    
    # Indicateur si inventaire par lot
    has_lot_tracking = fields.Boolean(
        compute='_compute_has_lot_tracking',
        string='Suivi par Lot',
        store=True
    )
    
    # Agrégation quantités depuis lignes lot
    real_qty_from_lots = fields.Float(
        compute='_compute_real_qty_from_lots',
        string='Qté Réelle (depuis lots)',
        help='Somme des quantités réelles des lignes de lot'
    )
    
    @api.depends('product_id.tracking')
    def _compute_has_lot_tracking(self):
        """Détermine si le produit nécessite un suivi par lot."""
        for line in self:
            line.has_lot_tracking = line.tracking in ('lot', 'serial')
    
    @api.depends('lot_line_ids.real_qty')
    def _compute_real_qty_from_lots(self):
        """Calcule la quantité réelle totale depuis les lignes de lot."""
        for line in self:
            if line.lot_line_ids:
                line.real_qty_from_lots = sum(line.lot_line_ids.mapped('real_qty'))
            else:
                line.real_qty_from_lots = 0.0
    
    @api.onchange('lot_line_ids')
    def _onchange_lot_lines(self):
        """Met à jour real_qty quand les lignes de lot changent."""
        if self.lot_line_ids and self.has_lot_tracking:
            self.real_qty = sum(self.lot_line_ids.mapped('real_qty'))
    
    def action_open_lot_details(self):
        """Ouvre la vue détaillée des lots pour cette ligne."""
        self.ensure_one()
        
        return {
            'name': _('Détail par Lot - %s') % self.product_id.name,
            'type': 'ir.actions.act_window',
            'res_model': 'stockex.inventory.lot.line',
            'view_mode': 'list,form',
            'domain': [('inventory_line_id', '=', self.id)],
            'context': {
                'default_inventory_line_id': self.id,
                'default_product_id': self.product_id.id,
            },
            'target': 'current',
        }
    
    def action_generate_lot_lines(self):
        """Génère automatiquement les lignes de lot depuis les quants existants."""
        self.ensure_one()
        
        if not self.has_lot_tracking:
            raise ValidationError(_("Ce produit n'a pas de suivi par lot/série."))
        
        # Supprime les lignes existantes
        self.lot_line_ids.unlink()
        
        # Récupère les quants par lot pour ce produit/emplacement
        quants = self.env['stock.quant'].search([
            ('product_id', '=', self.product_id.id),
            ('location_id', '=', self.inventory_id.location_id.id),
            ('lot_id', '!=', False),
            ('quantity', '>', 0),
        ])
        
        # Crée une ligne par lot
        lot_lines_vals = []
        for quant in quants:
            lot_lines_vals.append({
                'inventory_line_id': self.id,
                'lot_id': quant.lot_id.id,
                'theoretical_qty': quant.quantity - quant.reserved_quantity,
                'real_qty': 0.0,  # À saisir par l'utilisateur
            })
        
        if lot_lines_vals:
            self.env['stockex.inventory.lot.line'].create(lot_lines_vals)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Succès'),
                    'message': _('%d ligne(s) de lot générée(s)') % len(lot_lines_vals),
                    'type': 'success',
                    'sticky': False,
                }
            }


class InventoryLotLine(models.Model):
    """Ligne d'inventaire détaillée par lot/série."""
    _name = 'stockex.inventory.lot.line'
    _description = 'Inventaire par Lot/Série'
    _order = 'expiration_date, lot_name'
    
    # Relations
    inventory_line_id = fields.Many2one(
        'stockex.stock.inventory.line',
        string='Ligne Inventaire',
        required=True,
        ondelete='cascade',
        index=True
    )
    
    inventory_id = fields.Many2one(
        'stockex.stock.inventory',
        string='Inventaire',
        related='inventory_line_id.inventory_id',
        store=True,
        index=True
    )
    
    product_id = fields.Many2one(
        'product.product',
        string='Produit',
        related='inventory_line_id.product_id',
        store=True,
        index=True
    )
    
    lot_id = fields.Many2one(
        'stock.lot',
        string='Lot/Série',
        required=True,
        domain="[('product_id', '=', product_id)]",
        index=True
    )
    
    lot_name = fields.Char(
        related='lot_id.name',
        string='Numéro Lot',
        store=True
    )
    
    # Dates
    expiration_date = fields.Date(
        string='Date Expiration',
        help='Date d\'expiration du lot (depuis product.expiry ou saisie manuelle)'
    )
    
    removal_date = fields.Date(
        string='Date Retrait',
        help='Date de retrait du lot'
    )
    
    use_date = fields.Date(
        string="Date d'Utilisation Optimale",
        help="Date d'utilisation optimale du lot"
    )
    
    @api.onchange('lot_id')
    def _onchange_lot_id(self):
        """Remplit automatiquement les dates depuis le lot sélectionné."""
        if self.lot_id:
            # Essaie d'obtenir les dates si module product_expiry installé
            if hasattr(self.lot_id, 'expiration_date') and self.lot_id.expiration_date:
                self.expiration_date = self.lot_id.expiration_date
            
            if hasattr(self.lot_id, 'use_date') and self.lot_id.use_date:
                self.use_date = self.lot_id.use_date
            
            if hasattr(self.lot_id, 'removal_date') and self.lot_id.removal_date:
                self.removal_date = self.lot_id.removal_date
    
    # Quantités
    theoretical_qty = fields.Float(
        string='Qté Théorique',
        digits='Product Unit of Measure',
        help='Quantité théorique en stock pour ce lot'
    )
    
    real_qty = fields.Float(
        string='Qté Réelle',
        digits='Product Unit of Measure',
        help='Quantité réelle comptée pour ce lot'
    )
    
    difference = fields.Float(
        compute='_compute_difference',
        string='Écart',
        digits='Product Unit of Measure',
        store=True
    )
    
    difference_percent = fields.Float(
        compute='_compute_difference',
        string='Écart %',
        store=True
    )
    
    # Valorisation
    standard_price = fields.Float(
        related='product_id.standard_price',
        string='Coût Unitaire',
        store=True
    )
    
    difference_value = fields.Float(
        compute='_compute_difference_value',
        string='Valeur Écart',
        store=True
    )
    
    # État du lot
    lot_state = fields.Selection([
        ('good', 'Bon'),
        ('warning', 'Alerte Expiration'),
        ('expired', 'Expiré'),
        ('quarantine', 'Quarantaine'),
    ], string='État Lot', compute='_compute_lot_state', store=True)
    
    # Jours avant expiration
    days_to_expiry = fields.Integer(
        compute='_compute_days_to_expiry',
        string='Jours avant Expiration',
        store=True
    )
    
    # Notes
    note = fields.Text(string='Remarques')
    
    @api.depends('theoretical_qty', 'real_qty')
    def _compute_difference(self):
        """Calcule l'écart entre théorique et réel."""
        for line in self:
            line.difference = line.real_qty - line.theoretical_qty
            
            if line.theoretical_qty != 0:
                line.difference_percent = (line.difference / line.theoretical_qty) * 100
            else:
                line.difference_percent = 0.0 if line.difference == 0 else 100.0
    
    @api.depends('difference', 'standard_price')
    def _compute_difference_value(self):
        """Calcule la valeur de l'écart."""
        for line in self:
            line.difference_value = line.difference * line.standard_price
    
    @api.depends('expiration_date')
    def _compute_lot_state(self):
        """Détermine l'état du lot selon la date d'expiration."""
        today = date.today()
        warning_days = 60  # Alerte 60 jours avant expiration
        
        for line in self:
            if not line.expiration_date:
                line.lot_state = 'good'
            elif line.expiration_date < today:
                line.lot_state = 'expired'
            elif line.expiration_date <= (today + timedelta(days=warning_days)):
                line.lot_state = 'warning'
            else:
                line.lot_state = 'good'
    
    @api.depends('expiration_date')
    def _compute_days_to_expiry(self):
        """Calcule le nombre de jours avant expiration."""
        today = date.today()
        
        for line in self:
            if line.expiration_date:
                delta = line.expiration_date - today
                line.days_to_expiry = delta.days
            else:
                line.days_to_expiry = 0
    
    @api.constrains('real_qty')
    def _check_real_qty(self):
        """Valide que la quantité réelle est >= 0."""
        for line in self:
            if line.real_qty < 0:
                raise ValidationError(_("La quantité réelle ne peut pas être négative."))
    
    @api.constrains('lot_id', 'inventory_line_id')
    def _check_unique_lot(self):
        """Valide qu'un lot n'est pas en double pour la même ligne."""
        for line in self:
            duplicate = self.search([
                ('id', '!=', line.id),
                ('inventory_line_id', '=', line.inventory_line_id.id),
                ('lot_id', '=', line.lot_id.id),
            ], limit=1)
            
            if duplicate:
                raise ValidationError(_(
                    "Le lot '%s' est déjà présent dans cette ligne d'inventaire."
                ) % line.lot_name)


class StockLot(models.Model):
    """Extension du modèle stock.lot pour conformité réglementaire."""
    _inherit = 'stock.lot'
    
    # Informations réglementaires
    supplier_lot_number = fields.Char(
        string='N° Lot Fournisseur',
        help='Numéro de lot du fournisseur (traçabilité amont)'
    )
    
    internal_lot_number = fields.Char(
        string='N° Lot Interne',
        help='Numéro de lot interne (si différent)'
    )
    
    # Documents qualité
    certificate_of_analysis = fields.Binary(
        string='Certificat Analyse',
        attachment=True
    )
    
    certificate_filename = fields.Char(string='Nom Fichier Certificat')
    
    quality_status = fields.Selection([
        ('pending', 'En Attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
        ('quarantine', 'Quarantaine'),
    ], string='Statut Qualité', default='pending', tracking=True)
    
    # Traçabilité
    manufacturing_date = fields.Date(
        string='Date Fabrication',
        help='Date de fabrication du lot'
    )
    
    reception_date = fields.Date(
        string='Date Réception',
        help='Date de réception du lot'
    )
    
    # Alertes
    alert_expiry_days = fields.Integer(
        string='Alerte Expiration (jours)',
        default=60,
        help='Nombre de jours avant expiration pour déclencher alerte'
    )
    
    is_expiring_soon = fields.Boolean(
        compute='_compute_is_expiring_soon',
        string='Expire Bientôt',
        search='_search_expiring_soon'
    )
    
    is_expired = fields.Boolean(
        compute='_compute_is_expired',
        string='Expiré',
        search='_search_expired'
    )
    
    # Notes conformité
    compliance_notes = fields.Text(
        string='Notes Conformité',
        help='Notes pour audit et conformité réglementaire'
    )
    
    @api.depends('alert_expiry_days')
    def _compute_is_expiring_soon(self):
        """Détermine si le lot expire bientôt."""
        today = date.today()
        
        for lot in self:
            expiration = None
            # Cherche expiration_date (product_expiry) ou use_date (stock standard)
            if hasattr(lot, 'expiration_date') and lot.expiration_date:
                expiration = lot.expiration_date
            elif hasattr(lot, 'use_date') and lot.use_date:
                expiration = lot.use_date
            
            if expiration:
                alert_date = today + timedelta(days=lot.alert_expiry_days)
                lot.is_expiring_soon = (
                    expiration <= alert_date and
                    expiration >= today
                )
            else:
                lot.is_expiring_soon = False
    
    def _compute_is_expired(self):
        """Détermine si le lot est expiré."""
        today = date.today()
        
        for lot in self:
            expiration = None
            # Cherche expiration_date (product_expiry) ou use_date (stock standard)
            if hasattr(lot, 'expiration_date') and lot.expiration_date:
                expiration = lot.expiration_date
            elif hasattr(lot, 'use_date') and lot.use_date:
                expiration = lot.use_date
            
            if expiration:
                lot.is_expired = expiration < today
            else:
                lot.is_expired = False
    
    def _search_expiring_soon(self, operator, value):
        """Recherche des lots expirant bientôt."""
        # Note: Cette recherche fonctionne si module product_expiry installé
        # Sinon retourne domaine vide
        if not hasattr(self.env['stock.lot'], 'expiration_date'):
            return [('id', '=', 0)]  # Aucun résultat
        
        today = date.today()
        alert_days = 60  # Par défaut
        alert_date = today + timedelta(days=alert_days)
        
        if (operator == '=' and value) or (operator == '!=' and not value):
            return [
                ('expiration_date', '!=', False),
                ('expiration_date', '<=', alert_date),
                ('expiration_date', '>=', today),
            ]
        else:
            return [
                '|',
                ('expiration_date', '=', False),
                '|',
                ('expiration_date', '>', alert_date),
                ('expiration_date', '<', today),
            ]
    
    def _search_expired(self, operator, value):
        """Recherche des lots expirés."""
        # Note: Cette recherche fonctionne si module product_expiry installé
        # Sinon retourne domaine vide
        if not hasattr(self.env['stock.lot'], 'expiration_date'):
            return [('id', '=', 0)]  # Aucun résultat
        
        today = date.today()
        
        if (operator == '=' and value) or (operator == '!=' and not value):
            return [
                ('expiration_date', '!=', False),
                ('expiration_date', '<', today),
            ]
        else:
            return [
                '|',
                ('expiration_date', '=', False),
                ('expiration_date', '>=', today),
            ]
    
    def action_view_inventory_history(self):
        """Affiche l'historique des inventaires pour ce lot."""
        self.ensure_one()
        
        return {
            'name': _('Historique Inventaires - Lot %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'stockex.inventory.lot.line',
            'view_mode': 'list,form',
            'domain': [('lot_id', '=', self.id)],
            'context': {'create': False},
        }
