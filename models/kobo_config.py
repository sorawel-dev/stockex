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
        help='Permet d\'activer/désactiver cette configuration'
    )
    
    # API Configuration
    kobo_url = fields.Char(
        string='URL Kobo',
        required=True,
        default='https://kf.kesafrica.com',
        help='URL de votre serveur Kobo (ex: https://kf.kesafrica.com ou https://kf.kobotoolbox.org)'
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
        default='begin_group_TSW6h0mGE/material_description',
        required=True,
        help='Nom du champ dans Kobo contenant le code produit'
    )
    
    mapping_product_name = fields.Char(
        string='Champ Nom Produit',
        default='begin_group_TSW6h0mGE/nom_materiel',
        help='Nom du champ dans Kobo contenant le nom du produit'
    )
    
    mapping_quantity = fields.Char(
        string='Champ Quantité',
        default='begin_group_TSW6h0mGE/quantity',
        required=True,
        help='Nom du champ dans Kobo contenant la quantité'
    )
    
    mapping_location = fields.Char(
        string='Champ Emplacement',
        default='begin_group_TSW6h0mGE/Sous_magasin',
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
    
    mapping_gps_lat = fields.Char(
        string='Champ Latitude GPS',
        default='_geolocation[0]',
        help='Nom du champ dans Kobo contenant la latitude (utiliser _geolocation pour coordonnées)'
    )
    
    mapping_gps_lon = fields.Char(
        string='Champ Longitude GPS',
        default='_geolocation[1]',
        help='Nom du champ dans Kobo contenant la longitude'
    )
    
    mapping_gps_alt = fields.Char(
        string='Champ Altitude GPS',
        default='_Coordonnées géographiques_altitude',
        help='Nom du champ dans Kobo contenant l\'altitude'
    )
    
    mapping_warehouse = fields.Char(
        string='Champ Entrepôt/Sous-emplacement',
        default='begin_group_TSW6h0mGE/Sous_magasin',
        help='Nom du champ dans Kobo contenant le sous-emplacement détaillé'
    )
    
    mapping_brand = fields.Char(
        string='Champ Marque',
        default='begin_group_TSW6h0mGE/marque',
        help='Nom du champ dans Kobo contenant la marque du produit'
    )
    
    mapping_product_type = fields.Char(
        string='Champ Type Produit',
        default='begin_group_TSW6h0mGE/type_article',
        help='Nom du champ indiquant si l\'article est sérialisé ou non'
    )
    
    mapping_photo_url = fields.Char(
        string='Champ URL Photo Produit',
        default='begin_group_TSW6h0mGE/photo',
        help='Nom du champ contenant le nom de fichier de la photo du produit'
    )
    
    mapping_label_url = fields.Char(
        string='Champ URL Photo Étiquette',
        default='begin_group_HZpqEzA1G/Ajouter_une_photo_de_te_d_inventaire_ENEO',
        help='Nom du champ contenant le nom de fichier de la photo de l\'étiquette'
    )
    
    mapping_submission_id = fields.Char(
        string='Champ ID Soumission',
        default='_id',
        help='Nom du champ contenant l\'ID unique de la soumission'
    )
    
    mapping_submission_time = fields.Char(
        string='Champ Date Soumission',
        default='_submission_time',
        help='Nom du champ contenant la date/heure de soumission'
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
    
    # Cron Configuration
    cron_interval_number = fields.Integer(
        string='Intervalle',
        default=1,
        help='Nombre d\'unités pour l\'intervalle d\'import automatique'
    )
    
    cron_interval_type = fields.Selection(
        selection=[
            ('minutes', 'Minutes'),
            ('hours', 'Heures'),
            ('days', 'Jours'),
            ('weeks', 'Semaines'),
            ('months', 'Mois'),
        ],
        string='Type d\'Intervalle',
        default='hours',
        help='Type d\'unité pour l\'intervalle d\'import automatique'
    )
    
    cron_active = fields.Boolean(
        string='CRON Actif',
        compute='_compute_cron_active',
        inverse='_inverse_cron_active',
        help='Active ou désactive le CRON d\'import automatique'
    )
    
    create_missing_products = fields.Boolean(
        string='Créer les Produits Manquants',
        default=True
    )
    
    create_missing_locations = fields.Boolean(
        string='Créer les Emplacements Manquants',
        default=True
    )
    
    # Options de gestion des photos
    download_photos = fields.Boolean(
        string='Télécharger les Photos',
        default=True,
        help='Télécharger et attacher les photos des soumissions'
    )
    
    compress_photos = fields.Boolean(
        string='Compresser les Photos',
        default=True,
        help='Compresser les photos pour économiser l\'espace disque (redimensionne à 1600px max, qualité 90%)'
    )
    
    photo_max_size = fields.Integer(
        string='Taille Max Photo (px)',
        default=1600,
        help='Dimension maximale des photos (largeur ou hauteur). Recommandé: 1600px pour qualité optimale'
    )
    
    photo_quality = fields.Integer(
        string='Qualité JPEG (%)',
        default=90,
        help='Qualité de compression JPEG (1-100). Recommandé: 90% pour équilibre qualité/taille'
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
    
    # Configuration Telegram - Utilisation des paramètres globaux
    telegram_enabled = fields.Boolean(
        string='Notifications Telegram',
        default=False,
        help='Activer les notifications Telegram pour les synchronisations (utilise les paramètres globaux)'
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
    
    @api.onchange('active')
    def _onchange_active(self):
        """Désactive automatiquement les autres configurations quand celle-ci est activée."""
        if self.active:
            # Trouver d'autres configurations actives de la même société
            other_active = self.search([
                ('id', '!=', self.id),
                ('active', '=', True),
                ('company_id', '=', self.company_id.id)
            ])
            
            # Si d'autres configurations sont actives, les désactiver
            if other_active:
                other_active.write({'active': False})
                # Afficher un message d'information
                return {
                    'warning': {
                        'title': 'Configuration désactivée',
                        'message': f"Les configurations suivantes ont été automatiquement désactivées : {', '.join(other_active.mapped('name'))}"
                    }
                }
    
    def action_test_connection(self):
        """Teste la connexion à l'API Kobo avec correction automatique de l'UID en cas de 404."""
        self.ensure_one()
        
        try:
            import requests
            
            # Normaliser l'URL et l'UID
            base_url = (self.kobo_url or '').rstrip('/')
            uid = (self.form_id or '').strip()
            if not base_url:
                raise UserError("Veuillez renseigner l'URL Kobo.")
            if not uid:
                # Si l'UID est vide, tenter de le détecter automatiquement
                headers = {
                    'Authorization': f'Token {self.api_token}',
                    'Accept': 'application/json',
                }
                assets_resp = requests.get(f"{base_url}/api/v2/assets/?format=json", headers=headers, timeout=10)
                if assets_resp.status_code == 200:
                    assets = assets_resp.json().get('results', [])
                    # Choisir un formulaire déployé avec des soumissions
                    candidate = None
                    for a in assets:
                        if a.get('has_deployment') and (a.get('deployment__submission_count') or 0) > 0:
                            candidate = a
                            break
                    candidate = candidate or (assets[0] if assets else None)
                    if candidate:
                        uid = candidate.get('uid')
                        self.form_id = uid
                        self.form_name = candidate.get('name')
                    else:
                        raise UserError("Aucun formulaire disponible pour détecter automatiquement l'UID.")
                else:
                    raise UserError(f"Impossible de lister les formulaires (Code {assets_resp.status_code}).")
            
            headers = {
                'Authorization': f'Token {self.api_token}',
                'Accept': 'application/json',
            }
            
            url = f"{base_url}/api/v2/assets/{uid}/?format=json"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Certaines instances peuvent renvoyer du HTML si les en-têtes ne sont pas acceptés
                try:
                    data = response.json()
                except Exception:
                    ct = response.headers.get('Content-Type') or 'n/a'
                    preview = (response.text or '')[:300].strip()
                    raise UserError(
                        "Réponse non-JSON de l'API Kobo.\n"
                        f"Content-Type: {ct}\n"
                        f"URL testée: {url}\n"
                        "Vérifiez l'UID, le token et que l'API renvoie bien du JSON (?format=json).\n"
                        f"Aperçu: {preview}"
                    )
                self.form_name = data.get('name', 'Formulaire sans nom')
                
                # Auto-détection des champs depuis une soumission
                try:
                    data_resp = requests.get(f"{base_url}/api/v2/assets/{uid}/data/?format=json&limit=1", headers=headers, timeout=20)
                    if data_resp.status_code == 200:
                        payload = data_resp.json()
                        results = payload.get('results') or payload.get('data') or []
                        if results:
                            sample = results[0]
                            keys = list(sample.keys())
                            def pick(*subs):
                                for k in keys:
                                    kl = k.lower()
                                    if any(s in kl for s in subs):
                                        return k
                                return None
                            code = pick('material_description','code','reference','article')
                            name = pick('nom_materiel','nom','name','designation')
                            qty  = pick('quantity','quantite','qty','nombre')
                            loc  = pick('sous_magasin','location','magasin','warehouse','emplacement')
                            brand= pick('marque','brand')
                            photo= pick('photo')
                            if code: self.mapping_product_code = code
                            if name: self.mapping_product_name = name
                            if qty: self.mapping_quantity = qty
                            if loc:
                                self.mapping_location = loc
                                self.mapping_warehouse = loc
                            if brand: self.mapping_brand = brand
                            if photo: self.mapping_photo_url = photo
                            if '_geolocation' in sample:
                                self.mapping_gps_lat = '_geolocation[0]'
                                self.mapping_gps_lon = '_geolocation[1]'
                except Exception:
                    pass
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': '✅ Connexion Réussie',
                        'message': f"Formulaire trouvé : {self.form_name} (champs auto-détectés)",
                        'type': 'success',
                        'sticky': False,
                    }
                }
            elif response.status_code == 404:
                # Tentative de correction automatique: choisir un formulaire déployé avec soumissions
                assets_resp = requests.get(f"{base_url}/api/v2/assets/?format=json", headers=headers, timeout=10)
                if assets_resp.status_code == 200:
                    assets = assets_resp.json().get('results', [])
                    candidate = None
                    for a in assets:
                        if a.get('has_deployment') and (a.get('deployment__submission_count') or 0) > 0:
                            candidate = a
                            break
                    candidate = candidate or (assets[0] if assets else None)
                    if candidate:
                        self.form_id = candidate.get('uid')
                        self.form_name = candidate.get('name')
                        # Re-tester
                        retry_url = f"{base_url}/api/v2/assets/{self.form_id}/?format=json"
                        retry_resp = requests.get(retry_url, headers=headers, timeout=10)
                        if retry_resp.status_code == 200:
                            return {
                                'type': 'ir.actions.client',
                                'tag': 'display_notification',
                                'params': {
                                    'title': '✅ Connexion Réussie',
                                    'message': f"Configuration mise à jour automatiquement (UID: {self.form_id})",
                                    'type': 'success',
                                    'sticky': False,
                                }
                            }
                
                raise UserError(
                    "Erreur de connexion à Kobo:\n"
                    f"Code: 404\n"
                    "Vérifiez que l'UID du formulaire est correct et que le token a accès.\n"
                    f"URL testée: {url}"
                )
            elif response.status_code == 401:
                raise UserError("Non autorisé (401). Vérifiez le token API et ses permissions.")
            else:
                raise UserError(
                    "Erreur de connexion à Kobo:\n"
                    f"Code: {response.status_code}\n"
                    f"Message: {response.text}\n"
                    f"URL testée: {url}"
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
    
    def _compute_cron_active(self):
        """Calcule l'état du CRON."""
        cron = self.env.ref('stockex.ir_cron_kobo_auto_sync', raise_if_not_found=False)
        for config in self:
            config.cron_active = cron.active if cron else False
    
    def _inverse_cron_active(self):
        """Active ou désactive le CRON."""
        cron = self.env.ref('stockex.ir_cron_kobo_auto_sync', raise_if_not_found=False)
        if cron:
            cron.active = self.cron_active
    
    @api.model
    def default_get(self, fields_list):
        """Initialise les valeurs par défaut du CRON depuis la config existante."""
        res = super().default_get(fields_list)
        cron = self.env.ref('stockex.ir_cron_kobo_auto_sync', raise_if_not_found=False)
        if cron:
            res['cron_interval_number'] = cron.interval_number
            res['cron_interval_type'] = cron.interval_type
            res['cron_active'] = cron.active  # S'assurer que l'état actif est récupéré
        return res
    
    def action_update_cron_interval(self):
        """Met à jour l'intervalle du CRON."""
        self.ensure_one()
        cron = self.env.ref('stockex.ir_cron_kobo_auto_sync', raise_if_not_found=False)
        if cron:
            cron.write({
                'interval_number': self.cron_interval_number,
                'interval_type': self.cron_interval_type,
                'active': self.cron_active,  # Ajout de l'activation/désactivation
            })
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '✅ CRON Mis à Jour',
                    'message': f"Intervalle défini à {self.cron_interval_number} {dict(self._fields['cron_interval_type'].selection).get(self.cron_interval_type)} - Statut: {'Activé' if self.cron_active else 'Désactivé'}",
                    'type': 'success',
                    'sticky': False,
                }
            }
    
    @api.model
    def _cron_auto_sync(self):
        """Méthode appelée par le cron pour synchronisation automatique."""
        configs = self.search([('active', '=', True), ('auto_import', '=', True)])
        for config in configs:
            try:
                # Créer un wizard et lancer l'import
                wizard = self.env['stockex.import.kobo.wizard'].create({
                    'name': f'Import Auto Kobo - {fields.Date.today()}',
                    'date': fields.Date.today(),
                    'config_id': config.id,
                    'company_id': config.company_id.id,
                    'import_mode': 'all',
                    'auto_validate': config.auto_validate,
                })
                
                wizard.action_import()
                _logger.info(f"Synchronisation automatique Kobo réussie: {config.name}")
                
                # Envoyer notification Telegram si activé
                config._send_telegram_notification("Synchronisation automatique", "réussie")
                
            except Exception as e:
                _logger.error(f"Erreur synchronisation auto Kobo {config.name}: {e}", exc_info=True)
                # Envoyer notification d'erreur Telegram si activé
                config._send_telegram_notification("Synchronisation automatique", f"échouée: {str(e)}")
    
    def action_manual_sync(self):
        """Synchronisation manuelle avec KoboToolbox."""
        self.ensure_one()
        try:
            # Créer un wizard et lancer l'import
            wizard = self.env['stockex.import.kobo.wizard'].create({
                'name': f'Sync Manuelle - {fields.Datetime.now()}',
                'date': fields.Date.today(),
                'config_id': self.id,
                'company_id': self.company_id.id,
                'import_mode': 'all',  # Correction: utiliser 'all' au lieu de 'all_submissions'
                'auto_validate': self.auto_validate,
            })
            
            result = wizard.action_import()
            
            # Mettre à jour la date de dernière synchronisation
            self.write({
                'last_sync': fields.Datetime.now(),
            })
            
            # Envoyer notification Telegram si activé
            self._send_telegram_notification("Synchronisation manuelle", "réussie")
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '✅ Synchronisation réussie',
                    'message': f'Synchronisation terminée avec succès pour {self.name}',
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            _logger.error(f"Erreur synchronisation manuelle Kobo {self.name}: {e}", exc_info=True)
            # Envoyer notification d'erreur Telegram si activé
            self._send_telegram_notification("Synchronisation manuelle", f"échouée: {str(e)}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '❌ Erreur de synchronisation',
                    'message': f'Échec de la synchronisation: {str(e)}',
                    'type': 'danger',
                    'sticky': False,
                }
            }
    
    def _send_telegram_notification(self, sync_type, status):
        """Envoie une notification Telegram en utilisant les paramètres globaux."""
        self.ensure_one()
        
        # Vérifier si les notifications sont activées pour cette configuration
        if not self.telegram_enabled:
            return
        
        try:
            import requests
            import json
            
            # Récupérer les paramètres Telegram depuis la configuration globale
            # Utiliser les bons noms de paramètres avec le préfixe stockex.
            settings = self.env['ir.config_parameter'].sudo()
            telegram_bot_token = settings.get_param('stockex.telegram_bot_token')
            telegram_chat_ids = settings.get_param('stockex.telegram_chat_ids')
            
            # Vérifier que les paramètres globaux sont configurés
            if not telegram_bot_token or not telegram_chat_ids:
                _logger.warning(f"Paramètres Telegram non configurés dans les paramètres globaux pour {self.name}")
                return
            
            # Extraire le premier Chat ID de la liste
            chat_id_list = telegram_chat_ids.split(',')
            telegram_chat_id = chat_id_list[0].strip() if chat_id_list else None
            
            if not telegram_chat_id:
                _logger.warning(f"Aucun Chat ID Telegram trouvé pour {self.name}")
                return
            
            # Construire le message
            message = f"""
🔔 *Notification Stockex - {self.name}*

• Type: {sync_type}
• Statut: {status}
• Date: {fields.Datetime.now()}
• Base de données: {self.env.cr.dbname}

Configuration Kobo:
• Formulaire: {self.form_name or 'N/A'}
• URL: {self.kobo_url}
            """.strip()
            
            # Envoyer la notification
            url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
            payload = {
                'chat_id': telegram_chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, data=payload, timeout=10)
            response.raise_for_status()
            
            _logger.info(f"Notification Telegram envoyée pour {self.name}")
            
        except Exception as e:
            _logger.error(f"Erreur lors de l'envoi de la notification Telegram pour {self.name}: {e}")