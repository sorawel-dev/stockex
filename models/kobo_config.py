# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class KoboCollectConfig(models.Model):
    """Configuration pour l'intégration Kobo Collect."""
    _name = 'stockex.kobo.config'
    _description = 'Configuration Kobo Collect'
    _order = 'id desc'
    
    name = fields.Char(
        string='Nom de la Configuration',
        required=True,
        default='Configuration Kobo Collect'
    )
    
    active = fields.Boolean(
        string='Actif',
        default=True,
        help='Seule une configuration peut être active à la fois'
    )
    
    # API Configuration
    kobo_url = fields.Char(
        string='URL Kobo',
        required=True,
        default='https://kf.kobotoolbox.org',
        help='URL de votre serveur Kobo (ex: https://kf.kobotoolbox.org ou https://kobo.humanitarianresponse.info)'
    )
    
    api_token = fields.Char(
        string='Token API',
        required=True,
        help='Token d\'authentification Kobo (obtenu depuis Paramètres → Sécurité)'
    )
    
    # Form Configuration
    form_id = fields.Char(
        string='ID du Formulaire',
        required=True,
        help='ID du formulaire Kobo (ex: aXYZ123456)'
    )
    
    form_name = fields.Char(
        string='Nom du Formulaire',
        help='Nom descriptif du formulaire'
    )
    
    # Mapping Configuration
    mapping_product_code = fields.Char(
        string='Champ Code Produit',
        default='product_code',
        required=True,
        help='Nom du champ dans Kobo contenant le code produit'
    )
    
    mapping_product_name = fields.Char(
        string='Champ Nom Produit',
        default='product_name',
        help='Nom du champ dans Kobo contenant le nom du produit'
    )
    
    mapping_quantity = fields.Char(
        string='Champ Quantité',
        default='quantity',
        required=True,
        help='Nom du champ dans Kobo contenant la quantité'
    )
    
    mapping_location = fields.Char(
        string='Champ Emplacement',
        default='warehouse',
        required=True,
        help='Nom du champ dans Kobo contenant l\'emplacement/entrepôt'
    )
    
    mapping_category = fields.Char(
        string='Champ Catégorie',
        default='category',
        help='Nom du champ dans Kobo contenant la catégorie'
    )
    
    mapping_price = fields.Char(
        string='Champ Prix',
        default='unit_price',
        help='Nom du champ dans Kobo contenant le prix unitaire'
    )
    
    mapping_gps = fields.Char(
        string='Champ GPS',
        default='gps_location',
        help='Nom du champ dans Kobo contenant les coordonnées GPS'
    )
    
    # Options
    auto_import = fields.Boolean(
        string='Import Automatique',
        default=False,
        help='Importer automatiquement les nouvelles soumissions'
    )
    
    auto_validate = fields.Boolean(
        string='Validation Automatique',
        default=False,
        help='Valider automatiquement les inventaires créés'
    )
    
    create_missing_products = fields.Boolean(
        string='Créer les Produits Manquants',
        default=True
    )
    
    create_missing_locations = fields.Boolean(
        string='Créer les Emplacements Manquants',
        default=True
    )
    
    # Status
    last_sync = fields.Datetime(
        string='Dernière Synchronisation',
        readonly=True
    )
    
    last_submission_id = fields.Integer(
        string='Dernier ID Soumission',
        readonly=True,
        help='ID de la dernière soumission importée'
    )
    
    submissions_count = fields.Integer(
        string='Nombre de Soumissions',
        compute='_compute_submissions_count',
        store=False
    )
    
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Société',
        required=True,
        default=lambda self: self.env.company
    )
    
    # Unicité de la config active gérée au niveau Python via @api.constrains('active')
    
    @api.depends('form_id')
    def _compute_submissions_count(self):
        """Compte le nombre de soumissions (simulé pour l'instant)."""
        for config in self:
            config.submissions_count = 0
    
    @api.constrains('active')
    def _check_unique_active(self):
        """Vérifie qu'une seule configuration est active."""
        for config in self:
            if config.active:
                other_active = self.search([
                    ('id', '!=', config.id),
                    ('active', '=', True),
                    ('company_id', '=', config.company_id.id)
                ])
                if other_active:
                    raise UserError(
                        "Une seule configuration Kobo Collect peut être active à la fois.\n"
                        f"Désactivez d'abord : {other_active[0].name}"
                    )
    
    def action_test_connection(self):
        """Teste la connexion à l'API Kobo."""
        self.ensure_one()
        
        try:
            import requests
            
            headers = {
                'Authorization': f'Token {self.api_token}'
            }
            
            url = f"{self.kobo_url}/api/v2/assets/{self.form_id}/"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.form_name = data.get('name', 'Formulaire sans nom')
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': '✅ Connexion Réussie',
                        'message': f"Formulaire trouvé : {self.form_name}",
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise UserError(
                    f"Erreur de connexion à Kobo:\n"
                    f"Code: {response.status_code}\n"
                    f"Message: {response.text}"
                )
                
        except ImportError:
            raise UserError(
                "Le module 'requests' n'est pas installé.\n"
                "Installez-le avec : pip3 install requests"
            )
        except Exception as e:
            raise UserError(f"Erreur lors du test de connexion:\n{str(e)}")
    
    def action_view_submissions(self):
        """Ouvre la vue des soumissions Kobo."""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Soumissions Kobo',
            'res_model': 'stockex.kobo.submission',
            'view_mode': 'list,form',
            'domain': [('config_id', '=', self.id)],
            'context': {
                'default_config_id': self.id,
            },
        }
    
    @api.model
    def _cron_auto_sync(self):
        """Méthode appelée par le cron pour synchronisation automatique."""
        for config in self:
            if not config.active or not config.auto_import:
                continue
            
            try:
                # Créer un wizard et lancer l'import
                wizard = self.env['stockex.import.kobo.wizard'].create({
                    'name': f'Import Auto Kobo - {fields.Date.today()}',
                    'date': fields.Date.today(),
                    'config_id': config.id,
                    'company_id': config.company_id.id,
                    'import_mode': 'new_only',
                    'auto_validate': config.auto_validate,
                })
                
                wizard.action_import()
                _logger.info(f"Synchronisation automatique Kobo réussie: {config.name}")
                
            except Exception as e:
                _logger.error(f"Erreur synchronisation auto Kobo {config.name}: {e}", exc_info=True)
