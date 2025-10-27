# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, tools

_logger = logging.getLogger(__name__)


class InventoryDashboard(models.Model):
    """Dashboard d'analyse des inventaires - Vue SQL."""
    _name = 'stockex.inventory.dashboard'
    _description = 'Dashboard Inventaire'
    _auto = False
    _order = 'inventory_id desc'
    
    # Inventaire
    inventory_id = fields.Many2one(
        comodel_name='stockex.stock.inventory',
        string='Inventaire',
        readonly=True
    )
    inventory_name = fields.Char(
        string='Nom Inventaire',
        readonly=True
    )
    inventory_date = fields.Date(
        string='Date Inventaire',
        readonly=True
    )
    inventory_state = fields.Selection([
        ('draft', 'Brouillon'),
        ('done', 'Validé'),
        ('cancel', 'Annulé'),
    ], string='État', readonly=True)
    
    # Statistiques produits
    total_products = fields.Integer(
        string='Nombre de Produits',
        readonly=True
    )
    total_categories = fields.Integer(
        string='Nombre de Catégories',
        readonly=True
    )
    total_warehouses = fields.Integer(
        string='Nombre d\'Entrepôts',
        readonly=True
    )
    
    # Statistiques quantités
    total_quantity = fields.Float(
        string='Quantité Totale',
        readonly=True,
        digits='Product Unit of Measure'
    )
    total_value = fields.Float(
        string='Valeur Totale',
        readonly=True,
        digits='Product Price'
    )
    average_price = fields.Float(
        string='Prix Moyen',
        readonly=True,
        digits='Product Price'
    )
    
    # Statistiques par catégorie
    category_id = fields.Many2one(
        comodel_name='product.category',
        string='Catégorie',
        readonly=True
    )
    category_name = fields.Char(
        string='Nom Catégorie',
        readonly=True
    )
    
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Société',
        readonly=True
    )
    
    def init(self):
        """Créer la vue SQL pour le dashboard."""
        tools.drop_view_if_exists(self.env.cr, self._table)
        
        query = """
            CREATE OR REPLACE VIEW stockex_inventory_dashboard AS (
                SELECT
                    ROW_NUMBER() OVER (ORDER BY inv.id DESC) AS id,
                    inv.id AS inventory_id,
                    inv.name AS inventory_name,
                    inv.date AS inventory_date,
                    inv.state AS inventory_state,
                    inv.company_id AS company_id,
                    COUNT(DISTINCT line.product_id) AS total_products,
                    COUNT(DISTINCT cat.id) AS total_categories,
                    COUNT(DISTINCT line.location_id) AS total_warehouses,
                    SUM(line.product_qty) AS total_quantity,
                    SUM(line.product_qty * line.standard_price) AS total_value,
                    AVG(line.standard_price) AS average_price,
                    cat.id AS category_id,
                    cat.name AS category_name
                FROM
                    stockex_stock_inventory inv
                    LEFT JOIN stockex_stock_inventory_line line ON line.inventory_id = inv.id
                    LEFT JOIN product_product prod ON prod.id = line.product_id
                    LEFT JOIN product_template tmpl ON tmpl.id = prod.product_tmpl_id
                    LEFT JOIN product_category cat ON cat.id = tmpl.categ_id
                WHERE
                    inv.state = 'done'
                GROUP BY
                    inv.id, inv.name, inv.date, inv.state, inv.company_id, cat.id, cat.name
            )
        """
        self.env.cr.execute(query)


class InventorySummary(models.Model):
    """Résumé global des inventaires."""
    _name = 'stockex.inventory.summary'
    _description = 'Résumé Inventaires'
    
    name = fields.Char(
        string='Nom',
        compute='_compute_name',
        store=False
    )
    
    # ==================== FILTRES ====================
    # Filtres temporels
    period_filter = fields.Selection([
        ('all', "Toute la période"),
        ('today', "Aujourd'hui"),
        ('week', "Cette Semaine"),
        ('month', "Ce Mois"),
        ('quarter', "Ce Trimestre"),
        ('year', "Cette Année"),
        ('last_30', "30 Derniers Jours"),
        ('last_90', "90 Derniers Jours"),
        ('last_year', "12 Derniers Mois"),
        ('custom', "Période Personnalisée"),
    ], string="📅 Période", default='all')
    
    date_from = fields.Date(string="Du")
    date_to = fields.Date(string="Au")
    
    # Filtres par catégorie
    category_ids = fields.Many2many(
        'product.category',
        'stockex_summary_category_rel',
        'summary_id',
        'category_id',
        string="📁 Catégories"
    )
    
    # Filtres par entrepôt/emplacement
    warehouse_ids = fields.Many2many(
        'stock.warehouse',
        'stockex_summary_warehouse_rel',
        'summary_id',
        'warehouse_id',
        string="🏭 Entrepôts"
    )
    
    location_ids = fields.Many2many(
        'stock.location',
        'stockex_summary_location_rel',
        'summary_id',
        'location_id',
        string="📍 Emplacements"
    )
    
    # Filtres par valeur
    value_range = fields.Selection([
        ('all', "Toutes valeurs"),
        ('high', "> 1M FCFA"),
        ('medium', "100K - 1M FCFA"),
        ('low', "< 100K FCFA"),
    ], string="💰 Plage de valeur", default='all')
    
    # Filtres écarts
    show_differences = fields.Selection([
        ('all', "Tous les écarts"),
        ('positive', "Écarts positifs seulement"),
        ('negative', "Écarts négatifs seulement"),
        ('significant', "Écarts > 5%"),
    ], string="📊 Écarts", default='all')
    
    # Indicateur de filtres actifs
    filters_active = fields.Boolean(
        string="Filtres actifs",
        compute='_compute_filters_active',
        store=False
    )
    filters_info = fields.Char(
        string="Info filtres",
        compute='_compute_filters_active',
        store=False
    )
    
    # Statistiques globales
    total_inventories = fields.Integer(
        string='Nombre d\'Inventaires',
        compute='_compute_global_stats'
    )
    total_inventories_done = fields.Integer(
        string='Inventaires Validés',
        compute='_compute_global_stats'
    )
    total_products_all = fields.Integer(
        string='Total Produits (Tous Inventaires)',
        compute='_compute_global_stats'
    )
    total_quantity_all = fields.Float(
        string='Quantité Totale (Tous Inventaires)',
        compute='_compute_global_stats'
    )
    total_value_all = fields.Float(
        string='Valeur Totale (Tous Inventaires)',
        compute='_compute_global_stats'
    )
    total_value_all_fcfa = fields.Char(
        string='Valeur Totale FCFA',
        compute='_compute_global_stats'
    )
    
    # Écarts d'inventaire
    total_differences_value = fields.Float(
        string='Valeur Totale des Écarts',
        compute='_compute_global_stats',
        help='Valeur totale des écarts (positifs + négatifs)'
    )
    total_differences_value_fcfa = fields.Char(
        string='Valeur Écarts FCFA',
        compute='_compute_global_stats'
    )
    positive_differences_value = fields.Float(
        string='Valeur Écarts Positifs',
        compute='_compute_global_stats'
    )
    positive_differences_value_fcfa = fields.Char(
        string='Écarts Positifs FCFA',
        compute='_compute_global_stats'
    )
    negative_differences_value = fields.Float(
        string='Valeur Écarts Négatifs',
        compute='_compute_global_stats'
    )
    negative_differences_value_fcfa = fields.Char(
        string='Écarts Négatifs FCFA',
        compute='_compute_global_stats'
    )
    
    # Dernier inventaire
    last_inventory_id = fields.Many2one(
        comodel_name='stockex.stock.inventory',
        string='Dernier Inventaire',
        compute='_compute_last_inventory'
    )
    last_inventory_date = fields.Date(
        string='Date Dernier Inventaire',
        compute='_compute_last_inventory'
    )
    last_inventory_products = fields.Integer(
        string='Produits (Dernier)',
        compute='_compute_last_inventory'
    )
    last_inventory_value = fields.Float(
        string='Valeur (Dernier)',
        compute='_compute_last_inventory'
    )
    last_inventory_value_fcfa = fields.Char(
        string='Valeur (Dernier) FCFA',
        compute='_compute_last_inventory'
    )
    
    # Top catégories
    top_categories_html = fields.Html(
        string='Top 10 Catégories',
        compute='_compute_top_categories'
    )
    
    # Top entrepôts
    top_warehouses_html = fields.Html(
        string='Top 10 Entrepôts',
        compute='_compute_top_warehouses'
    )
    
    # Évolution
    evolution_chart_html = fields.Html(
        string='Évolution',
        compute='_compute_evolution'
    )
    
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Société',
        default=lambda self: self.env.company
    )
    
    def _compute_name(self):
        """Nom du résumé."""
        for record in self:
            record.name = 'Dashboard Inventaire'
    
    @api.depends('period_filter', 'date_from', 'date_to', 'category_ids', 'warehouse_ids', 'location_ids', 'value_range', 'show_differences')
    def _compute_filters_active(self):
        """Calcule si des filtres sont actifs."""
        for record in self:
            filters = []
            
            if record.period_filter and record.period_filter != 'all':
                filters.append(dict(record._fields['period_filter'].selection).get(record.period_filter))
            
            if record.category_ids:
                filters.append(f"{len(record.category_ids)} catégorie(s)")
            
            if record.warehouse_ids:
                filters.append(f"{len(record.warehouse_ids)} entrepôt(s)")
            
            if record.location_ids:
                filters.append(f"{len(record.location_ids)} emplacement(s)")
            
            if record.value_range and record.value_range != 'all':
                filters.append(dict(record._fields['value_range'].selection).get(record.value_range))
            
            if record.show_differences and record.show_differences != 'all':
                filters.append(dict(record._fields['show_differences'].selection).get(record.show_differences))
            
            record.filters_active = len(filters) > 0
            record.filters_info = " | ".join(filters) if filters else "Aucun filtre actif"
    
    def _get_date_range(self):
        """Calcule la plage de dates selon le filtre de période."""
        self.ensure_one()
        from datetime import datetime, timedelta
        from dateutil.relativedelta import relativedelta
        
        today = fields.Date.today()
        
        if self.period_filter == 'custom':
            return self.date_from or False, self.date_to or False
        
        elif self.period_filter == 'today':
            return today, today
        
        elif self.period_filter == 'week':
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)
            return start, end
        
        elif self.period_filter == 'month':
            start = today.replace(day=1)
            next_month = start + relativedelta(months=1)
            end = next_month - timedelta(days=1)
            return start, end
        
        elif self.period_filter == 'quarter':
            quarter = (today.month - 1) // 3
            start = datetime(today.year, quarter * 3 + 1, 1).date()
            end = (start + relativedelta(months=3)) - timedelta(days=1)
            return start, end
        
        elif self.period_filter == 'year':
            start = datetime(today.year, 1, 1).date()
            end = datetime(today.year, 12, 31).date()
            return start, end
        
        elif self.period_filter == 'last_30':
            return today - timedelta(days=30), today
        
        elif self.period_filter == 'last_90':
            return today - timedelta(days=90), today
        
        elif self.period_filter == 'last_year':
            return today - timedelta(days=365), today
        
        else:  # 'all'
            return False, False
    
    def _get_filtered_inventories(self):
        """Retourne les inventaires filtrés selon les critères actifs."""
        self.ensure_one()
        
        domain = [('company_id', '=', self.company_id.id)]
        
        # Filtre temporel
        date_from, date_to = self._get_date_range()
        if date_from:
            domain.append(('date', '>=', date_from))
        if date_to:
            domain.append(('date', '<=', date_to))
        
        # Filtre par emplacement
        if self.location_ids:
            domain.append(('location_id', 'in', self.location_ids.ids))
        
        return self.env['stockex.stock.inventory'].search(domain)
    
    def _get_filtered_lines_domain(self):
        """Retourne le domaine SQL pour filtrer les lignes d'inventaire."""
        self.ensure_one()
        
        conditions = []
        params = []
        
        # Filtre temporel
        date_from, date_to = self._get_date_range()
        if date_from:
            conditions.append("inv.date >= %s")
            params.append(date_from)
        if date_to:
            conditions.append("inv.date <= %s")
            params.append(date_to)
        
        # Filtre par catégorie
        if self.category_ids:
            conditions.append("cat.id IN %s")
            params.append(tuple(self.category_ids.ids))
        
        # Filtre par entrepôt
        if self.warehouse_ids:
            # Récupérer les emplacements des entrepôts sélectionnés
            warehouse_locations = self.env['stock.location'].search([
                ('warehouse_id', 'in', self.warehouse_ids.ids)
            ])
            if warehouse_locations:
                conditions.append("line.location_id IN %s")
                params.append(tuple(warehouse_locations.ids))
        
        # Filtre par emplacement
        if self.location_ids:
            conditions.append("line.location_id IN %s")
            params.append(tuple(self.location_ids.ids))
        
        return conditions, params
    
    @api.depends('company_id', 'period_filter', 'date_from', 'date_to', 'category_ids', 'warehouse_ids', 'location_ids')
    def _compute_global_stats(self):
        """Calcule les statistiques globales avec filtres appliqués."""
        for record in self:
            # Utiliser les inventaires filtrés
            inventories = record._get_filtered_inventories()
            
            record.total_inventories = len(inventories)
            record.total_inventories_done = len(inventories.filtered(lambda i: i.state == 'done'))
            
            # Compter tous les produits et valeurs
            total_products = 0
            total_qty = 0
            total_val = 0
            total_diff_val = 0
            positive_diff_val = 0
            negative_diff_val = 0
            
            for inv in inventories.filtered(lambda i: i.state == 'done'):
                total_products += len(inv.line_ids.mapped('product_id'))
                total_qty += sum(inv.line_ids.mapped('product_qty'))
                total_val += sum(line.product_qty * line.standard_price for line in inv.line_ids)
                
                # Calculer les écarts
                for line in inv.line_ids:
                    diff = line.difference
                    diff_value = diff * line.standard_price
                    total_diff_val += diff_value
                    if diff_value > 0:
                        positive_diff_val += diff_value
                    elif diff_value < 0:
                        negative_diff_val += diff_value
            
            record.total_products_all = total_products
            record.total_quantity_all = total_qty
            record.total_value_all = total_val
            record.total_value_all_fcfa = f"{total_val:,.0f} FCFA" if total_val else "0 FCFA"
            
            # Écarts
            record.total_differences_value = total_diff_val
            record.total_differences_value_fcfa = f"{total_diff_val:,.0f} FCFA"
            record.positive_differences_value = positive_diff_val
            record.positive_differences_value_fcfa = f"{positive_diff_val:,.0f} FCFA"
            record.negative_differences_value = negative_diff_val
            record.negative_differences_value_fcfa = f"{negative_diff_val:,.0f} FCFA"
    
    @api.depends('company_id')
    def _compute_last_inventory(self):
        """Calcule les stats du dernier inventaire."""
        for record in self:
            last_inv = self.env['stockex.stock.inventory'].search([
                ('company_id', '=', record.company_id.id),
                ('state', '=', 'done')
            ], limit=1, order='date desc, id desc')
            
            if last_inv:
                record.last_inventory_id = last_inv.id
                record.last_inventory_date = last_inv.date
                record.last_inventory_products = len(last_inv.line_ids.mapped('product_id'))
                value = sum(line.product_qty * line.standard_price for line in last_inv.line_ids)
                record.last_inventory_value = value
                record.last_inventory_value_fcfa = f"{value:,.2f} FCFA"
            else:
                record.last_inventory_id = False
                record.last_inventory_date = False
                record.last_inventory_products = 0
                record.last_inventory_value = 0
                record.last_inventory_value_fcfa = "0 FCFA"
    
    @api.depends('company_id', 'period_filter', 'date_from', 'date_to', 'category_ids', 'warehouse_ids', 'location_ids')
    def _compute_top_categories(self):
        """Calcule le top 10 des catégories avec filtres appliqués."""
        for record in self:
            # Construire la requête avec filtres
            conditions, params = record._get_filtered_lines_domain()
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            query = f"""
                SELECT 
                    cat.name,
                    COUNT(DISTINCT line.product_id) as nb_products,
                    SUM(line.product_qty) as total_qty,
                    SUM(line.product_qty * line.standard_price) as total_value
                FROM stockex_stock_inventory_line line
                JOIN stockex_stock_inventory inv ON inv.id = line.inventory_id
                JOIN product_product prod ON prod.id = line.product_id
                JOIN product_template tmpl ON tmpl.id = prod.product_tmpl_id
                JOIN product_category cat ON cat.id = tmpl.categ_id
                WHERE inv.state = 'done' AND inv.company_id = %s AND {where_clause}
                GROUP BY cat.name
                ORDER BY total_value DESC
                LIMIT 5
            """
            all_params = [record.company_id.id] + params
            self.env.cr.execute(query, all_params)
            results = self.env.cr.fetchall()
            
            html = """
            <table class='table table-sm table-striped mb-0'>
                <thead>
                    <tr>
                        <th>Catégorie</th>
                        <th class='text-end'>Valeur</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for cat_name, nb_prod, qty, value in results:
                html += f"""
                <tr>
                    <td><small><strong>{cat_name or 'Sans catégorie'}</strong></small></td>
                    <td class='text-end'><small>{value:,.0f} FCFA</small></td>
                </tr>
                """
            
            html += """
                </tbody>
            </table>
            """
            
            record.top_categories_html = html if results else "<p class='text-muted'>Aucune donnée disponible</p>"
    
    @api.depends('company_id', 'period_filter', 'date_from', 'date_to', 'category_ids', 'warehouse_ids', 'location_ids')
    def _compute_top_warehouses(self):
        """Calcule le top 10 des entrepôts avec filtres appliqués."""
        for record in self:
            # Construire la requête avec filtres
            conditions, params = record._get_filtered_lines_domain()
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            query = f"""
                SELECT 
                    loc.complete_name,
                    COUNT(DISTINCT line.product_id) as nb_products,
                    SUM(line.product_qty) as total_qty,
                    SUM(line.product_qty * line.standard_price) as total_value
                FROM stockex_stock_inventory_line line
                JOIN stockex_stock_inventory inv ON inv.id = line.inventory_id
                JOIN stock_location loc ON loc.id = line.location_id
                WHERE inv.state = 'done' AND inv.company_id = %s AND {where_clause}
                GROUP BY loc.complete_name
                ORDER BY total_value DESC
                LIMIT 5
            """
            all_params = [record.company_id.id] + params
            self.env.cr.execute(query, all_params)
            results = self.env.cr.fetchall()
            
            html = """
            <table class='table table-sm table-striped mb-0'>
                <thead>
                    <tr>
                        <th>Entrepôt</th>
                        <th class='text-end'>Valeur</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for loc_name, nb_prod, qty, value in results:
                # Raccourcir le nom si trop long
                display_name = loc_name if len(loc_name) <= 25 else loc_name[:22] + '...'
                html += f"""
                <tr>
                    <td><small><strong>{display_name}</strong></small></td>
                    <td class='text-end'><small>{value:,.0f} FCFA</small></td>
                </tr>
                """
            
            html += """
                </tbody>
            </table>
            """
            
            record.top_warehouses_html = html if results else "<p class='text-muted'>Aucune donnée disponible</p>"
    
    @api.depends('company_id', 'period_filter', 'date_from', 'date_to', 'category_ids', 'warehouse_ids', 'location_ids')
    def _compute_evolution(self):
        """Calcule l'évolution sur les 12 derniers inventaires avec filtres appliqués."""
        for record in self:
            # Construire la requête avec filtres
            conditions, params = record._get_filtered_lines_domain()
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            query = f"""
                SELECT 
                    inv.name,
                    inv.date,
                    COUNT(DISTINCT line.product_id) as nb_products,
                    SUM(line.product_qty * line.standard_price) as total_value
                FROM stockex_stock_inventory inv
                LEFT JOIN stockex_stock_inventory_line line ON line.inventory_id = inv.id
                LEFT JOIN product_product prod ON prod.id = line.product_id
                LEFT JOIN product_template tmpl ON tmpl.id = prod.product_tmpl_id
                LEFT JOIN product_category cat ON cat.id = tmpl.categ_id
                WHERE inv.state = 'done' AND inv.company_id = %s AND {where_clause}
                GROUP BY inv.id, inv.name, inv.date
                ORDER BY inv.date DESC, inv.id DESC
                LIMIT 12
            """
            all_params = [record.company_id.id] + params
            self.env.cr.execute(query, all_params)
            results = self.env.cr.fetchall()
            
            if results:
                html = """
                <table class='table table-sm'>
                    <thead class='bg-info text-white'>
                        <tr>
                            <th>Inventaire</th>
                            <th>Date</th>
                            <th class='text-end'>Produits</th>
                            <th class='text-end'>Valeur</th>
                        </tr>
                    </thead>
                    <tbody>
                """
                
                for name, date, nb_prod, value in reversed(results):
                    html += f"""
                    <tr>
                        <td>{name}</td>
                        <td>{date}</td>
                        <td class='text-end'>{int(nb_prod)}</td>
                        <td class='text-end'>{value:,.2f} FCFA</td>
                    </tr>
                    """
                
                html += """
                    </tbody>
                </table>
                """
                record.evolution_chart_html = html
            else:
                record.evolution_chart_html = "<p class='text-muted'>Aucun historique disponible</p>"
    
    def action_view_inventories(self):
        """Ouvre la liste des inventaires filtrés."""
        self.ensure_one()
        inventories = self._get_filtered_inventories()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Inventaires',
            'res_model': 'stockex.stock.inventory',
            'view_mode': 'list,form',
            'domain': [('id', 'in', inventories.ids)],
            'context': {'default_company_id': self.company_id.id},
        }
    
    def action_apply_filters(self):
        """Applique les filtres et recharge le dashboard."""
        self.ensure_one()
        # Les computed fields se mettront à jour automatiquement
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': '🔍 Filtres Appliqués',
                'message': self.filters_info,
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_reset_filters(self):
        """Réinitialise tous les filtres."""
        self.ensure_one()
        self.write({
            'period_filter': 'all',
            'date_from': False,
            'date_to': False,
            'category_ids': [(5, 0, 0)],  # Clear all
            'warehouse_ids': [(5, 0, 0)],
            'location_ids': [(5, 0, 0)],
            'value_range': 'all',
            'show_differences': 'all',
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': '🔄 Filtres Réinitialisés',
                'message': 'Tous les filtres ont été supprimés',
                'type': 'info',
                'sticky': False,
            }
        }
    
    def action_filter_this_month(self):
        """Filtre rapide : Ce mois."""
        self.ensure_one()
        self.period_filter = 'month'
        return self.action_apply_filters()
    
    def action_filter_high_value(self):
        """Filtre rapide : Haute valeur (> 1M FCFA)."""
        self.ensure_one()
        self.value_range = 'high'
        return self.action_apply_filters()
    
    def action_filter_significant_differences(self):
        """Filtre rapide : Écarts importants (> 5%)."""
        self.ensure_one()
        self.show_differences = 'significant'
        return self.action_apply_filters()
