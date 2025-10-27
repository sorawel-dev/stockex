# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, tools
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class InventoryComparison(models.TransientModel):
    """Assistant de comparaison d'inventaires."""
    _name = 'stockex.inventory.comparison'
    _description = 'Comparaison d\'Inventaires'
    
    inventory_1_id = fields.Many2one(
        comodel_name='stockex.stock.inventory',
        string='Premier Inventaire',
        required=True,
        domain="[('state', '=', 'done')]"
    )
    
    inventory_2_id = fields.Many2one(
        comodel_name='stockex.stock.inventory',
        string='Deuxième Inventaire',
        required=True,
        domain="[('state', '=', 'done'), ('id', '!=', inventory_1_id)]"
    )
    
    comparison_type = fields.Selection(
        selection=[
            ('quantity', 'Écarts de Quantité'),
            ('value', 'Écarts de Valeur'),
            ('both', 'Quantité et Valeur'),
        ],
        string='Type de Comparaison',
        default='both',
        required=True
    )
    
    show_only_differences = fields.Boolean(
        string='Afficher uniquement les différences',
        default=True,
        help='Masquer les produits sans changement'
    )
    
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Société',
        default=lambda self: self.env.company
    )
    
    def action_compare(self):
        """Effectue la comparaison et affiche les résultats."""
        self.ensure_one()
        
        if self.inventory_1_id.date > self.inventory_2_id.date:
            raise UserError("Le premier inventaire doit être antérieur au deuxième.")
        
        # Récupérer les lignes des deux inventaires
        lines_1 = {
            (line.product_id.id, line.location_id.id): line 
            for line in self.inventory_1_id.line_ids
        }
        
        lines_2 = {
            (line.product_id.id, line.location_id.id): line 
            for line in self.inventory_2_id.line_ids
        }
        
        # Créer les lignes de comparaison
        comparison_lines = []
        all_keys = set(lines_1.keys()) | set(lines_2.keys())
        
        for key in all_keys:
            product_id, location_id = key
            line_1 = lines_1.get(key)
            line_2 = lines_2.get(key)
            
            qty_1 = line_1.product_qty if line_1 else 0.0
            qty_2 = line_2.product_qty if line_2 else 0.0
            price_1 = line_1.standard_price if line_1 else 0.0
            price_2 = line_2.standard_price if line_2 else 0.0
            
            qty_diff = qty_2 - qty_1
            value_1 = qty_1 * price_1
            value_2 = qty_2 * price_2
            value_diff = value_2 - value_1
            
            # Filtrer si uniquement les différences
            if self.show_only_differences and qty_diff == 0 and value_diff == 0:
                continue
            
            product = self.env['product.product'].browse(product_id)
            location = self.env['stock.location'].browse(location_id)
            
            comparison_lines.append({
                'product_id': product_id,
                'product_name': product.name,
                'product_code': product.default_code,
                'location_id': location_id,
                'location_name': location.complete_name,
                'quantity_1': qty_1,
                'quantity_2': qty_2,
                'quantity_diff': qty_diff,
                'price_1': price_1,
                'price_2': price_2,
                'value_1': value_1,
                'value_2': value_2,
                'value_diff': value_diff,
            })
        
        # Générer le rapport HTML
        html_report = self._generate_comparison_report(comparison_lines)
        
        # Créer un rapport temporaire ou afficher dans une vue
        return {
            'type': 'ir.actions.act_window',
            'name': f'Comparaison: {self.inventory_1_id.name} vs {self.inventory_2_id.name}',
            'res_model': 'stockex.inventory.comparison.result',
            'view_mode': 'list',
            'target': 'new',
            'context': {
                'default_comparison_data': comparison_lines,
                'default_inventory_1_name': self.inventory_1_id.name,
                'default_inventory_2_name': self.inventory_2_id.name,
            }
        }
    
    def _generate_comparison_report(self, lines):
        """Génère un rapport HTML de comparaison."""
        html = f"""
        <div class="container-fluid">
            <h2>Comparaison d'Inventaires</h2>
            <div class="row mb-3">
                <div class="col-6">
                    <strong>Inventaire 1:</strong> {self.inventory_1_id.name} ({self.inventory_1_id.date})
                </div>
                <div class="col-6">
                    <strong>Inventaire 2:</strong> {self.inventory_2_id.name} ({self.inventory_2_id.date})
                </div>
            </div>
            
            <table class="table table-striped table-sm">
                <thead class="table-dark">
                    <tr>
                        <th>Produit</th>
                        <th>Emplacement</th>
                        <th class="text-end">Qté 1</th>
                        <th class="text-end">Qté 2</th>
                        <th class="text-end">Écart Qté</th>
                        <th class="text-end">Valeur 1</th>
                        <th class="text-end">Valeur 2</th>
                        <th class="text-end">Écart Valeur</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        total_value_diff = 0
        
        for line in lines:
            qty_diff_class = 'text-success' if line['quantity_diff'] > 0 else ('text-danger' if line['quantity_diff'] < 0 else '')
            value_diff_class = 'text-success' if line['value_diff'] > 0 else ('text-danger' if line['value_diff'] < 0 else '')
            
            html += f"""
                <tr>
                    <td><small>{line['product_code']} - {line['product_name']}</small></td>
                    <td><small>{line['location_name']}</small></td>
                    <td class="text-end">{line['quantity_1']:,.2f}</td>
                    <td class="text-end">{line['quantity_2']:,.2f}</td>
                    <td class="text-end {qty_diff_class}"><strong>{line['quantity_diff']:+,.2f}</strong></td>
                    <td class="text-end">{line['value_1']:,.0f} FCFA</td>
                    <td class="text-end">{line['value_2']:,.0f} FCFA</td>
                    <td class="text-end {value_diff_class}"><strong>{line['value_diff']:+,.0f} FCFA</strong></td>
                </tr>
            """
            total_value_diff += line['value_diff']
        
        html += f"""
                </tbody>
                <tfoot class="table-secondary">
                    <tr>
                        <th colspan="7" class="text-end">Écart Total de Valeur:</th>
                        <th class="text-end {'text-success' if total_value_diff > 0 else 'text-danger'}">
                            {total_value_diff:+,.0f} FCFA
                        </th>
                    </tr>
                </tfoot>
            </table>
        </div>
        """
        
        return html


class InventoryComparisonResult(models.TransientModel):
    """Résultats de la comparaison d'inventaires."""
    _name = 'stockex.inventory.comparison.result'
    _description = 'Résultats Comparaison Inventaires'
    
    product_id = fields.Many2one('product.product', string='Produit')
    product_code = fields.Char(string='Code')
    location_id = fields.Many2one('stock.location', string='Emplacement')
    quantity_1 = fields.Float(string='Quantité 1')
    quantity_2 = fields.Float(string='Quantité 2')
    quantity_diff = fields.Float(string='Écart Qté', compute='_compute_differences')
    value_1 = fields.Float(string='Valeur 1')
    value_2 = fields.Float(string='Valeur 2')
    value_diff = fields.Float(string='Écart Valeur', compute='_compute_differences')
    
    @api.depends('quantity_1', 'quantity_2', 'value_1', 'value_2')
    def _compute_differences(self):
        for record in self:
            record.quantity_diff = record.quantity_2 - record.quantity_1
            record.value_diff = record.value_2 - record.value_1
