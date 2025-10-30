# Changelog Odoo 18 - Module Stockex

Ce document liste tous les changements appliqués pour aligner le module sur les **standards et bonnes pratiques Odoo 18**.

---

## 🔄 Changements Odoo 18 Appliqués

### 1. **Balise `<tree>` → `<list>`** ⚠️ IMPORTANT

#### ❌ Ancienne méthode (Odoo < 18)
```xml
<tree string="Inventaires">
    <field name="name"/>
</tree>
```

#### ✅ Nouvelle méthode (Odoo 18)
```xml
<list string="Inventaires">
    <field name="name"/>
</list>
```

**Raison:** Odoo 18 utilise `<list>` au lieu de `<tree>` pour les vues de liste. C'est une nomenclature plus claire et cohérente.

**Impact:**
- ID de vue : `view_..._tree` → `view_..._list`
- view_mode : `tree,form` → `list,form`
- Nom de vue : `....tree` → `....list`

---

### 2. **Attribut `attrs` déprécié** ⚠️ IMPORTANT

#### ❌ Ancienne méthode (Odoo < 18)
```xml
<field name="date" attrs="{'readonly': [('state', '!=', 'draft')]}"/>
<button name="action_start" attrs="{'invisible': [('state', '!=', 'draft')]}"/>
```

#### ✅ Nouvelle méthode (Odoo 18)
```xml
<field name="date" readonly="state != 'draft'"/>
<button name="action_start" invisible="state != 'draft'"/>
```

**Raison:** Les attributs directs (`invisible`, `readonly`, `required`) utilisent des expressions Python plus simples et plus lisibles.

**Avantages:**
- Syntaxe Python directe (plus simple)
- Moins verbose
- Meilleure lisibilité
- Support complet des expressions Python

---

### 3. **Structure XML des Vues**

#### ❌ Ancienne méthode (Odoo < 18)
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <record id="..." model="...">
            ...
        </record>
    </data>
</odoo>
```

#### ✅ Nouvelle méthode (Odoo 18)
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="..." model="...">
        ...
    </record>
</odoo>
```

**Raison:** Odoo 18 ne requiert plus la balise `<data>` pour encapsuler les records.

---

### 2. **Visibilité des Boutons**

#### ❌ Ancienne méthode
```xml
<button name="action_start" states="draft" .../>
```

#### ✅ Nouvelle méthode (Odoo 18)
```xml
<button name="action_start" invisible="state != 'draft'" .../>
```

**Raison:** L'attribut `invisible` offre plus de flexibilité avec des expressions Python complètes.

---

### 3. **Widgets Modernes**

#### Nouveaux widgets ajoutés
```xml
<!-- Avatar utilisateur avec photo -->
<field name="user_id" widget="many2one_avatar_user"/>

<!-- Badge coloré pour état -->
<field name="state" widget="badge" 
       decoration-info="state == 'draft'" 
       decoration-warning="state == 'in_progress'"/>
```

---

### 4. **Décorations Visuelles dans Tree View**

```xml
<tree decoration-info="state == 'draft'" 
      decoration-warning="state == 'in_progress'" 
      decoration-success="state == 'done'"
      decoration-muted="state == 'cancel'">
```

**Couleurs:**
- `decoration-info` : Bleu (informations)
- `decoration-warning` : Orange (attention)
- `decoration-success` : Vert (succès)
- `decoration-danger` : Rouge (danger)
- `decoration-muted` : Gris (inactif)

---

### 5. **Définition des Champs Python**

#### ❌ Ancienne méthode
```python
name = fields.Char('Référence', required=True)
```

#### ✅ Nouvelle méthode (Odoo 18 - Best Practice)
```python
name = fields.Char(
    string='Référence',
    required=True,
    index=True,
    copy=False,
    tracking=True
)
```

**Avantages:**
- Lisibilité améliorée
- Paramètres explicites
- Facilite la maintenance

---

### 6. **Attributs de Modèle**

#### Nouveaux attributs ajoutés
```python
class StockInventory(models.Model):
    _name = 'stockex.stock.inventory'
    _description = 'Inventaire de Stock'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'  # ✅ Nouveau
    _rec_name = 'name'  # ✅ Nouveau
    _rec_names_search = ['name']  # ✅ Nouveau
```

**Bénéfices:**
- `_order` : Tri par défaut optimisé
- `_rec_name` : Champ d'affichage principal
- `_rec_names_search` : Champs utilisés pour la recherche

---

### 7. **Indexation des Champs**

```python
# Champs indexés pour performance
name = fields.Char(..., index=True)
date = fields.Date(..., index=True)
state = fields.Selection(..., index=True)
location_id = fields.Many2one(..., index=True)
user_id = fields.Many2one(..., index=True)
company_id = fields.Many2one(..., index=True)
```

**Impact:** Amélioration significative des performances de recherche et filtrage.

---

### 8. **Champs Non-Copiables**

```python
name = fields.Char(..., copy=False)
state = fields.Selection(..., copy=False)
```

**Raison:** Évite la duplication de références uniques ou d'états lors de la copie d'enregistrements.

---

### 9. **Paramètres Explicites Many2one/One2many**

#### ❌ Ancienne méthode
```python
user_id = fields.Many2one('res.users', string='Responsable')
line_ids = fields.One2many('stockex.stock.inventory.line', 'inventory_id')
```

#### ✅ Nouvelle méthode (Odoo 18)
```python
user_id = fields.Many2one(
    comodel_name='res.users',
    string='Responsable'
)
line_ids = fields.One2many(
    comodel_name='stockex.stock.inventory.line',
    inverse_name='inventory_id'
)
```

---

### 10. **Docstrings sur Méthodes**

```python
def action_start(self):
    """Démarre l'inventaire."""
    if not self.line_ids:
        raise UserError("Vous devez ajouter au moins une ligne...")
    return self.write({'state': 'in_progress'})
```

**Standard:** Toutes les méthodes publiques doivent avoir une docstring.

---

### 11. **Contraintes et Validations**

```python
@api.constrains('product_id', 'inventory_id')
def _check_product_uniqueness(self):
    """Vérifie qu'un produit n'apparaît qu'une seule fois par inventaire."""
    for line in self:
        if self.search_count([...]) > 0:
            raise UserError("Le produit est déjà présent...")
```

---

### 12. **Options dans les Vues**

```xml
<!-- Empêche la création inline -->
<field name="product_id" options="{'no_create': True}"/>

<!-- Champ optionnel -->
<field name="location_id" optional="show"/>

<!-- Readonly dynamique -->
<field name="date" readonly="state != 'draft'"/>
```

---

### 13. **Search View Enrichie**

```xml
<search>
    <!-- Recherche intelligente -->
    <field name="name" filter_domain="[('name','ilike',self)]"/>
    
    <!-- Séparateurs pour organiser -->
    <separator/>
    
    <!-- Filtres intelligents -->
    <filter name="my_inventories" domain="[('user_id','=',uid)]"/>
    <filter name="this_month" domain="[('date','&gt;=',context_today().strftime('%Y-%m-01'))]"/>
</search>
```

---

### 14. **Context par Défaut dans Actions**

```xml
<record id="action_stockex_inventory" model="ir.actions.act_window">
    ...
    <field name="context">{'search_default_draft': 1, 'search_default_in_progress': 1}</field>
</record>
```

**Effet:** Affiche automatiquement les inventaires en brouillon et en cours à l'ouverture.

---

### 15. **Groupes et Pages Nommés**

```xml
<group name="main_info">
    <group name="left_info">
        ...
    </group>
</group>

<notebook>
    <page name="inventory_lines" string="Lignes d'inventaire">
        ...
    </page>
</notebook>
```

**Avantage:** Facilite l'héritage et l'extension des vues.

---

### 16. **Messages d'Aide Enrichis**

```xml
<field name="help" type="html">
    <p class="o_view_nocontent_smiling_face">
        Créer un nouvel inventaire de stock
    </p>
    <p>
        Cliquez sur le bouton "Nouveau" pour créer votre premier inventaire.
    </p>
</field>
```

---

### 17. **Sécurité sur les Menus**

```xml
<menuitem id="menu_stockex_root"
          name="Gestion de Stock"
          groups="base.group_user"/>
```

---

## 📊 Résumé des Améliorations

| Catégorie | Changements | Impact |
|-----------|-------------|--------|
| **Performance** | Indexation, _order, _rec_names_search | 🚀 Recherche et tri rapides |
| **UX** | Widgets modernes, décorations, badges | 🎨 Interface intuitive |
| **Sécurité** | Contraintes, validations, groupes | 🔒 Données protégées |
| **Maintenabilité** | Docstrings, champs nommés | 📝 Code documenté |
| **Standards** | Structure Odoo 18 complète | ✅ Conformité totale |

---

## 🎯 Checklist de Conformité Odoo 18

### Changements critiques ⚠️
- [x] **`<tree>` → `<list>`** (balise renommée)
- [x] **`attrs` déprécié** (utiliser invisible, readonly, required)
- [x] **Pas de balise `<data>`** dans les XML
- [x] **`view_mode`** : `list,form` au lieu de `tree,form`

### Modèles Python
- [x] `_order`, `_rec_name`, `_rec_names_search` définis
- [x] `index=True` sur champs recherchés
- [x] `copy=False` sur champs non-copiables
- [x] `tracking=True` sur champs importants
- [x] `comodel_name` et `inverse_name` explicites
- [x] Docstrings sur toutes les méthodes
- [x] Contraintes `@api.constrains`
- [x] Messages d'erreur clairs en français
- [x] `return` sur toutes les actions

### Vues XML
- [x] Utilisation de `invisible` au lieu de `states`
- [x] Widgets modernes (badge, many2one_avatar_user)
- [x] Décorations visuelles dans les vues
- [x] Groupes et pages nommés dans les vues
- [x] Options `no_create` pour éviter création inline
- [x] Context par défaut dans les actions
- [x] Filtres intelligents dans search view
- [x] Groupes de sécurité sur les menus

---

## 🚀 Migration d'Anciennes Versions

Si vous migrez depuis Odoo < 18, voici les principaux changements à appliquer :

### Changements OBLIGATOIRES ⚠️

1. **Remplacer `<tree>` par `<list>`** dans tous les fichiers XML
   ```bash
   # Remplacer globalement
   sed -i 's/<tree/<list/g' views/*.xml
   sed -i 's/<\/tree>/<\/list>/g' views/*.xml
   ```

2. **Renommer les ID de vues**
   - `view_..._tree` → `view_..._list`
   - `....tree` → `....list`

3. **Mettre à jour view_mode**
   - `tree,form` → `list,form`
   - `tree,kanban,form` → `list,kanban,form`

4. **Supprimer `attrs` et utiliser attributs directs**
   ```xml
   <!-- Ancien -->
   <field name="date" attrs="{'readonly': [('state', '!=', 'draft')]}"/>
   
   <!-- Nouveau -->
   <field name="date" readonly="state != 'draft'"/>
   ```

### Autres changements recommandés

5. **Supprimer toutes les balises `<data>`** dans les fichiers XML
6. **Remplacer `states="..."` par `invisible="..."`**
7. **Ajouter `_order`, `_rec_name` sur les modèles**
8. **Indexer les champs fréquemment recherchés**
9. **Ajouter les widgets modernes** (badge, many2one_avatar_user)
10. **Documenter toutes les méthodes** avec des docstrings
11. **Utiliser des paramètres explicites** (comodel_name, string, etc.)

---

## 📚 Références

- Documentation Odoo 18: https://www.odoo.com/documentation/18.0/
- Coding Guidelines: https://www.odoo.com/documentation/18.0/contributing/development/coding_guidelines.html
- ORM API: https://www.odoo.com/documentation/18.0/developer/reference/backend/orm.html

---

**Version:** 18.0.1.0.0  
**Dernière mise à jour:** 18 Octobre 2025  
**Module:** stockex - Gestion d'Inventaire de Stock
