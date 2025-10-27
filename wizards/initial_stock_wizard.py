# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class InitialStockWizard(models.TransientModel):
    """Assistant pour créer le stock initial dans une base vide."""
    _name = 'stockex.initial.stock.wizard'
    _description = 'Assistant Stock Initial'
    
    name = fields.Char(
        string='Nom de l\'Inventaire Initial',
        default='Stock Initial',
        required=True
    )
    
    date = fields.Date(
        string='Date du Stock Initial',
        required=True,
        default=fields.Date.today,
        help='Date de référence pour le stock initial (ex: date de mise en service)'
    )
    
    location_id = fields.Many2one(
        comodel_name='stock.location',
        string='Emplacement Principal',
        required=True,
        domain="[('usage', '=', 'internal')]",
        help='Emplacement où sera enregistré le stock initial'
    )
    
    import_file = fields.Binary(
        string='Fichier d\'Import (Excel)',
        help='Fichier Excel avec colonnes: CODE PRODUIT, QUANTITE, PRIX UNITAIRE'
    )
    
    filename = fields.Char(string='Nom du Fichier')
    
    create_products = fields.Boolean(
        string='Créer les Produits Manquants',
        default=True,
        help='Si coché, crée automatiquement les produits non trouvés'
    )
    
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Société',
        default=lambda self: self.env.company,
        required=True
    )
    
    def action_create_initial_stock(self):
        """Crée l'inventaire initial et met à jour les stocks."""
        self.ensure_one()
        
        # Vérifier qu'il n'y a pas déjà de stock
        existing_quants = self.env['stock.quant'].search([
            ('quantity', '>', 0),
            ('location_id.usage', '=', 'internal'),
            ('company_id', '=', self.company_id.id),
        ])
        
        if existing_quants:
            raise UserError(
                f"⚠️ ATTENTION : {len(existing_quants)} mouvement(s) de stock déjà enregistré(s).\n\n"
                f"Cette fonction est destinée aux bases de données VIDES.\n"
                f"Pour mettre à jour un stock existant, utilisez plutôt un inventaire normal."
            )
        
        # Créer l'inventaire initial
        inventory = self.env['stockex.stock.inventory'].create({
            'name': self.name,
            'date': self.date,
            'location_id': self.location_id.id,
            'company_id': self.company_id.id,
            'state': 'draft',
            'description': 'Inventaire initial - Stock de départ pour nouvelle base de données'
        })
        
        # Si fichier Excel fourni, l'importer
        if self.import_file:
            lines = self._parse_excel_file()
            self._create_inventory_lines(inventory, lines)
        
        # Message de succès
        return {
            'type': 'ir.actions.act_window',
            'name': 'Inventaire Initial Créé',
            'res_model': 'stockex.stock.inventory',
            'res_id': inventory.id,
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'form_view_initial_mode': 'edit',
                'default_state': 'draft',
            }
        }
    
    def _parse_excel_file(self):
        """Parse le fichier Excel du stock initial."""
        try:
            from openpyxl import load_workbook
            import base64
            from io import BytesIO
        except ImportError:
            raise UserError(
                "Le module 'openpyxl' n'est pas installé.\n"
                "Installez-le avec: pip install openpyxl"
            )
        
        file_content = base64.b64decode(self.import_file)
        excel_file = BytesIO(file_content)
        wb = load_workbook(excel_file, read_only=True, data_only=True)
        ws = wb.active
        
        # Lire les en-têtes
        headers = [cell.value for cell in ws[1]]
        
        # Lire les données
        lines = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            if not any(row):
                continue
            
            row_dict = {}
            for idx, value in enumerate(row):
                if idx < len(headers):
                    row_dict[headers[idx]] = value if value is not None else ''
            
            lines.append(row_dict)
        
        wb.close()
        return lines
    
    def _create_inventory_lines(self, inventory, lines):
        """Crée les lignes d'inventaire depuis les données Excel."""
        created_count = 0
        errors = []
        
        for i, line_data in enumerate(lines):
            try:
                product_code = str(line_data.get('CODE PRODUIT', '')).strip()
                product_name = str(line_data.get('PRODUIT', '')).strip()
                quantity = float(line_data.get('QUANTITE', 0))
                price = float(line_data.get('PRIX UNITAIRE', 0))
                
                if not product_code:
                    continue
                
                # Rechercher ou créer le produit
                product = self.env['product.product'].search([
                    ('default_code', '=', product_code)
                ], limit=1)
                
                if not product and self.create_products:
                    product = self.env['product.product'].create({
                        'name': product_name or product_code,
                        'default_code': product_code,
                        'type': 'product',
                        'standard_price': price,
                    })
                
                if product:
                    # Créer la ligne d'inventaire
                    self.env['stockex.stock.inventory.line'].create({
                        'inventory_id': inventory.id,
                        'product_id': product.id,
                        'location_id': self.location_id.id,
                        'product_qty': quantity,
                        'standard_price': price,
                    })
                    created_count += 1
                else:
                    errors.append(f"Ligne {i+2}: Produit '{product_code}' non trouvé")
                    
            except Exception as e:
                errors.append(f"Ligne {i+2}: {str(e)}")
        
        # Message récapitulatif
        message = f"✅ {created_count} ligne(s) créée(s)"
        if errors:
            message += f"\n⚠️ {len(errors)} erreur(s):\n" + "\n".join(errors[:10])
        
        inventory.message_post(body=message)
        
        return created_count
