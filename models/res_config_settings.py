# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    """Configuration des paramètres du module Stockex."""
    _inherit = 'res.config.settings'
    
    # Méthode d'import par défaut
    stockex_default_import_method = fields.Selection(
        selection=[
            ('excel', '📊 Fichier Excel/CSV'),
            ('kobo', '📱 Kobo Collect'),
            ('choice', '🎯 Demander à Chaque Fois'),
        ],
        string='Méthode d\'Import par Défaut',
        default='choice',
        config_parameter='stockex.default_import_method',
        help='Définit la méthode utilisée par défaut pour créer de nouveaux inventaires'
    )
    
    # Options Excel
    stockex_excel_create_products = fields.Boolean(
        string='Créer les Produits Manquants (Excel)',
        default=True,
        config_parameter='stockex.excel_create_products',
        help='Créer automatiquement les produits lors de l\'import Excel'
    )
    
    stockex_excel_create_locations = fields.Boolean(
        string='Créer les Emplacements Manquants (Excel)',
        default=True,
        config_parameter='stockex.excel_create_locations',
        help='Créer automatiquement les entrepôts lors de l\'import Excel'
    )
    
    stockex_excel_update_prices = fields.Boolean(
        string='Mettre à Jour les Prix (Excel)',
        default=True,
        config_parameter='stockex.excel_update_prices',
        help='Mettre à jour les prix des produits lors de l\'import Excel'
    )
    
    stockex_excel_import_geolocation = fields.Boolean(
        string='Importer la Géolocalisation (Excel)',
        default=True,
        config_parameter='stockex.excel_import_geolocation',
        help='Importer les coordonnées GPS lors de l\'import Excel'
    )
    
    # Options Kobo
    stockex_kobo_default_config_id = fields.Many2one(
        comodel_name='stockex.kobo.config',
        string='Configuration Kobo par Défaut',
        config_parameter='stockex.kobo_default_config_id',
        domain="[('active', '=', True)]",
        help='Configuration Kobo utilisée par défaut'
    )
    
    stockex_kobo_create_products = fields.Boolean(
        string='Créer les Produits Manquants (Kobo)',
        default=True,
        config_parameter='stockex.kobo_create_products',
        help='Créer automatiquement les produits lors de l\'import Kobo'
    )
    
    stockex_kobo_create_locations = fields.Boolean(
        string='Créer les Emplacements Manquants (Kobo)',
        default=True,
        config_parameter='stockex.kobo_create_locations',
        help='Créer automatiquement les entrepôts lors de l\'import Kobo'
    )
    
    stockex_kobo_auto_validate = fields.Boolean(
        string='Validation Automatique (Kobo)',
        default=False,
        config_parameter='stockex.kobo_auto_validate',
        help='Valider automatiquement les inventaires créés depuis Kobo'
    )
    
    # Notifications Email
    stockex_notify_by_email = fields.Boolean(
        string='📧 Activer Notifications Email',
        default=False,
        config_parameter='stockex.notify_by_email',
        help='Envoyer des notifications par email lors des imports réussis'
    )
    
    stockex_notification_emails = fields.Char(
        string='Emails de Notification',
        config_parameter='stockex.notification_emails',
        help='Liste d\'emails séparés par des virgules (ex: user1@example.com, user2@example.com)'
    )
    
    # Notifications WhatsApp
    stockex_notify_by_whatsapp = fields.Boolean(
        string='💬 Activer Notifications WhatsApp',
        default=False,
        config_parameter='stockex.notify_by_whatsapp',
        help='Envoyer des notifications WhatsApp lors des imports réussis'
    )
    
    stockex_whatsapp_provider = fields.Selection(
        selection=[
            ('twilio', 'Twilio'),
            ('meta', 'Meta WhatsApp Business API'),
            ('vonage', 'Vonage (Nexmo)'),
            ('360dialog', '360dialog'),
            ('custom', 'URL Personnalisée'),
        ],
        string='Fournisseur WhatsApp',
        default='twilio',
        config_parameter='stockex.whatsapp_provider',
        help='Sélectionnez votre fournisseur d\'API WhatsApp'
    )
    
    stockex_whatsapp_numbers = fields.Char(
        string='Numéros WhatsApp',
        config_parameter='stockex.whatsapp_numbers',
        help='Liste de numéros au format international séparés par des virgules (ex: +237690000001, +237690000002)'
    )
    
    stockex_whatsapp_api_url = fields.Char(
        string='URL API WhatsApp',
        config_parameter='stockex.whatsapp_api_url',
        help='URL de votre API WhatsApp (remplie automatiquement selon le fournisseur)'
    )
    
    stockex_whatsapp_api_token = fields.Char(
        string='Token/Clé API WhatsApp',
        config_parameter='stockex.whatsapp_api_token',
        help='Token d\'authentification pour l\'API WhatsApp'
    )
    
    stockex_whatsapp_account_sid = fields.Char(
        string='Account SID (Twilio)',
        config_parameter='stockex.whatsapp_account_sid',
        help='Account SID Twilio (requis pour Twilio)'
    )
    
    stockex_whatsapp_phone_number_id = fields.Char(
        string='Phone Number ID (Meta)',
        config_parameter='stockex.whatsapp_phone_number_id',
        help='ID du numéro de téléphone WhatsApp Business (requis pour Meta)'
    )
    
    # Règle de valorisation
    stockex_valuation_rule = fields.Selection(
        selection=[
            ('standard', '📌 Coût Standard'),
            ('average', '⚖️ Coût Moyen (AVCO)'),
            ('fifo', '🔄 Premier Entré Premier Sorti (FIFO)'),
            ('economic', '💰 Coût économique réel'),
        ],
        string='Méthode de valorisation',
        default='standard',
        config_parameter='stockex.valuation_rule',
        help="📌 Coût Standard: Prix fixe défini manuellement\n"
             "⚖️ Coût Moyen (AVCO): Moyenne pondérée des achats\n"
             "🔄 FIFO: Premier entré, premier sorti\n"
             "💰 Coût économique réel: Dernier prix d'achat réel (défini dans les paramètres Stockex)"
    )
    
    @api.onchange('stockex_valuation_rule')
    def _onchange_stockex_valuation_rule(self):
        """Avertit uniquement si la valeur change par rapport aux paramètres enregistrés."""
        if self.stockex_valuation_rule:
            params = self.env['ir.config_parameter'].sudo()
            current = params.get_param('stockex.valuation_rule', default='standard')
            if self.stockex_valuation_rule != current:
                method_labels = {
                    'standard': 'Coût Standard',
                    'average': 'Coût Moyen (AVCO)',
                    'fifo': 'Premier Entré Premier Sorti (FIFO)',
                    'economic': 'Coût économique réel'
                }
                method_name = method_labels.get(self.stockex_valuation_rule, self.stockex_valuation_rule)
                return {
                    'warning': {
                        'title': 'Mise à jour des catégories',
                        'message': f'Les catégories de produits seront mises à jour avec la méthode "{method_name}" lors de la sauvegarde.'
                    }
                }
    
    def set_values(self):
        """Surcharge pour mettre à jour les catégories lors de la sauvegarde
        et ajuster la visibilité du menu Rapport de Décote selon la règle."""
        super(ResConfigSettings, self).set_values()
        # Mise à jour des catégories selon la règle choisie
        if self.stockex_valuation_rule:
            self._update_product_categories_cost_method(self.stockex_valuation_rule)
        # Activer/Désactiver le menu Rapport de Décote dynamiquement
        menu = self.env.ref('stockex.menu_depreciation_report', raise_if_not_found=False)
        if menu:
            menu.sudo().write({'active': self.stockex_valuation_rule == 'economic'})
    
    def _update_product_categories_cost_method(self, cost_method):
        """Met à jour la méthode de coût de toutes les catégories de produits.
        
        Args:
            cost_method (str): 'standard', 'average', 'fifo' ou 'economic'
        """
        ProductCategory = self.env['product.category']
        
        # Vérifier si le module stock_account est installé
        if not hasattr(ProductCategory, 'property_cost_method'):
            return
        
        # Récupérer toutes les catégories
        categories = ProductCategory.search([])
        
        # Mettre à jour la méthode de coût pour chaque catégorie
        # Utilisation de sudo() pour avoir les droits d'écriture
        for category in categories.sudo():
            try:
                # Vérifier si la catégorie a déjà une méthode de coût personnalisée
                # Si oui, on la met à jour, sinon on crée la propriété
                category.property_cost_method = cost_method
            except Exception as e:
                # Logger l'erreur mais continuer avec les autres catégories
                import logging
                _logger = logging.getLogger(__name__)
                _logger.warning(
                    f"Impossible de mettre à jour la méthode de coût pour la catégorie {category.name}: {str(e)}"
                )
    
    # Décote selon rotation du stock
    stockex_apply_depreciation = fields.Boolean(
        string='Appliquer la décote selon rotation',
        default=False,
        config_parameter='stockex.apply_depreciation',
        help='Appliquer une décote sur la valorisation selon la rotation du stock (stock mort, rotation lente)'
    )
    
    stockex_depreciation_active_days = fields.Integer(
        string='Période stock actif (jours)',
        default=365,
        config_parameter='stockex.depreciation_active_days',
        help='Nombre de jours sans mouvement pour considérer le stock comme actif (décote 0%)'
    )
    
    stockex_depreciation_slow_days = fields.Integer(
        string='Période rotation lente (jours)',
        default=1095,
        config_parameter='stockex.depreciation_slow_days',
        help='Nombre de jours sans mouvement pour considérer le stock en rotation lente (au-delà = stock mort)'
    )
    
    stockex_depreciation_slow_rate = fields.Float(
        string='Taux décote rotation lente (%)',
        default=40.0,
        config_parameter='stockex.depreciation_slow_rate',
        help='Pourcentage de décote pour les produits en rotation lente (ex: 40%)'
    )
    
    stockex_depreciation_dead_rate = fields.Float(
        string='Taux décote stock mort (%)',
        default=100.0,
        config_parameter='stockex.depreciation_dead_rate',
        help='Pourcentage de décote pour les produits en stock mort (ex: 100% = valeur nulle)'
    )

    # Notifications Telegram
    stockex_notify_by_telegram = fields.Boolean(
        string='📱 Activer Notifications Telegram',
        default=False,
        config_parameter='stockex.notify_by_telegram',
        help='Envoyer des notifications Telegram lors des imports réussis'
    )
    
    stockex_telegram_bot_token = fields.Char(
        string='Bot Token Telegram',
        config_parameter='stockex.telegram_bot_token',
        help='Token du bot Telegram (obtenu via @BotFather)'
    )
    
    stockex_telegram_chat_ids = fields.Char(
        string='Chat IDs Telegram',
        config_parameter='stockex.telegram_chat_ids',
        help='Liste des Chat IDs séparés par des virgules (ex: 123456789, 987654321)'
    )
    
    # Statistiques

    # Configuration MinIO
    minio_enabled = fields.Boolean(
        string='Activer MinIO',
        default=False,
        config_parameter='minio.enabled',
        help='Activer le stockage des pièces jointes sur MinIO',
        store=False
    )
    
    minio_endpoint = fields.Char(
        string='Endpoint MinIO',
        config_parameter='minio.endpoint',
        help='Adresse du serveur MinIO (ex: minio.example.com:9000)',
        store=False
    )
    
    minio_access_key = fields.Char(
        string='MinIO Access Key',
        config_parameter='minio.access_key',
        help='Clé d\'accès MinIO',
        store=False
    )
    
    minio_secret_key = fields.Char(
        string='MinIO Secret Key',
        config_parameter='minio.secret_key',
        help='Clé secrète MinIO',
        store=False
    )
    
    minio_bucket = fields.Char(
        string='Bucket',
        default='stockex-documents',
        config_parameter='minio.bucket',
        help='Nom du bucket MinIO pour stocker les documents',
        store=False
    )
    
    minio_secure = fields.Boolean(
        string='Utiliser HTTPS',
        default=True,
        config_parameter='minio.secure',
        help='Utiliser une connexion sécurisée (HTTPS) pour MinIO',
        store=False
    )
    
    minio_region = fields.Char(
        string='Région',
        default='Deutchland',
        config_parameter='minio.region',
        help='Région du serveur MinIO',
        store=False
    )

    def test_minio_connection(self):
        """Teste la connexion au serveur MinIO."""
        MinioStorage = self.env['minio.storage']
        try:
            client = MinioStorage._get_minio_client()
            bucket = MinioStorage._get_bucket_name()
            
            # Vérifier la connexion et créer le bucket si nécessaire
            if not client.bucket_exists(bucket):
                client.make_bucket(bucket)
                message = f"✅ Connexion réussie ! Bucket '{bucket}' créé."
            else:
                message = f"✅ Connexion réussie ! Bucket '{bucket}' existe déjà."
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Test MinIO',
                    'message': message,
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Erreur MinIO',
                    'message': f"❌ Échec de la connexion: {str(e)}",
                    'type': 'danger',
                    'sticky': True,
                }
            }

    

    
    @api.onchange('stockex_whatsapp_provider', 'stockex_whatsapp_account_sid', 'stockex_whatsapp_phone_number_id')
    def _onchange_whatsapp_provider(self):
        """Génère automatiquement l'URL API selon le fournisseur."""
        if self.stockex_whatsapp_provider == 'twilio' and self.stockex_whatsapp_account_sid:
            self.stockex_whatsapp_api_url = f'https://api.twilio.com/2010-04-01/Accounts/{self.stockex_whatsapp_account_sid}/Messages.json'
        elif self.stockex_whatsapp_provider == 'meta' and self.stockex_whatsapp_phone_number_id:
            self.stockex_whatsapp_api_url = f'https://graph.facebook.com/v18.0/{self.stockex_whatsapp_phone_number_id}/messages'
        elif self.stockex_whatsapp_provider == 'vonage':
            self.stockex_whatsapp_api_url = 'https://messages-sandbox.nexmo.com/v0.1/messages'
        elif self.stockex_whatsapp_provider == '360dialog':
            self.stockex_whatsapp_api_url = 'https://waba.360dialog.io/v1/messages'
        elif self.stockex_whatsapp_provider != 'custom':
            self.stockex_whatsapp_api_url = ''
    
    def action_open_kobo_config(self):
        """Ouvre la configuration Kobo Collect."""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Configuration Kobo Collect',
            'res_model': 'stockex.kobo.config',
            'view_mode': 'list,form',
            'target': 'current',
        }
    
    def action_open_eneo_regions(self):
        """Ouvre la liste des régions électriques ENEO."""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Régions Électriques ENEO',
            'res_model': 'stockex.eneo.region',
            'view_mode': 'list,form',
            'target': 'current',
        }
