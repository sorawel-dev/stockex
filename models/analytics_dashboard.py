# -*- coding: utf-8 -*-
"""
Dashboard Analytique Avancé
============================
KPIs temps réel et visualisations avancées pour module Stockex.

Features:
- 5 KPIs essentiels temps réel
- Graphiques tendances (Chart.js)
- Valorisation stock par catégorie
- Taux de rotation stocks
- Analyse précision inventaire
"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json
import logging

_logger = logging.getLogger(__name__)


class AnalyticsDashboard(models.Model):
    """Dashboard analytique avec KPIs temps réel."""
    _name = 'stockex.analytics.dashboard'
    _description = 'Dashboard Analytique Stockex'
    
    name = fields.Char(string='Nom', default='Dashboard Analytique', readonly=True)
    
    # Période d'analyse
    period = fields.Selection([
        ('today', "Aujourd'hui"),
        ('week', 'Cette Semaine'),
        ('month', 'Ce Mois'),
        ('quarter', 'Ce Trimestre'),
        ('year', 'Cette Année'),
        ('custom', 'Personnalisé'),
    ], string='Période', default='month')
    
    date_from = fields.Date(string='Date Début')
    date_to = fields.Date(string='Date Fin')
    
    # ========== KPIs ESSENTIELS ==========
    
    kpi_total_inventories = fields.Integer(
        compute='_compute_kpi_inventories',
        string='Total Inventaires'
    )
    
    kpi_completed_inventories = fields.Integer(
        compute='_compute_kpi_inventories',
        string='Inventaires Validés'
    )
    
    kpi_average_accuracy = fields.Float(
        compute='_compute_kpi_accuracy',
        string='Précision Moyenne (%)',
        digits=(5, 2)
    )
    
    kpi_total_variance_value = fields.Monetary(
        compute='_compute_kpi_variance',
        string='Valeur Totale Écarts',
        currency_field='currency_id'
    )
    
    kpi_stock_turnover_ratio = fields.Float(
        compute='_compute_kpi_turnover',
        string='Taux Rotation Stock',
        digits=(5, 2),
        help='Nombre de fois que le stock est renouvelé'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        default=lambda self: self.env.company.currency_id
    )
    
    # ========== GRAPHIQUES ==========
    
    chart_inventory_trend_data = fields.Text(
        compute='_compute_chart_inventory_trend',
        string='Données Tendance Inventaires'
    )
    
    chart_variance_by_category_data = fields.Text(
        compute='_compute_chart_variance_category',
        string='Données Écarts par Catégorie'
    )
    
    chart_stock_value_evolution_data = fields.Text(
        compute='_compute_chart_stock_value',
        string='Données Évolution Valeur Stock'
    )
    
    # ========== STATISTIQUES DÉTAILLÉES ==========
    
    stat_total_products_counted = fields.Integer(
        compute='_compute_statistics',
        string='Produits Inventoriés'
    )
    
    stat_total_locations_covered = fields.Integer(
        compute='_compute_statistics',
        string='Emplacements Couverts'
    )
    
    stat_average_time_per_inventory = fields.Float(
        compute='_compute_statistics',
        string='Temps Moyen (heures)',
        digits=(5, 2)
    )
    
    # ========== COMPUTE METHODS ==========
    
    def _get_date_range(self):
        """Retourne les dates de début et fin selon la période."""
        today = fields.Date.today()
        
        if self.period == 'today':
            return today, today
        elif self.period == 'week':
            start = today - timedelta(days=today.weekday())
            return start, today
        elif self.period == 'month':
            start = today.replace(day=1)
            return start, today
        elif self.period == 'quarter':
            quarter = (today.month - 1) // 3
            start = today.replace(month=quarter * 3 + 1, day=1)
            return start, today
        elif self.period == 'year':
            start = today.replace(month=1, day=1)
            return start, today
        elif self.period == 'custom':
            return self.date_from or today, self.date_to or today
        
        return today, today
    
    @api.depends('period', 'date_from', 'date_to')
    def _compute_kpi_inventories(self):
        """Calcule les KPIs des inventaires."""
        for dashboard in self:
            date_from, date_to = dashboard._get_date_range()
            
            domain = [
                ('date', '>=', date_from),
                ('date', '<=', date_to),
            ]
            
            inventories = self.env['stockex.stock.inventory'].search(domain)
            
            dashboard.kpi_total_inventories = len(inventories)
            dashboard.kpi_completed_inventories = len(
                inventories.filtered(lambda i: i.state == 'validated')
            )
    
    @api.depends('period', 'date_from', 'date_to')
    def _compute_kpi_accuracy(self):
        """Calcule la précision moyenne des inventaires."""
        for dashboard in self:
            date_from, date_to = dashboard._get_date_range()
            
            domain = [
                ('date', '>=', date_from),
                ('date', '<=', date_to),
                ('state', '=', 'validated'),
            ]
            
            inventories = self.env['stockex.stock.inventory'].search(domain)
            
            if not inventories:
                dashboard.kpi_average_accuracy = 0.0
                continue
            
            total_accuracy = 0.0
            count = 0
            
            for inventory in inventories:
                lines = inventory.inventory_line_ids.filtered(
                    lambda l: l.theoretical_qty > 0
                )
                
                if not lines:
                    continue
                
                # Calcul précision: (1 - |écart| / théorique) * 100
                for line in lines:
                    if line.theoretical_qty > 0:
                        accuracy = (1 - abs(line.difference) / line.theoretical_qty) * 100
                        accuracy = max(0, min(100, accuracy))  # Clamp 0-100
                        total_accuracy += accuracy
                        count += 1
            
            dashboard.kpi_average_accuracy = total_accuracy / count if count > 0 else 0.0
    
    @api.depends('period', 'date_from', 'date_to')
    def _compute_kpi_variance(self):
        """Calcule la valeur totale des écarts."""
        for dashboard in self:
            date_from, date_to = dashboard._get_date_range()
            
            domain = [
                ('inventory_id.date', '>=', date_from),
                ('inventory_id.date', '<=', date_to),
                ('inventory_id.state', '=', 'validated'),
            ]
            
            lines = self.env['stockex.stock.inventory.line'].search(domain)
            
            dashboard.kpi_total_variance_value = sum(
                line.difference * line.standard_price for line in lines
            )
    
    @api.depends('period', 'date_from', 'date_to')
    def _compute_kpi_turnover(self):
        """Calcule le taux de rotation du stock."""
        for dashboard in self:
            date_from, date_to = dashboard._get_date_range()
            
            # Coût des marchandises vendues (COGS)
            # Approximation: somme des mouvements sortants valorisés
            moves = self.env['stock.move'].search([
                ('date', '>=', date_from),
                ('date', '<=', date_to),
                ('state', '=', 'done'),
                ('location_id.usage', '=', 'internal'),
                ('location_dest_id.usage', '!=', 'internal'),
            ])
            
            cogs = sum(move.product_qty * move.product_id.standard_price for move in moves)
            
            # Valeur moyenne du stock
            # Approximation: valeur actuelle du stock
            quants = self.env['stock.quant'].search([
                ('location_id.usage', '=', 'internal'),
                ('quantity', '>', 0),
            ])
            
            avg_stock_value = sum(q.quantity * q.product_id.standard_price for q in quants)
            
            if avg_stock_value > 0:
                dashboard.kpi_stock_turnover_ratio = cogs / avg_stock_value
            else:
                dashboard.kpi_stock_turnover_ratio = 0.0
    
    @api.depends('period', 'date_from', 'date_to')
    def _compute_chart_inventory_trend(self):
        """Génère les données pour graphique tendance inventaires."""
        for dashboard in self:
            date_from, date_to = dashboard._get_date_range()
            
            # Données mensuelles des 12 derniers mois
            months_data = []
            labels = []
            
            for i in range(11, -1, -1):
                month_date = date_to - relativedelta(months=i)
                month_start = month_date.replace(day=1)
                
                if i == 0:
                    month_end = date_to
                else:
                    month_end = (month_start + relativedelta(months=1)) - timedelta(days=1)
                
                count = self.env['stockex.stock.inventory'].search_count([
                    ('date', '>=', month_start),
                    ('date', '<=', month_end),
                ])
                
                months_data.append(count)
                labels.append(month_start.strftime('%b %Y'))
            
            dashboard.chart_inventory_trend_data = json.dumps({
                'labels': labels,
                'datasets': [{
                    'label': 'Nombre d\'Inventaires',
                    'data': months_data,
                    'borderColor': 'rgb(75, 192, 192)',
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                }]
            })
    
    @api.depends('period', 'date_from', 'date_to')
    def _compute_chart_variance_category(self):
        """Génère les données pour graphique écarts par catégorie."""
        for dashboard in self:
            date_from, date_to = dashboard._get_date_range()
            
            # Agrégation par catégorie
            query = """
                SELECT 
                    pc.name as category,
                    SUM(sil.difference * sil.standard_price) as total_variance
                FROM stockex_stock_inventory_line sil
                JOIN product_product pp ON sil.product_id = pp.id
                JOIN product_template pt ON pp.product_tmpl_id = pt.id
                JOIN product_category pc ON pt.categ_id = pc.id
                JOIN stockex_stock_inventory si ON sil.inventory_id = si.id
                WHERE si.date >= %s 
                  AND si.date <= %s
                  AND si.state = 'validated'
                GROUP BY pc.name
                ORDER BY ABS(SUM(sil.difference * sil.standard_price)) DESC
                LIMIT 10
            """
            
            self.env.cr.execute(query, (date_from, date_to))
            results = self.env.cr.fetchall()
            
            labels = [r[0] for r in results]
            data = [float(r[1]) for r in results]
            
            dashboard.chart_variance_by_category_data = json.dumps({
                'labels': labels,
                'datasets': [{
                    'label': 'Valeur Écart (€)',
                    'data': data,
                    'backgroundColor': [
                        'rgba(255, 99, 132, 0.7)' if d < 0 else 'rgba(75, 192, 192, 0.7)'
                        for d in data
                    ],
                }]
            })
    
    @api.depends('period', 'date_from', 'date_to')
    def _compute_chart_stock_value(self):
        """Génère les données pour évolution valeur stock."""
        for dashboard in self:
            # Utiliser l'ORM Odoo au lieu de SQL pour éviter les problèmes de types
            quants = self.env['stock.quant'].search([
                ('location_id.usage', '=', 'internal'),
                ('quantity', '>', 0),
            ])
            
            # Agréger par catégorie
            category_values = {}
            for quant in quants:
                category = quant.product_id.categ_id.name or 'Sans catégorie'
                value = quant.quantity * quant.product_id.standard_price
                category_values[category] = category_values.get(category, 0) + value
            
            # Trier et prendre top 10
            sorted_categories = sorted(
                category_values.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            labels = [cat for cat, val in sorted_categories]
            data = [float(val) for cat, val in sorted_categories]
            
            dashboard.chart_stock_value_evolution_data = json.dumps({
                'labels': labels,
                'datasets': [{
                    'label': 'Valeur Stock (€)',
                    'data': data,
                    'backgroundColor': 'rgba(54, 162, 235, 0.7)',
                }]
            })
    
    @api.depends('period', 'date_from', 'date_to')
    def _compute_statistics(self):
        """Calcule les statistiques détaillées."""
        for dashboard in self:
            date_from, date_to = dashboard._get_date_range()
            
            domain = [
                ('date', '>=', date_from),
                ('date', '<=', date_to),
            ]
            
            inventories = self.env['stockex.stock.inventory'].search(domain)
            
            # Produits uniques inventoriés
            all_products = inventories.mapped('line_ids.product_id')
            dashboard.stat_total_products_counted = len(all_products)
            
            # Emplacements uniques
            all_locations = inventories.mapped('location_id')
            dashboard.stat_total_locations_covered = len(all_locations)
            
            # Temps moyen (approximation)
            # Supposons qu'un inventaire prend en moyenne 2-4h
            # En réalité, devrait être calculé depuis create_date et write_date
            completed = inventories.filtered(lambda i: i.state == 'validated')
            if completed:
                total_hours = 0
                for inv in completed:
                    if inv.create_date and inv.write_date:
                        delta = inv.write_date - inv.create_date
                        hours = delta.total_seconds() / 3600
                        total_hours += hours
                
                dashboard.stat_average_time_per_inventory = total_hours / len(completed)
            else:
                dashboard.stat_average_time_per_inventory = 0.0
    
    # ========== ACTIONS ==========
    
    def action_refresh_kpis(self):
        """Force le recalcul des KPIs."""
        self.ensure_one()
        
        # Invalide le cache pour forcer le recalcul
        self.invalidate_model()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Actualisé'),
                'message': _('Les KPIs ont été actualisés.'),
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_view_inventories(self):
        """Ouvre la liste des inventaires de la période."""
        self.ensure_one()
        date_from, date_to = self._get_date_range()
        
        return {
            'name': _('Inventaires - %s') % dict(self._fields['period'].selection).get(self.period),
            'type': 'ir.actions.act_window',
            'res_model': 'stockex.stock.inventory',
            'view_mode': 'list,form',
            'domain': [
                ('date', '>=', date_from),
                ('date', '<=', date_to),
            ],
            'context': {'create': False},
        }
