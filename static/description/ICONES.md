# 🎨 Configuration des Icônes - Module Gestion d'Inventaire

## Icônes du Module

### 1. Icône App Store (Liste des modules)
**Fichier:** `static/description/icon.png`
- **Dimensions:** Recommandé 256x256 pixels
- **Format:** PNG avec transparence
- **Utilisation:** Icône affichée dans la liste des applications Odoo
- **Détection automatique:** Odoo détecte automatiquement ce fichier

### 2. Icône Menu Racine
**Configuration dans:** `__manifest__.py` et `views/stock_inventory_views.xml`

#### Dans le manifest (__manifest__.py)
```python
'web_icon': 'stockex/static/description/icon.png',
```
Cette configuration définit l'icône utilisée dans l'interface web (App Store).

#### Dans les vues (stock_inventory_views.xml)
**Configuration actuelle avec Font Awesome:**
```xml
<menuitem id="menu_stockex_root" 
          name="Gestion de Stock" 
          sequence="10" 
          web_icon="fa fa-boxes"/>

<menuitem id="menu_stockex_inventory" 
          name="Inventaires" 
          parent="menu_stockex_root" 
          action="action_stockex_inventory" 
          sequence="10" 
          web_icon="fa fa-clipboard-list"/>
```

✅ **Avantage:** Icônes vectorielles, légères et cohérentes avec l'interface Odoo 18

### 3. Icône Menu Supplémentaire (Optionnel)
**Fichier:** `static/description/menu.png`
- Peut être utilisé pour des sous-menus ou variantes
- Disponible mais non utilisé actuellement

## Structure des Fichiers

```
stockex/
├── static/
│   └── description/
│       ├── icon.png          # Icône principale (256x256)
│       ├── menu.png          # Icône menu alternative
│       ├── index.html        # Page description App Store
│       └── ICONES.md         # Ce fichier
├── __manifest__.py           # Configuration web_icon
└── views/
    └── stock_inventory_views.xml  # Configuration menuitem
```

## Format des Icônes

### Recommandations Odoo 18
- **Taille:** 256x256 pixels minimum
- **Format:** PNG (avec canal alpha pour transparence)
- **Poids:** < 50 KB pour optimisation
- **Style:** Design moderne, flat design ou matériel
- **Couleurs:** Harmonieuses avec l'interface Odoo

### Bonnes Pratiques
1. **Simplicité:** Design épuré et facilement reconnaissable
2. **Contraste:** Bonne visibilité sur fond clair et foncé
3. **Cohérence:** Style cohérent avec l'écosystème Odoo
4. **Évolutivité:** Lisible à différentes tailles (16px à 256px)

## Utilisation Alternative avec Font Awesome

Au lieu d'une image, vous pouvez utiliser des icônes Font Awesome :

### Dans le menuitem
```xml
<menuitem id="menu_stockex_root" 
          name="Gestion de Stock" 
          sequence="10" 
          web_icon="fa fa-boxes"/>
```

### Icônes Font Awesome suggérées pour la gestion de stock
- `fa fa-boxes` - Boîtes (inventaire)
- `fa fa-warehouse` - Entrepôt
- `fa fa-clipboard-list` - Liste de contrôle
- `fa fa-inventory` - Inventaire
- `fa fa-cubes` - Cubes (produits multiples)
- `fa fa-dolly` - Chariot (logistique)

## Modification des Icônes

### Pour changer l'icône du module
1. Remplacez le fichier `static/description/icon.png`
2. Respectez les dimensions 256x256 pixels
3. Redémarrez Odoo
4. Mettez à jour la liste des modules

### Pour changer l'icône du menu
**Option 1: Image personnalisée**
```python
# Dans __manifest__.py
'web_icon': 'stockex/static/description/custom_icon.png',
```

**Option 2: Font Awesome**
```xml
<!-- Dans stock_inventory_views.xml -->
<menuitem id="menu_stockex_root" 
          name="Gestion de Stock" 
          web_icon="fa fa-warehouse"/>
```

## Vérification

Pour vérifier que les icônes sont correctement configurées :

1. **App Store:** Allez dans Applications → Vérifiez l'icône du module
2. **Menu:** Vérifiez le menu principal (barre latérale gauche)
3. **Cache:** Si l'icône ne s'affiche pas, videz le cache du navigateur

## Ressources

### Outils de Création d'Icônes
- **Figma** - https://figma.com
- **Inkscape** - Logiciel libre de dessin vectoriel
- **GIMP** - Éditeur d'images libre
- **Canva** - Création en ligne

### Inspirations
- Material Design Icons - https://materialdesignicons.com
- Font Awesome - https://fontawesome.com
- Flaticon - https://flaticon.com

### Convertisseurs
- PNG to ICO Converter
- Image Resizer (pour optimiser les dimensions)

## Support

Pour toute question sur les icônes ou leur configuration, référez-vous à :
- Documentation Odoo 18 : https://www.odoo.com/documentation/18.0/
- Forum Odoo : https://www.odoo.com/forum
- GitHub Odoo : https://github.com/odoo/odoo

---

**Note:** Les icônes sont un élément important de l'identité visuelle de votre module. 
Prenez le temps de créer ou choisir des icônes de qualité professionnelle pour 
une meilleure expérience utilisateur.
