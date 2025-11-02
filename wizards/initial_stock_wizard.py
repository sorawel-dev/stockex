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
        comodel_name='stock.warehouse',
        string='Entrepôt par Défaut',
        required=False,
        help='Entrepôt par défaut si non spécifié dans le fichier Excel. Si le fichier contient une colonne ENTREPOT, elle sera prioritaire.'
    )
    
    create_warehouses = fields.Boolean(
        string='Créer les Entrepôts Manquants',
        default=True,
        help='Si coché, crée automatiquement les entrepôts non trouvés'
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
    
    create_categories = fields.Boolean(
        string='Créer les Catégories Manquantes',
        default=True,
        help='Si coché, crée automatiquement les catégories de produits non trouvées'
    )
    
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Société',
        default=lambda self: self.env.company,
        required=True
    )
    
    force_reset = fields.Boolean(
        string='⚠️ Réinitialiser tous les stocks',
        default=False,
        help='ATTENTION : Supprime TOUS les mouvements de stock et remet toutes les quantités à 0 avant l\'import. '
             'Cette action est IRRÉVERSIBLE. À utiliser uniquement pour une réinitialisation complète de la base.'
    )
    
    # Champs pour la prévisualisation
    state = fields.Selection([
        ('step1', 'Import'),
        ('step2', 'Prévisualisation'),
    ], string='Étape', default='step1')
    
    preview_data = fields.Text(string='Données de prévisualisation', readonly=True)
    preview_summary = fields.Html(string='Résumé', readonly=True)
    lines_count = fields.Integer(string='Nombre de lignes', readonly=True)
    warehouses_preview = fields.Char(string='Entrepôts détectés', readonly=True)
    categories_preview = fields.Char(string='Catégories détectées', readonly=True)
    
    # Champ de progression
    progress = fields.Float(string='Progression', readonly=True, default=0.0)
    progress_message = fields.Char(string='Message de progression', readonly=True)
    
    def action_preview(self):
        """Prévisualiser les données avant import."""
        self.ensure_one()
        
        if not self.import_file:
            raise UserError("⚠️ Veuillez sélectionner un fichier Excel.")
        
        # Parser le fichier
        lines = self._parse_excel_file()
        
        if not lines:
            raise UserError("⚠️ Le fichier Excel ne contient aucune donnée.")
        
        # Analyser les données
        warehouses = set()
        categories = set()
        products_count = 0
        total_quantity = 0
        total_cost = 0
        
        for line_data in lines:
            product_code = str(line_data.get('CODE PRODUIT', '')).strip()
            if product_code:
                products_count += 1
                
            warehouse_name = str(line_data.get('ENTREPOT', '') or line_data.get('EMPLACEMENT', '')).strip()
            if warehouse_name:
                warehouses.add(warehouse_name)
            
            category_name = str(line_data.get('CATEGORIE', '')).strip()
            if category_name:
                categories.add(category_name)
            
            quantity = float(line_data.get('QUANTITE', 0))
            price = float(line_data.get('PRIX UNITAIRE', 0))
            total_quantity += quantity
            total_cost += quantity * price
        
        # Générer le résumé HTML
        summary_html = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 900px; margin: 0 auto;">
            <!-- En-tête -->
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 12px 12px 0 0; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h2 style="margin: 0 0 10px 0; font-size: 28px; font-weight: 600;">
                    <span style="font-size: 32px; margin-right: 10px;">📊</span>
                    Prévisualisation de l'Import
                </h2>
                <p style="margin: 0; font-size: 14px; opacity: 0.9;">Vérifiez les données avant de créer l'inventaire</p>
            </div>
            
            <!-- Statistiques principales -->
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; padding: 30px; background: #f8f9fa;">
                <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-left: 4px solid #667eea;">
                    <div style="font-size: 32px; color: #667eea; margin-bottom: 8px;">📄</div>
                    <div style="font-size: 28px; font-weight: bold; color: #2d3748; margin-bottom: 4px;">{len(lines):,}</div>
                    <div style="font-size: 11px; color: #718096; text-transform: uppercase; letter-spacing: 0.5px;">Lignes totales</div>
                </div>
                
                <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-left: 4px solid #48bb78;">
                    <div style="font-size: 32px; color: #48bb78; margin-bottom: 8px;">📦</div>
                    <div style="font-size: 28px; font-weight: bold; color: #2d3748; margin-bottom: 4px;">{products_count:,}</div>
                    <div style="font-size: 11px; color: #718096; text-transform: uppercase; letter-spacing: 0.5px;">Produits distincts</div>
                </div>
                
                <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-left: 4px solid #ed8936;">
                    <div style="font-size: 32px; color: #ed8936; margin-bottom: 8px;">📊</div>
                    <div style="font-size: 28px; font-weight: bold; color: #2d3748; margin-bottom: 4px;">{total_quantity:,.0f}</div>
                    <div style="font-size: 11px; color: #718096; text-transform: uppercase; letter-spacing: 0.5px;">Quantité totale</div>
                </div>
                
                <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-left: 4px solid #9f7aea;">
                    <div style="font-size: 32px; color: #9f7aea; margin-bottom: 8px;">💰</div>
                    <div style="font-size: 24px; font-weight: bold; color: #2d3748; margin-bottom: 4px;">{total_cost:,.0f}</div>
                    <div style="font-size: 11px; color: #718096; text-transform: uppercase; letter-spacing: 0.5px;">Coût total (FCFA)</div>
                </div>
            </div>
            
            <!-- Détails des entrepôts et catégories -->
            <div style="padding: 0 30px 30px 30px; background: #f8f9fa;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <!-- Entrepôts -->
                    <div style="background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                        <div style="display: flex; align-items: center; margin-bottom: 15px;">
                            <span style="font-size: 24px; margin-right: 10px;">🏭</span>
                            <div>
                                <div style="font-size: 18px; font-weight: 600; color: #2d3748;">Entrepôts</div>
                                <div style="font-size: 24px; font-weight: bold; color: #667eea;">{len(warehouses)}</div>
                            </div>
                        </div>
                        <div style="max-height: 200px; overflow-y: auto;">
                            {''.join([f'<div style="padding: 8px 12px; margin: 5px 0; background: #f7fafc; border-radius: 6px; font-size: 13px; color: #4a5568; border-left: 3px solid #667eea;">{wh}</div>' for wh in list(warehouses)[:10]])}
                            {f'<div style="padding: 8px; text-align: center; color: #a0aec0; font-size: 12px; font-style: italic;">... et {len(warehouses) - 10} autre(s)</div>' if len(warehouses) > 10 else ''}
                        </div>
                    </div>
                    
                    <!-- Catégories -->
                    <div style="background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                        <div style="display: flex; align-items: center; margin-bottom: 15px;">
                            <span style="font-size: 24px; margin-right: 10px;">📁</span>
                            <div>
                                <div style="font-size: 18px; font-weight: 600; color: #2d3748;">Catégories</div>
                                <div style="font-size: 24px; font-weight: bold; color: #48bb78;">{len(categories)}</div>
                            </div>
                        </div>
                        <div style="max-height: 200px; overflow-y: auto;">
                            {''.join([f'<div style="padding: 8px 12px; margin: 5px 0; background: #f0fff4; border-radius: 6px; font-size: 13px; color: #4a5568; border-left: 3px solid #48bb78;">{cat}</div>' for cat in list(categories)[:10]])}
                            {f'<div style="padding: 8px; text-align: center; color: #a0aec0; font-size: 12px; font-style: italic;">... et {len(categories) - 10} autre(s)</div>' if len(categories) > 10 else ''}
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Aperçu des premières lignes -->
            <div style="padding: 0 30px 30px 30px; background: #f8f9fa;">
                <div style="background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                    <div style="display: flex; align-items: center; margin-bottom: 20px;">
                        <span style="font-size: 24px; margin-right: 10px;">👁️</span>
                        <div style="font-size: 18px; font-weight: 600; color: #2d3748;">Aperçu des 5 premières lignes</div>
                    </div>
                    <div style="overflow-x: auto;">
                        <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                            <thead>
                                <tr style="background: #f7fafc; border-bottom: 2px solid #e2e8f0;">
                                    <th style="padding: 12px; text-align: left; font-weight: 600; color: #4a5568;">#</th>
                                    <th style="padding: 12px; text-align: left; font-weight: 600; color: #4a5568;">Code</th>
                                    <th style="padding: 12px; text-align: left; font-weight: 600; color: #4a5568;">Produit</th>
                                    <th style="padding: 12px; text-align: left; font-weight: 600; color: #4a5568;">Entrepôt</th>
                                    <th style="padding: 12px; text-align: right; font-weight: 600; color: #4a5568;">Quantité</th>
                                    <th style="padding: 12px; text-align: right; font-weight: 600; color: #4a5568;">Prix U.</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join([f'''<tr style="border-bottom: 1px solid #f7fafc;">
                                    <td style="padding: 10px; color: #a0aec0;">{idx + 1}</td>
                                    <td style="padding: 10px; color: #2d3748; font-family: monospace; font-size: 12px;">{str(line.get('CODE PRODUIT', ''))[:15]}</td>
                                    <td style="padding: 10px; color: #4a5568;">{str(line.get('PRODUIT', '') or line.get('NOM PRODUIT', ''))[:30]}</td>
                                    <td style="padding: 10px;">
                                        <span style="background: #edf2f7; padding: 4px 8px; border-radius: 4px; font-size: 11px; color: #667eea;">{str(line.get('ENTREPOT', '') or line.get('EMPLACEMENT', ''))[:20]}</span>
                                    </td>
                                    <td style="padding: 10px; text-align: right; font-weight: 500; color: #2d3748;">{float(line.get('QUANTITE', 0)):,.0f}</td>
                                    <td style="padding: 10px; text-align: right; font-weight: 500; color: #2d3748;">{float(line.get('PRIX UNITAIRE', 0)):,.0f}</td>
                                </tr>''' for idx, line in enumerate(lines[:5])])}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- Message d'information -->
            <div style="padding: 0 30px 30px 30px; background: #f8f9fa; border-radius: 0 0 12px 12px;">
                <div style="background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); padding: 20px; border-radius: 10px; border: 2px solid #667eea30;">
                    <div style="display: flex; align-items: start;">
                        <span style="font-size: 24px; margin-right: 15px;">ℹ️</span>
                        <div>
                            <div style="font-weight: 600; color: #2d3748; margin-bottom: 5px;">Prêt à importer</div>
                            <div style="color: #4a5568; font-size: 14px; line-height: 1.6;">
                                Les données ci-dessus sont une prévisualisation de votre fichier Excel.<br/>
                                Cliquez sur <strong>"✅ Confirmer l'import"</strong> pour créer l'inventaire initial avec ces données.
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
        
        # Mettre à jour les champs de prévisualisation
        self.write({
            'state': 'step2',
            'preview_summary': summary_html,
            'lines_count': len(lines),
            'warehouses_preview': ', '.join(list(warehouses)[:5]),
            'categories_preview': ', '.join(list(categories)[:5]),
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stockex.initial.stock.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
    
    def action_back(self):
        """Retour à l'étape 1."""
        self.write({'state': 'step1'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stockex.initial.stock.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
    
    def _send_email_notification(self, inventory, created_count):
        """Envoie une notification par email depuis les paramètres globaux."""
        # Récupérer les paramètres depuis la configuration
        ICP = self.env['ir.config_parameter'].sudo()
        notify_email = ICP.get_param('stockex.notify_by_email', 'False') == 'True'
        email_list = ICP.get_param('stockex.notification_emails', '')
        
        if not notify_email or not email_list:
            return
        
        emails = [email.strip() for email in email_list.split(',') if email.strip()]
        if not emails:
            return
        
        subject = f"✅ Import Stock Initial Réussi - {inventory.name}"
        
        body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center;">
                <h1 style="margin: 0; font-size: 28px;">✅ Import Réussi</h1>
            </div>
            
            <div style="padding: 30px; background: #f8f9fa;">
                <div style="background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                    <h2 style="color: #2d3748; margin-top: 0;">Inventaire Initial Créé</h2>
                    
                    <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                        <tr>
                            <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #4a5568;">Nom:</td>
                            <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; color: #2d3748;">{inventory.name}</td>
                        </tr>
                        <tr>
                            <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #4a5568;">Date:</td>
                            <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; color: #2d3748;">{inventory.date}</td>
                        </tr>
                        <tr>
                            <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #4a5568;">Lignes importées:</td>
                            <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; color: #48bb78; font-weight: bold;">{created_count}</td>
                        </tr>
                        <tr>
                            <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #4a5568;">Emplacement:</td>
                            <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; color: #2d3748;">{inventory.location_id.complete_name}</td>
                        </tr>
                        {"<tr><td style='padding: 12px; font-weight: bold; color: #e53e3e;'>⚠️ Réinitialisation:</td><td style='padding: 12px; color: #e53e3e;'>Stocks réinitialisés avant import</td></tr>" if self.force_reset else ""}
                    </table>
                    
                    <div style="background: #edf2f7; padding: 15px; border-radius: 8px; margin-top: 20px;">
                        <p style="margin: 0; color: #4a5568; font-size: 14px;">
                            <strong>📊 Prochaine étape :</strong> Consultez et validez l'inventaire dans Odoo.
                        </p>
                    </div>
                </div>
            </div>
            
            <div style="padding: 20px; text-align: center; color: #a0aec0; font-size: 12px;">
                <p>Notification automatique envoyée par Stockex - Odoo</p>
            </div>
        </div>
        """
        
        try:
            # Créer l'email
            mail_values = {
                'subject': subject,
                'body_html': body,
                'email_to': ', '.join(emails),
                'email_from': self.env.user.company_id.email or 'noreply@odoo.com',
                'auto_delete': False,
            }
            
            mail = self.env['mail.mail'].sudo().create(mail_values)
            mail.send()
            
            _logger.info(f"📧 Email envoyé à : {', '.join(emails)}")
            
        except Exception as e:
            _logger.error(f"❌ Erreur envoi email : {str(e)}")
    
    def _send_whatsapp_notification(self, inventory, created_count):
        """Envoie une notification WhatsApp depuis les paramètres globaux."""
        # Récupérer les paramètres depuis la configuration
        ICP = self.env['ir.config_parameter'].sudo()
        notify_whatsapp = ICP.get_param('stockex.notify_by_whatsapp', 'False') == 'True'
        numbers_list = ICP.get_param('stockex.whatsapp_numbers', '')
        api_url = ICP.get_param('stockex.whatsapp_api_url', '')
        api_token = ICP.get_param('stockex.whatsapp_api_token', '')
        
        if not notify_whatsapp or not numbers_list:
            return
        
        if not api_url:
            _logger.warning("⚠️ URL API WhatsApp non configurée dans les Paramètres")
            return
        
        numbers = [num.strip() for num in numbers_list.split(',') if num.strip()]
        if not numbers:
            return
        
        message = f"""✅ *Import Stock Initial Réussi*

📦 *Inventaire:* {inventory.name}
📅 *Date:* {inventory.date}
📊 *Lignes importées:* {created_count}
📍 *Emplacement:* {inventory.location_id.complete_name}
"""
        
        if self.force_reset:
            message += "\n⚠️ *Stocks réinitialisés* avant import"
        
        message += "\n\n_Notification automatique Stockex - Odoo_"
        
        try:
            import requests
            
            headers = {}
            if api_token:
                headers['Authorization'] = f'Bearer {api_token}'
            
            for number in numbers:
                try:
                    # Format générique pour API WhatsApp
                    # Adapter selon votre provider (Twilio, WhatsApp Business API, etc.)
                    payload = {
                        'to': number,
                        'message': message
                    }
                    
                    response = requests.post(
                        api_url,
                        json=payload,
                        headers=headers,
                        timeout=10
                    )
                    
                    if response.status_code in [200, 201]:
                        _logger.info(f"💬 WhatsApp envoyé à : {number}")
                    else:
                        _logger.error(f"❌ Erreur WhatsApp pour {number} : {response.status_code}")
                        
                except Exception as num_error:
                    _logger.error(f"❌ Erreur envoi WhatsApp à {number} : {str(num_error)}")
                    
        except ImportError:
            _logger.error("❌ Module 'requests' non installé. Installez-le : pip install requests")
        except Exception as e:
            _logger.error(f"❌ Erreur envoi WhatsApp : {str(e)}")
    
    def _send_telegram_notification(self, inventory, created_count):
        """Envoie une notification Telegram depuis les paramètres globaux."""
        # Récupérer les paramètres depuis la configuration
        ICP = self.env['ir.config_parameter'].sudo()
        notify_telegram = ICP.get_param('stockex.notify_by_telegram', 'False') == 'True'
        bot_token = ICP.get_param('stockex.telegram_bot_token', '')
        chat_ids_list = ICP.get_param('stockex.telegram_chat_ids', '')
        
        if not notify_telegram or not bot_token or not chat_ids_list:
            return
        
        chat_ids = [chat_id.strip() for chat_id in chat_ids_list.split(',') if chat_id.strip()]
        if not chat_ids:
            return
        
        # Message formaté pour Telegram (support Markdown)
        message = f"""✅ *Import Stock Initial Réussi*

📦 *Inventaire :* {inventory.name}
📅 *Date :* {inventory.date}
📊 *Lignes importées :* {created_count}
📍 *Emplacement :* {inventory.location_id.complete_name}
"""
        
        if self.force_reset:
            message += "\n⚠️ *Stocks réinitialisés* avant import"
        
        message += "\n\n_Notification automatique Stockex - Odoo_"
        
        try:
            import requests
            
            # URL de l'API Telegram
            api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            
            for chat_id in chat_ids:
                try:
                    payload = {
                        'chat_id': chat_id,
                        'text': message,
                        'parse_mode': 'Markdown'
                    }
                    
                    response = requests.post(
                        api_url,
                        json=payload,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        _logger.info(f"📱 Telegram envoyé à Chat ID : {chat_id}")
                    else:
                        _logger.error(f"❌ Erreur Telegram pour Chat ID {chat_id} : {response.status_code} - {response.text}")
                        
                except Exception as chat_error:
                    _logger.error(f"❌ Erreur envoi Telegram à Chat ID {chat_id} : {str(chat_error)}")
                    
        except ImportError:
            _logger.error("❌ Module 'requests' non installé. Installez-le : pip install requests")
        except Exception as e:
            _logger.error(f"❌ Erreur envoi Telegram : {str(e)}")
    
    def _reset_all_stocks(self):
        """Réinitialise complètement tous les stocks (DANGEREUX !)."""
        self.ensure_one()
        
        _logger.warning("🔥 RÉINITIALISATION COMPLÈTE DES STOCKS DEMANDÉE")
        
        # 1. Supprimer tous les mouvements de stock
        stock_moves = self.env['stock.move'].search([
            ('company_id', '=', self.company_id.id)
        ])
        moves_count = len(stock_moves)
        _logger.warning(f"🗑️ Suppression de {moves_count} mouvements de stock...")
        
        # Supprimer les mouvements en lot pour éviter les timeouts
        batch_size = 500
        for i in range(0, moves_count, batch_size):
            batch = stock_moves[i:i+batch_size]
            try:
                # Forcer la suppression même si done
                batch.sudo().write({'state': 'draft'})
                batch.sudo().unlink()
                self.env.cr.commit()
            except Exception as e:
                _logger.error(f"❌ Erreur suppression mouvements batch {i}: {str(e)}")
        
        # 2. Supprimer tous les quants (quantités en stock)
        stock_quants = self.env['stock.quant'].search([
            ('company_id', '=', self.company_id.id)
        ])
        quants_count = len(stock_quants)
        _logger.warning(f"🗑️ Suppression de {quants_count} quants...")
        
        # Suppression en lot
        for i in range(0, quants_count, batch_size):
            batch = stock_quants[i:i+batch_size]
            try:
                batch.sudo().unlink()
                self.env.cr.commit()
            except Exception as e:
                _logger.error(f"❌ Erreur suppression quants batch {i}: {str(e)}")
        
        # 3. Supprimer toutes les lignes de stock à zéro ou négatives restantes
        remaining_quants = self.env['stock.quant'].search([
            ('company_id', '=', self.company_id.id)
        ])
        if remaining_quants:
            _logger.warning(f"🗑️ Suppression de {len(remaining_quants)} quants restants...")
            remaining_quants.sudo().unlink()
            self.env.cr.commit()
        
        _logger.warning(f"✅ Réinitialisation terminée: {moves_count} mouvements + {quants_count} quants supprimés")
        
        return {
            'moves_deleted': moves_count,
            'quants_deleted': quants_count
        }
    
    def action_create_initial_stock(self):
        """Crée l'inventaire initial et met à jour les stocks."""
        self.ensure_one()
        
        # Si réinitialisation forcée demandée
        if self.force_reset:
            # Confirmation supplémentaire
            existing_quants = self.env['stock.quant'].search([
                ('company_id', '=', self.company_id.id),
            ])
            existing_moves = self.env['stock.move'].search([
                ('company_id', '=', self.company_id.id),
            ])
            
            if existing_quants or existing_moves:
                _logger.warning(
                    f"⚠️ RÉINITIALISATION FORCÉE : "
                    f"{len(existing_quants)} quants et {len(existing_moves)} mouvements seront supprimés"
                )
                
                # Effectuer la réinitialisation
                reset_result = self._reset_all_stocks()
                
                # Loguer le résultat de la réinitialisation
                _logger.warning(
                    f"✅ Réinitialisation terminée : "
                    f"{reset_result['moves_deleted']} mouvements et "
                    f"{reset_result['quants_deleted']} quants supprimés"
                )
        else:
            # Vérifier qu'il n'y a pas déjà de stock (comportement par défaut)
            existing_quants = self.env['stock.quant'].search([
                ('quantity', '>', 0),
                ('location_id.usage', '=', 'internal'),
                ('company_id', '=', self.company_id.id),
            ])
            
            if existing_quants:
                raise UserError(
                    f"⚠️ ATTENTION : {len(existing_quants)} mouvement(s) de stock déjà enregistré(s).\n\n"
                    f"Cette fonction est destinée aux bases de données VIDES.\n\n"
                    f"Options :\n"
                    f"1. Utilisez un inventaire normal pour mettre à jour le stock existant\n"
                    f"2. Cochez l'option '⚠️ Réinitialiser tous les stocks' pour forcer une réinitialisation complète (DANGEREUX)"
                )
        
        # Générer un nom unique pour l'inventaire
        inventory_name = self.name
        counter = 1
        while self.env['stockex.stock.inventory'].search([
            ('name', '=', inventory_name),
            ('company_id', '=', self.company_id.id)
        ], limit=1):
            inventory_name = f"{self.name} ({counter})"
            counter += 1
        
        # Créer l'inventaire initial (sans entrepôt fixe)
        # L'entrepôt sera déterminé ligne par ligne depuis le fichier Excel
        default_warehouse = self.location_id if self.location_id else self.env['stock.warehouse'].search([], limit=1)
        default_location = default_warehouse.lot_stock_id if default_warehouse else self.env.ref('stock.stock_location_stock')
        
        inventory = self.env['stockex.stock.inventory'].create({
            'name': inventory_name,
            'date': self.date,
            'location_id': default_location.id,
            'company_id': self.company_id.id,
            'state': 'draft',
            'description': 'Inventaire initial - Import multi-entrepôts depuis fichier Excel'
        })
        
        # Si fichier Excel fourni, l'importer
        created_count = 0
        if self.import_file:
            lines = self._parse_excel_file()
            created_count = self._create_inventory_lines(inventory, lines)
            
            # Si aucune ligne créée, supprimer l'inventaire et afficher un message d'erreur
            if created_count == 0:
                inventory.unlink()
                raise UserError(
                    "⚠️ Aucune ligne n'a pu être créée.\n\n"
                    "Vérifiez que votre fichier Excel contient des données valides.\n"
                    "Consultez les logs Odoo pour plus de détails."
                )
        
        # Message de succès dans le chatter
        message = f"✅ Inventaire initial créé avec succès !\n\n"
        if self.import_file:
            message += f"• {created_count} ligne(s) importée(s)\n"
        if self.force_reset:
            message += f"• Stocks préalablement réinitialisés\n"
        message += f"• Nom : {inventory.name}\n"
        message += f"• Date : {inventory.date}\n"
        
        # Poster le message dans le chatter de l'inventaire
        inventory.message_post(
            body=message,
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )
        
        # Envoyer les notifications
        try:
            self._send_email_notification(inventory, created_count)
            self._send_whatsapp_notification(inventory, created_count)
            self._send_telegram_notification(inventory, created_count)
        except Exception as notif_error:
            _logger.error(f"❌ Erreur lors de l'envoi des notifications : {str(notif_error)}")
            # Ne pas bloquer l'import si les notifications échouent
        
        # Retourner l'action d'ouverture de l'inventaire
        return {
            'type': 'ir.actions.act_window',
            'name': 'Inventaire Initial Créé',
            'res_model': 'stockex.stock.inventory',
            'res_id': inventory.id,
            'view_mode': 'form',
            'target': 'current',
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
        _logger.info(f"📄 En-têtes Excel: {headers}")
        
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
        _logger.info(f"📄 {len(lines)} lignes lues depuis Excel")
        _logger.info(f"📄 En-têtes détectés: {headers}")
        if len(lines) > 0:
            _logger.info(f"📄 Première ligne: {lines[0]}")
            _logger.info(f"📄 Clés disponibles: {list(lines[0].keys())}")
        else:
            _logger.warning("⚠️ Aucune ligne de données trouvée dans le fichier Excel")
        return lines
    
    def _get_or_create_warehouse(self, warehouse_name):
        """
Recherche ou crée un entrepôt.
        """
        if not warehouse_name:
            # Utiliser l'entrepôt par défaut du formulaire ou le premier
            return self.location_id if self.location_id else self.env['stock.warehouse'].search([], limit=1)
        
        warehouse_name = str(warehouse_name).strip()
        
        try:
            # Savepoint pour isoler cette opération
            savepoint_name = f"warehouse_{id(self)}_{hash(warehouse_name)}"
            self.env.cr.execute(f'SAVEPOINT "{savepoint_name}"')
            
            # Rechercher par nom
            warehouse = self.env['stock.warehouse'].search([
                ('name', '=', warehouse_name),
                ('company_id', 'in', [self.company_id.id, False])
            ], limit=1)
            
            # Si trouvé, libérer le savepoint et retourner
            if warehouse:
                self.env.cr.execute(f'RELEASE SAVEPOINT "{savepoint_name}"')
                return warehouse
            
            # Si pas trouvé et qu'on autorise la création
            if self.create_warehouses:
                # Créer un code unique pour l'entrepôt (utiliser plus de caractères)
                # Enlever les espaces et prendre jusqu'à 10 caractères
                code_base = warehouse_name.upper().replace(' ', '').replace('-', '')[:10]
                
                # Si le code est trop court, le compléter
                if len(code_base) < 3:
                    code_base = code_base.ljust(3, 'X')
                
                # Chercher un code disponible
                counter = 0
                test_code = code_base[:5]  # Commencer avec 5 caractères
                while True:
                    existing = self.env['stock.warehouse'].search([
                        ('code', '=', test_code),
                        ('company_id', '=', self.company_id.id)
                    ], limit=1)
                    
                    if not existing:
                        break
                    
                    counter += 1
                    # Utiliser plus de caractères du nom si disponible
                    if counter == 1 and len(code_base) > 5:
                        test_code = code_base[:min(10, len(code_base))]
                    else:
                        test_code = f"{code_base[:5]}{counter}"
                    
                    # Sécurité : max 1000 itérations
                    if counter > 1000:
                        _logger.error(f"❌ Impossible de générer un code unique pour '{warehouse_name}'")
                        self.env.cr.execute(f'ROLLBACK TO SAVEPOINT "{savepoint_name}"')
                        return None
                
                warehouse_vals = {
                    'name': warehouse_name,
                    'code': test_code,
                    'company_id': self.company_id.id,
                }
                
                warehouse = self.env['stock.warehouse'].create(warehouse_vals)
                _logger.info(f"✅ Entrepôt créé: {warehouse.name} (Code: {warehouse.code})")
            
            # Libérer le savepoint
            self.env.cr.execute(f'RELEASE SAVEPOINT "{savepoint_name}"')
            return warehouse
            
        except Exception as e:
            _logger.error(f"❌ Erreur lors de la gestion de l'entrepôt '{warehouse_name}': {str(e)}")
            # Rollback au savepoint uniquement
            try:
                self.env.cr.execute(f'ROLLBACK TO SAVEPOINT "{savepoint_name}"')
            except:
                pass
            return None
    
    def _get_or_create_category(self, category_name, category_code=None):
        """Recherche ou crée une catégorie de produit."""
        if not category_name:
            # Retourner la catégorie par défaut 'All'
            return self.env.ref('product.product_category_all', raise_if_not_found=False)
        
        category_name = str(category_name).strip()
        
        # Rechercher par nom d'abord
        category = self.env['product.category'].search([
            ('name', '=', category_name)
        ], limit=1)
        
        # Si pas trouvée et qu'on autorise la création
        if not category and self.create_categories:
            category_vals = {
                'name': category_name,
            }
            
            # Ajouter le code de catégorie si fourni
            if category_code:
                category_code = str(category_code).strip()
                if category_code:
                    # Vérifier si le code existe déjà
                    existing_with_code = self.env['product.category'].search([
                        ('property_account_income_categ_id', '=', category_code)
                    ], limit=1)
                    
                    if not existing_with_code:
                        # Stockage du code dans le champ de référence
                        category_vals['complete_name'] = f"[{category_code}] {category_name}"
            
            category = self.env['product.category'].create(category_vals)
            _logger.info(f"✅ Catégorie créée: {category.name} (Code: {category_code or 'N/A'})")
        
        return category
    
    def _create_inventory_lines(self, inventory, lines):
        """
Crée les lignes d'inventaire depuis les données Excel.
        """
        created_count = 0
        errors = []
        created_categories = set()
        created_warehouses = set()
        total_lines = len(lines)
        
        _logger.info(f"🔍 Début création lignes: {total_lines} lignes à traiter")
        
        for i, line_data in enumerate(lines):
            # Mettre à jour la progression tous les 50 lignes ou pour les 10 premières
            if i % 50 == 0 or i < 10:
                progress_percent = (i / total_lines) * 100
                self.write({
                    'progress': progress_percent,
                    'progress_message': f'Traitement ligne {i + 1}/{total_lines} ({progress_percent:.1f}%)'
                })
                self.env.cr.commit()  # Commit pour afficher la progression en temps réel
            
            try:
                product_code = str(line_data.get('CODE PRODUIT', '')).strip()
                product_name = str(line_data.get('PRODUIT', '') or line_data.get('NOM PRODUIT', '')).strip()
                category_name = str(line_data.get('CATEGORIE', '')).strip() if line_data.get('CATEGORIE') else None
                category_code = str(line_data.get('CODE CATEGORIE', '')).strip() if line_data.get('CODE CATEGORIE') else None
                warehouse_name = str(line_data.get('ENTREPOT', '') or line_data.get('EMPLACEMENT', '')).strip() if line_data.get('ENTREPOT') or line_data.get('EMPLACEMENT') else None
                quantity = float(line_data.get('QUANTITE', 0))
                price = float(line_data.get('PRIX UNITAIRE', 0))
                
                if i < 3:  # Log des 3 premières lignes
                    _logger.info(f"🔍 Ligne {i+1}: CODE={product_code}, NOM={product_name[:30]}, ENTREP={warehouse_name}, QTE={quantity}")
                
                if not product_code:
                    _logger.warning(f"⚠️ Ligne {i+2}: CODE PRODUIT vide, ignorée. Données: {line_data}")
                    errors.append(f"Ligne {i+2}: CODE PRODUIT vide")
                    continue
                
                # Gérer l'entrepôt
                warehouse = self._get_or_create_warehouse(warehouse_name)
                if not warehouse:
                    errors.append(f"Ligne {i+2}: Entrepôt '{warehouse_name}' non trouvé et création désactivée")
                    continue
                
                if warehouse and warehouse.name not in created_warehouses:
                    created_warehouses.add(warehouse.name)
                
                # Utiliser l'emplacement stock de l'entrepôt
                location = warehouse.lot_stock_id
                
                # Vérifier que l'emplacement est de type internal
                if not location or location.usage != 'internal':
                    _logger.error(f"❌ Ligne {i+2}: Emplacement '{location.name if location else 'None'}' n'est pas de type 'internal' (type: {location.usage if location else 'None'})")
                    errors.append(f"Ligne {i+2}: Emplacement invalide pour entrepôt '{warehouse.name}'")
                    continue
                
                # Rechercher ou créer le produit
                product = self.env['product.product'].search([
                    ('default_code', '=', product_code)
                ], limit=1)
                
                # Gérer la catégorie (pour produits nouveaux ET existants)
                category = None
                if category_name:
                    category = self._get_or_create_category(category_name, category_code)
                    if category:
                        if category.name not in created_categories:
                            created_categories.add(category.name)
                        if i < 3:  # Log des 3 premières
                            _logger.info(f"📁 Catégorie gérée: {category.name} (ID: {category.id})")
                
                if not product:
                    if not self.create_products:
                        errors.append(f"Ligne {i+2}: Produit '{product_code}' non trouvé et création désactivée")
                        continue
                    
                    # Créer le nouveau produit
                    product_vals = {
                        'name': product_name or product_code,
                        'default_code': product_code,
                        'type': 'consu',  # Biens/Goods stockables
                        'is_storable': True,  # Activer le suivi d'inventaire
                        'standard_price': price,
                    }
                    
                    # Ajouter la catégorie si disponible
                    if category:
                        product_vals['categ_id'] = category.id
                    
                    product = self.env['product.product'].create(product_vals)
                    if i < 3:
                        _logger.info(f"✅ Produit créé: {product_code} ({product.name}) - Catégorie: {category.name if category else 'Par défaut'}")
                
                elif category:
                    # Mettre à jour la catégorie du produit existant si spécifiée
                    if product.categ_id.id != category.id:
                        product.write({'categ_id': category.id})
                        if i < 3:
                            _logger.info(f"🔄 Catégorie mise à jour: {product_code} → {category.name}")
                
                if product:
                    # Créer la ligne d'inventaire avec l'emplacement du fichier
                    try:
                        line_vals = {
                            'inventory_id': inventory.id,
                            'product_id': product.id,
                            'location_id': location.id,
                            'product_qty': quantity,
                            'standard_price': price,
                            'theoretical_qty': 0.0,  # STOCK INITIAL : forcer à 0
                        }
                        
                        # Log détaillé pour les 3 premières lignes
                        if i < 3:
                            _logger.info(
                                f"📝 Création ligne {i+1}: "
                                f"Produit={product.display_name}, "
                                f"Catégorie={product.categ_id.name}, "
                                f"Emplacement={location.complete_name} (usage={location.usage}), "
                                f"Quantité={quantity}, "
                                f"Prix={price}"
                            )
                        
                        new_line = self.env['stockex.stock.inventory.line'].create(line_vals)
                        created_count += 1
                        
                        # Vérifier que la ligne a bien été créée avec les bonnes valeurs
                        if i < 3:
                            _logger.info(
                                f"✅ Ligne créée: ID={new_line.id}, "
                                f"Quantité enregistrée={new_line.product_qty}, "
                                f"Catégorie={new_line.product_id.categ_id.name}"
                            )
                        
                    except Exception as line_error:
                        errors.append(f"Ligne {i+2}: Erreur création ligne - {str(line_error)}")
                        _logger.error(f"❌ Erreur ligne {i+2}: {str(line_error)}")
                else:
                    errors.append(f"Ligne {i+2}: Produit '{product_code}' non trouvé")
                    
            except Exception as e:
                errors.append(f"Ligne {i+2}: {str(e)}")
                _logger.error(f"❌ Erreur ligne {i+2}: {str(e)}")
        
        _logger.info(f"✅ Import terminé: {created_count} lignes créées")
        
        # Mettre la progression à 100%
        self.write({
            'progress': 100.0,
            'progress_message': f'Import terminé : {created_count} lignes créées'
        })
        self.env.cr.commit()
        
        # Message récapitulatif
        message = f"✅ {created_count} ligne(s) créée(s)"
        if created_warehouses:
            message += f"\n🏭 {len(created_warehouses)} entrepôt(s): {', '.join(list(created_warehouses)[:5])}"
            if len(created_warehouses) > 5:
                message += f" et {len(created_warehouses) - 5} autre(s)"
        if created_categories:
            message += f"\n📁 {len(created_categories)} catégorie(s) créée(s): {', '.join(list(created_categories)[:5])}"
            if len(created_categories) > 5:
                message += f" et {len(created_categories) - 5} autre(s)"
        if errors:
            message += f"\n⚠️ Lignes ignorées : {len(errors)}"
            # Afficher les 20 premières erreurs
            if len(errors) <= 20:
                message += "\n" + "\n".join(errors)
            else:
                message += "\n" + "\n".join(errors[:20])
                message += f"\n... et {len(errors) - 20} autre(s) erreur(s)"
            
            # Logger toutes les erreurs
            _logger.warning(f"⚠️ {len(errors)} lignes ignorées lors de l'import:")
            for error in errors[:50]:  # Logger les 50 premières
                _logger.warning(f"  - {error}")
        
        # Enregistrer le message dans le chatter
        try:
            # Utiliser sudo() pour éviter les problèmes de permissions et d'email
            inventory.sudo().message_post(
                body=message,
                message_type='comment',
                subtype_xmlid='mail.mt_note'
            )
        except Exception as msg_error:
            _logger.warning(f"⚠️ Impossible d'enregistrer le message dans le chatter: {str(msg_error)}")
            # Message enregistré uniquement dans les logs
        
        return created_count
