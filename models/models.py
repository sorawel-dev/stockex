# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class StockWarehouse(models.Model):
    """Héritage de stock.warehouse pour ajouter une hiérarchie d'entrepôts"""
    _inherit = 'stock.warehouse'
    
    # Code entrepôt (ancien "nom court")
    warehouse_code = fields.Char(
        string='Code Entrepôt',
        size=10,
        index=True,
        help='Code unique de l\'entrepôt (ex: WH-ABJ-001, WH-YOP-002)'
    )
    
    parent_id = fields.Many2one(
        comodel_name='stock.warehouse',
        string='Entrepôt Parent',
        ondelete='restrict',
        index=True,
        help='Entrepôt parent pour créer une hiérarchie d\'entrepôts'
    )
    
    parent_name_upper = fields.Char(
        string='Magasin Parent',
        compute='_compute_parent_name_upper',
        store=False,
        help='Nom de l\'entrepôt parent en MAJUSCULES'
    )
    
    child_ids = fields.One2many(
        comodel_name='stock.warehouse',
        inverse_name='parent_id',
        string='Entrepôts Enfants',
        help='Entrepôts dépendant de cet entrepôt'
    )
    child_count = fields.Integer(
        string='Nombre d\'enfants',
        compute='_compute_child_count',
        store=True
    )
    
    warehouse_type = fields.Selection(
        selection=[
            ('production', 'Production'),
            ('distribution', 'Distribution'),
            ('commercialisation', 'Commercialisation'),
        ],
        string='Type de Magasin',
        required=True,
        default='distribution',
        index=True,
        help='Type de magasin : Production, Distribution ou Commercialisation'
    )
    
    # Champs de géolocalisation
    latitude = fields.Float(
        string='Latitude',
        digits=(10, 7),
        help='Latitude GPS de l\'entrepôt (ex: 5.3599517)'
    )
    longitude = fields.Float(
        string='Longitude',
        digits=(10, 7),
        help='Longitude GPS de l\'entrepôt (ex: -4.0082563)'
    )
    coordinates = fields.Char(
        string='Coordonnées GPS',
        compute='_compute_coordinates',
        store=False,
        help='Coordonnées au format "Latitude, Longitude"'
    )
    google_maps_url = fields.Char(
        string='Lien Google Maps',
        compute='_compute_google_maps_url',
        store=False
    )
    
    # Informations de contact
    address = fields.Text(string='Adresse complète')
    city = fields.Char(string='Ville')
    phone = fields.Char(string='Téléphone')
    email = fields.Char(string='Email')
    
    def _generate_warehouse_code(self, name):
        """
        Génère un diminutif intelligent du nom de l'entrepôt.
        
        Args:
            name (str): Nom de l'entrepôt
            
        Returns:
            str: Code diminutif (max 5 caractères)
        
        Exemples:
            - "Abidjan" → "ABIDJ"
            - "Entrepôt Central" → "EC"
            - "Grand Bassam Site Nord" → "GBSN"
        """
        if not name:
            return 'WH'
        
        name = name.strip()
        words = name.split()
        
        if len(words) == 1:
            # Un seul mot : prendre les 5 premiers caractères
            code = name[:5].upper()
        else:
            # Plusieurs mots : prendre la première lettre de chaque mot (max 5)
            code = ''.join([word[0].upper() for word in words[:5] if word])
            # Si le code est trop court, compléter avec les premières lettres du premier mot
            if len(code) < 3 and words:
                code = (words[0][:3] + code).upper()[:5]
        
        return code
    
    @api.onchange('name')
    def _onchange_name_generate_code(self):
        """Génère automatiquement le code (diminutif) lors de la saisie du nom."""
        if self.name and not self.code:
            self.code = self._generate_warehouse_code(self.name)
    
    @api.model_create_multi
    def create(self, vals_list):
        """Génère automatiquement le code si non fourni lors de la création."""
        for vals in vals_list:
            if vals.get('name') and not vals.get('code'):
                vals['code'] = self._generate_warehouse_code(vals['name'])
        return super().create(vals_list)
    
    def write(self, vals):
        """Met à jour le code si le nom change et que le code n'est pas explicitement fourni."""
        if 'name' in vals and 'code' not in vals:
            for warehouse in self:
                # Regénérer le code si le nom change
                new_code = self._generate_warehouse_code(vals['name'])
                vals['code'] = new_code
        return super().write(vals)
    
    @api.depends('parent_id', 'parent_id.name')
    def _compute_parent_name_upper(self):
        """Calcule le nom du parent en MAJUSCULES."""
        for warehouse in self:
            if warehouse.parent_id:
                warehouse.parent_name_upper = warehouse.parent_id.name.upper()
            else:
                warehouse.parent_name_upper = False
    
    @api.depends('child_ids')
    def _compute_child_count(self):
        """Calcule le nombre d'entrepôts enfants."""
        for warehouse in self:
            warehouse.child_count = len(warehouse.child_ids)
    
    @api.depends('latitude', 'longitude')
    def _compute_coordinates(self):
        """Calcule les coordonnées GPS au format texte."""
        for warehouse in self:
            if warehouse.latitude and warehouse.longitude:
                warehouse.coordinates = f"{warehouse.latitude}, {warehouse.longitude}"
            else:
                warehouse.coordinates = False
    
    @api.depends('latitude', 'longitude')
    def _compute_google_maps_url(self):
        """Génère l'URL Google Maps."""
        for warehouse in self:
            if warehouse.latitude and warehouse.longitude:
                warehouse.google_maps_url = f"https://www.google.com/maps?q={warehouse.latitude},{warehouse.longitude}"
            else:
                warehouse.google_maps_url = False
    
    def action_open_map(self):
        """Ouvre Google Maps dans un nouvel onglet."""
        self.ensure_one()
        if not self.google_maps_url:
            raise UserError("Veuillez renseigner les coordonnées GPS de cet entrepôt.")
        return {
            'type': 'ir.actions.act_url',
            'url': self.google_maps_url,
            'target': 'new',
        }


class StockInventory(models.Model):
    _name = 'stockex.stock.inventory'
    _description = 'Inventaire de Stock'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'
    _rec_name = 'name'
    _rec_names_search = ['name']

    name = fields.Char(
        string='Référence',
        required=True,
        default='Nouveau',
        index=True,
        copy=False,
        tracking=True
    )
    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.today,
        index=True,
        tracking=True
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Brouillon'),
            ('in_progress', 'En cours'),
            ('pending_approval', 'En attente d\'approbation'),
            ('approved', 'Approuvé'),
            ('done', 'Validé'),
            ('cancel', 'Annulé')
        ],
        string='État',
        default='draft',
        required=True,
        copy=False,
        tracking=True,
        index=True
    )
    is_initial_stock = fields.Boolean(
        string='Stock Initial',
        default=False,
        help='Cocher si c\'est un inventaire de stock initial (base vide). Les écarts ne seront pas comptabilisés dans les statistiques.',
        tracking=True
    )
    description = fields.Text(string='Notes')
    location_id = fields.Many2one(
        comodel_name='stock.location',
        string='Emplacement',
        index=True,
        tracking=True
    )
    warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse',
        string='Entrepôt',
        index=True,
        tracking=True,
        help='Entrepôt principal de cet inventaire'
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Société',
        required=True,
        default=lambda self: self.env.company,
        index=True
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsable',
        required=True,
        default=lambda self: self.env.user,
        index=True,
        tracking=True
    )
    approver_id = fields.Many2one(
        comodel_name='res.users',
        string='Approbateur',
        tracking=True,
        help='Utilisateur qui a approuvé l\'inventaire'
    )
    approval_date = fields.Datetime(
        string='Date d\'approbation',
        readonly=True,
        tracking=True
    )
    validator_id = fields.Many2one(
        comodel_name='res.users',
        string='Validateur',
        tracking=True,
        help='Utilisateur qui a validé l\'inventaire'
    )
    validation_date = fields.Datetime(
        string='Date de validation',
        readonly=True,
        tracking=True
    )
    line_ids = fields.One2many(
        comodel_name='stockex.stock.inventory.line',
        inverse_name='inventory_id',
        string='Lignes'
    )
    account_move_ids = fields.One2many(
        comodel_name='account.move',
        inverse_name='stockex_inventory_id',
        string='Écritures Comptables',
        readonly=True,
        help='Écritures comptables générées par la validation de cet inventaire'
    )
    account_move_count = fields.Integer(
        string='Nombre d\'écritures',
        compute='_compute_account_move_count',
        store=True
    )
    
    # Totaux inventaire
    total_quantity_real = fields.Float(string='Quantité réelle totale', compute='_compute_totals', digits='Product Unit of Measure')
    total_quantity_theoretical = fields.Float(string='Quantité théorique totale', compute='_compute_totals', digits='Product Unit of Measure')
    total_quantity_difference = fields.Float(string='Écart de quantité total', compute='_compute_totals', digits='Product Unit of Measure')
    total_value_real = fields.Float(string='Valeur totale réelle', compute='_compute_totals', digits='Product Price')
    total_value_theoretical = fields.Float(string='Valeur totale théorique', compute='_compute_totals', digits='Product Price')
    total_value_difference = fields.Float(
        string='Valeur totale des écarts',
        compute='_compute_value_difference',
        digits='Product Price',
        help='Différence entre la valeur inventoriée et la valeur réelle du stock Odoo'
    )
    
    # Valeur réelle du stock Odoo (tous produits de l'emplacement/entrepôt)
    odoo_stock_value = fields.Float(
        string='Valeur Stock Odoo',
        compute='_compute_odoo_stock_value',
        digits='Product Price',
        help='Valeur totale du stock dans Odoo pour l\'emplacement/entrepôt de cet inventaire'
    )
    
    company_currency_id = fields.Many2one(comodel_name='res.currency', string='Devise', related='company_id.currency_id', store=False)
    
    _sql_constraints = [
        ('name_company_uniq', 'unique(name, company_id)', 
         'La référence doit être unique par société !'),
    ]
    
    @api.depends('account_move_ids')
    def _compute_account_move_count(self):
        """Calcule le nombre d'écritures comptables."""
        for inventory in self:
            inventory.account_move_count = len(inventory.account_move_ids)
    
    def _get_product_valuation_price(self, product):
        """Retourne le prix de valorisation d'un produit selon la règle Stockex.
        
        Args:
            product: recordset product.product
            
        Returns:
            float: Prix de valorisation unitaire (avec décote éventuelle)
            
        Règles Stockex:
        - Règle 1 (standard): Utilise product.standard_price
        - Règle 2 (economic): Utilise stock.valuation.layer (coût économique réel)
        
        Décote selon rotation (optionnel):
        - Si activée, applique un coefficient de décote selon la rotation du produit
        - Stock actif (< 12 mois) : 0% de décote
        - Rotation lente (12-36 mois) : 40% de décote
        - Stock mort (> 36 mois) : 100% de décote
        
        Configuration: Inventaire > Configuration > Paramètres > Règle de valorisation
        """
        self.ensure_one()
        
        if not product:
            return 0.0
        
        # Récupérer la règle de valorisation configurée dans Stockex
        ICP = self.env['ir.config_parameter'].sudo()
        rule = ICP.get_param('stockex.valuation_rule', 'standard')
        
        # Étape 1: Calculer le prix de base selon la règle
        base_price = 0.0
        
        # Règle 2: Coût économique réel (stock.valuation.layer)
        if rule == 'economic':
            ValuationLayer = self.env['stock.valuation.layer']
            
            # Rechercher la dernière couche de valorisation du produit
            layer = ValuationLayer.search([
                ('product_id', '=', product.id),
                ('company_id', '=', self.company_id.id),
            ], limit=1, order='create_date desc')
            
            if layer and (layer.unit_cost or layer.value):
                # Utiliser unit_cost si disponible, sinon calculer depuis value/quantity
                unit = layer.unit_cost or (layer.value / layer.quantity if layer.quantity else 0.0)
                if unit and unit > 0:
                    base_price = unit
        
        # Règle 1 (fallback): Coût standard
        if base_price == 0.0:
            base_price = product.standard_price or 0.0
        
        # Étape 2: Appliquer la décote selon rotation (si activée)
        apply_depreciation = ICP.get_param('stockex.apply_depreciation', 'False') == 'True'
        
        if apply_depreciation and base_price > 0:
            depreciation_coef = self._get_depreciation_coefficient(product)
            return base_price * depreciation_coef
        
        return base_price
    
    def _get_depreciation_coefficient(self, product):
        """Retourne le coefficient de décote selon la rotation du produit.
        
        Args:
            product: recordset product.product
            
        Returns:
            float: Coefficient de décote (1.0 = pas de décote, 0.6 = 40%, 0.0 = 100%)
            
        Catégories:
        - Stock actif: Mouvement dans les N derniers jours → Coefficient 1.0 (0% décote)
        - Rotation lente: Mouvement entre N et M jours → Coefficient 0.6 (40% décote)
        - Stock mort: Aucun mouvement depuis plus de M jours → Coefficient 0.0 (100% décote)
        """
        self.ensure_one()
        
        if not product:
            return 1.0
        
        # Récupérer les paramètres de décote
        ICP = self.env['ir.config_parameter'].sudo()
        active_days = int(ICP.get_param('stockex.depreciation_active_days', '365'))
        slow_days = int(ICP.get_param('stockex.depreciation_slow_days', '1095'))
        slow_rate = float(ICP.get_param('stockex.depreciation_slow_rate', '40.0'))
        dead_rate = float(ICP.get_param('stockex.depreciation_dead_rate', '100.0'))
        
        # Chercher le dernier mouvement du produit (sortie ou entrée)
        StockMove = self.env['stock.move']
        last_move = StockMove.search([
            ('product_id', '=', product.id),
            ('state', '=', 'done'),
        ], limit=1, order='date desc')
        
        if not last_move:
            # Aucun mouvement = stock mort (décote maximale)
            return 1.0 - (dead_rate / 100.0)
        
        # Calculer le nombre de jours depuis le dernier mouvement
        from datetime import datetime
        
        # Convertir last_move.date en date si c'est un datetime
        if isinstance(last_move.date, datetime):
            last_move_date = last_move.date.date()
        else:
            last_move_date = last_move.date
        
        now = datetime.now().date()
        days_since_last_move = (now - last_move_date).days
        
        # Appliquer les règles de décote
        if days_since_last_move <= active_days:
            # Stock actif: pas de décote
            return 1.0
        
        elif days_since_last_move <= slow_days:
            # Rotation lente: décote partielle
            return 1.0 - (slow_rate / 100.0)
        
        else:
            # Stock mort: décote maximale
            return 1.0 - (dead_rate / 100.0)
    
    @api.depends('line_ids.product_qty','line_ids.theoretical_qty','line_ids.difference','line_ids.standard_price','line_ids.product_id.standard_price')
    def _compute_totals(self):
        """Calcule les totaux (quantités et valeur) de l'inventaire.
        
        Pour l'écart de quantité, on utilise la somme des écarts des lignes
        (qui prend en compte la règle : si stock initial et qte_theo=0 alors écart=0)
        
        IMPORTANT: total_value_difference = total_value_real - odoo_stock_value
        (c'est-à-dire la différence entre la valeur inventoriée et la valeur réelle du stock Odoo)
        
        ⚠️ VALORISATION: Utilise line.standard_price si défini (prix capturé lors de l'inventaire),
        sinon utilise la méthode de valorisation du produit (FIFO/AVCO/Standard)
        """
        for inv in self:
            qty_real = sum(inv.line_ids.mapped('product_qty'))
            qty_theo = sum(inv.line_ids.mapped('theoretical_qty'))
            # Utiliser la somme des écarts calculés (qui respecte la règle stock initial)
            qty_diff = sum(inv.line_ids.mapped('difference'))
            total_val_real = 0.0
            total_val_theo = 0.0
            
            for line in inv.line_ids:
                # Utiliser line.standard_price si défini (prix capturé lors de l'inventaire)
                # Sinon, utiliser la méthode de valorisation du produit
                if line.standard_price and line.standard_price > 0:
                    price = line.standard_price
                else:
                    price = inv._get_product_valuation_price(line.product_id)
                
                total_val_real += (line.product_qty or 0.0) * price
                total_val_theo += (line.theoretical_qty or 0.0) * price
            
            inv.total_quantity_real = qty_real
            inv.total_quantity_theoretical = qty_theo
            inv.total_quantity_difference = qty_diff
            inv.total_value_real = total_val_real
            inv.total_value_theoretical = total_val_theo
    
    @api.depends('total_value_real', 'odoo_stock_value')
    def _compute_value_difference(self):
        """Calcule l'écart de valeur entre l'inventaire et le stock Odoo.
        
        total_value_difference = total_value_real - odoo_stock_value
        Cela garantit que l'écart reflète la différence avec la valeur totale du stock Odoo.
        """
        for inv in self:
            inv.total_value_difference = inv.total_value_real - inv.odoo_stock_value
    
    @api.depends('location_id', 'warehouse_id', 'company_id')
    def _compute_odoo_stock_value(self):
        """Calcule la valeur totale réelle du stock dans Odoo.
        
        Cette valeur représente la somme de tous les stock.quants
        dans l'emplacement/entrepôt de l'inventaire.
        Cela permet de comparer la valeur inventoriée avec la valeur réelle du stock Odoo.
        
        IMPORTANT: Utilise la règle de valorisation Stockex configurée:
        - Règle 1 (standard): product.standard_price
        - Règle 2 (economic): stock.valuation.layer (coût économique réel)
        
        Configuration: Inventaire > Configuration > Paramètres > Règle de valorisation
        """
        StockQuant = self.env['stock.quant']
        
        for inv in self:
            odoo_value = 0.0
            
            # Déterminer les emplacements à inclure
            location_ids = []
            if inv.location_id:
                # Emplacement spécifique + ses enfants
                location_ids.append(inv.location_id.id)
                location_ids.extend(inv.location_id.child_ids.ids)
            elif inv.warehouse_id:
                # Tous les emplacements de l'entrepôt (stock internal)
                stock_location = inv.warehouse_id.lot_stock_id
                if stock_location:
                    location_ids.append(stock_location.id)
                    location_ids.extend(stock_location.child_ids.ids)
            
            if not location_ids:
                inv.odoo_stock_value = 0.0
                continue
            
            # Récupérer tous les quants pour ces emplacements
            domain = [
                ('location_id', 'in', location_ids),
                ('company_id', '=', inv.company_id.id),
            ]
            
            quants = StockQuant.search(domain)
            
            # Calculer la valeur totale selon la règle de valorisation Stockex
            for quant in quants:
                available_qty = quant.quantity - quant.reserved_quantity
                
                if available_qty <= 0:
                    continue
                
                # Utiliser la méthode de valorisation Stockex
                product_price = inv._get_product_valuation_price(quant.product_id)
                odoo_value += available_qty * product_price
            
            inv.odoo_stock_value = odoo_value
            
            _logger.info(
                f"📊 Inventaire {inv.name}: Valeur Stock Odoo = {odoo_value:.2f} | "
                f"Valeur Inventoriée = {inv.total_value_real:.2f} | "
                f"Écart = {inv.total_value_real - odoo_value:.2f}"
            )

    def unlink(self):
        """Empêcher la suppression des inventaires validés."""
        for inventory in self:
            if inventory.state == 'done':
                raise UserError(
                    f"🚫 Impossible de supprimer l'inventaire '{inventory.name}'.\n\n"
                    f"L'inventaire a été validé le {inventory.validation_date.strftime('%d/%m/%Y à %H:%M') if inventory.validation_date else 'N/A'}.\n"
                    f"Les stocks Odoo ont déjà été mis à jour.\n\n"
                    f"❌ Un inventaire validé ne peut jamais être supprimé pour des raisons de traçabilité et d'audit.\n\n"
                    f"💡 Si vous devez corriger des erreurs :\n"
                    f"   - Créez un nouvel inventaire correctif\n"
                    f"   - Documentez les changements dans les notes"
                )
            elif inventory.state == 'approved':
                raise UserError(
                    f"🚫 Impossible de supprimer l'inventaire '{inventory.name}'.\n\n"
                    f"L'inventaire a été approuvé le {inventory.approval_date.strftime('%d/%m/%Y à %H:%M') if inventory.approval_date else 'N/A'}.\n"
                    f"Vous devez d'abord le rejeter avant de pouvoir le supprimer."
                )
        return super(StockInventory, self).unlink()
    
    def _notify_telegram(self, text):
        ICP = self.env['ir.config_parameter'].sudo()
        enabled = ICP.get_param('stockex.notify_by_telegram') or ''
        if str(enabled).lower() in ('false', '0', '', 'none'):
            return
        token = ICP.get_param('stockex.telegram_bot_token') or ''
        chats = ICP.get_param('stockex.telegram_chat_ids') or ''
        if not token or not chats:
            return
        import requests
        for chat_id in [c.strip() for c in chats.split(',') if c.strip()]:
            try:
                requests.post(
                    f'https://api.telegram.org/bot{token}/sendMessage',
                    data={'chat_id': chat_id, 'text': text}
                )
            except Exception as e:
                _logger.error(f"Telegram notification error: {e}")

    def action_start(self):
        """Démarre l'inventaire."""
        if not self.line_ids:
            raise UserError("Vous devez ajouter au moins une ligne avant de démarrer l'inventaire.")
        return self.write({'state': 'in_progress'})
    
    def action_request_approval(self):
        """Demande l'approbation de l'inventaire."""
        if not self.line_ids:
            raise UserError("Impossible de demander l'approbation d'un inventaire sans lignes.")
        
        # Créer une activité pour le manager
        manager = self.user_id.parent_id or self.env.ref('base.user_admin')
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            user_id=manager.id,
            summary=f"Approbation d'inventaire : {self.name}",
            note=f"Merci d'approuver l'inventaire {self.name} du {self.date}"
        )
        
        return self.write({'state': 'pending_approval'})
    
    def action_approve(self):
        """Approuve l'inventaire."""
        self.write({
            'state': 'approved',
            'approver_id': self.env.user.id,
            'approval_date': fields.Datetime.now()
        })
        
        # Marquer l'activité comme terminée
        activity = self.activity_ids.filtered(lambda a: a.user_id == self.env.user)
        if activity:
            activity.action_done()
        
        return True
    
    def action_reject(self):
        """Rejette l'inventaire et le remet en brouillon."""
        # Marquer l'activité comme annulée
        activity = self.activity_ids.filtered(lambda a: a.user_id == self.env.user)
        if activity:
            activity.unlink()
        
        return self.write({'state': 'draft'})
    
    def action_validate(self):
        """Valide l'inventaire et met à jour les stocks Odoo."""
        import threading
        
        for inventory in self:
            if not inventory.line_ids:
                raise UserError("Impossible de valider un inventaire sans lignes.")
            
            total_lines = len(inventory.line_ids)
            
            # Pour les gros inventaires (> 500 lignes), utiliser traitement asynchrone
            if total_lines > 500:
                _logger.info(f"🚀 Gros inventaire ({total_lines} lignes) → Traitement en thread séparé")
                
                # Marquer comme validé immédiatement
                inventory.write({
                    'state': 'done',
                    'validator_id': self.env.user.id,
                    'validation_date': fields.Datetime.now()
                })
                self.env.cr.commit()
                inventory._notify_telegram(f"✅ Inventaire {inventory.name} validé ({total_lines} lignes). Mise à jour en arrière-plan.")
                
                # Lancer le traitement dans un thread séparé
                thread = threading.Thread(
                    target=inventory._update_odoo_stock_async,
                    args=(inventory.id, self.env.cr.dbname)
                )
                thread.daemon = True
                thread.start()
                
                # Message utilisateur
                inventory.message_post(
                    body=f"⏳ Mise à jour de {total_lines} lignes de stock en cours en arrière-plan...",
                    message_type='notification'
                )
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': '✅ Inventaire validé',
                        'message': f'La mise à jour de {total_lines} lignes se fait en arrière-plan. Vous pouvez continuer à travailler.',
                        'type': 'success',
                        'sticky': True,
                    }
                }
            else:
                # Pour petits inventaires (≤ 500 lignes), traitement immédiat
                inventory._update_odoo_stock()
                
                res = inventory.write({
                    'state': 'done',
                    'validator_id': self.env.user.id,
                    'validation_date': fields.Datetime.now()
                })
                inventory._notify_telegram(f"✅ Inventaire {inventory.name} validé ({total_lines} lignes). Stocks mis à jour.")
                return res
    
    def _update_odoo_stock(self):
        """Met à jour les stocks Odoo avec les quantités de l'inventaire (optimisé avec commits par lots)."""
        self.ensure_one()
        
        StockQuant = self.env['stock.quant']
        adjusted_count = 0
        errors = []
        skipped_no_data = 0
        skipped_bad_location = 0
        skipped_qty_zero = 0
        
        total_lines = len(self.line_ids)
        batch_size = 50  # Traiter 50 lignes à la fois
        
        _logger.info(f"🚀 Début mise à jour stocks pour inventaire {self.name} - {total_lines} lignes (par lots de {batch_size})")
        
        for batch_num, i in enumerate(range(0, total_lines, batch_size), 1):
            batch_lines = self.line_ids[i:i + batch_size]
            batch_start = i + 1
            batch_end = min(i + batch_size, total_lines)
            
            _logger.info(f"📦 Traitement lot {batch_num}: lignes {batch_start}-{batch_end} / {total_lines}")
            
            for line in batch_lines:
                try:
                    if not line.product_id or not line.location_id:
                        skipped_no_data += 1
                        continue
                    
                    # Vérifier que l'emplacement est de type interne
                    if line.location_id.usage != 'internal':
                        skipped_bad_location += 1
                        errors.append(f"Emplacement '{line.location_id.name}' n'est pas de type 'internal' (type: {line.location_id.usage})")
                        continue
                    
                    # Trouver ou créer le quant avec company_id
                    quant = StockQuant.search([
                        ('product_id', '=', line.product_id.id),
                        ('location_id', '=', line.location_id.id),
                        ('company_id', '=', self.company_id.id),
                    ], limit=1)
                    
                    if quant:
                        # Mettre à jour la quantité existante
                        quant.inventory_quantity = line.product_qty
                        quant.inventory_quantity_set = True
                        quant.action_apply_inventory()
                        adjusted_count += 1
                    else:
                        # Créer un nouveau quant si nécessaire
                        if line.product_qty != 0:
                            new_quant = StockQuant.create({
                                'product_id': line.product_id.id,
                                'location_id': line.location_id.id,
                                'company_id': self.company_id.id,
                                'inventory_quantity': line.product_qty,
                                'inventory_quantity_set': True,
                            })
                            new_quant.action_apply_inventory()
                            adjusted_count += 1
                        else:
                            skipped_qty_zero += 1
                            
                except Exception as e:
                    error_msg = f"Produit {line.product_id.default_code} @ {line.location_id.name}: {str(e)}"
                    errors.append(error_msg)
                    _logger.error(f"❌ Erreur ligne: {error_msg}")
            
            # Commit après chaque lot pour éviter timeout
            self.env.cr.commit()
            progress_pct = (batch_end / total_lines) * 100
            _logger.info(f"✅ Lot {batch_num} terminé: {adjusted_count} ajustements ({progress_pct:.1f}%)")
        
        # Statistiques détaillées
        stats = f"""
📊 Statistiques de mise à jour:
- Total lignes: {len(self.line_ids)}
- ✅ Ajustements réussis: {adjusted_count}
- ⚠️ Ignorées (emplacement non 'internal'): {skipped_bad_location}
- ⚠️ Ignorées (sans données): {skipped_no_data}
- ⚠️ Ignorées (quantité = 0): {skipped_qty_zero}
- ❌ Erreurs: {len(errors)}
"""
        
        # Message de confirmation
        message = f"✅ Stocks mis à jour : {adjusted_count} ajustements effectués sur {len(self.line_ids)} lignes"
        message += stats
        
        if errors:
            message += f"\n\n⚠️ Détails des erreurs ({len(errors)}):\n" + "\n".join(errors[:20])
        
        _logger.info(message)
        
        # Poster un message dans le chatter
        try:
            self.message_post(
                body=message,
                message_type='notification',
                subtype_xmlid='mail.mt_note'
            )
        except Exception as msg_error:
            _logger.warning(f"⚠️ Impossible de poster le message dans le chatter: {msg_error}")
    
    @staticmethod
    def _update_odoo_stock_async(inventory_id, dbname):
        """Version asynchrone de _update_odoo_stock pour gros inventaires (utilise un nouveau curseur)."""
        import odoo
        from odoo import api, SUPERUSER_ID
        
        try:
            # Créer un nouveau curseur et registry
            registry = odoo.registry(dbname)
            with registry.cursor() as new_cr:
                env = api.Environment(new_cr, SUPERUSER_ID, {})
                inventory = env['stockex.stock.inventory'].browse(inventory_id)
                
                _logger.info(f"🚀 Début traitement asynchrone pour inventaire {inventory.name}")
                inventory._update_odoo_stock()
                new_cr.commit()
                _logger.info(f"✅ Traitement asynchrone terminé pour inventaire {inventory.name}")
                
        except Exception as e:
            _logger.error(f"❌ Erreur traitement asynchrone: {e}", exc_info=True)
            # Essayer de poster l'erreur dans le chatter
            try:
                with registry.cursor() as err_cr:
                    err_env = api.Environment(err_cr, SUPERUSER_ID, {})
                    inventory = err_env['stockex.stock.inventory'].browse(inventory_id)
                    inventory.message_post(
                        body=f"❌ Erreur lors de la mise à jour des stocks: {str(e)}",
                        message_type='notification',
                        subtype_xmlid='mail.mt_note'
                    )
                    err_cr.commit()
            except Exception as msg_err:
                _logger.error(f"❌ Impossible de poster l'erreur: {msg_err}")
    
    def action_draft(self):
        """Remet l'inventaire en brouillon."""
        return self.write({'state': 'draft'})
    
    def action_cancel(self):
        """Annule l'inventaire validé en inversant les ajustements de stock et en supprimant les écritures comptables."""
        for inventory in self:
            if inventory.state != 'done':
                raise UserError("Seuls les inventaires validés peuvent être annulés.")
            
            _logger.info(f"🔄 Début de l'annulation de l'inventaire {inventory.name}")
            
            quants_adjusted = 0
            account_moves_count = 0
            errors = []
            
            # 1. INVERSER LES AJUSTEMENTS DE STOCK DANS LES QUANTS
            # Au lieu de chercher des stock.move, on inverse directement les quants
            StockQuant = self.env['stock.quant']
            
            for line in inventory.line_ids:
                try:
                    if not line.product_id or not line.location_id:
                        continue
                    
                    # Vérifier que l'emplacement est de type interne
                    if line.location_id.usage != 'internal':
                        continue
                    
                    # Trouver le quant
                    quant = StockQuant.search([
                        ('product_id', '=', line.product_id.id),
                        ('location_id', '=', line.location_id.id),
                        ('company_id', '=', inventory.company_id.id),
                    ], limit=1)
                    
                    if quant:
                        # Calculer la quantité à restaurer (quantité avant inventaire)
                        # product_qty = quantité après inventaire (dans l'inventaire)
                        # theoretical_qty = quantité avant inventaire (théorique)
                        qty_to_restore = line.theoretical_qty
                        
                        # Restaurer la quantité d'avant inventaire
                        quant.inventory_quantity = qty_to_restore
                        quant.inventory_quantity_set = True
                        quant.action_apply_inventory()
                        
                        quants_adjusted += 1
                        _logger.info(
                            f"✅ Quant inversé: {line.product_id.default_code} @ {line.location_id.name}: "
                            f"{line.product_qty} → {qty_to_restore}"
                        )
                    else:
                        # Si le quant n'existe plus et que la quantité théorique était > 0, le recréer
                        if line.theoretical_qty > 0:
                            new_quant = StockQuant.create({
                                'product_id': line.product_id.id,
                                'location_id': line.location_id.id,
                                'company_id': inventory.company_id.id,
                                'inventory_quantity': line.theoretical_qty,
                                'inventory_quantity_set': True,
                            })
                            new_quant.action_apply_inventory()
                            quants_adjusted += 1
                            _logger.info(
                                f"✅ Quant recréé: {line.product_id.default_code} @ {line.location_id.name}: "
                                f"0 → {line.theoretical_qty}"
                            )
                            
                except Exception as e:
                    error_msg = f"Produit {line.product_id.default_code} @ {line.location_id.name}: {str(e)}"
                    errors.append(error_msg)
                    _logger.error(f"❌ Erreur inversion ligne: {error_msg}")
            
            _logger.info(f"📦 {quants_adjusted} quant(s) inversé(s)")
            
            # 2. SUPPRIMER LES ÉCRITURES COMPTABLES LIÉES
            account_moves = inventory.move_ids if hasattr(inventory, 'move_ids') else self.env['account.move']
            
            # Rechercher aussi par référence si aucune écriture liée
            if not account_moves:
                account_moves = self.env['account.move'].search([
                    ('ref', 'ilike', inventory.name),
                    ('move_type', '=', 'entry'),
                ])
            
            if account_moves:
                _logger.info(f"📒 Trouvé {len(account_moves)} écriture(s) comptable(s) à supprimer")
                account_moves_count = len(account_moves)
                
                for account_move in account_moves:
                    try:
                        move_name = account_move.name
                        move_id = account_move.id
                        
                        # Annuler l'écriture si elle est validée
                        if account_move.state == 'posted':
                            account_move.button_draft()
                            _logger.info(f"✅ Écriture {move_name} remise en brouillon")
                        
                        # Supprimer l'écriture avec force
                        try:
                            account_move.with_context(force_delete=True).unlink()
                            _logger.info(f"🗑️ Écriture {move_name} supprimée")
                        except Exception as unlink_error:
                            # Si unlink échoue, forcer la suppression via SQL
                            _logger.warning(f"⚠️ unlink() a échoué pour {move_name}, utilisation de SQL: {str(unlink_error)}")
                            self.env.cr.execute("DELETE FROM account_move_line WHERE move_id = %s", (move_id,))
                            self.env.cr.execute("DELETE FROM account_move WHERE id = %s", (move_id,))
                            _logger.info(f"🗑️ Écriture {move_name} (ID:{move_id}) supprimée via SQL")
                    except Exception as e:
                        error_msg = f"Écriture {account_move.name}: {str(e)}"
                        errors.append(error_msg)
                        _logger.error(f"❌ Erreur suppression écriture: {error_msg}")
            
            # 3. Annuler l'inventaire
            inventory.write({'state': 'cancel'})
            
            # 4. Message dans le chatter
            message_body = f"""
            <div style="padding: 20px; background: #f8d7da; border-left: 5px solid #dc3545; border-radius: 5px;">
                <h3 style="color: #721c24; margin-top: 0;">❌ Inventaire annulé par {self.env.user.name}</h3>
                <hr style="border-color: #dc3545;"/>
                <p><strong>🔄 Ajustements inversés :</strong></p>
                <ul>
                    <li>📦 {quants_adjusted} quant(s) restauré(s) à leur état avant inventaire</li>
                    <li>📒 {account_moves_count} écriture(s) comptable(s) supprimée(s)</li>
                </ul>
            """
            
            if errors:
                message_body += f"""
                <hr style="border-color: #ffc107;"/>
                <p><strong>⚠️ Erreurs ({len(errors)}) :</strong></p>
                <ul style="color: #856404; font-size: 12px;">
                """
                for error in errors[:10]:
                    message_body += f"<li>{error}</li>"
                if len(errors) > 10:
                    message_body += f"<li>... et {len(errors) - 10} autre(s) erreur(s)</li>"
                message_body += "</ul>"
            
            message_body += "</div>"
            
            inventory.message_post(
                body=message_body,
                message_type='comment',
                subtype_xmlid='mail.mt_note'
            )
            
            _logger.info(
                f"✅ Inventaire {inventory.name} annulé avec succès: "
                f"{quants_adjusted} quants inversés, {account_moves_count} écritures supprimées"
            )
        
        return True
    
    def name_get(self):
        """Affichage personnalisé du nom."""
        result = []
        for record in self:
            name = f"{record.name} - {record.date}"
            if record.location_id:
                name += f" ({record.location_id.name})"
            result.append((record.id, name))
        return result
    
    @api.model_create_multi
    def create(self, vals_list):
        """Génère automatiquement la référence si elle n'est pas fournie."""
        for vals in vals_list:
            if vals.get('name', 'Nouveau') == 'Nouveau' or not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code('stockex.stock.inventory') or 'Nouveau'
        return super().create(vals_list)
    
    def action_export_excel(self):
        """Exporter l'inventaire en Excel."""
        self.ensure_one()
        
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
            from openpyxl.utils import get_column_letter
            import base64
            from io import BytesIO
        except ImportError:
            raise UserError("La bibliothèque openpyxl est requise pour l'export Excel.")
        
        # Créer le workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Inventaire"
        
        # Styles
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=12)
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # En-tête du document
        ws['A1'] = f"INVENTAIRE DE STOCK - {self.name}"
        ws['A1'].font = Font(bold=True, size=14)
        ws.merge_cells('A1:J1')
        
        ws['A2'] = f"Date: {self.date}"
        ws['A3'] = f"Responsable: {self.user_id.name}"
        ws['A4'] = f"Société: {self.company_id.name}"
        ws['A5'] = f"État: {dict(self._fields['state'].selection).get(self.state)}"
        
        # En-têtes colonnes (ligne 7)
        headers = [
            'Produit',
            'Référence',
            'Catégorie',
            'Emplacement',
            'Qté Théorique',
            'Qté Réelle',
            'Écart',
            'Prix Standard (FCFA)',
            'Valeur Écart (FCFA)'
        ]
        
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=7, column=col_num, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.border = border
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        # Données
        row_num = 8
        total_theoretical = 0
        total_real = 0
        total_difference_value = 0
        
        for line in self.line_ids:
            ws.cell(row=row_num, column=1, value=line.product_id.name or '')
            ws.cell(row=row_num, column=2, value=line.product_id.default_code or '')
            ws.cell(row=row_num, column=3, value=line.product_id.categ_id.name or '')
            ws.cell(row=row_num, column=4, value=line.location_id.display_name or '')
            ws.cell(row=row_num, column=5, value=line.theoretical_qty)
            ws.cell(row=row_num, column=6, value=line.product_qty)
            ws.cell(row=row_num, column=7, value=line.difference)
            ws.cell(row=row_num, column=8, value=line.standard_price)
            
            diff_value = line.difference * line.standard_price
            ws.cell(row=row_num, column=9, value=diff_value)
            
            # Bordures
            for col in range(1, 10):
                ws.cell(row=row_num, column=col).border = border
            
            # Colorer les écarts
            diff_cell = ws.cell(row=row_num, column=7)
            if line.difference > 0:
                diff_cell.font = Font(color="008000", bold=True)  # Vert
            elif line.difference < 0:
                diff_cell.font = Font(color="FF0000", bold=True)  # Rouge
            
            total_theoretical += line.theoretical_qty
            total_real += line.product_qty
            total_difference_value += diff_value
            row_num += 1
        
        # Ligne totaux
        row_num += 1
        ws.cell(row=row_num, column=1, value="TOTAUX").font = Font(bold=True)
        ws.cell(row=row_num, column=5, value=total_theoretical).font = Font(bold=True)
        ws.cell(row=row_num, column=6, value=total_real).font = Font(bold=True)
        ws.cell(row=row_num, column=7, value=total_real - total_theoretical).font = Font(bold=True)
        ws.cell(row=row_num, column=9, value=total_difference_value).font = Font(bold=True)
        
        for col in range(1, 10):
            ws.cell(row=row_num, column=col).fill = PatternFill(start_color="E0E0E0", end_color="E0E0E0", fill_type="solid")
        
        # Ajuster largeur colonnes
        column_widths = [30, 15, 20, 35, 15, 15, 12, 15, 15]
        for i, width in enumerate(column_widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = width
        
        # Sauvegarder en mémoire
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        # Créer l'attachement
        attachment = self.env['ir.attachment'].create({
            'name': f'Inventaire_{self.name.replace("/", "_")}.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
    
    def action_print_pdf(self):
        """Imprimer l'inventaire en PDF."""
        self.ensure_one()
        return self.env.ref('stockex.action_report_inventory').report_action(self)
    
    def action_refresh_theoretical_qty(self):
        """Recalcule les quantités théoriques ET les prix unitaires depuis le stock Odoo actuel."""
        self.ensure_one()
        _logger.info(f"🔄 Recalcul des quantités théoriques ET prix pour inventaire {self.name}")
        
        if not self.line_ids:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Aucune ligne',
                    'message': 'Cet inventaire ne contient aucune ligne.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        # Forcer le recalcul pour chaque ligne
        updated_count = 0
        price_updated = 0
        for line in self.line_ids:
            if not line.product_id or not line.location_id:
                continue
            
            # Récupérer la quantité depuis stock.quant
            quants = self.env['stock.quant'].search([
                ('product_id', '=', line.product_id.id),
                ('location_id', '=', line.location_id.id),
            ])
            
            qty_available = sum(quants.mapped('quantity')) - sum(quants.mapped('reserved_quantity'))
            
            # Récupérer le prix du produit
            product_price = line.product_id.standard_price
            
            # Calculer la différence
            difference = line.product_qty - qty_available
            
            # Forcer l'écriture directe (bypass du compute)
            self.env.cr.execute("""
                UPDATE stockex_stock_inventory_line 
                SET theoretical_qty = %s, difference = %s, standard_price = %s
                WHERE id = %s
            """, (qty_available, difference, product_price, line.id))
            
            if qty_available > 0:
                updated_count += 1
            if product_price > 0:
                price_updated += 1
            
            _logger.info(
                f"📦 Ligne {line.id}: {line.product_id.name} → "
                f"Théo: {qty_available}, Réel: {line.product_qty}, Écart: {difference}, Prix: {product_price}"
            )
        
        # Invalider le cache pour forcer le rechargement
        self.line_ids.invalidate_recordset(['theoretical_qty', 'difference', 'difference_display', 'standard_price'])
        
        # Compter les résultats
        lines_with_qty = len([l for l in self.line_ids if l.theoretical_qty > 0])
        
        message = f"✅ Quantités théoriques ET prix recalculés\n"
        message += f"📊 {lines_with_qty} ligne(s) avec stock > 0\n"
        message += f"💰 {price_updated} ligne(s) avec prix > 0\n"
        message += f"📦 {len(self.line_ids) - lines_with_qty} ligne(s) avec stock = 0"
        
        _logger.info(f"✅ Recalcul terminé: {lines_with_qty}/{len(self.line_ids)} lignes avec stock, {price_updated} avec prix")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Recalcul terminé',
                'message': message,
                'type': 'success',
                'sticky': False,
            }
        }
    
    @api.model
    def _send_inventory_reminders(self):
        """Envoie des rappels pour les inventaires en cours depuis plus de 7 jours."""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=7)
        old_inventories = self.search([
            ('state', 'in', ['in_progress', 'pending_approval']),
            ('create_date', '<=', cutoff_date)
        ])
        
        for inventory in old_inventories:
            # Créer une activité de rappel
            inventory.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=inventory.user_id.id,
                summary=f"Rappel: Inventaire en attente - {inventory.name}",
                note=f"L'inventaire {inventory.name} est en cours depuis plus de 7 jours. Merci de le finaliser.",
                date_deadline=fields.Date.today()
            )
            
            _logger.info(f"Rappel envoyé pour inventaire {inventory.name}")
        
        return True


class StockInventoryLine(models.Model):
    _name = 'stockex.stock.inventory.line'
    _description = 'Ligne d\'inventaire'
    _order = 'product_id, id'
    _rec_name = 'product_id'
    
    inventory_id = fields.Many2one(
        comodel_name='stockex.stock.inventory',
        string='Inventaire',
        required=True,
        ondelete='cascade',
        index=True
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Produit',
        required=True,
        index=True
    )
    product_barcode = fields.Char(
        string='Code-barres',
        related='product_id.barcode',
        readonly=True,
        help='Code-barres du produit pour scan mobile'
    )
    product_categ_id = fields.Many2one(
        comodel_name='product.category',
        string='Catégorie',
        related='product_id.categ_id',
        readonly=True,
        store=True
    )
    scanned_barcode = fields.Char(
        string='Code-barres scanné',
        help='Code-barres scanné pour recherche rapide de produit'
    )
    theoretical_qty = fields.Float(
        string='Quantité théorique',
        digits='Product Unit of Measure',
        readonly=True,
        compute='_compute_theoretical_qty',
        store=True,
        compute_sudo=True,
        inverse='_inverse_theoretical_qty',  # Permettre de forcer la valeur
    )
    product_qty = fields.Float(
        string='Quantité réelle',
        digits='Product Unit of Measure',
        default=0.0
    )
    difference = fields.Float(
        string='Différence',
        compute='_compute_difference',
        store=True,
        digits='Product Unit of Measure',
        readonly=True
    )
    difference_display = fields.Html(
        string='Écart',
        compute='_compute_difference_display',
        readonly=True
    )
    location_id = fields.Many2one(
        comodel_name='stock.location',
        string='Emplacement',
        index=True
    )
    standard_price = fields.Float(
        string='Prix unitaire',
        digits='Product Price',
        help='Prix unitaire du produit au moment de l\'inventaire'
    )
    product_uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Unité de Mesure',
        related='product_id.uom_id',
        readonly=True
    )
    
    # Pièces jointes et photos
    image_1 = fields.Binary(
        string='Photo 1',
        attachment=True,
        help='Première photo du produit compté'
    )
    image_2 = fields.Binary(
        string='Photo 2',
        attachment=True,
        help='Deuxième photo du produit compté'
    )
    image_3 = fields.Binary(
        string='Photo 3',
        attachment=True,
        help='Troisième photo du produit compté'
    )
    note = fields.Text(
        string='Remarques',
        help='Notes ou observations sur cette ligne d\'inventaire'
    )
    
    @api.depends('product_id', 'location_id')
    def _compute_theoretical_qty(self):
        """Calcule la quantité théorique depuis le stock Odoo.
        
        Cherche dans l'emplacement exact ET ses enfants pour plus de flexibilité.
        """
        # Préparer l'ensemble des lignes pertinentes (avec produit et emplacement)
        lines = self.filtered(lambda l: l.product_id and l.location_id)

        # Initialiser les lignes sans données requises à 0
        for line in (self - lines):
            line.theoretical_qty = 0.0

        if not lines:
            return

        product_ids = list(set(lines.mapped('product_id').ids))
        
        # Récupérer tous les emplacements + leurs enfants
        location_ids = set()
        for loc in lines.mapped('location_id'):
            # Ajouter l'emplacement lui-même
            location_ids.add(loc.id)
            # Ajouter tous ses enfants (child_ids est récursif dans Odoo)
            location_ids.update(loc.child_ids.ids)
        
        location_ids = list(location_ids)
        
        # Récupérer les company_ids des lignes
        company_ids = list(set(lines.mapped('inventory_id.company_id').ids))
        if not company_ids:
            company_ids = [self.env.company.id]

        _logger.info(
            f"🔍 Calcul theoretical_qty pour {len(lines)} lignes, "
            f"{len(product_ids)} produits, {len(location_ids)} emplacements (incluant enfants), "
            f"companies: {company_ids}"
        )

        # Agréger en une seule requête SQL AVEC FILTRE COMPANY ET EMPLACEMENTS ENFANTS
        groups = self.env['stock.quant'].read_group(
            domain=[
                ('product_id', 'in', product_ids),
                ('location_id', 'in', location_ids),  # ✅ Inclut les enfants
                ('company_id', 'in', company_ids),
            ],
            fields=['quantity:sum', 'reserved_quantity:sum'],
            groupby=['product_id', 'location_id'],
        )

        _logger.info(f"📊 {len(groups)} groupes de stock.quant trouvés")

        # Construire un mapping (product_id, location_id) -> quantity
        # Inclure les quantités des emplacements enfants
        qty_map = {}  # (product_id, location_id) -> qty
        
        for g in groups:
            if 'product_id' in g and 'location_id' in g:
                prod_id = g['product_id'][0] if g['product_id'] else None
                loc_id = g['location_id'][0] if g['location_id'] else None
                if prod_id and loc_id:
                    qty = g.get('quantity_sum', 0.0) or 0.0
                    reserved = g.get('reserved_quantity_sum', 0.0) or 0.0
                    available = qty - reserved
                    
                    # Ajouter à toutes les lignes dont le location_id correspond
                    # (soit exact, soit parent de loc_id)
                    for line in lines:
                        if line.product_id.id == prod_id:
                            # Vérifier si loc_id est l'emplacement de la ligne ou un enfant
                            if (loc_id == line.location_id.id or 
                                loc_id in line.location_id.child_ids.ids):
                                key = (line.product_id.id, line.location_id.id)
                                qty_map[key] = qty_map.get(key, 0.0) + available

        # Appliquer les quantités
        updated_count = 0
        for line in lines:
            theo_qty = qty_map.get((line.product_id.id, line.location_id.id), 0.0)
            line.theoretical_qty = theo_qty
            if theo_qty > 0:
                updated_count += 1
        
        if updated_count > 0:
            _logger.info(f"✅ {updated_count} lignes avec quantité théorique > 0")
        else:
            _logger.warning(
                f"⚠️ Aucune ligne avec stock trouvée ! "
                f"Vérifiez que les emplacements correspondent."
            )

    def _inverse_theoretical_qty(self):
        """Méthode inverse pour permettre de forcer la valeur theoretical_qty (pour stock initial)."""
        # Ne rien faire - la valeur est déjà écrite par le create/write
        pass
    
    @api.depends('theoretical_qty', 'product_qty', 'inventory_id.is_initial_stock')
    def _compute_difference(self):
        """Calcule la différence entre la quantité réelle et théorique.
        
        Pour les inventaires de stock initial :
        - Si qte_theorique = 0, alors écart = 0 (pas d'écart sur stock initial vide)
        - Sinon, écart normal = qte_reelle - qte_theorique
        """
        for line in self:
            # Pour stock initial avec qte théorique = 0 : écart = 0
            if line.inventory_id.is_initial_stock and line.theoretical_qty == 0:
                line.difference = 0.0
            else:
                line.difference = line.product_qty - line.theoretical_qty
    
    @api.depends('difference')
    def _compute_difference_display(self):
        """Affiche la différence en couleur selon le signe."""
        for line in self:
            diff = line.difference
            if diff < 0:
                color = 'red'
                icon = '⚠️'
            elif diff > 0:
                color = 'green'
                icon = '✓'
            else:
                color = 'gray'
                icon = '='
            line.difference_display = f'<span style="color: {color}; font-weight: bold;">{icon} {diff:,.2f}</span>'
    
    @api.onchange('scanned_barcode')
    def _onchange_scanned_barcode(self):
        """Recherche le produit par code-barres scanné."""
        if self.scanned_barcode:
            product = self.env['product.product'].search([
                ('barcode', '=', self.scanned_barcode)
            ], limit=1)
            if product:
                self.product_id = product.id
                self.scanned_barcode = False  # Reset après scan
            else:
                return {
                    'warning': {
                        'title': 'Code-barres non trouvé',
                        'message': f"Aucun produit trouvé avec le code-barres '{self.scanned_barcode}'"
                    }
                }
    
    @api.onchange('product_id', 'location_id')
    def _onchange_product_location(self):
        """Remplit automatiquement la quantité théorique et le prix unitaire."""
        if self.product_id:
            # Récupérer le prix unitaire du produit
            self.standard_price = self.product_id.standard_price
            
            # Récupérer la quantité théorique si l'emplacement est défini
            if self.location_id:
                quant = self.env['stock.quant'].search([
                    ('product_id', '=', self.product_id.id),
                    ('location_id', '=', self.location_id.id),
                    ('company_id', '=', self.inventory_id.company_id.id if self.inventory_id else self.env.company.id),
                ], limit=1)
                
                if quant:
                    theoretical_qty = quant.quantity - quant.reserved_quantity
                    self.theoretical_qty = theoretical_qty
                    _logger.info(
                        f"✅ Auto-rempli: {self.product_id.default_code} @ {self.location_id.name}: "
                        f"Qté théo={theoretical_qty}, Prix={self.standard_price}"
                    )
                else:
                    self.theoretical_qty = 0.0
    
    @api.constrains('product_id', 'inventory_id')
    def _check_product_uniqueness(self):
        """Vérifie qu'un produit n'apparaît qu'une seule fois par inventaire."""
        for line in self:
            domain = [
                ('inventory_id', '=', line.inventory_id.id),
                ('product_id', '=', line.product_id.id),
                ('id', '!=', line.id)
            ]
            if line.location_id:
                domain.append(('location_id', '=', line.location_id.id))
            if self.search_count(domain) > 0:
                raise UserError(
                    f"Le produit '{line.product_id.display_name}' est déjà présent dans cet inventaire "
                    f"pour cet emplacement."
                )

