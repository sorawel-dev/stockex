# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo import fields


class TestInventoryDashboard(TransactionCase):
    """Tests unitaires pour le dashboard d'inventaire."""
    
    def setUp(self):
        super(TestInventoryDashboard, self).setUp()
        
        # Créer un entrepôt de test
        self.warehouse = self.env['stock.warehouse'].create({
            'name': 'Entrepôt Test Dashboard',
            'code': 'TESTDB',
        })
        
        # Créer des produits de test
        self.product1 = self.env['product.product'].create({
            'name': 'Produit Test Dashboard 1',
            'type': 'product',
            'default_code': 'PTDB1',
            'standard_price': 1000.0,
        })
        
        self.product2 = self.env['product.product'].create({
            'name': 'Produit Test Dashboard 2',
            'type': 'product',
            'default_code': 'PTDB2',
            'standard_price': 2000.0,
        })
        
        # Créer des inventaires de test
        self.inventory1 = self.env['stockex.stock.inventory'].create({
            'name': 'INV-TEST-DB-001',
            'date': fields.Date.today(),
            'warehouse_id': self.warehouse.id,
            'state': 'draft',
        })
        
        self.inventory2 = self.env['stockex.stock.inventory'].create({
            'name': 'INV-TEST-DB-002',
            'date': fields.Date.today() - timedelta(days=15),
            'warehouse_id': self.warehouse.id,
            'state': 'done',
            'validation_date': fields.Datetime.now() - timedelta(days=10),
        })
        
        # Créer des lignes d'inventaire avec écarts
        self.line1 = self.env['stockex.stock.inventory.line'].create({
            'inventory_id': self.inventory2.id,
            'product_id': self.product1.id,
            'location_id': self.warehouse.lot_stock_id.id,
            'theoretical_qty': 100.0,
            'product_qty': 120.0,  # Surplus de 20
        })
        
        self.line2 = self.env['stockex.stock.inventory.line'].create({
            'inventory_id': self.inventory2.id,
            'product_id': self.product2.id,
            'location_id': self.warehouse.lot_stock_id.id,
            'theoretical_qty': 50.0,
            'product_qty': 45.0,  # Manquant de 5
        })
        
        # Créer le dashboard
        self.dashboard = self.env['stockex.inventory.dashboard'].create({
            'name': 'Dashboard Test',
        })
    
    def test_01_compute_inventory_kpis(self):
        """Test du calcul des KPIs d'inventaires."""
        self.dashboard._compute_inventory_kpis()
        
        # Vérifier les compteurs
        self.assertGreaterEqual(self.dashboard.total_inventories, 2, 
                               "Au moins 2 inventaires devraient être comptés")
        self.assertGreaterEqual(self.dashboard.inventories_done, 1,
                               "Au moins 1 inventaire validé devrait être compté")
        
        # Vérifier les inventaires du mois
        self.assertGreaterEqual(self.dashboard.inventories_this_month, 0,
                               "Le compteur mensuel devrait être >= 0")
    
    def test_02_compute_stock_value_kpis(self):
        """Test du calcul des KPIs de valorisation."""
        # Créer un quant pour avoir une valeur de stock
        self.env['stock.quant'].sudo().create({
            'product_id': self.product1.id,
            'location_id': self.warehouse.lot_stock_id.id,
            'quantity': 100.0,
        })
        
        self.dashboard._compute_stock_value_kpis()
        
        # Vérifier que la valeur du stock est calculée
        self.assertGreater(self.dashboard.total_stock_value, 0,
                          "La valeur du stock devrait être > 0")
        
        # Vérifier que le taux d'écart est un pourcentage valide
        self.assertGreaterEqual(self.dashboard.avg_variance_rate, 0,
                               "Le taux d'écart devrait être >= 0")
        self.assertLessEqual(self.dashboard.avg_variance_rate, 100,
                            "Le taux d'écart devrait être <= 100")
    
    def test_03_compute_product_kpis(self):
        """Test du calcul des KPIs produits."""
        self.dashboard._compute_product_kpis()
        
        # Vérifier que les produits inventoriés sont comptés
        self.assertGreaterEqual(self.dashboard.products_inventoried, 2,
                               "Au moins 2 produits inventoriés")
        
        # Vérifier le taux de couverture
        self.assertGreaterEqual(self.dashboard.coverage_rate, 0,
                               "Le taux de couverture devrait être >= 0")
        self.assertLessEqual(self.dashboard.coverage_rate, 100,
                            "Le taux de couverture devrait être <= 100")
    
    def test_04_compute_warehouse_kpis(self):
        """Test du calcul des KPIs entrepôts."""
        self.dashboard._compute_warehouse_kpis()
        
        # Vérifier les compteurs
        self.assertGreaterEqual(self.dashboard.total_warehouses, 1,
                               "Au moins 1 entrepôt devrait exister")
        self.assertGreaterEqual(self.dashboard.warehouses_inventoried, 1,
                               "Au moins 1 entrepôt inventorié")
    
    def test_05_compute_performance_kpis(self):
        """Test du calcul des KPIs de performance."""
        self.dashboard._compute_performance_kpis()
        
        # Vérifier le délai moyen
        self.assertGreaterEqual(self.dashboard.avg_processing_days, 0,
                               "Le délai moyen devrait être >= 0")
        
        # Vérifier le taux de complétion
        self.assertGreaterEqual(self.dashboard.completion_rate, 0,
                               "Le taux de complétion devrait être >= 0")
        self.assertLessEqual(self.dashboard.completion_rate, 100,
                            "Le taux de complétion devrait être <= 100")
    
    def test_06_compute_top_variances(self):
        """Test du calcul du top des écarts."""
        self.dashboard._compute_top_variances()
        
        # Vérifier que des écarts sont détectés
        self.assertGreater(len(self.dashboard.top_variance_ids), 0,
                          "Des écarts devraient être détectés")
        
        # Vérifier que les écarts sont triés par valeur
        variances = self.dashboard.top_variance_ids
        if len(variances) > 1:
            for i in range(len(variances) - 1):
                self.assertGreaterEqual(
                    abs(variances[i].difference_value),
                    abs(variances[i+1].difference_value),
                    "Les écarts devraient être triés par valeur décroissante"
                )
    
    def test_07_compute_monthly_trend(self):
        """Test du calcul de l'évolution mensuelle."""
        self.dashboard._compute_monthly_trend()
        
        # Vérifier que 12 mois sont créés
        self.assertEqual(len(self.dashboard.monthly_trend_ids), 12,
                        "12 mois devraient être créés")
        
        # Vérifier que les mois sont triés chronologiquement
        trends = self.dashboard.monthly_trend_ids.sorted('month')
        for i in range(len(trends) - 1):
            self.assertLess(trends[i].month, trends[i+1].month,
                           "Les mois devraient être triés chronologiquement")
    
    def test_08_compute_warehouse_distribution(self):
        """Test du calcul de la répartition par entrepôt."""
        self.dashboard._compute_warehouse_distribution()
        
        # Vérifier que l'entrepôt de test est inclus
        warehouse_ids = self.dashboard.warehouse_distribution_ids.mapped('warehouse_id')
        self.assertIn(self.warehouse, warehouse_ids,
                     "L'entrepôt de test devrait être dans la répartition")
        
        # Vérifier que les compteurs sont cohérents
        for wh_dist in self.dashboard.warehouse_distribution_ids:
            self.assertGreaterEqual(wh_dist.inventory_count, 0,
                                   "Le nombre d'inventaires devrait être >= 0")
            self.assertGreaterEqual(wh_dist.stock_value, 0,
                                   "La valeur du stock devrait être >= 0")
    
    def test_09_action_refresh(self):
        """Test de l'action de rafraîchissement."""
        result = self.dashboard.action_refresh()
        
        # Vérifier que l'action retourne une notification
        self.assertEqual(result.get('type'), 'ir.actions.client',
                        "L'action devrait retourner un client action")
        self.assertEqual(result.get('tag'), 'display_notification',
                        "L'action devrait afficher une notification")
        
        # Vérifier que tous les KPIs sont recalculés
        self.assertIsNotNone(self.dashboard.total_inventories,
                            "Les KPIs devraient être calculés")
    
    def test_10_variance_model(self):
        """Test du modèle dashboard.variance."""
        variance = self.env['stockex.inventory.dashboard.variance'].create({
            'dashboard_id': self.dashboard.id,
            'product_id': self.product1.id,
            'warehouse_id': self.warehouse.id,
            'difference': 20.0,
            'difference_value': 20000.0,
        })
        
        self.assertEqual(variance.product_id, self.product1,
                        "Le produit devrait être correctement lié")
        self.assertEqual(variance.warehouse_id, self.warehouse,
                        "L'entrepôt devrait être correctement lié")
        self.assertEqual(variance.difference, 20.0,
                        "La différence devrait être 20.0")
    
    def test_11_trend_model(self):
        """Test du modèle dashboard.trend."""
        today = fields.Date.today()
        trend = self.env['stockex.inventory.dashboard.trend'].create({
            'dashboard_id': self.dashboard.id,
            'month': today,
            'inventory_count': 5,
            'variance_value': 10000.0,
        })
        
        self.assertEqual(trend.month, today,
                        "Le mois devrait être correctement défini")
        self.assertEqual(trend.inventory_count, 5,
                        "Le nombre d'inventaires devrait être 5")
        self.assertGreater(trend.variance_value, 0,
                          "La valeur des écarts devrait être > 0")
    
    def test_12_warehouse_distribution_model(self):
        """Test du modèle dashboard.warehouse."""
        wh_dist = self.env['stockex.inventory.dashboard.warehouse'].create({
            'dashboard_id': self.dashboard.id,
            'warehouse_id': self.warehouse.id,
            'inventory_count': 3,
            'stock_value': 50000.0,
        })
        
        self.assertEqual(wh_dist.warehouse_id, self.warehouse,
                        "L'entrepôt devrait être correctement lié")
        self.assertEqual(wh_dist.inventory_count, 3,
                        "Le nombre d'inventaires devrait être 3")
        self.assertGreater(wh_dist.stock_value, 0,
                          "La valeur du stock devrait être > 0")
    
    def test_13_dashboard_without_data(self):
        """Test du dashboard sans données (edge case)."""
        # Supprimer tous les inventaires
        self.env['stockex.stock.inventory'].search([]).unlink()
        
        # Créer un nouveau dashboard
        empty_dashboard = self.env['stockex.inventory.dashboard'].create({
            'name': 'Dashboard Vide',
        })
        
        # Calculer tous les KPIs
        empty_dashboard._compute_inventory_kpis()
        empty_dashboard._compute_stock_value_kpis()
        empty_dashboard._compute_product_kpis()
        
        # Vérifier que ça ne plante pas et retourne des valeurs par défaut
        self.assertEqual(empty_dashboard.total_inventories, 0,
                        "Total inventaires devrait être 0")
        self.assertEqual(empty_dashboard.total_stock_value, 0,
                        "Valeur stock devrait être 0")
        self.assertEqual(empty_dashboard.avg_variance_rate, 0,
                        "Taux écart devrait être 0")
    
    def test_14_dashboard_currency(self):
        """Test de la gestion de la devise."""
        self.assertIsNotNone(self.dashboard.currency_id,
                            "La devise devrait être définie")
        self.assertEqual(self.dashboard.currency_id, self.env.company.currency_id,
                        "La devise devrait être celle de la société")
    
    def test_15_cascade_delete(self):
        """Test de la suppression en cascade."""
        # Créer des lignes liées
        self.dashboard._compute_top_variances()
        variance_count = len(self.dashboard.top_variance_ids)
        
        # Supprimer le dashboard
        self.dashboard.unlink()
        
        # Vérifier que les lignes sont supprimées
        remaining_variances = self.env['stockex.inventory.dashboard.variance'].search([
            ('dashboard_id', '=', self.dashboard.id)
        ])
        self.assertEqual(len(remaining_variances), 0,
                        "Les variances devraient être supprimées en cascade")
