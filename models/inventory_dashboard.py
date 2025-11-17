# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, tools

_logger = logging.getLogger(__name__)


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
    
    # Valeurs de stock arrêté (stock initial)
    current_stock_value = fields.Float(
        string='Valeur Stock Arrêté (avec décote)',
        compute='_compute_current_stock_value',
        help='Valeur du stock avec décote appliquée selon rotation'
    )
    current_stock_value_fcfa = fields.Char(
        string='Valeur Stock Arrêté FCFA (avec décote)',
        compute='_compute_current_stock_value'
    )
    current_stock_value_no_depreciation = fields.Float(
        string='Valeur Stock Arrêté (sans décote)',
        compute='_compute_current_stock_value',
        help='Valeur du stock sans décote appliquée'
    )
    current_stock_value_no_depreciation_fcfa = fields.Char(
        string='Valeur Stock Arrêté FCFA (sans décote)',
        compute='_compute_current_stock_value'
    )
    initial_stock_date = fields.Date(
        string='Date Stock Initial',
        compute='_compute_current_stock_value',
        help='Date du premier inventaire de stock initial'
    )
    
    # Valeurs des stocks inventoriés (dernier inventaire validé)
    inventoried_stock_value = fields.Float(
        string='Valeur Stocks Inventoriés',
        compute='_compute_inventoried_stock_value',
        help='Valeur des stocks selon le dernier inventaire validé'
    )
    inventoried_stock_value_fcfa = fields.Char(
        string='Valeur Stocks Inventoriés FCFA',
        compute='_compute_inventoried_stock_value'
    )
    
    # Écart entre stock actuel et inventorié
    stock_value_difference = fields.Float(
        string='Écart Valeur Stock',
        compute='_compute_stock_value_difference',
        help='Différence entre stock actuel et stocks inventoriés'
    )
    stock_value_difference_fcfa = fields.Char(
        string='Écart Valeur Stock FCFA',
        compute='_compute_stock_value_difference'
    )
    stock_value_difference_percent = fields.Float(
        string='Écart Valeur Stock %',
        compute='_compute_stock_value_difference',
        help='Pourcentage de différence entre stock actuel et stocks inventoriés'
    )
    
    # Valorisation par entrepôt (en temps réel)
    warehouse_valuation_html = fields.Html(
        string='Valorisation par Entrepôt',
        compute='_compute_warehouse_valuation'
    )
    
    inventoried_warehouse_valuation_html = fields.Html(
        string='Valorisation Inventoriée par Entrepôt',
        compute='_compute_inventoried_warehouse_valuation'
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
    company_currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Devise Société',
        related='company_id.currency_id',
        store=False
    )
    
    # Indicateur si règle de valorisation = Coût économique
    is_economic_valuation = fields.Boolean(
        string='Valorisation Économique Active',
        compute='_compute_is_economic_valuation',
        store=False
    )
    
    # Nouveaux champs pour graphiques dashboard
    warehouse_gaps_chart_data = fields.Text(
        string='Données graphique écarts par entrepôt',
        compute='_compute_warehouse_gaps_chart',
        help='Données JSON pour le graphique à barres des écarts par entrepôt'
    )
    category_value_chart_data = fields.Text(
        string='Données graphique valeur par famille',
        compute='_compute_category_value_chart',
        help='Données JSON pour le graphique donut valeur par famille'
    )
    inventory_precision = fields.Float(
        string='Précision inventaire (%)',
        compute='_compute_inventory_precision',
        help='Précision = 1 - (|Σ écarts quantités| / Σ quantités système)'
    )
    obsolescence_count = fields.Integer(
        string='Articles obsolètes (nb)',
        compute='_compute_obsolescence',
        help='Nombre d\'articles obsolètes (rotation lente ou stock mort)'
    )
    obsolescence_value = fields.Float(
        string='Valeur articles obsolètes',
        compute='_compute_obsolescence'
    )
    
    # Analyse stock initial (pour import Excel)
    initial_stock_analysis_html = fields.Html(
        string='Analyse Stock Initial',
        compute='_compute_initial_stock_analysis',
        help='Analyse détaillée du stock initial (entrepôts, catégories, concentration)'
    )
    initial_stock_total_value = fields.Float(
        string='Valeur totale stock initial',
        compute='_compute_initial_stock_analysis'
    )
    initial_stock_products_count = fields.Integer(
        string='Nombre produits stock initial',
        compute='_compute_initial_stock_analysis'
    )
    initial_stock_no_price_count = fields.Integer(
        string='Articles sans prix',
        compute='_compute_initial_stock_analysis'
    )
    initial_stock_top3_concentration = fields.Float(
        string='Concentration TOP 3 entrepôts (%)',
        compute='_compute_initial_stock_analysis',
        help='% de valeur concentrée dans les 3 premiers entrepôts'
    )
    initial_stock_top_category_pct = fields.Float(
        string='% catégorie dominante',
        compute='_compute_initial_stock_analysis'
    )
    
    def _get_cost_price(self, product, line_price=None):
        """Retourne le coût selon la règle de valorisation configurée."""
        rule = self.env['ir.config_parameter'].sudo().get_param('stockex.valuation_rule', 'standard')
        
        # Préférer line_price s'il est fourni et non nul
        if line_price and line_price > 0:
            return line_price
            
        if rule == 'economic':
            layer = self.env['stock.valuation.layer'].search([
                ('product_id', '=', product.id),
                ('company_id', '=', self.company_id.id),
            ], limit=1, order='create_date desc')
            if layer and (layer.unit_cost or layer.value):
                unit = layer.unit_cost or (layer.value / layer.quantity if layer.quantity else 0.0)
                if unit and unit > 0:
                    return unit
        
        # Sinon standard_price du produit
        return product.standard_price or 0.0
    
    def _get_product_valuation_price(self, product):
        """Retourne le prix de valorisation selon la règle Stockex avec décote optionnelle.
        
        Cette méthode calcule le prix de valorisation d'un produit en 2 étapes :
        1. Calcul du prix de base selon la règle configurée (standard ou économique réel)
        2. Application de la décote selon rotation si activée
        
        Args:
            product: recordset product.product
            
        Returns:
            float: Prix de valorisation final (après décote si applicable)
        """
        self.ensure_one()
        
        if not product:
            return 0.0
        
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
    
    @api.depends('company_id')
    def _compute_initial_stock_analysis(self):
        """Analyse du stock initial (premier inventaire marqué is_initial_stock)."""
        for record in self:
            try:
                # Chercher les inventaires de stock initial
                initial_inventories = self.env['stockex.stock.inventory'].search([
                    ('company_id', '=', record.company_id.id),
                    ('is_initial_stock', '=', True),
                ])
                
                if not initial_inventories:
                    record.initial_stock_analysis_html = "<p class='text-muted'>Aucun stock initial trouvé</p>"
                    record.initial_stock_total_value = 0
                    record.initial_stock_products_count = 0
                    record.initial_stock_no_price_count = 0
                    continue
                
                # Récupérer toutes les lignes
                lines = self.env['stockex.stock.inventory.line'].search([
                    ('inventory_id', 'in', initial_inventories.ids)
                ])
                
                if not lines:
                    record.initial_stock_analysis_html = "<p class='text-muted'>Aucune ligne de stock initial</p>"
                    record.initial_stock_total_value = 0
                    record.initial_stock_products_count = 0
                    record.initial_stock_no_price_count = 0
                    continue
                
                # Statistiques globales
                total_value = 0.0
                products_set = set()
                no_price_count = 0
                
                # Agrégations par entrepôt
                by_warehouse = {}
                # Agrégations par catégorie
                by_category = {}
                
                for line in lines:
                    product = line.product_id
                    products_set.add(product.id)
                    
                    qty = line.product_qty or 0.0
                    price = record._get_cost_price(product, line.standard_price)
                    
                    if price == 0:
                        no_price_count += 1
                    
                    value = qty * price
                    total_value += value
                    
                    # Par entrepôt
                    warehouse = line.location_id.warehouse_id
                    wh_name = warehouse.name if warehouse else 'Sans entrepôt'
                    if wh_name not in by_warehouse:
                        by_warehouse[wh_name] = {'value': 0.0, 'lines': 0}
                    by_warehouse[wh_name]['value'] += value
                    by_warehouse[wh_name]['lines'] += 1
                    
                    # Par catégorie
                    category = product.categ_id
                    cat_name = category.name if category else 'Sans catégorie'
                    if cat_name not in by_category:
                        by_category[cat_name] = {'value': 0.0, 'lines': 0}
                    by_category[cat_name]['value'] += value
                    by_category[cat_name]['lines'] += 1
                
                # Stocker les stats
                record.initial_stock_total_value = total_value
                record.initial_stock_products_count = len(products_set)
                record.initial_stock_no_price_count = no_price_count
                
                # Calcul concentration TOP 3 entrepôts
                sorted_warehouses = sorted(by_warehouse.items(), key=lambda x: x[1]['value'], reverse=True)
                top3_value = sum(wh[1]['value'] for wh in sorted_warehouses[:3])
                top3_concentration = (top3_value / total_value * 100) if total_value > 0 else 0
                record.initial_stock_top3_concentration = top3_concentration
                
                # Calcul % catégorie dominante
                sorted_categories = sorted(by_category.items(), key=lambda x: x[1]['value'], reverse=True)
                top_category_pct = (sorted_categories[0][1]['value'] / total_value * 100) if sorted_categories and total_value > 0 else 0
                record.initial_stock_top_category_pct = top_category_pct
                
                # Construire HTML
                html = f"""
                <div class="p-3">
                    <!-- Points d'attention -->
                    <div class="row mb-4">
                        <div class="col-12 mb-3">
                            <h5 class="mb-0 fw-bold">⚠️ Points d'Attention</h5>
                            <hr class="mt-2 mb-3"/>
                        </div>
                        <div class="col-md-3 mb-3">
                            <div class="card border-{'warning' if no_price_count > 0 else 'success'} shadow-sm h-100">
                                <div class="card-body text-center p-3">
                                    <div class="mb-2">
                                        <i class="fa fa-tags fa-3x text-{'warning' if no_price_count > 0 else 'success'}"></i>
                                    </div>
                                    <p class="text-muted mb-1 small">Articles sans prix</p>
                                    <h2 class="mb-0 fw-bold text-{'warning' if no_price_count > 0 else 'success'}">{no_price_count}</h2>
                                    <small class="text-muted">{int(no_price_count/len(lines)*100)}% des lignes</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3 mb-3">
                            <div class="card border-{'danger' if top3_concentration > 80 else 'warning' if top3_concentration > 60 else 'success'} shadow-sm h-100">
                                <div class="card-body text-center p-3">
                                    <div class="mb-2">
                                        <i class="fa fa-chart-pie fa-3x text-{'danger' if top3_concentration > 80 else 'warning' if top3_concentration > 60 else 'success'}"></i>
                                    </div>
                                    <p class="text-muted mb-1 small">Concentration TOP 3</p>
                                    <h2 class="mb-0 fw-bold text-{'danger' if top3_concentration > 80 else 'warning' if top3_concentration > 60 else 'success'}">{int(top3_concentration)}%</h2>
                                    <small class="text-muted">{'Très concentré' if top3_concentration > 80 else 'Concentré' if top3_concentration > 60 else 'Équilibré'}</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3 mb-3">
                            <div class="card border-{'warning' if top_category_pct > 40 else 'success'} shadow-sm h-100">
                                <div class="card-body text-center p-3">
                                    <div class="mb-2">
                                        <i class="fa fa-folder fa-3x text-{'warning' if top_category_pct > 40 else 'success'}"></i>
                                    </div>
                                    <p class="text-muted mb-1 small">Catégorie dominante</p>
                                    <h2 class="mb-0 fw-bold text-{'warning' if top_category_pct > 40 else 'success'}">{int(top_category_pct)}%</h2>
                                    <small class="text-muted text-truncate d-block">{sorted_categories[0][0] if sorted_categories else 'N/A'}</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3 mb-3">
                            <div class="card border-info shadow-sm h-100">
                                <div class="card-body text-center p-3">
                                    <div class="mb-2">
                                        <i class="fa fa-warehouse fa-3x text-info"></i>
                                    </div>
                                    <p class="text-muted mb-1 small">Entrepôts actifs</p>
                                    <h2 class="mb-0 fw-bold text-info">{len(by_warehouse)}</h2>
                                    <small class="text-muted">{len(by_category)} catégories</small>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- KPIs principaux -->
                    <div class="row mb-4">
                        <div class="col-12 mb-3">
                            <h5 class="mb-0 fw-bold">📊 Indicateurs Clés</h5>
                            <hr class="mt-2 mb-3"/>
                        </div>
                        <div class="col-md-3 mb-3">
                            <div class="card bg-gradient text-white shadow h-100" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                                <div class="card-body p-3">
                                    <div class="d-flex align-items-center">
                                        <div class="flex-grow-1">
                                            <p class="mb-1 small opacity-75">Valeur Totale</p>
                                            <h3 class="mb-0 fw-bold">{int(total_value):,}</h3>
                                            <small class="opacity-75">FCFA</small>
                                        </div>
                                        <div class="ms-2">
                                            <i class="fa fa-wallet fa-3x opacity-50"></i>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3 mb-3">
                            <div class="card bg-gradient text-white shadow h-100" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                                <div class="card-body p-3">
                                    <div class="d-flex align-items-center">
                                        <div class="flex-grow-1">
                                            <p class="mb-1 small opacity-75">Nbre de références</p>
                                            <h3 class="mb-0 fw-bold">{len(products_set):,}</h3>
                                            <small class="opacity-75">produits</small>
                                        </div>
                                        <div class="ms-2">
                                            <i class="fa fa-box fa-3x opacity-50"></i>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3 mb-3">
                            <div class="card bg-gradient text-white shadow h-100" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
                                <div class="card-body p-3">
                                    <div class="d-flex align-items-center">
                                        <div class="flex-grow-1">
                                            <p class="mb-1 small opacity-75">Sans Prix</p>
                                            <h3 class="mb-0 fw-bold">{no_price_count}</h3>
                                            <small class="opacity-75">à valoriser</small>
                                        </div>
                                        <div class="ms-2">
                                            <i class="fa fa-exclamation-triangle fa-3x opacity-50"></i>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3 mb-3">
                            <div class="card bg-gradient text-white shadow h-100" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                                <div class="card-body p-3">
                                    <div class="d-flex align-items-center">
                                        <div class="flex-grow-1">
                                            <p class="mb-1 small opacity-75">Lignes</p>
                                            <h3 class="mb-0 fw-bold">{len(lines):,}</h3>
                                            <small class="opacity-75">entrées</small>
                                        </div>
                                        <div class="ms-2">
                                            <i class="fa fa-list fa-3x opacity-50"></i>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Tableaux -->
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <div class="card shadow-sm h-100">
                                <div class="card-header bg-white border-bottom">
                                    <h6 class="mb-0 fw-bold">🏢 Top 10 Entrepôts</h6>
                                </div>
                                <div class="card-body p-0">
                                    <div class="table-responsive">
                                        <table class="table table-hover mb-0">
                                            <thead class="table-light">
                                                <tr>
                                                    <th class="border-0">Entrepôt</th>
                                                    <th class="text-end border-0">Valeur (FCFA)</th>
                                                    <th class="text-end border-0">% Total</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                """
                
                # Trier par valeur décroissante
                sorted_warehouses = sorted(by_warehouse.items(), key=lambda x: x[1]['value'], reverse=True)
                for wh_name, wh_data in sorted_warehouses[:10]:  # Top 10
                    pct = int((wh_data['value'] / total_value * 100)) if total_value > 0 else 0
                    html += f"""
                                                <tr>
                                                    <td class="fw-medium">{wh_name}</td>
                                                    <td class="text-end">{int(wh_data['value']):,}</td>
                                                    <td class="text-end"><span class="badge bg-primary">{pct}%</span></td>
                                                </tr>
                    """
                
                html += """
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-md-6 mb-3">
                            <div class="card shadow-sm h-100">
                                <div class="card-header bg-white border-bottom">
                                    <h6 class="mb-0 fw-bold">📁 Top 10 Catégories</h6>
                                </div>
                                <div class="card-body p-0">
                                    <div class="table-responsive">
                                        <table class="table table-hover mb-0">
                                            <thead class="table-light">
                                                <tr>
                                                    <th class="border-0">Catégorie</th>
                                                    <th class="text-end border-0">Valeur (FCFA)</th>
                                                    <th class="text-end border-0">% Total</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                """
                
                # Trier par valeur décroissante
                sorted_categories = sorted(by_category.items(), key=lambda x: x[1]['value'], reverse=True)
                for cat_name, cat_data in sorted_categories[:10]:  # Top 10
                    pct = int((cat_data['value'] / total_value * 100)) if total_value > 0 else 0
                    html += f"""
                                                <tr>
                                                    <td class="fw-medium">{cat_name}</td>
                                                    <td class="text-end">{int(cat_data['value']):,}</td>
                                                    <td class="text-end"><span class="badge bg-success">{pct}%</span></td>
                                                </tr>
                    """
                
                html += """
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                """
                
                record.initial_stock_analysis_html = html
                
            except Exception as e:
                _logger.error(f"Erreur lors de l'analyse du stock initial: {e}")
                import traceback
                _logger.error(traceback.format_exc())
                record.initial_stock_analysis_html = f"<p class='text-danger'>Erreur: {str(e)}</p>"
                record.initial_stock_total_value = 0
                record.initial_stock_products_count = 0
                record.initial_stock_no_price_count = 0
    
    def _get_depreciation_coefficient(self, product):
        """Retourne le coefficient de décote selon la rotation du produit.
        
        Returns:
            float: Coefficient (1.0 = 0% décote, 0.6 = 40%, 0.0 = 100%)
        """
        self.ensure_one()
        
        if not product:
            return 1.0
        
        ICP = self.env['ir.config_parameter'].sudo()
        active_days = int(ICP.get_param('stockex.depreciation_active_days', '365'))
        slow_days = int(ICP.get_param('stockex.depreciation_slow_days', '1095'))
        slow_rate = float(ICP.get_param('stockex.depreciation_slow_rate', '40.0'))
        dead_rate = float(ICP.get_param('stockex.depreciation_dead_rate', '100.0'))
        
        # Chercher le dernier mouvement
        StockMove = self.env['stock.move']
        last_move = StockMove.search([
            ('product_id', '=', product.id),
            ('state', '=', 'done'),
        ], limit=1, order='date desc')
        
        if not last_move:
            return 1.0 - (dead_rate / 100.0)
        
        from datetime import datetime
        
        # Convertir last_move.date en date si c'est un datetime
        if isinstance(last_move.date, datetime):
            last_move_date = last_move.date.date()
        else:
            last_move_date = last_move.date
        
        now = datetime.now().date()
        days_since_last_move = (now - last_move_date).days
        
        if days_since_last_move <= active_days:
            return 1.0  # Stock actif
        elif days_since_last_move <= slow_days:
            return 1.0 - (slow_rate / 100.0)  # Rotation lente
        else:
            return 1.0 - (dead_rate / 100.0)  # Stock mort

    def _compute_name(self):
        """Nom du résumé."""
        for record in self:
            record.name = 'Dashboard Inventaire'
    
    def _compute_is_economic_valuation(self):
        """Vérifie si la règle de valorisation est 'Coût économique'."""
        for record in self:
            ICP = self.env['ir.config_parameter'].sudo()
            valuation_rule = ICP.get_param('stockex.valuation_rule', 'standard')
            record.is_economic_valuation = (valuation_rule == 'economic')
    
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
        """Calcule les statistiques globales avec filtres appliqués (optimisé)."""
        for record in self:
            try:
                # Construire le domaine des inventaires sans charger les enregistrements
                inv_domain = [('company_id', '=', record.company_id.id)]
                date_from, date_to = record._get_date_range()
                if date_from:
                    inv_domain.append(('date', '>=', date_from))
                if date_to:
                    inv_domain.append(('date', '<=', date_to))
                # Compter les inventaires
                record.total_inventories = self.env['stockex.stock.inventory'].search_count(inv_domain)
                done_domain = inv_domain + [('state', '=', 'done')]
                record.total_inventories_done = self.env['stockex.stock.inventory'].search_count(done_domain)

                # Récupérer les IDs d'inventaires pour agréger les lignes en une seule requête
                inventories = self.env['stockex.stock.inventory'].search(inv_domain)
                if not inventories:
                    record.total_products_all = 0
                    record.total_quantity_all = 0.0
                    record.total_value_all = 0.0
                    record.total_value_all_fcfa = "0 FCFA"
                    record.total_differences_value = 0.0
                    record.total_differences_value_fcfa = "0 FCFA"
                    record.positive_differences_value = 0.0
                    record.positive_differences_value_fcfa = "0 FCFA"
                    record.negative_differences_value = 0.0
                    record.negative_differences_value_fcfa = "0 FCFA"
                    continue

                # Domaine des lignes
                lines_domain = [('inventory_id', 'in', inventories.ids)]
                # Filtre par catégories
                if record.category_ids:
                    lines_domain.append(('product_id.categ_id', 'in', record.category_ids.ids))
                # Filtre par entrepôts -> emplacements internes des entrepôts sélectionnés
                if record.warehouse_ids:
                    warehouse_locations = self.env['stock.location'].search([
                        ('warehouse_id', 'in', record.warehouse_ids.ids),
                        ('usage', '=', 'internal'),
                    ])
                    if warehouse_locations:
                        lines_domain.append(('location_id', 'in', warehouse_locations.ids))
                # Filtre par emplacements
                if record.location_ids:
                    lines_domain.append(('location_id', 'in', record.location_ids.ids))

                lines = self.env['stockex.stock.inventory.line'].search(lines_domain)

                # Agrégations
                total_products = len(lines.mapped('product_id'))
                total_qty = sum(lines.mapped('product_qty'))
                total_val = 0.0
                total_diff_val = 0.0
                positive_diff_val = 0.0
                negative_diff_val = 0.0

                # Précharger produits pour éviter accès répétés
                products = {line.product_id.id: line.product_id for line in lines}

                for line in lines:
                    product = products.get(line.product_id.id) or line.product_id
                    price = record._get_cost_price(product, line.standard_price)
                    qty = line.product_qty or 0.0
                    val = qty * price
                    total_val += val

                    # Écarts (respecter la règle stock initial)
                    diff = 0.0 if line.inventory_id.is_initial_stock else (line.difference or 0.0)
                    diff_val = diff * price
                    total_diff_val += diff_val
                    if diff_val > 0:
                        positive_diff_val += diff_val
                    elif diff_val < 0:
                        negative_diff_val += diff_val

                record.total_products_all = total_products
                record.total_quantity_all = total_qty
                record.total_value_all = total_val
                record.total_value_all_fcfa = f"{total_val:,.0f} FCFA" if total_val else "0 FCFA"

                record.total_differences_value = total_diff_val
                record.total_differences_value_fcfa = f"{total_diff_val:,.0f} FCFA"
                record.positive_differences_value = positive_diff_val
                record.positive_differences_value_fcfa = f"{positive_diff_val:,.0f} FCFA"
                record.negative_differences_value = negative_diff_val
                record.negative_differences_value_fcfa = f"{negative_diff_val:,.0f} FCFA"

            except Exception as e:
                _logger.error(f"Erreur lors du calcul des statistiques globales (optimisé): {e}")
                if hasattr(self.env, 'cr'):
                    self.env.cr.rollback()
                record.total_inventories = 0
                record.total_inventories_done = 0
                record.total_products_all = 0
                record.total_quantity_all = 0
                record.total_value_all = 0
                record.total_value_all_fcfa = "0 FCFA"
                record.total_differences_value = 0
                record.total_differences_value_fcfa = "0 FCFA"
                record.positive_differences_value = 0
                record.positive_differences_value_fcfa = "0 FCFA"
                record.negative_differences_value = 0
                record.negative_differences_value_fcfa = "0 FCFA"
    
    @api.depends('company_id')
    def _compute_current_stock_value(self):
        """Calcule la valeur actuelle du stock en temps réel (tous les quants internes)."""
        for record in self:
            try:
                # Récupérer la date du premier inventaire de stock initial pour l'affichage
                initial_inventory = self.env['stockex.stock.inventory'].search([
                    ('company_id', '=', record.company_id.id),
                    ('is_initial_stock', '=', True),
                ], limit=1, order='date asc, id asc')
                
                if initial_inventory:
                    record.initial_stock_date = initial_inventory.date
                else:
                    record.initial_stock_date = False
                
                # Emplacements internes de la société
                locations = self.env['stock.location'].search([
                    ('company_id', '=', record.company_id.id),
                    ('usage', '=', 'internal'),
                ])
                
                # Récupérer tous les quants avec quantité > 0
                quants = self.env['stock.quant'].search([
                    ('company_id', '=', record.company_id.id),
                    ('location_id', 'in', locations.ids),
                    ('quantity', '>', 0),
                ])
                
                # Calculer valeur avec décote ET sans décote
                total_value_with_depreciation = 0.0
                total_value_no_depreciation = 0.0
                
                ICP = self.env['ir.config_parameter'].sudo()
                apply_depreciation = ICP.get_param('stockex.apply_depreciation', 'False') == 'True'
                
                for quant in quants:
                    # Prix avec décote (si activée)
                    price_with_depreciation = record._get_product_valuation_price(quant.product_id)
                    total_value_with_depreciation += quant.quantity * price_with_depreciation
                    
                    # Prix sans décote (toujours calculé)
                    if apply_depreciation:
                        # Calculer le prix de base sans décote
                        rule = ICP.get_param('stockex.valuation_rule', 'standard')
                        base_price = 0.0
                        
                        if rule == 'economic':
                            ValuationLayer = self.env['stock.valuation.layer']
                            layer = ValuationLayer.search([
                                ('product_id', '=', quant.product_id.id),
                                ('company_id', '=', record.company_id.id),
                            ], limit=1, order='create_date desc')
                            
                            if layer and (layer.unit_cost or layer.value):
                                unit = layer.unit_cost or (layer.value / layer.quantity if layer.quantity else 0.0)
                                if unit and unit > 0:
                                    base_price = unit
                        
                        if base_price == 0.0:
                            base_price = quant.product_id.standard_price or 0.0
                        
                        total_value_no_depreciation += quant.quantity * base_price
                    else:
                        # Si décote non activée, les deux valeurs sont identiques
                        total_value_no_depreciation = total_value_with_depreciation
                
                record.current_stock_value = total_value_with_depreciation
                record.current_stock_value_fcfa = f"{total_value_with_depreciation:,.0f} FCFA"
                record.current_stock_value_no_depreciation = total_value_no_depreciation
                record.current_stock_value_no_depreciation_fcfa = f"{total_value_no_depreciation:,.0f} FCFA"
                
                _logger.info(f"Valeur stock: Avec décote={total_value_with_depreciation:,.0f} FCFA, Sans décote={total_value_no_depreciation:,.0f} FCFA ({len(quants)} quants)")
            except Exception as e:
                _logger.error(f"Erreur lors du calcul de la valeur du stock actuel: {e}")
                import traceback
                _logger.error(traceback.format_exc())
                record.initial_stock_date = False
                record.current_stock_value = 0
                record.current_stock_value_fcfa = "0 FCFA"
                record.current_stock_value_no_depreciation = 0
                record.current_stock_value_no_depreciation_fcfa = "0 FCFA"
    
    @api.depends('company_id')
    def _compute_inventoried_stock_value(self):
        """Calcule la valeur des stocks selon le dernier inventaire validé (optimisé)."""
        for record in self:
            try:
                # Récupérer le dernier inventaire validé (hors stock initial)
                last_inventory = self.env['stockex.stock.inventory'].search([
                    ('company_id', '=', record.company_id.id),
                    ('state', 'in', ['draft','in_progress','pending_approval','approved','done']),
                    ('is_initial_stock', '=', False),
                ], limit=1, order='date desc, id desc')

                if last_inventory:
                    # Agréger les quantités par produit
                    grouped = self.env['stockex.stock.inventory.line'].read_group(
                        [('inventory_id', '=', last_inventory.id)],
                        ['product_id', 'product_qty:sum'],
                        ['product_id']
                    )
                    total_value = 0.0
                    for g in grouped:
                        pid = g.get('product_id') and g['product_id'][0]
                        qty = g.get('product_qty_sum') or 0.0
                        if pid and qty:
                            product = self.env['product.product'].browse(pid)
                            price = record._get_cost_price(product)
                            total_value += qty * price
                    record.inventoried_stock_value = total_value
                    record.inventoried_stock_value_fcfa = f"{total_value:,.0f} FCFA"
                else:
                    record.inventoried_stock_value = 0
                    record.inventoried_stock_value_fcfa = "0 FCFA"
            except Exception as e:
                _logger.error(f"Erreur lors du calcul de la valeur des stocks inventoriés (optimisé): {e}")
                record.inventoried_stock_value = 0
                record.inventoried_stock_value_fcfa = "0 FCFA"
    
    @api.depends('current_stock_value', 'inventoried_stock_value')
    def _compute_stock_value_difference(self):
        """Calcule la différence entre stock actuel et stocks inventoriés."""
        for record in self:
            try:
                current_value = record.current_stock_value
                inventoried_value = record.inventoried_stock_value
                
                difference = current_value - inventoried_value
                
                record.stock_value_difference = difference
                record.stock_value_difference_fcfa = f"{difference:,.0f} FCFA"
                
                # Calcul du pourcentage
                if inventoried_value != 0:
                    percent = (difference / inventoried_value) * 100
                    record.stock_value_difference_percent = percent
                else:
                    record.stock_value_difference_percent = 0
            except Exception as e:
                _logger.error(f"Erreur lors du calcul de la différence de valeur de stock: {e}")
                record.stock_value_difference = 0
                record.stock_value_difference_fcfa = "0 FCFA"
                record.stock_value_difference_percent = 0
    
    @api.depends('company_id', 'warehouse_ids')
    def _compute_warehouse_valuation(self):
        """Calcule la valorisation par entrepôt en temps réel."""
        for record in self:
            try:
                html = """
                <div class="table-responsive">
                <table class="table table-sm table-striped">
                    <thead class="table-light">
                        <tr>
                            <th>Entrepôt</th>
                            <th class="text-end">Quantité</th>
                            <th class="text-end">Valeur</th>
                        </tr>
                    </thead>
                    <tbody>
                """
                
                # Récupérer les entrepôts
                if record.warehouse_ids:
                    warehouses = record.warehouse_ids
                else:
                    warehouses = self.env['stock.warehouse'].search([
                        ('company_id', '=', record.company_id.id)
                    ])
                
                total_qty = 0
                total_value = 0
                
                for warehouse in warehouses:
                    # Récupérer les emplacements de cet entrepôt
                    locations = self.env['stock.location'].search([
                        ('warehouse_id', '=', warehouse.id),
                        ('usage', '=', 'internal')
                    ])
                    
                    if locations:
                        # Récupérer les quantités de produits dans ces emplacements
                        # Utiliser l'ORM pour obtenir la valeur
                        quants = self.env['stock.quant'].search([
                            ('location_id', 'in', locations.ids),
                            ('company_id', '=', record.company_id.id)
                        ])
                        
                        qty = sum(quants.mapped('quantity'))
                        value = sum(q.quantity * record._get_cost_price(q.product_id) for q in quants)
                        
                        # MASQUER les entrepôts avec valeur = 0 ou négative
                        if value <= 0:
                            continue
                        
                        total_qty += qty
                        total_value += value
                        
                        html += f"""
                        <tr>
                            <td><strong>{warehouse.name}</strong></td>
                            <td class=\"text-end\">{qty:,.0f}</td>
                            <td class=\"text-end\">{value:,.0f} FCFA</td>
                        </tr>
                        """
                
                html += f"""
                    <tr class="table-primary">
                        <td><strong>Total</strong></td>
                        <td class="text-end"><strong>{total_qty:,.0f}</strong></td>
                        <td class="text-end"><strong>{total_value:,.0f} FCFA</strong></td>
                    </tr>
                """
                
                html += """
                    </tbody>
                </table>
                </div>
                """
                
                record.warehouse_valuation_html = html
            except Exception as e:
                _logger.error(f"Erreur lors du calcul de la valorisation par entrepôt: {e}")
                record.warehouse_valuation_html = "<p class='text-danger'>Erreur lors du calcul</p>"
    @api.depends('company_id', 'period_filter', 'date_from', 'date_to', 'warehouse_ids')
    def _compute_inventoried_warehouse_valuation(self):
        """Calcule la valorisation inventoriée par entrepôt avec filtres période/entrepôt,
        et affiche % du total ainsi que l'écart vs temps réel par entrepôt."""
        for record in self:
            try:
                # Déterminer la période sélectionnée
                date_from, date_to = record._get_date_range()

                # Récupérer l'inventaire le plus récent dans la période, en incluant les états en cours et le stock initial
                inv_domain = [
                    ('company_id', '=', record.company_id.id),
                    ('state', 'in', ['draft','in_progress','pending_approval','approved','done']),
                ]
                if date_from:
                    inv_domain.append(('date', '>=', date_from))
                if date_to:
                    inv_domain.append(('date', '<=', date_to))

                inventories = self.env['stockex.stock.inventory'].search(inv_domain, order='date desc, id desc')
                if not inventories:
                    record.inventoried_warehouse_valuation_html = "<p class='text-muted'>Aucun inventaire disponible (y compris en cours) dans la période sélectionnée</p>"
                    continue

                # LOG: Inventaires trouvés
                _logger.info(f"=== VALORISATION INVENTORIÉE PAR ENTREPÔT ===")
                _logger.info(f"Période: {date_from} à {date_to}")
                _logger.info(f"Inventaires trouvés: {len(inventories)} - IDs: {inventories.ids}")
                for inv in inventories:
                    _logger.info(f"  - Inventaire #{inv.id}: {inv.name} - Date: {inv.date} - État: {inv.state} - Lignes: {len(inv.line_ids)}")

                # Limiter aux entrepôts sélectionnés si filtre actif
                if record.warehouse_ids:
                    filtered_locations = self.env['stock.location'].search([
                        ('warehouse_id', 'in', record.warehouse_ids.ids),
                        ('usage', '=', 'internal'),
                    ])
                    inv_lines = self.env['stockex.stock.inventory.line'].search([
                        ('inventory_id', 'in', inventories.ids),
                        ('location_id', 'in', filtered_locations.ids),
                    ])
                else:
                    inv_lines = self.env['stockex.stock.inventory.line'].search([
                        ('inventory_id', 'in', inventories.ids),
                    ])
                # Agréger inventorié par entrepôt
                inv_totals = {}
                total_qty = 0.0
                total_value = 0.0
                
                # LOG: Compteurs pour diagnostic
                lines_by_warehouse = {}
                lines_without_warehouse = 0
                
                for line in inv_lines:
                    warehouse = line.location_id.warehouse_id
                    wh_name = warehouse.name if warehouse else 'Sans entrepôt'
                    
                    # LOG: Comptage par entrepôt
                    if wh_name not in lines_by_warehouse:
                        lines_by_warehouse[wh_name] = 0
                    lines_by_warehouse[wh_name] += 1
                    
                    if not warehouse:
                        lines_without_warehouse += 1
                    
                    qty = line.product_qty or 0.0
                    price = record._get_cost_price(line.product_id, line.standard_price)
                    value = qty * price
                    if wh_name not in inv_totals:
                        inv_totals[wh_name] = {'qty': 0.0, 'value': 0.0}
                    inv_totals[wh_name]['qty'] += qty
                    inv_totals[wh_name]['value'] += value
                    total_qty += qty
                    total_value += value

                # LOG: Résultats agrégation
                _logger.info(f"Total lignes d'inventaire traitées: {len(inv_lines)}")
                _logger.info(f"Lignes sans entrepôt: {lines_without_warehouse}")
                _logger.info(f"Répartition par entrepôt:")
                for wh_name, count in lines_by_warehouse.items():
                    inv_data = inv_totals.get(wh_name, {'qty': 0.0, 'value': 0.0})
                    _logger.info(f"  - {wh_name}: {count} lignes, Qty={inv_data['qty']:,.0f}, Valeur={inv_data['value']:,.0f} FCFA")

                # Filtrer entrepôts à stock négatif
                filtered_inv_totals = {
                    name: agg for name, agg in inv_totals.items()
                    if (agg.get('qty', 0.0) >= 0.0 and agg.get('value', 0.0) >= 0.0)
                }
                
                # LOG: Entrepôts filtrés
                filtered_out = set(inv_totals.keys()) - set(filtered_inv_totals.keys())
                if filtered_out:
                    _logger.warning(f"Entrepôts EXCLUS (valeurs négatives): {filtered_out}")
                
                # Recalculer totaux après filtrage
                total_qty = sum(v['qty'] for v in filtered_inv_totals.values())
                total_value = sum(v['value'] for v in filtered_inv_totals.values())

                # Calcul VSD (Valeur définitive) par entrepôt selon décote
                # d = 1.00 pour stocks morts (aucun mouvement depuis 2022)
                # d = 0.40 pour rotation lente (exactement 1 mouvement sur les 12 derniers mois)
                from datetime import date
                from dateutil.relativedelta import relativedelta
                today = fields.Date.today()
                last12_start = today - relativedelta(months=12)
                start_2022 = date(2022, 1, 1)
                product_ids = set(inv_lines.mapped('product_id').ids)
                Move = self.env['stock.move']
                # Regrouper mouvements sur 12 derniers mois (compter par produit)
                grp_last12 = Move.read_group([
                    ('company_id', '=', record.company_id.id),
                    ('state', '!=', 'cancel'),
                    ('product_id', 'in', list(product_ids)),
                    ('date', '>=', last12_start),
                ], ['product_id'], ['product_id'], lazy=False)
                counts_last12 = {g['product_id'][0]: g['__count'] for g in grp_last12 if g.get('product_id')}
                lente_set = {pid for pid, cnt in counts_last12.items() if int(cnt or 0) == 1}
                # Regrouper mouvements depuis 2022
                grp_since2022 = Move.read_group([
                    ('company_id', '=', record.company_id.id),
                    ('state', '!=', 'cancel'),
                    ('product_id', 'in', list(product_ids)),
                    ('date', '>=', start_2022),
                ], ['product_id'], ['product_id'], lazy=False)
                alive_since_2022 = {g['product_id'][0] for g in grp_since2022 if g.get('product_id')}
                mort_set = product_ids - alive_since_2022
                vsd_by_wh = {}
                vsd_total = 0.0
                for line in inv_lines:
                    warehouse = line.location_id.warehouse_id
                    wh_name = warehouse.name if warehouse else 'Sans entrepôt'
                    qty = line.product_qty or 0.0
                    price = record._get_cost_price(line.product_id, line.standard_price)
                    value = qty * price
                    pid = line.product_id.id
                    if pid in mort_set:
                        d = 1.0
                    elif pid in lente_set:
                        d = 0.40
                    else:
                        d = 0.0
                    vsd_line = value * (1.0 - d)
                    vsd_by_wh[wh_name] = vsd_by_wh.get(wh_name, 0.0) + vsd_line
                    vsd_total += vsd_line

                # Calcul temps réel par entrepôt (pour l'écart)
                # Récupérer TOUS les entrepôts de la société pour affichage complet
                if record.warehouse_ids:
                    warehouses = record.warehouse_ids
                else:
                    warehouses = self.env['stock.warehouse'].search([('company_id', '=', record.company_id.id)])

                rt_totals = {}
                for wh in warehouses:
                    locations = self.env['stock.location'].search([
                        ('warehouse_id', '=', wh.id),
                        ('usage', '=', 'internal'),
                    ])
                    if not locations:
                        continue
                    quants = self.env['stock.quant'].search([
                        ('location_id', 'in', locations.ids),
                        ('company_id', '=', record.company_id.id),
                    ])
                    qty = sum(quants.mapped('quantity'))
                    value = sum(q.quantity * record._get_cost_price(q.product_id) for q in quants)
                    rt_totals[wh.name] = {'qty': qty, 'value': value}

                # Fusionner les entrepôts inventoriés et temps réel pour affichage complet
                all_warehouse_names = set(filtered_inv_totals.keys()) | set(rt_totals.keys())
                
                # LOG: Fusion entrepôts
                _logger.info(f"Entrepôts inventoriés: {set(filtered_inv_totals.keys())}")
                _logger.info(f"Entrepôts avec stock réel: {set(rt_totals.keys())}")
                _logger.info(f"Total entrepôts à afficher: {len(all_warehouse_names)}")
                
                # LOG: Identifier les entrepôts avec noms différents
                inv_only = set(filtered_inv_totals.keys()) - set(rt_totals.keys())
                rt_only = set(rt_totals.keys()) - set(filtered_inv_totals.keys())
                if inv_only:
                    _logger.warning(f"⚠️ Entrepôts UNIQUEMENT dans inventaires (possibles noms différents): {inv_only}")
                if rt_only:
                    _logger.warning(f"⚠️ Entrepôts UNIQUEMENT dans stock réel (vérifier noms): {rt_only}")
                
                # LOG: Détail par entrepôt
                for wh_name in sorted(all_warehouse_names):
                    inv_data = filtered_inv_totals.get(wh_name, {'qty': 0.0, 'value': 0.0})
                    rt_data = rt_totals.get(wh_name, {'qty': 0.0, 'value': 0.0})
                    status = "✓" if (inv_data['value'] > 0 and rt_data['value'] > 0) else "⚠️"
                    _logger.info(f"  {status} [{wh_name}] Inventorié: {inv_data['value']:,.0f} FCFA | Stock réel: {rt_data['value']:,.0f} FCFA")

                # Vérifier la règle de valorisation pour affichage conditionnel VSD
                ICP = self.env['ir.config_parameter'].sudo()
                valuation_rule = ICP.get_param('stockex.valuation_rule', 'standard')
                show_vsd = (valuation_rule == 'economic')

                # Construire l'HTML avec colonnes supplémentaires
                html = """
                <div class=\"table-responsive\">
                <table class=\"table table-sm table-striped\">
                    <thead class=\"table-light\">
                        <tr>
                            <th>Entrepôt</th>
                            <th class=\"text-end\">Quantité inventoriée</th>
                            <th class=\"text-end\">Valeur inventoriée</th>
                            <th class=\"text-end\">Stock initial</th>"""
                
                if show_vsd:
                    html += """
                            <th class=\"text-end\">Valeur définitive (VSD)</th>"""
                
                html += """
                            <th class=\"text-end\">% du total</th>
                            <th class=\"text-end\">Écart (Inventorié − Initial)</th>
                        </tr>
                    </thead>
                    <tbody>
                """

                for wh_name in sorted(all_warehouse_names):
                    # Récupérer les valeurs inventoriées (ou 0 si non inventorié)
                    inv_data = filtered_inv_totals.get(wh_name, {'qty': 0.0, 'value': 0.0})
                    inv_qty = inv_data['qty']
                    inv_value = inv_data['value']
                    
                    # Récupérer les valeurs temps réel (ou 0 si vide)
                    rt_data = rt_totals.get(wh_name, {'qty': 0.0, 'value': 0.0})
                    rt_val = rt_data['value']
                    
                    # MASQUER si AUCUNE valeur (ni inventoriée ni réelle)
                    if inv_value <= 0 and rt_val <= 0:
                        continue
                    
                    # Calcul VSD pour cet entrepôt
                    vsd_value = vsd_by_wh.get(wh_name, 0.0)
                    
                    # Pourcentage (sur le total inventorié)
                    percent = (inv_value / total_value * 100) if (total_value > 0 and inv_value > 0) else 0.0
                    
                    # Écart
                    diff_val = inv_value - rt_val
                    abs_exceed = abs(diff_val) >= 10000
                    rel_exceed = (inv_value > 0) and ((abs(diff_val) / inv_value) * 100 >= 2.0)
                    diff_class = ('text-danger fw-semibold') if (abs_exceed or rel_exceed) else ('text-success' if diff_val > 0 else ('text-danger' if diff_val < 0 else 'text-muted'))
                    diff_sign = '+' if diff_val > 0 else ''
                    
                    html += f"""
                    <tr>
                        <td><strong>{wh_name}</strong></td>
                        <td class=\"text-end\">{inv_qty:,.0f}</td>
                        <td class=\"text-end\">{inv_value:,.0f} FCFA</td>
                        <td class=\"text-end\">{rt_val:,.0f} FCFA</td>"""
                    
                    if show_vsd:
                        html += f"""
                        <td class=\"text-end\">{vsd_value:,.0f} FCFA</td>"""
                    
                    html += f"""
                        <td class=\"text-end\">{percent:,.2f} %</td>
                        <td class=\"text-end {diff_class}\">{diff_sign}{diff_val:,.0f} FCFA</td>
                    </tr>
                    """

                # Calculer le total des écarts
                rt_total = sum(v['value'] for v in rt_totals.values())
                total_ecart = total_value - rt_total
                abs_exceed_total = abs(total_ecart) >= 10000
                base_total = rt_total if rt_total > 0 else total_value
                rel_exceed_total = (base_total > 0) and ((abs(total_ecart) / base_total) * 100 >= 2.0)
                ecart_class = ('text-danger fw-semibold') if (abs_exceed_total or rel_exceed_total) else ('text-success' if total_ecart > 0 else ('text-danger' if total_ecart < 0 else 'text-muted'))
                ecart_sign = '+' if total_ecart > 0 else ''
                
                html += f"""
                    <tr class=\"table-warning\">
                        <td><strong>Total</strong></td>
                        <td class=\"text-end\"><strong>{total_qty:,.0f}</strong></td>
                        <td class=\"text-end\"><strong>{total_value:,.0f} FCFA</strong></td>
                        <td class=\"text-end\"><strong>{rt_total:,.0f} FCFA</strong></td>"""
                
                if show_vsd:
                    html += f"""
                        <td class=\"text-end\"><strong>{vsd_total:,.0f} FCFA</strong></td>"""
                
                html += f"""
                        <td class=\"text-end\"><strong>100.00 %</strong></td>
                        <td class=\"text-end {ecart_class}\"><strong>{ecart_sign}{total_ecart:,.0f} FCFA</strong></td>
                    </tr>
                """

                html += """
                    </tbody>
                </table>
                </div>
                """

                record.inventoried_warehouse_valuation_html = html
            except Exception as e:
                _logger.error(f"Erreur lors du calcul de la valorisation inventoriée par entrepôt: {e}")
                record.inventoried_warehouse_valuation_html = "<p class='text-danger'>Erreur lors du calcul</p>"

    @api.depends('company_id')
    def _compute_last_inventory(self):
        """Calcule les stats du dernier inventaire."""
        for record in self:
            try:
                last_inv = self.env['stockex.stock.inventory'].search([
                    ('company_id', '=', record.company_id.id),
                    ('state', '=', 'done')
                ], limit=1, order='date desc, id desc')
                
                if last_inv:
                    record.last_inventory_id = last_inv.id
                    record.last_inventory_date = last_inv.date
                    record.last_inventory_products = len(last_inv.line_ids.mapped('product_id'))
                    value = sum(line.product_qty * record._get_cost_price(line.product_id, line.standard_price) for line in last_inv.line_ids)
                    record.last_inventory_value = value
                    record.last_inventory_value_fcfa = f"{value:,.2f} FCFA"
                else:
                    record.last_inventory_id = False
                    record.last_inventory_date = False
                    record.last_inventory_products = 0
                    record.last_inventory_value = 0
                    record.last_inventory_value_fcfa = "0 FCFA"
            except Exception as e:
                _logger.error(f"Erreur lors du calcul du dernier inventaire: {e}")
                record.last_inventory_id = False
                record.last_inventory_date = False
                record.last_inventory_products = 0
                record.last_inventory_value = 0
                record.last_inventory_value_fcfa = "0 FCFA"
    
    @api.depends('company_id', 'period_filter', 'date_from', 'date_to', 'category_ids', 'warehouse_ids', 'location_ids')
    def _compute_top_categories(self):
        """Calcule le top 10 des catégories avec filtres appliqués."""
        for record in self:
            try:
                # Construire la requête avec filtres
                conditions, params = record._get_filtered_lines_domain()
                where_clause = " AND ".join(conditions) if conditions else "1=1"
                
                # Agrégation Python pour appliquer la règle de valorisation
                inventories = record._get_filtered_inventories().filtered(lambda i: i.state in ('draft','in_progress','pending_approval','approved','done'))
                if record.warehouse_ids:
                    filtered_locations = self.env['stock.location'].search([
                        ('warehouse_id', 'in', record.warehouse_ids.ids),
                        ('usage', '=', 'internal'),
                    ])
                    inv_lines = self.env['stockex.stock.inventory.line'].search([
                        ('inventory_id', 'in', inventories.ids),
                        ('location_id', 'in', filtered_locations.ids),
                    ])
                else:
                    inv_lines = self.env['stockex.stock.inventory.line'].search([
                        ('inventory_id', 'in', inventories.ids),
                    ])
                # Filtre catégories si actif
                if record.category_ids:
                    inv_lines = inv_lines.filtered(lambda l: l.product_id.categ_id in record.category_ids)

                # Regrouper par catégorie
                by_cat = {}
                for line in inv_lines:
                    cat_name = line.product_id.categ_id.name or 'Sans catégorie'
                    price = record._get_cost_price(line.product_id, line.standard_price)
                    value = (line.product_qty or 0.0) * price
                    diff_val = (line.difference or 0.0) * price if not line.inventory_id.is_initial_stock else 0.0
                    agg = by_cat.get(cat_name, {'value': 0.0, 'diff': 0.0})
                    agg['value'] += value
                    agg['diff'] += diff_val
                    by_cat[cat_name] = agg

                # Top 5 par valeur
                top = sorted(by_cat.items(), key=lambda kv: kv[1]['value'], reverse=True)[:5]

                html = """
                <div class="table-responsive">
                <table class='table table-sm table-striped mb-0'>
                    <thead class="table-light">
                        <tr>
                            <th>Catégorie</th>
                            <th class='text-end'>Valeur</th>
                            <th class='text-end'>Écarts</th>
                        </tr>
                    </thead>
                    <tbody>
                """
                for cat_name, agg in top:
                    diff = agg['diff']
                    value = agg['value']
                    diff_color = 'text-success' if diff > 0 else ('text-danger' if diff < 0 else 'text-muted')
                    diff_icon = '✓' if diff > 0 else ('⚠️' if diff < 0 else '=')
                    html += f"""
                    <tr>
                        <td><small><strong>{cat_name or 'Sans catégorie'}</strong></small></td>
                        <td class='text-end'><small>{value:,.0f} FCFA</small></td>
                        <td class='text-end {diff_color}'><small>{diff_icon} {diff:,.0f}</small></td>
                    </tr>
                    """
                html += """
                    </tbody>
                </table>
                </div>
                """
                record.top_categories_html = html if top else "<p class='text-muted'>Aucune donnée disponible</p>"

            except Exception as e:
                _logger.error(f"Erreur lors du calcul des top catégories: {e}")
                if hasattr(self.env, 'cr'):
                    self.env.cr.rollback()
                record.top_categories_html = "<p class='text-muted'>Erreur de calcul</p>"
    
    @api.depends('company_id', 'period_filter', 'date_from', 'date_to', 'category_ids', 'warehouse_ids', 'location_ids')
    def _compute_top_warehouses(self):
        """Calcule le top 10 des entrepôts avec filtres appliqués."""
        for record in self:
            try:
                # Construire la requête avec filtres
                conditions, params = record._get_filtered_lines_domain()
                where_clause = " AND ".join(conditions) if conditions else "1=1"
                
                # Agrégation Python pour appliquer la règle de valorisation
                inventories = record._get_filtered_inventories().filtered(lambda i: i.state in ('draft','in_progress','pending_approval','approved','done'))
                if record.warehouse_ids:
                    filtered_locations = self.env['stock.location'].search([
                        ('warehouse_id', 'in', record.warehouse_ids.ids),
                        ('usage', '=', 'internal'),
                    ])
                    inv_lines = self.env['stockex.stock.inventory.line'].search([
                        ('inventory_id', 'in', inventories.ids),
                        ('location_id', 'in', filtered_locations.ids),
                    ])
                else:
                    inv_lines = self.env['stockex.stock.inventory.line'].search([
                        ('inventory_id', 'in', inventories.ids),
                    ])

                by_loc = {}
                for line in inv_lines:
                    loc_name = line.location_id.complete_name or 'Sans entrepôt'
                    price = record._get_cost_price(line.product_id, line.standard_price)
                    value = (line.product_qty or 0.0) * price
                    diff_val = (line.difference or 0.0) * price if not line.inventory_id.is_initial_stock else 0.0
                    agg = by_loc.get(loc_name, {'value': 0.0, 'diff': 0.0})
                    agg['value'] += value
                    agg['diff'] += diff_val
                    by_loc[loc_name] = agg

                top = sorted(by_loc.items(), key=lambda kv: kv[1]['value'], reverse=True)[:5]

                html = """
                <div class="table-responsive">
                <table class='table table-sm table-striped mb-0'>
                    <thead class="table-light">
                        <tr>
                            <th>Entrepôt</th>
                            <th class='text-end'>Valeur</th>
                            <th class='text-end'>Écarts</th>
                        </tr>
                    </thead>
                    <tbody>
                """
                for loc_name, agg in top:
                    value = agg['value']
                    diff = agg['diff']
                    display_name = loc_name if len(loc_name) <= 25 else loc_name[:22] + '...'
                    diff_color = 'text-success' if diff > 0 else ('text-danger' if diff < 0 else 'text-muted')
                    diff_icon = '✓' if diff > 0 else ('⚠️' if diff < 0 else '=')
                    html += f"""
                    <tr>
                        <td><small><strong>{display_name}</strong></small></td>
                        <td class='text-end'><small>{value:,.0f} FCFA</small></td>
                        <td class='text-end {diff_color}'><small>{diff_icon} {diff:,.0f}</small></td>
                    </tr>
                    """
                html += """
                    </tbody>
                </table>
                </div>
                """
                record.top_warehouses_html = html if top else "<p class='text-muted'>Aucune donnée disponible</p>"

            except Exception as e:
                _logger.error(f"Erreur lors du calcul des top entrepôts: {e}")
                if hasattr(self.env, 'cr'):
                    self.env.cr.rollback()
                record.top_warehouses_html = "<p class='text-muted'>Erreur de calcul</p>"
    
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
                <div class="table-responsive">
                <table class='table table-sm'>
                    <thead class='table-info'>
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
                </div>
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
    
    def action_view_inventoried_products(self):
        """Ouvre la liste des produits inventoriés."""
        self.ensure_one()
        
        # Récupérer les inventaires filtrés
        inventories = self._get_filtered_inventories()
        
        # Récupérer tous les produits inventoriés
        lines = self.env['stockex.stock.inventory.line'].search([
            ('inventory_id', 'in', inventories.ids)
        ])
        product_ids = lines.mapped('product_id').ids
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Produits Inventoriés',
            'res_model': 'product.product',
            'view_mode': 'list,form',
            'domain': [('id', 'in', product_ids)],
            'context': {'default_company_id': self.company_id.id},
        }
    
    def action_view_inventory_lines(self):
        """Ouvre les lignes d'inventaire."""
        self.ensure_one()
        
        # Récupérer les inventaires filtrés
        inventories = self._get_filtered_inventories()
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Lignes d\'Inventaire',
            'res_model': 'stockex.stock.inventory.line',
            'view_mode': 'list,form',
            'domain': [('inventory_id', 'in', inventories.ids)],
            'context': {'default_company_id': self.company_id.id},
        }
    
    def action_view_warehouse_details(self):
        """Ouvre les détails des entrepôts."""
        self.ensure_one()
        
        # Si filtre entrepôt actif, montrer seulement ceux-là
        if self.warehouse_ids:
            warehouses = self.warehouse_ids
        else:
            warehouses = self.env['stock.warehouse'].search([
                ('company_id', '=', self.company_id.id)
            ])
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Entrepôts',
            'res_model': 'stock.warehouse',
            'view_mode': 'list,form',
            'domain': [('id', 'in', warehouses.ids)],
        }
    
    def action_view_top_categories(self):
        """Ouvre la liste des catégories de produits."""
        self.ensure_one()
        
        # Récupérer les inventaires filtrés
        inventories = self._get_filtered_inventories()
        
        # Récupérer toutes les catégories des produits inventoriés
        lines = self.env['stockex.stock.inventory.line'].search([
            ('inventory_id', 'in', inventories.ids)
        ])
        category_ids = lines.mapped('product_id.categ_id').ids
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Catégories de Produits',
            'res_model': 'product.category',
            'view_mode': 'list,form',
            'domain': [('id', 'in', category_ids)],
        }
    
    def action_export_warehouse_valuation_excel(self):
        """Exporte la valorisation par entrepôt en Excel."""
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
        ws.title = "Valorisation Entrepôts"
        
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
        ws['A1'] = f"VALORISATION PAR ENTREPÔT - {self.company_id.name}"
        ws['A1'].font = Font(bold=True, size=14)
        ws.merge_cells('A1:G1')
        
        ws['A2'] = f"Date: {fields.Date.today()}"
        
        # En-têtes colonnes (ligne 4)
        headers = [
            'Entrepôt',
            'Quantité Inventoriée',
            'Valeur Inventoriée (FCFA)',
            'Valeur Stock Réel (FCFA)',
            'Valeur Définitive VSD (FCFA)',
            '% du Total',
            'Écart Inventorié - Réel (FCFA)'
        ]
        
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=4, column=col_num, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.border = border
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        
        # Récupérer les données depuis le compute
        # Calculer comme dans _compute_inventoried_warehouse_valuation
        date_from, date_to = self._get_date_range()
        inv_domain = [
            ('company_id', '=', self.company_id.id),
            ('state', 'in', ['draft','in_progress','pending_approval','approved','done']),
        ]
        if date_from:
            inv_domain.append(('date', '>=', date_from))
        if date_to:
            inv_domain.append(('date', '<=', date_to))
        
        inventories = self.env['stockex.stock.inventory'].search(inv_domain, order='date desc, id desc')
        
        if not inventories:
            raise UserError("Aucun inventaire disponible dans la période sélectionnée.")
        
        # Limiter aux entrepôts sélectionnés si filtre actif
        if self.warehouse_ids:
            filtered_locations = self.env['stock.location'].search([
                ('warehouse_id', 'in', self.warehouse_ids.ids),
                ('usage', '=', 'internal'),
            ])
            inv_lines = self.env['stockex.stock.inventory.line'].search([
                ('inventory_id', 'in', inventories.ids),
                ('location_id', 'in', filtered_locations.ids),
            ])
        else:
            inv_lines = self.env['stockex.stock.inventory.line'].search([
                ('inventory_id', 'in', inventories.ids),
            ])
        
        # Agréger par entrepôt
        inv_totals = {}
        total_qty = 0.0
        total_value = 0.0
        for line in inv_lines:
            warehouse = line.location_id.warehouse_id
            wh_name = warehouse.name if warehouse else 'Sans entrepôt'
            qty = line.product_qty or 0.0
            price = self._get_cost_price(line.product_id, line.standard_price)
            value = qty * price
            if wh_name not in inv_totals:
                inv_totals[wh_name] = {'qty': 0.0, 'value': 0.0}
            inv_totals[wh_name]['qty'] += qty
            inv_totals[wh_name]['value'] += value
            total_qty += qty
            total_value += value
        
        # Calculer VSD et stock réel
        from datetime import date
        from dateutil.relativedelta import relativedelta
        today = fields.Date.today()
        last12_start = today - relativedelta(months=12)
        start_2022 = date(2022, 1, 1)
        product_ids = set(inv_lines.mapped('product_id').ids)
        Move = self.env['stock.move']
        
        grp_last12 = Move.read_group([
            ('company_id', '=', self.company_id.id),
            ('state', '!=', 'cancel'),
            ('product_id', 'in', list(product_ids)),
            ('date', '>=', last12_start),
        ], ['product_id'], ['product_id'], lazy=False)
        counts_last12 = {g['product_id'][0]: g['__count'] for g in grp_last12 if g.get('product_id')}
        lente_set = {pid for pid, cnt in counts_last12.items() if int(cnt or 0) == 1}
        
        grp_since2022 = Move.read_group([
            ('company_id', '=', self.company_id.id),
            ('state', '!=', 'cancel'),
            ('product_id', 'in', list(product_ids)),
            ('date', '>=', start_2022),
        ], ['product_id'], ['product_id'], lazy=False)
        alive_since_2022 = {g['product_id'][0] for g in grp_since2022 if g.get('product_id')}
        mort_set = product_ids - alive_since_2022
        
        vsd_by_wh = {}
        for line in inv_lines:
            warehouse = line.location_id.warehouse_id
            wh_name = warehouse.name if warehouse else 'Sans entrepôt'
            qty = line.product_qty or 0.0
            price = self._get_cost_price(line.product_id, line.standard_price)
            value = qty * price
            pid = line.product_id.id
            if pid in mort_set:
                d = 1.0
            elif pid in lente_set:
                d = 0.40
            else:
                d = 0.0
            vsd_line = value * (1.0 - d)
            vsd_by_wh[wh_name] = vsd_by_wh.get(wh_name, 0.0) + vsd_line
        
        # Stock réel
        if self.warehouse_ids:
            warehouses = self.warehouse_ids
        else:
            warehouses = self.env['stock.warehouse'].search([('company_id', '=', self.company_id.id)])
        
        rt_totals = {}
        for wh in warehouses:
            locations = self.env['stock.location'].search([
                ('warehouse_id', '=', wh.id),
                ('usage', '=', 'internal'),
            ])
            if not locations:
                continue
            quants = self.env['stock.quant'].search([
                ('location_id', 'in', locations.ids),
                ('company_id', '=', self.company_id.id),
            ])
            value = sum(q.quantity * self._get_cost_price(q.product_id) for q in quants)
            rt_totals[wh.name] = value
        
        # Écrire les données
        row_num = 5
        for wh_name, agg in sorted(inv_totals.items()):
            if agg['qty'] < 0 or agg['value'] < 0:
                continue
            
            rt_val = rt_totals.get(wh_name, 0.0)
            if rt_val < 0:
                continue
            
            percent = (agg['value'] / total_value * 100) if total_value > 0 else 0.0
            diff_val = agg['value'] - rt_val
            vsd = vsd_by_wh.get(wh_name, 0.0)
            
            ws.cell(row=row_num, column=1, value=wh_name)
            ws.cell(row=row_num, column=2, value=agg['qty'])
            ws.cell(row=row_num, column=3, value=agg['value'])
            ws.cell(row=row_num, column=4, value=rt_val)
            ws.cell(row=row_num, column=5, value=vsd)
            ws.cell(row=row_num, column=6, value=percent)
            ws.cell(row=row_num, column=7, value=diff_val)
            
            # Bordures et formatage
            for col in range(1, 8):
                cell = ws.cell(row=row_num, column=col)
                cell.border = border
                if col == 6:  # % du total
                    cell.number_format = '0.00"%"'
                elif col >= 2:  # Nombres
                    cell.number_format = '#,##0'
            
            # Colorer l'écart
            diff_cell = ws.cell(row=row_num, column=7)
            if diff_val > 0:
                diff_cell.font = Font(color="008000", bold=True)
            elif diff_val < 0:
                diff_cell.font = Font(color="FF0000", bold=True)
            
            row_num += 1
        
        # Ligne totaux
        row_num += 1
        ws.cell(row=row_num, column=1, value="TOTAL").font = Font(bold=True)
        ws.cell(row=row_num, column=2, value=total_qty).font = Font(bold=True)
        ws.cell(row=row_num, column=3, value=total_value).font = Font(bold=True)
        
        for col in range(1, 8):
            ws.cell(row=row_num, column=col).fill = PatternFill(start_color="E0E0E0", end_color="E0E0E0", fill_type="solid")
        
        # Ajuster largeur colonnes
        column_widths = [30, 20, 25, 25, 25, 15, 25]
        for i, width in enumerate(column_widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = width
        
        # Sauvegarder en mémoire
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        # Créer l'attachement
        attachment = self.env['ir.attachment'].create({
            'name': f'Valorisation_Entrepots_{fields.Date.today()}.xlsx',
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
    
    @api.depends('company_id', 'warehouse_ids')
    def _compute_warehouse_gaps_chart(self):
        """Calcule les données pour le graphique à barres des écarts par entrepôt."""
        import json
        for record in self:
            try:
                warehouses = record.warehouse_ids or self.env['stock.warehouse'].search([('company_id', '=', record.company_id.id)])
                labels = []
                values = []
                colors = []
                
                for wh in warehouses:
                    # Calculer écart: valorisation inventoriée - stock temps réel
                    locations = self.env['stock.location'].search([('warehouse_id', '=', wh.id), ('usage', '=', 'internal')])
                    if not locations:
                        continue
                    
                    # Stock temps réel
                    quants = self.env['stock.quant'].search([('location_id', 'in', locations.ids), ('company_id', '=', record.company_id.id)])
                    rt_value = sum(q.quantity * record._get_cost_price(q.product_id) for q in quants)
                    
                    # Valorisation inventoriée (dernier inventaire)
                    last_inv = self.env['stockex.stock.inventory'].search([
                        ('company_id', '=', record.company_id.id),
                        ('state', 'in', ['draft','in_progress','pending_approval','approved','done']),
                        ('is_initial_stock', '=', False),
                    ], limit=1, order='date desc')
                    
                    inv_value = 0.0
                    if last_inv:
                        inv_lines = self.env['stockex.stock.inventory.line'].search([('inventory_id', '=', last_inv.id), ('location_id', 'in', locations.ids)])
                        inv_value = sum(line.product_qty * record._get_cost_price(line.product_id, line.standard_price) for line in inv_lines)
                    
                    gap = inv_value - rt_value
                    if abs(gap) < 1:
                        continue
                    
                    labels.append(wh.name)
                    values.append(gap)
                    # Rouge si |gap| >= 10000 ou >=2%
                    abs_exceed = abs(gap) >= 10000
                    rel_exceed = (inv_value > 0) and ((abs(gap) / inv_value) * 100 >= 2.0)
                    colors.append('#dc3545' if (abs_exceed or rel_exceed) else ('#198754' if gap > 0 else '#6c757d'))
                
                record.warehouse_gaps_chart_data = json.dumps({'labels': labels, 'values': values, 'colors': colors})
            except Exception as e:
                _logger.error(f"Erreur calcul graphique écarts: {e}")
                record.warehouse_gaps_chart_data = json.dumps({'labels': [], 'values': [], 'colors': []})
    
    @api.depends('company_id', 'category_ids')
    def _compute_category_value_chart(self):
        """Calcule les données pour le graphique donut valeur par famille."""
        import json
        for record in self:
            try:
                last_inv = self.env['stockex.stock.inventory'].search([
                    ('company_id', '=', record.company_id.id),
                    ('state', 'in', ['draft','in_progress','pending_approval','approved','done']),
                    ('is_initial_stock', '=', False),
                ], limit=1, order='date desc')
                
                if not last_inv:
                    record.category_value_chart_data = json.dumps({'labels': [], 'values': [], 'colors': []})
                    continue
                
                # Agréger par catégorie
                category_values = {}
                for line in last_inv.line_ids:
                    cat = line.product_id.categ_id
                    cat_name = cat.name if cat else 'Sans catégorie'
                    price = record._get_cost_price(line.product_id, line.standard_price)
                    val = line.product_qty * price
                    category_values[cat_name] = category_values.get(cat_name, 0.0) + val
                
                # Trier et limiter à top 5
                sorted_cats = sorted(category_values.items(), key=lambda x: x[1], reverse=True)[:5]
                labels = [c[0] for c in sorted_cats]
                values = [c[1] for c in sorted_cats]
                colors = ['#0d6efd', '#198754', '#ffc107', '#dc3545', '#6c757d'][:len(labels)]
                
                record.category_value_chart_data = json.dumps({'labels': labels, 'values': values, 'colors': colors})
            except Exception as e:
                _logger.error(f"Erreur calcul graphique catégories: {e}")
                record.category_value_chart_data = json.dumps({'labels': [], 'values': [], 'colors': []})
    
    @api.depends('company_id')
    def _compute_inventory_precision(self):
        """Calcule la précision inventaire = 1 - (|Σ écarts quantités| / Σ quantités système)."""
        for record in self:
            try:
                last_inv = self.env['stockex.stock.inventory'].search([
                    ('company_id', '=', record.company_id.id),
                    ('state', 'in', ['draft','in_progress','pending_approval','approved','done']),
                    ('is_initial_stock', '=', False),
                ], limit=1, order='date desc')
                
                if not last_inv:
                    record.inventory_precision = 0.0
                    continue
                
                total_system_qty = sum(abs(line.theoretical_qty or 0.0) for line in last_inv.line_ids)
                total_gap_qty = sum(abs(line.difference or 0.0) for line in last_inv.line_ids if not line.inventory_id.is_initial_stock)
                
                if total_system_qty > 0:
                    record.inventory_precision = (1.0 - (total_gap_qty / total_system_qty)) * 100.0
                else:
                    record.inventory_precision = 0.0
            except Exception as e:
                _logger.error(f"Erreur calcul précision: {e}")
                record.inventory_precision = 0.0
    
    @api.depends('company_id')
    def _compute_obsolescence(self):
        """Calcule le nombre et la valeur des articles obsolètes."""
        for record in self:
            try:
                ICP = self.env['ir.config_parameter'].sudo()
                slow_days = int(ICP.get_param('stockex.depreciation_slow_days', '1095'))
                
                # Tous les quants internes
                locations = self.env['stock.location'].search([('company_id', '=', record.company_id.id), ('usage', '=', 'internal')])
                quants = self.env['stock.quant'].search([('location_id', 'in', locations.ids), ('quantity', '>', 0)])
                
                count = 0
                value = 0.0
                from datetime import datetime
                now = datetime.now().date()
                
                for quant in quants:
                    # Chercher dernier mouvement
                    last_move = self.env['stock.move'].search([('product_id', '=', quant.product_id.id), ('state', '=', 'done')], limit=1, order='date desc')
                    if not last_move:
                        days_since = 9999
                    else:
                        last_move_date = last_move.date.date() if isinstance(last_move.date, datetime) else last_move.date
                        days_since = (now - last_move_date).days
                    
                    if days_since > slow_days:
                        count += 1
                        value += quant.quantity * record._get_cost_price(quant.product_id)
                
                record.obsolescence_count = count
                record.obsolescence_value = value
            except Exception as e:
                _logger.error(f"Erreur calcul obsolescence: {e}")
                record.obsolescence_count = 0
                record.obsolescence_value = 0.0