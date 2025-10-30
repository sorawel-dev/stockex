# 💻 Exemples de Code - Optimisations Stockex

## 📋 Table des Matières

1. [Templates d'Inventaire](#templates)
2. [Validation en Masse](#validation-masse)
3. [Cache LRU](#cache-lru)
4. [Classification ABC](#abc)
5. [API REST](#api-rest)

---

## 🎯 1. Templates d'Inventaire {#templates}

### Nouveau Fichier: `models/inventory_template.py`

```python
# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class StockInventoryTemplate(models.Model):
    """Templates pour création rapide d'inventaires."""
    _name = 'stockex.inventory.template'
    _description = 'Template Inventaire'
    _inherit = ['mail.thread']
    
    name = fields.Char(
        string='Nom Template',
        required=True,
        tracking=True
    )
    active = fields.Boolean(default=True)
    
    # Configuration
    location_ids = fields.Many2many(
        'stock.location',
        string='Emplacements',
        domain="[('usage', '=', 'internal')]"
    )
    category_ids = fields.Many2many(
        'product.category',
        string='Catégories de Produits'
    )
    product_ids = fields.Many2many(
        'product.product',
        string='Produits Spécifiques'
    )
    
    # Options
    frequency = fields.Selection([
        ('daily', 'Quotidien'),
        ('weekly', 'Hebdomadaire'),
        ('monthly', 'Mensuel'),
        ('quarterly', 'Trimestriel'),
        ('yearly', 'Annuel'),
    ], string='Fréquence Suggérée', default='monthly')
    
    accounting_enabled = fields.Boolean(
        string='Comptabilité Activée',
        default=True
    )
    require_approval = fields.Boolean(
        string='Approbation Requise',
        default=True
    )
    
    # Statistiques
    usage_count = fields.Integer(
        string='Nombre d\'utilisations',
        compute='_compute_usage_count'
    )
    last_used = fields.Datetime(
        string='Dernière utilisation',
        compute='_compute_usage_count'
    )
    
    @api.depends('name')
    def _compute_usage_count(self):
        """Compte le nombre d'utilisations du template."""
        for template in self:
            inventories = self.env['stockex.stock.inventory'].search([
                ('description', 'ilike', f'Template: {template.name}')
            ])
            template.usage_count = len(inventories)
            template.last_used = inventories[0].create_date if inventories else False
    
    def action_create_from_template(self):
        """Crée un inventaire depuis le template."""
        self.ensure_one()
        
        # Créer l'inventaire
        inventory = self.env['stockex.stock.inventory'].create({
            'name': self.env['ir.sequence'].next_by_code('stockex.stock.inventory'),
            'date': fields.Date.today(),
            'accounting_enabled': self.accounting_enabled,
            'description': f'Créé depuis template: {self.name}',
            'state': 'draft',
        })
        
        # Créer les lignes automatiquement
        lines_vals = []
        
        for location in self.location_ids:
            # Déterminer les produits à inclure
            domain = [('type', '=', 'product')]
            
            if self.product_ids:
                # Produits spécifiques définis
                products = self.product_ids
            else:
                # Filtrer par catégories
                if self.category_ids:
                    domain.append(('categ_id', 'in', self.category_ids.ids))
                products = self.env['product.product'].search(domain)
            
            # Créer ligne pour chaque produit
            for product in products:
                lines_vals.append({
                    'inventory_id': inventory.id,
                    'product_id': product.id,
                    'location_id': location.id,
                    'standard_price': product.standard_price,
                    'product_qty': 0.0,  # À compléter par l'utilisateur
                })
        
        # Créer toutes les lignes en batch
        if lines_vals:
            self.env['stockex.stock.inventory.line'].create(lines_vals)
        
        # Message de confirmation
        self.message_post(
            body=f"Inventaire {inventory.name} créé avec {len(lines_vals)} lignes"
        )
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Inventaire Créé',
            'res_model': 'stockex.stock.inventory',
            'res_id': inventory.id,
            'view_mode': 'form',
            'target': 'current',
        }
```

### Vue XML: `views/inventory_template_views.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Form View -->
    <record id="view_inventory_template_form" model="ir.ui.view">
        <field name="name">stockex.inventory.template.form</field>
        <field name="model">stockex.inventory.template</field>
        <field name="arch" type="xml">
            <form>
                <header>
                    <button name="action_create_from_template" 
                            type="object" 
                            string="Créer Inventaire" 
                            class="oe_highlight"/>
                </header>
                <sheet>
                    <div class="oe_title">
                        <h1>
                            <field name="name" placeholder="Nom du template..."/>
                        </h1>
                    </div>
                    <group>
                        <group>
                            <field name="active"/>
                            <field name="frequency"/>
                            <field name="usage_count"/>
                        </group>
                        <group>
                            <field name="accounting_enabled"/>
                            <field name="require_approval"/>
                            <field name="last_used"/>
                        </group>
                    </group>
                    <notebook>
                        <page string="Configuration">
                            <group>
                                <field name="location_ids" widget="many2many_tags"/>
                                <field name="category_ids" widget="many2many_tags"/>
                                <field name="product_ids" widget="many2many_tags"/>
                            </group>
                        </page>
                    </notebook>
                </sheet>
                <div class="oe_chatter">
                    <field name="message_ids"/>
                </div>
            </form>
        </field>
    </record>

    <!-- Tree View -->
    <record id="view_inventory_template_tree" model="ir.ui.view">
        <field name="name">stockex.inventory.template.tree</field>
        <field name="model">stockex.inventory.template</field>
        <field name="arch" type="xml">
            <tree>
                <field name="name"/>
                <field name="frequency"/>
                <field name="usage_count"/>
                <field name="last_used"/>
                <field name="active" widget="boolean_toggle"/>
            </tree>
        </field>
    </record>

    <!-- Action -->
    <record id="action_inventory_template" model="ir.actions.act_window">
        <field name="name">Templates d'Inventaire</field>
        <field name="res_model">stockex.inventory.template</field>
        <field name="view_mode">tree,form</field>
    </record>

    <!-- Menu -->
    <menuitem id="menu_inventory_template"
              name="Templates"
              parent="menu_stockex_config"
              action="action_inventory_template"
              sequence="50"/>
</odoo>
```

---

## ✅ 2. Validation en Masse {#validation-masse}

### Modification: `models/models.py`

```python
# Ajouter cette méthode dans class StockInventory

def action_validate_batch(self):
    """Valide plusieurs inventaires en batch avec rapport."""
    validated = []
    errors = []
    
    for inventory in self:
        try:
            # Vérifier l'état
            if inventory.state not in ['approved', 'in_progress']:
                errors.append({
                    'inventory': inventory.name,
                    'error': f"État invalide: {inventory.state}"
                })
                continue
            
            # Vérifier lignes
            if not inventory.line_ids:
                errors.append({
                    'inventory': inventory.name,
                    'error': "Aucune ligne à valider"
                })
                continue
            
            # Valider
            inventory.action_validate()
            validated.append(inventory.name)
            
            # Commit après chaque inventaire pour sécurité
            self.env.cr.commit()
            
        except Exception as e:
            errors.append({
                'inventory': inventory.name,
                'error': str(e)
            })
            self.env.cr.rollback()
    
    # Message récapitulatif
    message = f"""
    ✅ Validation en Masse Terminée
    
    • Inventaires validés: {len(validated)}
    • Erreurs: {len(errors)}
    """
    
    if errors:
        message += "\n\nDétails des erreurs:\n"
        for err in errors[:10]:
            message += f"- {err['inventory']}: {err['error']}\n"
    
    return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
            'title': 'Validation en Masse',
            'message': message,
            'type': 'success' if not errors else 'warning',
            'sticky': True,
        }
    }
```

### Action Serveur: `data/server_actions.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="action_validate_inventory_batch" model="ir.actions.server">
        <field name="name">Valider en Masse</field>
        <field name="model_id" ref="model_stockex_stock_inventory"/>
        <field name="binding_model_id" ref="model_stockex_stock_inventory"/>
        <field name="binding_view_types">list</field>
        <field name="state">code</field>
        <field name="code">
action = records.action_validate_batch()
        </field>
    </record>
</odoo>
```

---

## 🚀 3. Cache LRU pour Imports {#cache-lru}

### Modification: `wizards/import_excel_wizard.py`

```python
from functools import lru_cache

class ImportExcelWizard(models.TransientModel):
    _name = 'stockex.import.excel.wizard'
    
    
    @api.model
    @lru_cache(maxsize=1000)
    def _cached_product_search(self, product_code):
        """Recherche produit avec cache."""
        product = self.env['product.product'].search([
            ('default_code', '=', product_code)
        ], limit=1)
        return product.id if product else False
    
    @api.model
    @lru_cache(maxsize=500)
    def _cached_location_search(self, location_code):
        """Recherche emplacement avec cache."""
        warehouse = self.env['stock.warehouse'].search([
            ('code', '=', location_code)
        ], limit=1)
        return warehouse.lot_stock_id.id if warehouse else False
    
    @api.model
    @lru_cache(maxsize=200)
    def _cached_category_search(self, category_code):
        """Recherche catégorie avec cache."""
        category = self.env['product.category'].search([
            ('name', '=', category_code)
        ], limit=1)
        return category.id if category else False
    
    def action_import(self):
        """Import avec cache optimisé."""
        self.ensure_one()
        
        # Vider les caches avant import
        self._cached_product_search.cache_clear()
        self._cached_location_search.cache_clear()
        self._cached_category_search.cache_clear()
        
        lines = self._parse_excel()
        
        # ... import logic ...
        
        for i, line in enumerate(lines):
            product_code = str(line.get('CODE PRODUIT', '')).strip()
            location_code = str(line.get('CODE ENTREPOT', '')).strip()
            
            # Utiliser cache
            product_id = self._cached_product_search(product_code)
            location_id = self._cached_location_search(location_code)
            
            if not product_id:
                # Créer et mettre en cache
                product = self._create_product(product_code, ...)
                self._cached_product_search.cache_info()  # Stats cache
            
            # ... rest of import ...
```

---

## 📊 4. Classification ABC {#abc}

### Nouveau Fichier: `models/product_abc.py`

```python
# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductABCAnalysis(models.Model):
    """Classification ABC des produits par valeur."""
    _name = 'stockex.product.abc'
    _description = 'Analyse ABC Produits'
    _rec_name = 'product_id'
    
    product_id = fields.Many2one(
        'product.product',
        string='Produit',
        required=True,
        ondelete='cascade'
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company
    )
    
    # Calculs
    annual_value = fields.Float(
        string='Valeur Annuelle Stock',
        compute='_compute_abc_metrics',
        store=True
    )
    turnover_count = fields.Integer(
        string='Nombre Rotations/An',
        compute='_compute_abc_metrics'
    )
    
    # Classification
    abc_class = fields.Selection([
        ('A', 'Classe A (80% valeur - Haute importance)'),
        ('B', 'Classe B (15% valeur - Moyenne importance)'),
        ('C', 'Classe C (5% valeur - Faible importance)'),
    ], string='Classe ABC', compute='_compute_abc_class', store=True)
    
    count_frequency = fields.Selection([
        ('weekly', 'Hebdomadaire'),
        ('bi_weekly', 'Bi-mensuel'),
        ('monthly', 'Mensuel'),
        ('quarterly', 'Trimestriel'),
        ('yearly', 'Annuel'),
    ], string='Fréquence Comptage Recommandée', 
       compute='_compute_abc_class', store=True)
    
    @api.depends('product_id')
    def _compute_abc_metrics(self):
        """Calcule métriques ABC."""
        for record in self:
            # Valeur stock actuel
            quants = self.env['stock.quant'].search([
                ('product_id', '=', record.product_id.id),
                ('location_id.usage', '=', 'internal'),
                ('company_id', '=', record.company_id.id),
            ])
            
            record.annual_value = sum(
                q.quantity * record.product_id.standard_price 
                for q in quants
            )
    
    @api.model
    def compute_abc_classification(self):
        """Calcule classification ABC pour tous produits."""
        # Récupérer tous produits avec leur valeur
        query = """
            SELECT 
                pp.id as product_id,
                SUM(sq.quantity * pp.standard_price) as total_value
            FROM product_product pp
            LEFT JOIN stock_quant sq ON sq.product_id = pp.id
            LEFT JOIN stock_location sl ON sl.id = sq.location_id
            WHERE sl.usage = 'internal'
            AND pp.type = 'product'
            GROUP BY pp.id
            HAVING SUM(sq.quantity) > 0
            ORDER BY total_value DESC
        """
        
        self.env.cr.execute(query)
        results = self.env.cr.fetchall()
        
        if not results:
            return
        
        total_value = sum(r[1] for r in results if r[1])
        cumulative = 0
        
        for product_id, value in results:
            cumulative += value or 0
            cumulative_pct = (cumulative / total_value * 100) if total_value else 0
            
            # Déterminer classe
            if cumulative_pct <= 80:
                abc_class = 'A'
                frequency = 'weekly'
            elif cumulative_pct <= 95:
                abc_class = 'B'
                frequency = 'bi_weekly'
            else:
                abc_class = 'C'
                frequency = 'monthly'
            
            # Créer/Mettre à jour enregistrement
            record = self.search([('product_id', '=', product_id)])
            if record:
                record.write({
                    'abc_class': abc_class,
                    'count_frequency': frequency,
                })
            else:
                self.create({
                    'product_id': product_id,
                    'abc_class': abc_class,
                    'count_frequency': frequency,
                })
    
    @api.model
    def _cron_update_abc(self):
        """Cron pour mise à jour ABC mensuelle."""
        self.compute_abc_classification()
```

---

## 🔗 5. API REST {#api-rest}

### Nouveau Fichier: `controllers/api_controller.py`

```python
# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import json
from datetime import datetime

class StockexAPIController(http.Controller):
    """API REST pour Stockex."""
    
    def _check_access(self):
        """Vérifie les droits d'accès API."""
        if not request.env.user.has_group('stockex.group_stockex_user'):
            return {'error': 'Accès non autorisé'}, 403
        return None, 200
    
    @http.route('/api/v1/stockex/inventories', 
                type='json', auth='user', methods=['GET'], csrf=False)
    def list_inventories(self, **params):
        """Liste les inventaires avec filtres."""
        # Check access
        error, status = self._check_access()
        if error:
            return error
        
        # Build domain
        domain = []
        if params.get('date_from'):
            domain.append(('date', '>=', params['date_from']))
        if params.get('date_to'):
            domain.append(('date', '<=', params['date_to']))
        if params.get('state'):
            domain.append(('state', '=', params['state']))
        
        # Search
        inventories = request.env['stockex.stock.inventory'].search(
            domain, 
            limit=params.get('limit', 100),
            offset=params.get('offset', 0)
        )
        
        return {
            'status': 'success',
            'count': len(inventories),
            'data': [{
                'id': inv.id,
                'name': inv.name,
                'date': inv.date.isoformat(),
                'state': inv.state,
                'total_lines': len(inv.line_ids),
                'user': inv.user_id.name,
            } for inv in inventories]
        }
    
    @http.route('/api/v1/stockex/inventory/<int:inventory_id>', 
                type='json', auth='user', methods=['GET'], csrf=False)
    def get_inventory(self, inventory_id):
        """Détails d'un inventaire."""
        inventory = request.env['stockex.stock.inventory'].browse(inventory_id)
        
        if not inventory.exists():
            return {'error': 'Inventaire non trouvé'}, 404
        
        return {
            'status': 'success',
            'data': {
                'id': inventory.id,
                'name': inventory.name,
                'date': inventory.date.isoformat(),
                'state': inventory.state,
                'responsible': inventory.user_id.name,
                'lines': [{
                    'product_code': l.product_id.default_code,
                    'product_name': l.product_id.name,
                    'location': l.location_id.complete_name,
                    'theoretical_qty': l.theoretical_qty,
                    'real_qty': l.product_qty,
                    'difference': l.difference,
                    'unit_price': l.standard_price,
                } for l in inventory.line_ids]
            }
        }
    
    @http.route('/api/v1/stockex/inventory', 
                type='json', auth='user', methods=['POST'], csrf=False)
    def create_inventory(self, **data):
        """Crée un inventaire via API."""
        try:
            inventory = request.env['stockex.stock.inventory'].create({
                'name': data.get('name') or request.env['ir.sequence'].next_by_code('stockex.stock.inventory'),
                'date': data.get('date', fields.Date.today()),
            })
            
            # Créer lignes
            for line_data in data.get('lines', []):
                request.env['stockex.stock.inventory.line'].create({
                    'inventory_id': inventory.id,
                    'product_id': line_data['product_id'],
                    'location_id': line_data['location_id'],
                    'product_qty': line_data['quantity'],
                })
            
            return {
                'status': 'success',
                'inventory_id': inventory.id,
                'message': f'Inventaire créé: {inventory.name}'
            }
        except Exception as e:
            return {'error': str(e)}, 400
```

---

**Développé par Sorawel** - www.sorawel.com
