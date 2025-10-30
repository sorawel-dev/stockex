# 🛠️ Guide d'Implémentation - Optimisations Stockex

## 📋 Introduction

Ce guide pas-à-pas vous accompagne dans l'implémentation des optimisations proposées pour le module Stockex.

---

## 🚀 Quick Start - Les 3 Premières Optimisations

### 1. Index SQL (15 minutes)

**Objectif** : Améliorer performances requêtes x5-10

#### Étapes

1. **Créer fichier** : `migrations/18.0.3.4.0/post-migrate.py`

```python
def migrate(cr, version):
    """Ajoute index composites pour performance."""
    
    # Index produit + emplacement
    cr.execute("""
        CREATE INDEX IF NOT EXISTS idx_inventory_line_product_location 
        ON stockex_stock_inventory_line (product_id, location_id)
    """)
    
    # Index inventaire + produit
    cr.execute("""
        CREATE INDEX IF NOT EXISTS idx_inventory_line_inv_product 
        ON stockex_stock_inventory_line (inventory_id, product_id)
    """)
    
    # Index date pour recherches temporelles
    cr.execute("""
        CREATE INDEX IF NOT EXISTS idx_inventory_date 
        ON stockex_stock_inventory (date DESC)
    """)
```

2. **Mettre à jour** `__manifest__.py`

```python
'version': '18.0.3.4.0',  # Nouvelle version
```

3. **Appliquer migration**

```bash
odoo-bin -d your_database -u stockex
```

4. **Vérifier index créés**

```sql
-- Dans PostgreSQL
SELECT indexname FROM pg_indexes 
WHERE tablename = 'stockex_stock_inventory_line';
```

---

### 2. Cache LRU Import (30 minutes)

**Objectif** : Réduire requêtes SQL de 60-80%

#### Étapes

1. **Modifier** `wizards/import_excel_wizard.py`

```python
from functools import lru_cache

class ImportExcelWizard(models.TransientModel):
    _name = 'stockex.import.excel.wizard'
    
    # Ajouter après les champs existants
    
    @lru_cache(maxsize=1000)
    def _cached_product_search(self, product_code):
        """Cache produits."""
        product = self.env['product.product'].search([
            ('default_code', '=', product_code)
        ], limit=1)
        return product.id if product else False
    
    @lru_cache(maxsize=500)
    def _cached_warehouse_search(self, warehouse_code):
        """Cache entrepôts."""
        warehouse = self.env['stock.warehouse'].search([
            ('code', '=', warehouse_code)
        ], limit=1)
        return warehouse.lot_stock_id.id if warehouse else False
```

2. **Utiliser dans action_import()**

```python
def action_import(self):
    
    # AVANT import : vider caches
    self._cached_product_search.cache_clear()
    self._cached_warehouse_search.cache_clear()
    
    for i, line in enumerate(lines):
        product_code = str(line.get('CODE PRODUIT', '')).strip()
        
        # REMPLACER
        # product_id = products_cache.get(product_code)
        
        # PAR
        product_id = self._cached_product_search(product_code)
        
        # Si pas trouvé, créer et mettre en cache
        if not product_id and self.create_missing_products:
            product = self._create_product(...)
            # Le cache se mettra à jour automatiquement
```

3. **Tester**

```bash
# Import fichier test 1000 lignes
# Comparer temps avant/après
```

---

### 3. Validation en Masse (1 heure)

**Objectif** : Valider 10 inventaires en 1 minute au lieu de 20

#### Étapes

1. **Ajouter méthode dans** `models/models.py`

```python
class StockInventory(models.Model):
    _name = 'stockex.stock.inventory'
    
    
    def action_validate_batch(self):
        """Valide plusieurs inventaires."""
        validated = []
        errors = []
        
        for inventory in self:
            try:
                if inventory.state not in ['approved', 'in_progress']:
                    continue
                
                inventory.action_validate()
                validated.append(inventory.name)
                self.env.cr.commit()
                
            except Exception as e:
                errors.append(f"{inventory.name}: {str(e)}")
                self.env.cr.rollback()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Validation Terminée',
                'message': f"✅ {len(validated)} validé(s)\n❌ {len(errors)} erreur(s)",
                'type': 'success',
                'sticky': True,
            }
        }
```

2. **Créer** `data/server_actions.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="action_validate_batch" model="ir.actions.server">
        <field name="name">Valider en Masse</field>
        <field name="model_id" ref="model_stockex_stock_inventory"/>
        <field name="binding_model_id" ref="model_stockex_stock_inventory"/>
        <field name="binding_view_types">list</field>
        <field name="state">code</field>
        <field name="code">action = records.action_validate_batch()</field>
    </record>
</odoo>
```

3. **Ajouter dans** `__manifest__.py`

```python
'data': [
    # ... existing files ...
    'data/server_actions.xml',  # AJOUTER
],
```

4. **Tester**

- Créer 5 inventaires test
- Sélectionner dans liste
- Action → Valider en Masse
- Vérifier résultat

---

## 📊 Optimisations Avancées

### Templates d'Inventaire (4 heures)

#### 1. Créer le Modèle

**Fichier** : `models/inventory_template.py`

```python
# Voir OPTIMISATIONS_CODE_EXEMPLES.md pour code complet
```

#### 2. Ajouter dans `models/__init__.py`

```python
from . import inventory_template
```

#### 3. Créer Vues

**Fichier** : `views/inventory_template_views.xml`

```xml
<!-- Voir OPTIMISATIONS_CODE_EXEMPLES.md -->
```

#### 4. Ajouter Sécurité

**Fichier** : `security/ir.model.access.csv`

```csv
access_inventory_template_user,Template User,model_stockex_inventory_template,group_stockex_user,1,1,1,0
access_inventory_template_manager,Template Manager,model_stockex_inventory_template,group_stockex_manager,1,1,1,1
```

#### 5. Mettre à jour Manifest

```python
'data': [
    # ... existing ...
    'views/inventory_template_views.xml',
],
```

---

### Classification ABC (6 heures)

#### Implémentation Complète

1. **Créer** `models/product_abc.py` (voir exemples)
2. **Ajouter** vues XML
3. **Créer** cron pour calcul automatique
4. **Intégrer** avec comptage cyclique
5. **Tester** sur données réelles

---

## 🧪 Tests & Validation

### Tests Unitaires

**Créer** : `tests/test_optimizations.py`

```python
from odoo.tests import TransactionCase

class TestOptimizations(TransactionCase):
    
    def test_cache_lru_performance(self):
        """Test cache LRU améliore performance."""
        wizard = self.env['stockex.import.excel.wizard'].create({...})
        
        # Mesurer temps sans cache
        start = time.time()
        for i in range(100):
            wizard._search_product(f'PROD{i}')
        time_without = time.time() - start
        
        # Mesurer temps avec cache
        start = time.time()
        for i in range(100):
            wizard._cached_product_search(f'PROD{i}')
        time_with = time.time() - start
        
        self.assertLess(time_with, time_without * 0.3)  # Au moins 70% plus rapide
    
    def test_batch_validation(self):
        """Test validation en masse."""
        inventories = self.env['stockex.stock.inventory'].create([
            {'name': f'Test {i}', 'state': 'approved'}
            for i in range(10)
        ])
        
        result = inventories.action_validate_batch()
        
        self.assertTrue(all(inv.state == 'done' for inv in inventories))
```

### Tests de Performance

**Script** : `tests/benchmark_optimizations.py`

```python
import time
from odoo import api

def benchmark_import(env, nb_lines):
    """Benchmark import Excel."""
    # Créer fichier test
    # ...
    
    start = time.time()
    wizard.action_import()
    duration = time.time() - start
    
    print(f"Import {nb_lines} lignes: {duration:.2f}s")
    print(f"Vitesse: {nb_lines/duration:.0f} lignes/sec")

# Exécuter
benchmark_import(env, 1000)
benchmark_import(env, 5000)
benchmark_import(env, 10000)
```

---

## 📈 Monitoring & Métriques

### Activer Logs Performance

**Fichier** : `models/models.py`

```python
import logging
import time
from functools import wraps

_logger = logging.getLogger(__name__)

def log_performance(func):
    """Décorateur pour logger performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        
        _logger.info(
            f"Performance: {func.__name__} executed in {duration:.3f}s"
        )
        return result
    return wrapper

class StockInventory(models.Model):
    # ... 
    
    @log_performance
    def action_validate(self):
        return super().action_validate()
```

### Dashboard Métriques

**Créer vue** pour suivre :

```python
class OptimizationMetrics(models.Model):
    _name = 'stockex.optimization.metrics'
    
    date = fields.Date(default=fields.Date.today)
    import_avg_time = fields.Float(string='Temps Import Moyen (s)')
    validation_avg_time = fields.Float(string='Temps Validation Moyen (s)')
    cache_hit_rate = fields.Float(string='Taux Cache Hit (%)')
    sql_query_count = fields.Integer(string='Nombre Requêtes SQL')
```

---

## 🔧 Dépannage

### Problèmes Courants

#### 1. Cache ne fonctionne pas

**Symptôme** : Pas d'amélioration performance

**Solution** :
```python
# Vérifier cache est actif
import sys
print(sys.modules['functools'].lru_cache)

# Vider cache si nécessaire
wizard._cached_product_search.cache_clear()
```

#### 2. Index non créés

**Symptôme** : Pas de gain performance

**Diagnostic** :
```sql
-- Vérifier index
SELECT * FROM pg_indexes 
WHERE tablename LIKE 'stockex%';

-- Recréer manuellement si besoin
CREATE INDEX ...
```

#### 3. Validation masse échoue

**Symptôme** : Erreur lors validation

**Solution** :
```python
# Ajouter try/except plus détaillé
try:
    inventory.action_validate()
except Exception as e:
    _logger.error(f"Erreur validation {inventory.name}: {e}", exc_info=True)
```

---

## 📚 Ressources

### Documentation

- [OPTIMISATIONS_PROPOSEES.md](OPTIMISATIONS_PROPOSEES.md) - Vue d'ensemble
- [OPTIMISATIONS_CODE_EXEMPLES.md](OPTIMISATIONS_CODE_EXEMPLES.md) - Code complet
- [OPTIMISATIONS_ROADMAP.md](OPTIMISATIONS_ROADMAP.md) - Planning

### Outils

- **pgAdmin** : Analyse requêtes SQL
- **py-spy** : Profiling Python
- **Odoo Debug Mode** : Tests en dev

---

## ✅ Checklist Finale

### Avant Déploiement

- [ ] Tests unitaires passent
- [ ] Benchmarks montrent amélioration
- [ ] Documentation à jour
- [ ] Code review OK
- [ ] Backup BDD

### Après Déploiement

- [ ] Monitoring 24h
- [ ] Vérifier logs erreurs
- [ ] Feedback utilisateurs
- [ ] Métriques collectées
- [ ] Hotfix si nécessaire

---

**Support** : contact@sorawel.com  
**Version** : 1.0  
**Date** : 2025-10-28
