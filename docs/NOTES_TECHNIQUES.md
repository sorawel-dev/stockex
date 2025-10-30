# Notes Techniques - Module Gestion d'Inventaire de Stock

## Architecture du module

### Conformité Odoo 18
Le module a été développé en respectant strictement les standards de codage Odoo 18 :

1. **Modèles**
   - Utilisation de `mail.thread` et `mail.activity.mixin` pour le suivi
   - `tracking=True` sur les champs critiques (date, state)
   - Nomenclature claire : `stockex.stock.inventory` et `stockex.stock.inventory.line`

2. **Vues**
   - Préfixe du module dans les IDs : `view_stockex_inventory_*`
   - Structure complète : Tree, Form, Search
   - Utilisation de `statusbar` pour l'affichage de l'état
   - Chatter intégré avec `message_follower_ids`, `activity_ids`, `message_ids`

3. **Workflow**
   - États : draft → in_progress → done (ou cancel)
   - Boutons avec attribut `states` pour contrôler la visibilité
   - Classes `oe_highlight` pour les actions principales

## Améliorations possibles

### 1. Génération automatique de lignes d'inventaire
```python
def action_generate_lines(self):
    """Génère automatiquement les lignes d'inventaire basées sur l'emplacement"""
    if not self.location_id:
        raise UserError("Veuillez sélectionner un emplacement")
    
    # Récupérer les produits en stock
    quants = self.env['stock.quant'].search([
        ('location_id', '=', self.location_id.id),
        ('quantity', '>', 0)
    ])
    
    # Créer les lignes
    lines_vals = []
    for quant in quants:
        lines_vals.append({
            'inventory_id': self.id,
            'product_id': quant.product_id.id,
            'location_id': quant.location_id.id,
            'theoretical_qty': quant.quantity,
            'product_qty': 0.0,
        })
    
    self.line_ids = [(0, 0, vals) for vals in lines_vals]
```

### 2. Validation des mouvements de stock
```python
def action_validate(self):
    """Valide l'inventaire et crée les ajustements de stock"""
    for line in self.line_ids:
        if line.difference != 0:
            # Créer un mouvement de stock pour ajuster
            move = self.env['stock.move'].create({
                'name': f'Ajustement inventaire {self.name}',
                'product_id': line.product_id.id,
                'product_uom': line.product_id.uom_id.id,
                'product_uom_qty': abs(line.difference),
                'location_id': line.location_id.id if line.difference < 0 else self.env.ref('stock.stock_location_inventory').id,
                'location_dest_id': self.env.ref('stock.stock_location_inventory').id if line.difference < 0 else line.location_id.id,
            })
            move._action_confirm()
            move._action_done()
    
    self.write({'state': 'done'})
    return True
```

### 3. Séquence automatique pour les références
Dans `__manifest__.py`, ajouter :
```python
'data': [
    'data/sequence_data.xml',
    'security/ir.model.access.csv',
    ...
]
```

Créer `data/sequence_data.xml` :
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        <record id="seq_stock_inventory" model="ir.sequence">
            <field name="name">Stock Inventory</field>
            <field name="code">stockex.stock.inventory</field>
            <field name="prefix">INV/</field>
            <field name="padding">5</field>
            <field name="company_id" eval="False"/>
        </record>
    </data>
</odoo>
```

Dans le modèle :
```python
@api.model
def create(self, vals):
    if vals.get('name', 'Nouveau') == 'Nouveau':
        vals['name'] = self.env['ir.sequence'].next_by_code('stockex.stock.inventory') or 'Nouveau'
    return super(StockInventory, self).create(vals)
```

### 4. Contraintes et validations
```python
from odoo.exceptions import ValidationError

@api.constrains('date')
def _check_date(self):
    for record in self:
        if record.date > fields.Date.today():
            raise ValidationError("La date d'inventaire ne peut pas être dans le futur")

@api.constrains('line_ids')
def _check_lines(self):
    for record in self:
        if record.state == 'in_progress' and not record.line_ids:
            raise ValidationError("Vous devez ajouter au moins une ligne avant de démarrer l'inventaire")
```

### 5. Rapports et analyses
Ajouter des champs calculés pour les statistiques :
```python
total_lines = fields.Integer('Nombre de lignes', compute='_compute_totals')
total_differences = fields.Integer('Nombre de différences', compute='_compute_totals')
total_value_difference = fields.Float('Valeur totale des différences', compute='_compute_totals')

@api.depends('line_ids', 'line_ids.difference')
def _compute_totals(self):
    for record in self:
        record.total_lines = len(record.line_ids)
        record.total_differences = len(record.line_ids.filtered(lambda l: l.difference != 0))
        record.total_value_difference = sum(
            line.difference * line.product_id.standard_price 
            for line in record.line_ids
        )
```

### 6. Vue Kanban
Ajouter une vue Kanban pour une meilleure visualisation :
```xml
<record id="view_stockex_inventory_kanban" model="ir.ui.view">
    <field name="name">stockex.stock.inventory.kanban</field>
    <field name="model">stockex.stock.inventory</field>
    <field name="arch" type="xml">
        <kanban default_group_by="state">
            <field name="name"/>
            <field name="date"/>
            <field name="user_id"/>
            <templates>
                <t t-name="kanban-box">
                    <div class="oe_kanban_card">
                        <div class="oe_kanban_content">
                            <strong><field name="name"/></strong>
                            <div><field name="date"/></div>
                            <div><field name="user_id"/></div>
                        </div>
                    </div>
                </t>
            </templates>
        </kanban>
    </field>
</record>
```

### 7. Droits d'accès avancés
Créer des groupes spécifiques :
- Utilisateur Inventaire : Peut créer et modifier
- Manager Inventaire : Peut valider
- Administrateur Stock : Accès complet

### 8. Import/Export
Ajouter un assistant pour importer les comptages depuis un fichier Excel

### 9. Application mobile
Intégration possible avec l'application mobile Odoo pour le comptage sur le terrain

### 10. Alertes et notifications
Envoyer des notifications automatiques :
- Quand un inventaire est assigné
- Quand des différences importantes sont détectées
- Rappels pour les inventaires en cours depuis trop longtemps

## Performance

Pour de grandes quantités de données :
- Utiliser `prefetch` pour optimiser les requêtes
- Indexer les champs fréquemment recherchés
- Utiliser des computed fields avec `store=True` judicieusement

## Tests

Créer des tests unitaires dans `tests/` :
```python
from odoo.tests.common import TransactionCase

class TestStockInventory(TransactionCase):
    def setUp(self):
        super(TestStockInventory, self).setUp()
        self.inventory = self.env['stockex.stock.inventory'].create({
            'name': 'TEST-INV-001',
            'date': fields.Date.today(),
        })
    
    def test_inventory_workflow(self):
        """Test du workflow complet d'un inventaire"""
        self.assertEqual(self.inventory.state, 'draft')
        self.inventory.action_start()
        self.assertEqual(self.inventory.state, 'in_progress')
        self.inventory.action_validate()
        self.assertEqual(self.inventory.state, 'done')
```

## Bonnes pratiques suivies

1. ✅ Utilisation de `_name` et `_description` pour tous les modèles
2. ✅ Héritage de `mail.thread` et `mail.activity.mixin`
3. ✅ Tracking sur les champs importants
4. ✅ Utilisation de `ondelete='cascade'` pour les relations One2many
5. ✅ Labels en français pour tous les champs
6. ✅ Valeurs par défaut appropriées
7. ✅ Computed fields avec `@api.depends`
8. ✅ Structure de vues complète (Tree, Form, Search)
9. ✅ Actions et menus bien organisés
10. ✅ Documentation claire

## Ressources

- [Documentation Odoo 18](https://www.odoo.com/documentation/18.0/)
- [Coding Guidelines Odoo](https://www.odoo.com/documentation/18.0/developer/reference/backend/guidelines.html)
- [Module Stock Odoo](https://github.com/odoo/odoo/tree/18.0/addons/stock)
