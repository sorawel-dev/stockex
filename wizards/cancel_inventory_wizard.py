# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class CancelInventoryWizard(models.TransientModel):
    _name = 'stockex.cancel.inventory.wizard'
    _description = 'Wizard de Confirmation d\'Annulation d\'Inventaire'

    inventory_id = fields.Many2one(
        'stockex.stock.inventory',
        string='Inventaire',
        required=True,
        readonly=True
    )
    
    inventory_name = fields.Char(
        related='inventory_id.name',
        string='Référence',
        readonly=True
    )
    
    inventory_date = fields.Date(
        related='inventory_id.date',
        string='Date',
        readonly=True
    )
    
    stock_moves_count = fields.Integer(
        string='Mouvements de Stock',
        compute='_compute_impacts',
        store=False
    )
    
    account_moves_count = fields.Integer(
        string='Écritures Comptables',
        compute='_compute_impacts',
        store=False
    )
    
    warning_message = fields.Html(
        string='Avertissement',
        compute='_compute_warning_message',
        store=False
    )
    
    @api.depends('inventory_id')
    def _compute_impacts(self):
        """Calcule le nombre de mouvements et écritures qui seront supprimés."""
        for wizard in self:
            if not wizard.inventory_id:
                wizard.stock_moves_count = 0
                wizard.account_moves_count = 0
                continue
            
            # Compter les mouvements de stock par origin
            stock_moves = self.env['stock.move'].search_count([
                ('origin', '=', wizard.inventory_id.name),
            ])
            
            # Si aucun résultat, chercher par reference
            if not stock_moves:
                stock_moves = self.env['stock.move'].search_count([
                    ('reference', 'ilike', wizard.inventory_id.name),
                ])
            
            wizard.stock_moves_count = stock_moves
            
            # Compter les écritures comptables via move_ids ou par référence
            if hasattr(wizard.inventory_id, 'move_ids'):
                account_moves = len(wizard.inventory_id.move_ids)
            else:
                account_moves = self.env['account.move'].search_count([
                    ('ref', 'ilike', wizard.inventory_id.name),
                    ('move_type', '=', 'entry'),
                ])
            
            wizard.account_moves_count = account_moves
    
    @api.depends('stock_moves_count', 'account_moves_count')
    def _compute_warning_message(self):
        """Génère le message d'avertissement."""
        for wizard in self:
            message = f"""
            <div style="padding: 20px; background: #fff3cd; border-left: 5px solid #ffc107; border-radius: 5px;">
                <h3 style="color: #856404; margin-top: 0;">
                    ⚠️ ATTENTION : Annulation d'Inventaire
                </h3>
                <p style="font-size: 14px; color: #856404;">
                    Vous êtes sur le point d'annuler l'inventaire <strong>{wizard.inventory_name}</strong>.
                </p>
                <p style="font-size: 14px; color: #856404;">
                    Cette action va <strong>SUPPRIMER DÉFINITIVEMENT</strong> :
                </p>
                <ul style="font-size: 14px; color: #856404;">
                    <li>📦 <strong>{wizard.stock_moves_count}</strong> mouvement(s) de stock</li>
                    <li>📒 <strong>{wizard.account_moves_count}</strong> écriture(s) comptable(s)</li>
                </ul>
                <hr style="border-color: #ffc107;"/>
                <p style="font-size: 13px; color: #721c24; font-weight: bold;">
                    ⚠️ Cette action est IRRÉVERSIBLE et impactera :
                </p>
                <ul style="font-size: 13px; color: #721c24;">
                    <li>Les quantités en stock (retour à l'état avant inventaire)</li>
                    <li>Les écritures comptables (suppression complète)</li>
                    <li>Les rapports et statistiques</li>
                </ul>
            </div>
            """
            wizard.warning_message = message
    
    def action_confirm_cancel(self):
        """Confirme l'annulation et appelle la méthode d'annulation de l'inventaire."""
        self.ensure_one()
        
        if not self.inventory_id:
            raise UserError("Aucun inventaire sélectionné.")
        
        # Appeler la méthode d'annulation de l'inventaire
        self.inventory_id.action_cancel()
        
        # Retourner à la vue de l'inventaire
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stockex.stock.inventory',
            'res_id': self.inventory_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_abort(self):
        """Annule l'opération et ferme le wizard."""
        return {'type': 'ir.actions.act_window_close'}
