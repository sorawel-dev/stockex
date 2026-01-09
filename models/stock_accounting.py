# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api
from odoo.exceptions import UserError
from markupsafe import Markup

_logger = logging.getLogger(__name__)


class StockInventoryAccounting(models.Model):
    """Extension comptable pour les inventaires."""
    _inherit = 'stockex.stock.inventory'
    
    accounting_enabled = fields.Boolean(
        string='Générer Écritures Comptables',
        default=False,
        help='Si coché, génère les écritures comptables lors de la validation'
    )
    
    move_ids = fields.One2many(
        comodel_name='account.move',
        inverse_name='stockex_inventory_id',
        string='Écritures Comptables',
        readonly=True
    )
    
    def _generate_accounting_entries(self):
        """Génère les écritures comptables pour les écarts d'inventaire."""
        self.ensure_one()
        
        if not self.accounting_enabled:
            return
        
        # Vérifier que le module stock_account est installé
        if not self.env['ir.module.module'].search([
            ('name', '=', 'stock_account'),
            ('state', '=', 'installed')
        ]):
            raise UserError(
                "Le module 'stock_account' doit être installé pour générer "
                "les écritures comptables."
            )
        
        AccountMove = self.env['account.move']
        
        # Grouper les lignes par catégorie de produit
        lines_by_category = {}
        for line in self.line_ids:
            if line.difference == 0:
                continue  # Pas d'écart, pas d'écriture
            
            category = line.product_id.categ_id
            if category not in lines_by_category:
                lines_by_category[category] = []
            lines_by_category[category].append(line)
        
        # Créer une écriture comptable par catégorie
        for category, lines in lines_by_category.items():
            # Vérifier que les comptes sont configurés
            valuation_account = category.property_stock_valuation_account_id
            variation_account = category.property_stock_account_output_categ_id
            
            if not valuation_account or not variation_account:
                raise UserError(
                    f"Les comptes comptables ne sont pas configurés pour la "
                    f"catégorie '{category.name}'.\n"
                    f"Aller dans : Inventaire → Configuration → Catégories de Produits"
                )
            
            # Préparer les lignes d'écriture
            move_lines = []
            total_debit = 0
            total_credit = 0
            
            for line in lines:
                # Utiliser le prix capturé dans la ligne d'inventaire
                # ou la méthode de valorisation du produit
                if line.standard_price and line.standard_price > 0:
                    unit_price = line.standard_price
                else:
                    # Utiliser la méthode de valorisation via l'inventaire
                    unit_price = line.inventory_id._get_product_valuation_price(line.product_id)
                
                value_diff = line.difference * unit_price
                
                if value_diff > 0:
                    # Surplus : augmentation du stock
                    # Débit : Compte de stock
                    # Crédit : Compte de variation
                    move_lines.append((0, 0, {
                        'name': f'Inventaire {self.name} - {line.product_id.name}',
                        'account_id': valuation_account.id,
                        'debit': abs(value_diff),
                        'credit': 0.0,
                        'product_id': line.product_id.id,
                        'quantity': line.difference,
                        'product_uom_id': line.product_id.uom_id.id,
                    }))
                    move_lines.append((0, 0, {
                        'name': f'Inventaire {self.name} - {line.product_id.name}',
                        'account_id': variation_account.id,
                        'debit': 0.0,
                        'credit': abs(value_diff),
                        'product_id': line.product_id.id,
                        'quantity': line.difference,
                        'product_uom_id': line.product_id.uom_id.id,
                    }))
                    total_debit += abs(value_diff)
                    total_credit += abs(value_diff)
                    
                elif value_diff < 0:
                    # Manquant : diminution du stock
                    # Débit : Compte de variation
                    # Crédit : Compte de stock
                    move_lines.append((0, 0, {
                        'name': f'Inventaire {self.name} - {line.product_id.name}',
                        'account_id': variation_account.id,
                        'debit': abs(value_diff),
                        'credit': 0.0,
                        'product_id': line.product_id.id,
                        'quantity': line.difference,
                        'product_uom_id': line.product_id.uom_id.id,
                    }))
                    move_lines.append((0, 0, {
                        'name': f'Inventaire {self.name} - {line.product_id.name}',
                        'account_id': valuation_account.id,
                        'debit': 0.0,
                        'credit': abs(value_diff),
                        'product_id': line.product_id.id,
                        'quantity': line.difference,
                        'product_uom_id': line.product_id.uom_id.id,
                    }))
                    total_debit += abs(value_diff)
                    total_credit += abs(value_diff)
            
            # Créer l'écriture comptable
            if move_lines:
                move = AccountMove.create({
                    'journal_id': self._get_inventory_journal().id,
                    'date': self.date,
                    'ref': f'Inventaire {self.name} - {category.name}',
                    'stockex_inventory_id': self.id,
                    'line_ids': move_lines,
                })
                
                # Comptabiliser l'écriture
                move.action_post()
                
                _logger.info(
                    f"Écriture comptable créée : {move.name} "
                    f"(Débit: {total_debit}, Crédit: {total_credit})"
                )
        
        # Message dans le chatter
        self.message_post(
            body=Markup(f"✅ {len(self.account_move_ids)} écriture(s) comptable(s) générée(s)")
        )
    
    def _get_inventory_journal(self):
        """Retourne le journal comptable pour les inventaires."""
        journal = self.env['account.journal'].search([
            ('type', '=', 'general'),
            ('company_id', '=', self.company_id.id),
        ], limit=1)
        
        if not journal:
            raise UserError(
                "Aucun journal de type 'Général' trouvé. "
                "Créez-en un dans Comptabilité → Configuration → Journaux"
            )
        
        return journal
    
    def action_validate(self):
        """Override pour générer les écritures comptables."""
        # Appeler la méthode parente
        res = super(StockInventoryAccounting, self).action_validate()
        
        # Générer les écritures comptables si activé
        if self.accounting_enabled:
            self._generate_accounting_entries()
        
        return res


class AccountMove(models.Model):
    """Ajout du lien vers l'inventaire."""
    _inherit = 'account.move'
    
    stockex_inventory_id = fields.Many2one(
        comodel_name='stockex.stock.inventory',
        string='Inventaire d\'Origine',
        readonly=True,
        index=True
    )
