# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from datetime import date


class TestStockInventory(TransactionCase):
    """Tests unitaires pour le module Stockex."""
    
    def setUp(self):
        super(TestStockInventory, self).setUp()
        
        # Créer des données de test
        self.product_1 = self.env['product.product'].create({
            'name': 'Produit Test 1',
            'default_code': 'TEST001',
            'type': 'product',
            'standard_price': 100.0,
        })
        
        self.product_2 = self.env['product.product'].create({
            'name': 'Produit Test 2',
            'default_code': 'TEST002',
            'type': 'product',
            'standard_price': 200.0,
        })
        
        self.location = self.env['stock.location'].create({
            'name': 'Emplacement Test',
            'usage': 'internal',
        })
        
        self.inventory = self.env['stockex.stock.inventory'].create({
            'name': 'TEST-INV-001',
            'date': date.today(),
            'location_id': self.location.id,
        })
    
    def test_01_inventory_creation(self):
        """Test la création d'un inventaire."""
        self.assertEqual(self.inventory.state, 'draft')
        self.assertEqual(self.inventory.name, 'TEST-INV-001')
        self.assertIsNotNone(self.inventory.user_id)
    
    def test_02_inventory_workflow(self):
        """Test le workflow complet d'un inventaire."""
        # Ajouter des lignes
        self.env['stockex.stock.inventory.line'].create({
            'inventory_id': self.inventory.id,
            'product_id': self.product_1.id,
            'location_id': self.location.id,
            'product_qty': 10.0,
            'standard_price': 100.0,
        })
        
        # Démarrer
        self.inventory.action_start()
        self.assertEqual(self.inventory.state, 'in_progress')
        
        # Valider
        self.inventory.action_validate()
        self.assertEqual(self.inventory.state, 'done')
        self.assertIsNotNone(self.inventory.validator_id)
        self.assertIsNotNone(self.inventory.validation_date)
    
    def test_03_inventory_line_difference(self):
        """Test le calcul des différences."""
        # Créer un quant initial
        self.env['stock.quant'].create({
            'product_id': self.product_1.id,
            'location_id': self.location.id,
            'quantity': 5.0,
        })
        
        # Créer une ligne d'inventaire
        line = self.env['stockex.stock.inventory.line'].create({
            'inventory_id': self.inventory.id,
            'product_id': self.product_1.id,
            'location_id': self.location.id,
            'product_qty': 10.0,
            'standard_price': 100.0,
        })
        
        # Vérifier la quantité théorique
        self.assertEqual(line.theoretical_qty, 5.0)
        
        # Vérifier la différence
        self.assertEqual(line.difference, 5.0)
    
    def test_04_inventory_validation_without_lines(self):
        """Test qu'on ne peut pas démarrer un inventaire sans lignes."""
        with self.assertRaises(UserError):
            self.inventory.action_start()
    
    def test_05_barcode_scan(self):
        """Test le scan de code-barres."""
        # Ajouter un code-barres au produit
        self.product_1.write({'barcode': '1234567890123'})
        
        # Créer une ligne avec scan
        line = self.env['stockex.stock.inventory.line'].create({
            'inventory_id': self.inventory.id,
            'scanned_barcode': '1234567890123',
            'location_id': self.location.id,
            'product_qty': 5.0,
            'standard_price': 100.0,
        })
        
        # Vérifier que le produit a été trouvé
        self.assertEqual(line.product_id.id, self.product_1.id)
    
    def test_06_approval_workflow(self):
        """Test le workflow d'approbation."""
        # Ajouter des lignes
        self.env['stockex.stock.inventory.line'].create({
            'inventory_id': self.inventory.id,
            'product_id': self.product_1.id,
            'location_id': self.location.id,
            'product_qty': 10.0,
            'standard_price': 100.0,
        })
        
        # Démarrer
        self.inventory.action_start()
        
        # Demander approbation
        self.inventory.action_request_approval()
        self.assertEqual(self.inventory.state, 'pending_approval')
        
        # Approuver
        self.inventory.action_approve()
        self.assertEqual(self.inventory.state, 'approved')
        self.assertIsNotNone(self.inventory.approver_id)
        self.assertIsNotNone(self.inventory.approval_date)
    
    def test_07_location_barcode_generation(self):
        """Test la génération de code-barres pour emplacements."""
        self.location.action_generate_barcode()
        self.assertIsNotNone(self.location.barcode)
        self.assertTrue(self.location.barcode.startswith('LOC'))
    
    def test_08_cycle_count_config(self):
        """Test la configuration de comptage cyclique."""
        config = self.env['stockex.cycle.count.config'].create({
            'name': 'Config Test',
            'location_ids': [(6, 0, [self.location.id])],
            'frequency': 'monthly',
            'products_per_count': 10,
        })
        
        self.assertEqual(config.name, 'Config Test')
        self.assertTrue(config.active)
        
        # Générer un comptage
        result = config.action_generate_cycle_count()
        self.assertEqual(result['res_model'], 'stockex.stock.inventory')
    
    def test_09_inventory_comparison(self):
        """Test la comparaison d'inventaires."""
        # Créer deux inventaires validés
        inv1 = self.env['stockex.stock.inventory'].create({
            'name': 'INV-001',
            'date': date.today(),
            'state': 'done',
        })
        
        inv2 = self.env['stockex.stock.inventory'].create({
            'name': 'INV-002',
            'date': date.today(),
            'state': 'done',
        })
        
        # Créer un wizard de comparaison
        wizard = self.env['stockex.inventory.comparison'].create({
            'inventory_1_id': inv1.id,
            'inventory_2_id': inv2.id,
            'comparison_type': 'both',
        })
        
        # Effectuer la comparaison
        result = wizard.action_compare()
        self.assertEqual(result['res_model'], 'stockex.inventory.comparison.result')
    
    def test_10_photo_attachments(self):
        """Test les pièces jointes photo sur les lignes."""
        import base64
        
        line = self.env['stockex.stock.inventory.line'].create({
            'inventory_id': self.inventory.id,
            'product_id': self.product_1.id,
            'location_id': self.location.id,
            'product_qty': 10.0,
            'standard_price': 100.0,
            'image_1': base64.b64encode(b'fake_image_data'),
            'note': 'Test note',
        })
        
        self.assertIsNotNone(line.image_1)
        self.assertEqual(line.note, 'Test note')
