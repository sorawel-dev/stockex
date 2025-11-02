# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class FixProductTypesWizard(models.TransientModel):
    _name = 'stockex.fix.product.types.wizard'
    _description = 'Corriger les Types de Produits'

    state = fields.Selection([
        ('draft', 'Configuration'),
        ('done', 'Terminé'),
    ], default='draft', string='État')
    
    message = fields.Html(string='Résultat', readonly=True)
    
    product_count = fields.Integer(
        string='Produits à Corriger',
        compute='_compute_product_count',
        store=False
    )
    
    @api.depends('state')
    def _compute_product_count(self):
        """Compte les produits qui ne sont pas correctement configurés.
        
        Un produit est correctement configuré si :
        - Type = 'consu' (Biens/Goods) ET
        - is_storable = True (Case "Suivre l'inventaire" cochée)
        
        Les 3 types de produits Odoo :
        - Biens/Goods (consu) : Produits physiques avec suivi d'inventaire par quantité
        - Services (service) : Prestations sans stock
        - Combo (combo) : Type combiné
        """
        for record in self:
            # Compter les produits qui ne sont PAS (type=consu ET is_storable=True)
            count = self.env['product.product'].search_count([
                '|',
                ('type', '!=', 'consu'),  # Type incorrect
                ('is_storable', '=', False),  # OU suivi d'inventaire non activé
            ])
            record.product_count = count
    
    def action_fix_products(self):
        """Convertit tous les produits en type 'consu' (Biens/Goods) et active le suivi d'inventaire par quantité.
        
        Action du wizard :
        1. Définir le type de produit à "Biens/Goods" (consu)
        2. Activer le suivi d'inventaire "Par Quantité"
        """
        self.ensure_one()
        
        # Rechercher tous les produits qui ne sont pas correctement configurés
        # (type != consu OU is_storable = False)
        products = self.env['product.product'].search([
            '|',
            ('type', '!=', 'consu'),  # Type incorrect
            ('is_storable', '=', False),  # OU suivi d'inventaire non activé
        ])
        
        if not products:
            message = """
            <div style="padding: 15px; background: #d4edda; border-left: 4px solid #28a745;">
                <h4 style="color: #155724;">✅ Aucune Correction Nécessaire</h4>
                <p>Tous les produits sont correctement configurés :</p>
                <ul style="margin: 10px 0;">
                    <li>✅ Type = <strong>Biens/Goods</strong> (consu)</li>
                    <li>✅ Case <strong>"Suivre l'inventaire"</strong> cochée</li>
                    <li>✅ Suivi d'inventaire <strong>par quantité</strong> activé</li>
                </ul>
            </div>
            """
        else:
            fixed_count = 0
            errors = []
            
            for product in products:
                try:
                    # Obtenir l'état actuel
                    old_type = product.type
                    old_is_storable = product.is_storable
                    old_type_label = {
                        'service': 'Service',
                        'consu': 'Consommable',
                        'product': 'Produit',
                        'combo': 'Combo',
                    }.get(old_type, old_type)
                    
                    # Action 1 : Définir le type à "Biens/Goods" (consu)
                    # Action 2 : Cocher "Suivre l'inventaire" (is_storable = True)
                    # Action 3 : Activer le suivi d'inventaire "Par Quantité"
                    # Note : Le champ 'tracking' reste 'none' pour suivi par quantité (pas de lot/série)
                    product.write({
                        'type': 'consu',  # Type = Biens/Goods
                        'is_storable': True,  # ✅ Cocher "Suivre l'inventaire"
                    })
                    
                    fixed_count += 1
                    status = f"Type: {old_type_label}→Biens, Suivre inventaire: {'✅' if old_is_storable else '❌'}→✅"
                    _logger.info(f"✅ Produit {product.default_code or product.name}: {status}")
                except Exception as e:
                    error_msg = f"Produit {product.default_code or product.name}: {str(e)}"
                    errors.append(error_msg)
                    _logger.error(f"❌ {error_msg}")
            
            # Message de résultat
            message = f"""
            <div style="padding: 15px; background: #d4edda; border-left: 4px solid #28a745;">
                <h4 style="color: #155724;">✅ Correction Réussie</h4>
                <p><strong>{fixed_count}</strong> produit(s) corrigé(s) :</p>
                <ul style="margin: 10px 0;">
                    <li>✅ <strong>Type défini à "Biens/Goods" (consu)</strong></li>
                    <li>✅ <strong>Case "Suivre l'inventaire" cochée (is_storable = True)</strong></li>
                    <li>✅ <strong>Suivi d'inventaire activé "Par Quantité"</strong></li>
                </ul>
                <p style="margin-top: 10px;">Ces produits peuvent maintenant être suivis en stock avec des quantités précises.</p>
            </div>
            """
            
            if errors:
                message += f"""
                <div style="padding: 15px; background: #fff3cd; border-left: 4px solid #ffc107; margin-top: 15px;">
                    <h4 style="color: #856404;">⚠️ Erreurs Rencontrées</h4>
                    <ul>
                        {''.join([f'<li>{error}</li>' for error in errors])}
                    </ul>
                </div>
                """
            
            # Détails des types de produits Odoo
            message += """
            <div style="padding: 15px; background: #e7f3ff; border-left: 4px solid #2196F3; margin-top: 15px;">
                <h4 style="color: #0d47a1;">📊 Les 3 Types de Produits Odoo</h4>
                <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                    <tr style="background: #f5f5f5;">
                        <th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Type Produit</th>
                        <th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Code Odoo</th>
                        <th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Suivi Inventaire</th>
                        <th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Usage</th>
                    </tr>
                    <tr style="background: #e8f5e9;">
                        <td style="padding: 8px; border: 1px solid #ddd;"><strong>🏭 Biens/Goods</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd;"><code>consu</code></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">✅ <strong>OUI</strong> (Par quantité)</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">Produits physiques stockables</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;">💼 Services</td>
                        <td style="padding: 8px; border: 1px solid #ddd;"><code>service</code></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">❌ NON</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">Prestations, consultations</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;">📦 Consommables</td>
                        <td style="padding: 8px; border: 1px solid #ddd;"><code>consu</code></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">❌ NON</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">Fournitures sans suivi</td>
                    </tr>
                </table>
                <div style="margin-top: 15px; padding: 10px; background: #fff9c4; border-radius: 4px;">
                    <p style="margin: 0;"><strong>💡 Ce wizard fait 3 choses :</strong></p>
                    <ol style="margin: 5px 0 0 20px;">
                        <li>Définit le type de produit à <strong>"Biens/Goods"</strong> (consu)</li>
                        <li>Coche la case <strong>"Suivre l'inventaire"</strong> (is_storable)</li>
                        <li>Active le suivi d'inventaire <strong>"Par Quantité"</strong></li>
                    </ol>
                </div>
            </div>
            """
        
        self.write({
            'state': 'done',
            'message': message,
        })
        
        # Retourner l'action pour garder le wizard ouvert
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stockex.fix.product.types.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }
    
    def action_close(self):
        """Ferme le wizard."""
        return {'type': 'ir.actions.act_window_close'}
