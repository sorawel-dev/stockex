# -*- coding: utf-8 -*-

import logging
import json
from datetime import datetime
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ImportKoboWizard(models.TransientModel):
    """Wizard pour importer les données depuis Kobo Collect."""
    _name = 'stockex.import.kobo.wizard'
    _description = 'Import Kobo Collect'
    
    name = fields.Char(
        string='Nom de l\'Inventaire',
        required=True,
        default=lambda self: f"Inventaire Kobo {fields.Date.today()}"
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
    
    config_id = fields.Many2one(
        comodel_name='stockex.kobo.config',
        string='Configuration Kobo',
        required=True,
        domain="[('active', '=', True), ('company_id', '=', company_id)]"
    )
    
    import_mode = fields.Selection(
        selection=[
            ('new_only', 'Nouvelles Soumissions Uniquement'),
            ('all', 'Toutes les Soumissions'),
            ('date_range', 'Plage de Dates'),
        ],
        string='Mode d\'Import',
        default='new_only',
        required=True
    )
    
    date_from = fields.Date(
        string='Date Début',
        help='Importer les soumissions à partir de cette date'
    )
    
    date_to = fields.Date(
        string='Date Fin',
        help='Importer les soumissions jusqu\'à cette date'
    )
    
    # Options
    create_missing_products = fields.Boolean(
        string='Créer les Produits Manquants',
        default=True,
        related='config_id.create_missing_products',
        readonly=False
    )
    
    create_missing_locations = fields.Boolean(
        string='Créer les Emplacements Manquants',
        default=True,
        related='config_id.create_missing_locations',
        readonly=False
    )
    
    update_product_prices = fields.Boolean(
        string='Mettre à Jour les Prix',
        default=True
    )
    
    import_geolocation = fields.Boolean(
        string='Importer la Géolocalisation',
        default=True
    )
    
    auto_validate = fields.Boolean(
        string='Valider Automatiquement',
        default=False,
        related='config_id.auto_validate',
        readonly=False
    )
    
    # Preview
    submissions_count = fields.Integer(
        string='Soumissions à Importer',
        compute='_compute_submissions_preview'
    )
    
    preview_html = fields.Html(
        string='Aperçu',
        compute='_compute_submissions_preview'
    )
    
    @api.depends('config_id', 'import_mode', 'date_from', 'date_to')
    def _compute_submissions_preview(self):
        """Calcule un aperçu des soumissions à importer."""
        for wizard in self:
            if not wizard.config_id:
                wizard.submissions_count = 0
                wizard.preview_html = "<p class='text-muted'>Sélectionnez une configuration Kobo</p>"
                continue
            
            # Simuler pour l'instant
            wizard.submissions_count = 0
            wizard.preview_html = f"""
            <div class='alert alert-info'>
                <h5>Configuration : {wizard.config_id.name}</h5>
                <ul>
                    <li><strong>Formulaire :</strong> {wizard.config_id.form_name or wizard.config_id.form_id}</li>
                    <li><strong>URL :</strong> {wizard.config_id.kobo_url}</li>
                    <li><strong>Mode :</strong> {dict(wizard._fields['import_mode'].selection).get(wizard.import_mode)}</li>
                </ul>
                <p class='text-warning'>⏳ Connexion à Kobo... Cliquez sur "Synchroniser" pour récupérer les données.</p>
            </div>
            """
    
    def action_sync_kobo(self):
        """Synchronise avec Kobo et récupère les soumissions."""
        self.ensure_one()
        
        if not self.config_id:
            raise UserError("Veuillez sélectionner une configuration Kobo.")
        
        try:
            import requests
            
            headers = {
                'Authorization': f'Token {self.config_id.api_token}'
            }
            
            # Récupérer les soumissions
            url = f"{self.config_id.kobo_url}/api/v2/assets/{self.config_id.form_id}/data/"
            
            params = {}
            if self.import_mode == 'new_only' and self.config_id.last_submission_id:
                params['query'] = json.dumps({'_id': {'$gt': self.config_id.last_submission_id}})
            elif self.import_mode == 'date_range' and self.date_from:
                params['query'] = json.dumps({
                    '_submission_time': {
                        '$gte': self.date_from.strftime('%Y-%m-%d'),
                        '$lte': (self.date_to or fields.Date.today()).strftime('%Y-%m-%d')
                    }
                })
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                submissions = data.get('results', [])
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': '✅ Synchronisation Réussie',
                        'message': f"{len(submissions)} soumission(s) trouvée(s)",
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise UserError(
                    f"Erreur lors de la synchronisation:\n"
                    f"Code: {response.status_code}\n"
                    f"Message: {response.text}"
                )
                
        except ImportError:
            raise UserError(
                "Le module 'requests' n'est pas installé.\n"
                "Installez-le avec : pip3 install requests"
            )
        except Exception as e:
            raise UserError(f"Erreur lors de la synchronisation:\n{str(e)}")
    
    def action_import(self):
        """Importe les données depuis Kobo et crée l'inventaire."""
        self.ensure_one()
        
        if not self.config_id:
            raise UserError("Veuillez sélectionner une configuration Kobo.")
        
        try:
            import requests
            
            headers = {
                'Authorization': f'Token {self.config_id.api_token}'
            }
            
            # Récupérer les soumissions
            url = f"{self.config_id.kobo_url}/api/v2/assets/{self.config_id.form_id}/data/"
            
            params = {}
            if self.import_mode == 'new_only' and self.config_id.last_submission_id:
                params['query'] = json.dumps({'_id': {'$gt': self.config_id.last_submission_id}})
            elif self.import_mode == 'date_range' and self.date_from:
                params['query'] = json.dumps({
                    '_submission_time': {
                        '$gte': self.date_from.strftime('%Y-%m-%d'),
                        '$lte': (self.date_to or fields.Date.today()).strftime('%Y-%m-%d')
                    }
                })
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code != 200:
                raise UserError(
                    f"Erreur lors de la récupération des données:\n"
                    f"Code: {response.status_code}\n"
                    f"Message: {response.text}"
                )
            
            data = response.json()
            submissions = data.get('results', [])
            
            if not submissions:
                raise UserError("Aucune soumission à importer.")
            
            # Créer l'inventaire
            inventory = self._create_inventory_from_submissions(submissions)
            
            # Mettre à jour la configuration
            if submissions:
                last_id = max(s.get('_id', 0) for s in submissions)
                self.config_id.write({
                    'last_sync': fields.Datetime.now(),
                    'last_submission_id': last_id,
                })
            
            # Auto-validation si demandé
            if self.auto_validate:
                inventory.action_validate()
            
            return {
                'type': 'ir.actions.act_window',
                'name': 'Inventaire Importé',
                'res_model': 'stockex.stock.inventory',
                'res_id': inventory.id,
                'view_mode': 'form',
                'target': 'current',
            }
            
        except ImportError:
            raise UserError(
                "Le module 'requests' n'est pas installé.\n"
                "Installez-le avec : pip3 install requests"
            )
        except Exception as e:
            _logger.error(f"Erreur import Kobo: {e}", exc_info=True)
            raise UserError(f"Erreur lors de l'import:\n{str(e)}")
    
    def _create_inventory_from_submissions(self, submissions):
        """Crée un inventaire à partir des soumissions Kobo."""
        # Créer l'inventaire
        inventory = self.env['stockex.stock.inventory'].create({
            'name': self.name,
            'date': self.date,
            'company_id': self.company_id.id,
            'user_id': self.env.user.id,
            'state': 'draft',
            'description': f'Import Kobo Collect - {len(submissions)} soumissions\nFormulaire: {self.config_id.form_name or self.config_id.form_id}'
        })
        
        # Caches
        products_cache = {}
        warehouses_cache = {}
        categories_cache = {}
        
        imported = 0
        skipped = 0
        errors_detail = []
        
        # Mapping des champs
        field_product_code = self.config_id.mapping_product_code
        field_product_name = self.config_id.mapping_product_name
        field_quantity = self.config_id.mapping_quantity
        field_location = self.config_id.mapping_location
        field_category = self.config_id.mapping_category
        field_price = self.config_id.mapping_price
        field_gps = self.config_id.mapping_gps
        
        for i, submission in enumerate(submissions):
            try:
                # Extraire les données selon le mapping
                product_code = str(submission.get(field_product_code, '')).strip()
                product_name = str(submission.get(field_product_name, '')).strip()
                location_name = str(submission.get(field_location, '')).strip()
                
                if not product_code or not location_name:
                    skipped += 1
                    errors_detail.append(f"Soumission {i+1}: Code produit ou emplacement manquant")
                    continue
                
                # Quantité
                try:
                    quantity = float(submission.get(field_quantity, 0))
                except:
                    quantity = 0.0
                
                # Prix
                try:
                    price = float(submission.get(field_price, 0))
                except:
                    price = 0.0
                
                # Catégorie
                category_name = str(submission.get(field_category, '')).strip()
                category_id = None
                if category_name and category_name not in categories_cache:
                    category = self.env['product.category'].search([('name', '=', category_name)], limit=1)
                    if not category and self.create_missing_products:
                        category = self.env['product.category'].create({'name': category_name})
                    categories_cache[category_name] = category.id if category else False
                category_id = categories_cache.get(category_name)
                
                # Entrepôt
                if location_name not in warehouses_cache:
                    warehouse = self.env['stock.warehouse'].search([('name', '=', location_name)], limit=1)
                    if not warehouse and self.create_missing_locations:
                        warehouse = self.env['stock.warehouse'].create({
                            'name': location_name,
                            'code': location_name[:5].upper(),
                            'company_id': self.company_id.id,
                        })
                    warehouses_cache[location_name] = warehouse.lot_stock_id.id if warehouse else False
                
                location_id = warehouses_cache.get(location_name)
                if not location_id:
                    skipped += 1
                    errors_detail.append(f"Soumission {i+1}: Entrepôt '{location_name}' non trouvé")
                    continue
                
                # Produit
                if product_code not in products_cache:
                    product = self.env['product.product'].search([('default_code', '=', product_code)], limit=1)
                    if not product and self.create_missing_products:
                        product = self.env['product.product'].create({
                            'name': product_name or product_code,
                            'default_code': product_code,
                            'type': 'product',
                            'categ_id': category_id if category_id else self.env.ref('product.product_category_all').id,
                            'standard_price': price,
                        })
                    elif product and self.update_product_prices and price > 0:
                        product.write({'standard_price': price})
                    
                    products_cache[product_code] = product.id if product else False
                
                product_id = products_cache.get(product_code)
                if not product_id:
                    skipped += 1
                    errors_detail.append(f"Soumission {i+1}: Produit '{product_code}' non trouvé")
                    continue
                
                # Créer la ligne d'inventaire
                self.env['stockex.stock.inventory.line'].create({
                    'inventory_id': inventory.id,
                    'product_id': product_id,
                    'location_id': location_id,
                    'product_qty': quantity,
                    'standard_price': price,
                })
                
                imported += 1
                
            except Exception as e:
                skipped += 1
                errors_detail.append(f"Soumission {i+1}: {str(e)}")
                _logger.error(f"Erreur import soumission {i+1}: {e}")
        
        # Message de résultat
        message = f"✅ Import Kobo terminé\n\n"
        message += f"📊 Statistiques:\n"
        message += f"- Total soumissions: {len(submissions)}\n"
        message += f"- ✅ Importées: {imported}\n"
        message += f"- ⚠️ Ignorées: {skipped}\n"
        
        if errors_detail:
            message += f"\n⚠️ Détails des erreurs:\n" + "\n".join(errors_detail[:10])
        
        inventory.message_post(body=message)
        
        return inventory
