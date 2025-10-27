# -*- coding: utf-8 -*-
{
    'name': "Stockex",
    'summary': "Module de gestion avancée des inventaires de stock (Compatible Odoo 18/19)",
    'description': """
Gestion d'Inventaire de Stock
==============================
Ce module permet de gérer les inventaires de stock avec :
* Création et suivi d'inventaires
* Gestion des lignes d'inventaire avec quantités théoriques et réelles
* Calcul automatique des différences
* Workflow de validation avancé (Brouillon -> En cours -> Approbation -> Validé)
* Suivi des activités et messagerie intégrée
* Import CSV et Excel pour création rapide d'inventaires
* Intégration Kobo Collect pour collecte mobile
* **NOUVEAU**: Scan de codes-barres pour inventaire mobile
* **NOUVEAU**: Pièces jointes photo par ligne d'inventaire
* **NOUVEAU**: Workflow d'approbation multi-niveaux
* **NOUVEAU**: Comparaison d'inventaires entre périodes
* **NOUVEAU**: Comptage cyclique automatisé
* **NOUVEAU**: Génération de codes-barres pour emplacements
* **NOUVEAU**: Synchronisation automatique Kobo (cron)
* **NOUVEAU**: Tests unitaires complets
* **NOUVEAU v18.0.3.0.0**: Génération écritures comptables automatiques
* **NOUVEAU v18.0.3.0.0**: Assistant de stock initial pour BD vide
* **NOUVEAU v18.0.3.0.0**: Configuration guidée des catégories de produits
    """,

    'author': 'Sorawel, www.sorawel.com',
    'website': 'https://www.sorawel.com',
    'depends': ['base', 'mail', 'stock', 'product', 'account'],
    'external_dependencies': {
        'python': ['openpyxl', 'python-barcode'],
    },
    'category': 'Inventory/Inventory',
    'version': '18.0.3.2.0',
    # Compatible avec Odoo 18.0 et 19.0
    'data': [
        'security/stockex_security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/dashboard_data.xml',
        'data/product_categories_config.xml',
        'data/cron_jobs.xml',
        'views/res_config_settings_views.xml',
        'views/stock_warehouse_views.xml',
        'views/stock_location_views.xml',
        'views/product_category_config_views.xml',
        'views/kobo_config_views.xml',
        'views/inventory_dashboard_views.xml',
        'views/dashboard_home_form_view.xml',
        'views/dashboard_home_views.xml',
        'views/stock_reports_views.xml',
        'wizards/import_method_wizard_views.xml',
        'wizards/import_inventory_wizard_views.xml',
        'wizards/import_excel_wizard_views.xml',
        'wizards/import_kobo_wizard_views.xml',
        'wizards/fix_locations_wizard_views.xml',
        'wizards/initial_stock_wizard_views.xml',
        'views/stock_inventory_views.xml',
        'reports/inventory_report.xml',
        'views/menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'stockex/static/src/css/dashboard.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'web_icon': 'stockex/static/description/icon.png',
}

