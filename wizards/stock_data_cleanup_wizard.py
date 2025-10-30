# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging
import requests
from datetime import datetime

_logger = logging.getLogger(__name__)


class StockDataCleanupWizard(models.TransientModel):
    """Wizard pour la réinitialisation forcée des données de stock."""
    _name = 'stockex.stock.data.cleanup.wizard'
    _description = 'Assistant de Nettoyage des Données de Stock'
    
    # Options de nettoyage
    delete_products = fields.Boolean(
        string='🗑️ Supprimer les Produits',
        default=False,
        help='Supprime tous les produits (sauf ceux utilisés dans des commandes validées)'
    )
    delete_categories = fields.Boolean(
        string='🗑️ Supprimer les Catégories',
        default=False,
        help='Supprime toutes les catégories de produits (sauf celles par défaut)'
    )
    delete_stock_moves = fields.Boolean(
        string='🗑️ Supprimer les Mouvements de Stock',
        default=False,
        help='Supprime tous les mouvements de stock (pickings, transferts, etc.)'
    )
    delete_warehouses = fields.Boolean(
        string='🗑️ Supprimer les Entrepôts',
        default=False,
        help='Supprime tous les entrepôts personnalisés et leurs emplacements'
    )
    delete_locations = fields.Boolean(
        string='🗑️ Supprimer les Emplacements',
        default=False,
        help='Supprime tous les emplacements personnalisés'
    )
    delete_inventories = fields.Boolean(
        string='🗑️ Supprimer les Inventaires StockEx',
        default=False,
        help='Supprime tous les inventaires créés avec StockEx'
    )
    delete_all = fields.Boolean(
        string='⚠️ TOUT SUPPRIMER (DANGER)',
        default=False,
        help='Active toutes les options de suppression'
    )
    
    # Confirmation de sécurité
    confirmation_text = fields.Char(
        string='Confirmation',
        help='Tapez "SUPPRIMER" pour confirmer'
    )
    
    # Informations statistiques
    products_count = fields.Integer(
        string='Produits',
        compute='_compute_counts'
    )
    categories_count = fields.Integer(
        string='Catégories',
        compute='_compute_counts'
    )
    moves_count = fields.Integer(
        string='Mouvements',
        compute='_compute_counts'
    )
    warehouses_count = fields.Integer(
        string='Entrepôts',
        compute='_compute_counts'
    )
    locations_count = fields.Integer(
        string='Emplacements',
        compute='_compute_counts'
    )
    inventories_count = fields.Integer(
        string='Inventaires StockEx',
        compute='_compute_counts'
    )
    
    @api.depends('delete_products', 'delete_categories', 'delete_stock_moves', 
                 'delete_warehouses', 'delete_locations', 'delete_inventories')
    def _compute_counts(self):
        """Calcule le nombre d'enregistrements pour chaque type."""
        for wizard in self:
            wizard.products_count = self.env['product.product'].search_count([])
            wizard.categories_count = self.env['product.category'].search_count([])
            wizard.moves_count = self.env['stock.move'].search_count([])
            wizard.warehouses_count = self.env['stock.warehouse'].search_count([])
            wizard.locations_count = self.env['stock.location'].search_count([
                ('usage', 'in', ['internal', 'view'])
            ])
            wizard.inventories_count = self.env['stockex.stock.inventory'].search_count([])
    
    @api.onchange('delete_all')
    def _onchange_delete_all(self):
        """Coche/décoche toutes les options."""
        if self.delete_all:
            self.delete_products = True
            self.delete_categories = True
            self.delete_stock_moves = True
            self.delete_warehouses = True
            self.delete_locations = True
            self.delete_inventories = True
        else:
            self.delete_products = False
            self.delete_categories = False
            self.delete_stock_moves = False
            self.delete_warehouses = False
            self.delete_locations = False
            self.delete_inventories = False
    
    def _check_confirmation(self):
        """Vérifie que l'utilisateur a bien tapé la confirmation."""
        self.ensure_one()
        if not self.confirmation_text or self.confirmation_text.upper() != 'SUPPRIMER':
            raise UserError(
                "⚠️ Confirmation requise\n\n"
                "Pour confirmer cette action IRRÉVERSIBLE, "
                "veuillez taper exactement 'SUPPRIMER' dans le champ de confirmation."
            )
    
    def _check_at_least_one_option(self):
        """Vérifie qu'au moins une option est sélectionnée."""
        self.ensure_one()
        if not any([
            self.delete_products,
            self.delete_categories,
            self.delete_stock_moves,
            self.delete_warehouses,
            self.delete_locations,
            self.delete_inventories,
        ]):
            raise UserError(
                "❌ Aucune option sélectionnée\n\n"
                "Veuillez sélectionner au moins une option de suppression."
            )
    
    def action_cleanup(self):
        """Effectue le nettoyage selon les options sélectionnées."""
        self.ensure_one()
        
        # Vérifications de sécurité
        self._check_at_least_one_option()
        self._check_confirmation()
        
        deleted_counts = {
            'products': 0,
            'categories': 0,
            'moves': 0,
            'warehouses': 0,
            'locations': 0,
            'inventories': 0,
        }
        
        try:
            # 1. Supprimer les inventaires StockEx
            if self.delete_inventories:
                inventories = self.env['stockex.stock.inventory'].search([])
                deleted_counts['inventories'] = len(inventories)
                inventories.unlink()
                _logger.info(f"✅ {deleted_counts['inventories']} inventaires supprimés")
            
            # 2. Supprimer les mouvements de stock
            if self.delete_stock_moves:
                # Supprimer les pickings d'abord
                pickings = self.env['stock.picking'].search([])
                pickings_count = len(pickings)
                pickings.unlink()
                
                # Puis les mouvements restants
                moves = self.env['stock.move'].search([])
                deleted_counts['moves'] = len(moves) + pickings_count
                moves.unlink()
                _logger.info(f"✅ {deleted_counts['moves']} mouvements supprimés")
            
            # 3. Supprimer les emplacements personnalisés
            if self.delete_locations:
                # Étape 3.1 : Supprimer d'abord les règles de stock liées
                _logger.info("🔍 Suppression des règles de stock...")
                stock_rules = self.env['stock.rule'].search([])
                rules_count = len(stock_rules)
                if stock_rules:
                    stock_rules.unlink()
                    _logger.info(f"✅ {rules_count} règles de stock supprimées")
                
                # Étape 3.3 : Supprimer les emplacements
                # Ne pas supprimer les emplacements système
                system_locations = [
                    'stock_location_stock',
                    'stock_location_customers',
                    'stock_location_suppliers',
                    'stock_location_locations',
                    'stock_location_company',
                ]
                
                locations = self.env['stock.location'].search([
                    ('usage', 'in', ['internal', 'view']),
                    ('complete_name', 'not ilike', 'Physical Locations'),
                ])
                
                # Filtrer pour garder les emplacements système
                locations_to_delete = locations.filtered(
                    lambda l: not any(sys_loc in (l.get_external_id().get(l.id) or '') 
                                    for sys_loc in system_locations)
                )
                
                deleted_counts['locations'] = len(locations_to_delete)
                if locations_to_delete:
                    locations_to_delete.unlink()
                    _logger.info(f"✅ {deleted_counts['locations']} emplacements supprimés")
            
            # 4. Supprimer les entrepôts personnalisés
            if self.delete_warehouses:
                # Étape 4.1 : Supprimer d'abord les règles de réapprovisionnement
                _logger.info("🔍 Suppression des règles de réapprovisionnement...")
                reorder_rules = self.env['stock.warehouse.orderpoint'].search([])
                reorder_count = len(reorder_rules)
                if reorder_rules:
                    reorder_rules.unlink()
                    _logger.info(f"✅ {reorder_count} règles de réapprovisionnement supprimées")
                
                # Étape 4.2 : Dé-référencer les routes des entrepôts avant suppression
                _logger.info("🔍 Dé-référencement des routes des entrepôts...")
                all_warehouses = self.env['stock.warehouse'].search([])
                for wh in all_warehouses:
                    wh.write({
                        'reception_route_id': False,
                        'delivery_route_id': False,
                        'crossdock_route_id': False,
                    })
                _logger.info(f"✅ Routes dé-référencées pour {len(all_warehouses)} entrepôts")
                
                # Étape 4.3 : Supprimer les règles de stock
                _logger.info("🔍 Suppression des règles de stock...")
                all_rules = self.env['stock.rule'].search([])
                if all_rules:
                    all_rules.unlink()
                    _logger.info(f"✅ {len(all_rules)} règles de stock supprimées")
                
                # Étape 4.4 : Supprimer les entrepôts (qui ne référencent plus de routes)
                _logger.info("🔍 Suppression des entrepôts...")
                warehouses = self.env['stock.warehouse'].search([
                    ('company_id', '=', self.env.company.id)
                ])
                
                if len(warehouses) > 1:
                    # Garder le premier (principal) et supprimer les autres
                    warehouses_to_delete = warehouses[1:]
                    deleted_counts['warehouses'] = len(warehouses_to_delete)
                    warehouses_to_delete.unlink()
                    _logger.info(f"✅ {deleted_counts['warehouses']} entrepôts supprimés")
                else:
                    _logger.info("ℹ️ Un seul entrepôt trouvé, conservation de l'entrepôt principal")
                
                # Étape 4.5 : Supprimer les routes maintenant qu'elles ne sont plus référencées
                _logger.info("🔍 Suppression des routes...")
                all_routes = self.env['stock.route'].search([])
                if all_routes:
                    routes_count = len(all_routes)
                    all_routes.unlink()
                    _logger.info(f"✅ {routes_count} routes supprimées")
            
            # 5. Supprimer les produits
            if self.delete_products:
                # Ne supprimer que les produits sans mouvement validé
                products = self.env['product.product'].search([])
                products_to_delete = products.filtered(
                    lambda p: not p.stock_move_ids.filtered(lambda m: m.state == 'done')
                )
                
                deleted_counts['products'] = len(products_to_delete)
                products_to_delete.unlink()
                _logger.info(f"✅ {deleted_counts['products']} produits supprimés")
            
            # 6. Supprimer les catégories
            if self.delete_categories:
                # Garder la catégorie "All" par défaut
                default_category = self.env.ref('product.product_category_all', raise_if_not_found=False)
                
                categories = self.env['product.category'].search([])
                if default_category:
                    categories = categories - default_category
                
                # Ne supprimer que les catégories sans produits
                categories_to_delete = categories.filtered(lambda c: not c.product_count)
                
                deleted_counts['categories'] = len(categories_to_delete)
                categories_to_delete.unlink()
                _logger.info(f"✅ {deleted_counts['categories']} catégories supprimées")
            
            # Message de succès
            message = self._build_success_message(deleted_counts)
            
            # Envoyer les notifications
            self._send_telegram_notification(deleted_counts)
            self._send_email_notification(deleted_counts)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '✅ Nettoyage Terminé',
                    'message': message,
                    'type': 'success',
                    'sticky': True,
                }
            }
            
        except Exception as e:
            _logger.error(f"❌ Erreur lors du nettoyage: {str(e)}")
            raise UserError(
                f"❌ Erreur lors du nettoyage\n\n"
                f"Une erreur s'est produite : {str(e)}\n\n"
                f"Certaines données peuvent avoir été supprimées partiellement."
            )
    
    def _build_success_message(self, counts):
        """Construit le message de succès avec les statistiques."""
        messages = []
        
        if counts['inventories'] > 0:
            messages.append(f"📋 {counts['inventories']} inventaires")
        if counts['moves'] > 0:
            messages.append(f"📦 {counts['moves']} mouvements")
        if counts['locations'] > 0:
            messages.append(f"📍 {counts['locations']} emplacements")
        if counts['warehouses'] > 0:
            messages.append(f"🏭 {counts['warehouses']} entrepôts")
        if counts['products'] > 0:
            messages.append(f"🏷️ {counts['products']} produits")
        if counts['categories'] > 0:
            messages.append(f"📁 {counts['categories']} catégories")
        
        if messages:
            return "Éléments supprimés :\n• " + "\n• ".join(messages)
        else:
            return "Aucun élément supprimé"
    
    def _send_telegram_notification(self, counts):
        """Envoie une notification Telegram après le nettoyage."""
        ICP = self.env['ir.config_parameter'].sudo()
        
        # Vérifier si les notifications Telegram sont activées
        notify_telegram = ICP.get_param('stockex.notify_by_telegram', default=False)
        if not notify_telegram or notify_telegram == 'False':
            return
        
        bot_token = ICP.get_param('stockex.telegram_bot_token')
        chat_ids = ICP.get_param('stockex.telegram_chat_ids')
        
        if not bot_token or not chat_ids:
            _logger.warning("⚠️ Notifications Telegram activées mais token/chat_ids manquants")
            return
        
        # Construire le message
        user_name = self.env.user.name
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
        message = f"""
🚨 *ALERTE - RÉINITIALISATION DES DONNÉES* 🚨

⚠️ *Action Critique Effectuée*

👤 *Administrateur* : {user_name}
🕐 *Date/Heure* : {timestamp}
🏢 *Société* : {self.env.company.name}

📊 *DONNÉES SUPPRIMÉES :*
"""
        
        if counts['inventories'] > 0:
            message += f"\n• 📋 *{counts['inventories']}* inventaires StockEx"
        if counts['moves'] > 0:
            message += f"\n• 📦 *{counts['moves']}* mouvements de stock"
        if counts['locations'] > 0:
            message += f"\n• 📍 *{counts['locations']}* emplacements"
        if counts['warehouses'] > 0:
            message += f"\n• 🏭 *{counts['warehouses']}* entrepôts"
        if counts['products'] > 0:
            message += f"\n• 🏷️ *{counts['products']}* produits"
        if counts['categories'] > 0:
            message += f"\n• 📁 *{counts['categories']}* catégories"
        
        total = sum(counts.values())
        message += f"\n\n*TOTAL : {total} éléments supprimés*"
        message += f"\n\n⚠️ _Cette action est IRRÉVERSIBLE_"
        
        # Envoyer à chaque chat_id
        for chat_id in chat_ids.split(','):
            chat_id = chat_id.strip()
            if not chat_id:
                continue
            
            try:
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                payload = {
                    'chat_id': chat_id,
                    'text': message,
                    'parse_mode': 'Markdown'
                }
                response = requests.post(url, json=payload, timeout=10)
                
                if response.status_code == 200:
                    _logger.info(f"✅ Notification Telegram envoyée au chat {chat_id}")
                else:
                    _logger.warning(f"⚠️ Échec notification Telegram: {response.text}")
            except Exception as e:
                _logger.error(f"❌ Erreur envoi Telegram: {str(e)}")
    
    def _send_email_notification(self, counts):
        """Envoie une notification email aux administrateurs."""
        try:
            # Récupérer tous les administrateurs
            admin_group = self.env.ref('base.group_system')
            admin_users = admin_group.users
            
            if not admin_users:
                _logger.warning("⚠️ Aucun administrateur trouvé pour l'envoi d'email")
                return
            
            # Construire le message
            user_name = self.env.user.name
            timestamp = datetime.now().strftime('%d/%m/%Y à %H:%M:%S')
            
            # Corps de l'email HTML
            body_html = f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); 
                                color: white; padding: 30px; border-radius: 10px 10px 0 0;">
                        <h1 style="margin: 0; font-size: 24px;">
                            🚨 ALERTE - RÉINITIALISATION DES DONNÉES
                        </h1>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
                        <div style="background: white; padding: 20px; border-radius: 8px; 
                                    border-left: 4px solid #dc3545; margin-bottom: 20px;">
                            <h3 style="color: #dc3545; margin-top: 0;">⚠️ Action Critique Effectuée</h3>
                            <p><strong>Administrateur :</strong> {user_name}</p>
                            <p><strong>Date/Heure :</strong> {timestamp}</p>
                            <p><strong>Société :</strong> {self.env.company.name}</p>
                        </div>
                        
                        <div style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                            <h3 style="color: #495057; margin-top: 0;">📊 Données Supprimées</h3>
                            <ul style="list-style: none; padding: 0;">
            """
            
            if counts['inventories'] > 0:
                body_html += f'<li style="padding: 8px 0; border-bottom: 1px solid #dee2e6;">📋 <strong>{counts["inventories"]}</strong> inventaires StockEx</li>'
            if counts['moves'] > 0:
                body_html += f'<li style="padding: 8px 0; border-bottom: 1px solid #dee2e6;">📦 <strong>{counts["moves"]}</strong> mouvements de stock</li>'
            if counts['locations'] > 0:
                body_html += f'<li style="padding: 8px 0; border-bottom: 1px solid #dee2e6;">📍 <strong>{counts["locations"]}</strong> emplacements</li>'
            if counts['warehouses'] > 0:
                body_html += f'<li style="padding: 8px 0; border-bottom: 1px solid #dee2e6;">🏭 <strong>{counts["warehouses"]}</strong> entrepôts</li>'
            if counts['products'] > 0:
                body_html += f'<li style="padding: 8px 0; border-bottom: 1px solid #dee2e6;">🏷️ <strong>{counts["products"]}</strong> produits</li>'
            if counts['categories'] > 0:
                body_html += f'<li style="padding: 8px 0; border-bottom: 1px solid #dee2e6;">📁 <strong>{counts["categories"]}</strong> catégories</li>'
            
            total = sum(counts.values())
            body_html += f"""
                            </ul>
                            <div style="background: #dc3545; color: white; padding: 15px; 
                                        border-radius: 5px; margin-top: 20px; text-align: center;">
                                <h2 style="margin: 0;">TOTAL : {total} éléments supprimés</h2>
                            </div>
                        </div>
                        
                        <div style="background: #fff3cd; border: 1px solid #ffc107; 
                                    padding: 15px; border-radius: 8px; color: #856404;">
                            <strong>⚠️ Avertissement :</strong> Cette action est IRRÉVERSIBLE. 
                            Les données supprimées ne peuvent pas être récupérées.
                        </div>
                        
                        <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #dee2e6; 
                                    font-size: 12px; color: #6c757d; text-align: center;">
                            <p>Cet email a été envoyé automatiquement par le système StockEx</p>
                            <p>{self.env.company.name} - {timestamp}</p>
                        </div>
                    </div>
                </div>
            """
            
            # Envoyer l'email
            mail_values = {
                'subject': f'🚨 ALERTE - Réinitialisation des données par {user_name}',
                'body_html': body_html,
                'email_to': ','.join([user.email for user in admin_users if user.email]),
                'email_from': self.env.user.email or self.env.company.email,
                'auto_delete': False,
            }
            
            mail = self.env['mail.mail'].sudo().create(mail_values)
            mail.send()
            
            _logger.info(f"✅ Email de notification envoyé à {len(admin_users)} administrateur(s)")
            
        except Exception as e:
            _logger.error(f"❌ Erreur envoi email: {str(e)}")
    
    def action_cancel(self):
        """Annule le wizard."""
        return {'type': 'ir.actions.act_window_close'}
