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
    stockex_inventory_count = fields.Integer(
        string='Nombre d\'Inventaires',
        compute='_compute_stockex_stats',
        readonly=True
    )
    
    stockex_last_import_date = fields.Datetime(
        string='Dernier Import',
        compute='_compute_stockex_stats',
        readonly=True
    )
    
    @api.depends('company_id')
    def _compute_stockex_stats(self):
        """Calcule les statistiques d'utilisation."""
        for config in self:
            inventories = self.env['stockex.stock.inventory'].search([
                ('company_id', '=', config.company_id.id)
            ])
            
            config.stockex_inventory_count = len(inventories)
            config.stockex_last_import_date = inventories[0].create_date if inventories else False
    
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
