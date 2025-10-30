# -*- coding: utf-8 -*-
{
    'name': "StockInv",
    'summary': "Gestion avancée des inventaires de stock (Odoo 18/19)",
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
* **NOUVEAU v18.0.4.0.0**: API REST avec 6 endpoints pour intégrations externes
* **NOUVEAU v18.0.4.0.0**: Gestion complète lots/séries avec traçabilité réglementaire
* **NOUVEAU v18.0.4.0.0**: Dashboard Analytique avec 5 KPIs temps réel et 3 graphiques
* **NOUVEAU v18.0.4.0.0**: Alertes expiration lots automatiques (pharma/alimentaire)
* **NOUVEAU v18.0.4.0.0**: Conformité réglementaire (certificats, statut qualité)
* **NOUVEAU v18.0.5.0.0**: Application Mobile PWA avec scan codes-barres
* **NOUVEAU v18.0.5.0.0**: Mode hors ligne complet (Service Worker + IndexedDB)
* **NOUVEAU v18.0.5.0.0**: Synchronisation automatique inventaires offline
* **NOUVEAU v18.0.5.0.0**: Interface tactile optimisée pour terrain
    """,

    'author': 'Sorawel, www.sorawel.com',
    'website': 'https://www.sorawel.com',
    'depends': ['base', 'mail', 'stock', 'product', 'account'],
    'external_dependencies': {
        'python': ['openpyxl'],
    },
    'category': 'Inventory/Inventory',
    'version': '18.0.7.9.1',
    # Compatible avec Odoo 18.0 et 19.0
    'data': [
        'security/stockex_security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/dashboard_data.xml',
        'data/stock_accounts_ohada.xml',
        'data/product_categories_config.xml',
        'data/cron_jobs.xml',
        'views/res_config_settings_views.xml',
        'views/stock_warehouse_views.xml',
        'views/stock_location_views.xml',
        'views/product_category_config_views.xml',
        'views/product_category_views.xml',
        'views/kobo_config_views.xml',
        'views/inventory_dashboard_views.xml',
        # Wizards d'import (définissent les actions)
        'wizards/import_method_wizard_views.xml',
        'wizards/import_inventory_wizard_views.xml',  # Définit action_import_inventory_wizard
        'wizards/import_excel_wizard_views.xml',
        'wizards/import_kobo_wizard_views.xml',
        'wizards/fix_locations_wizard_views.xml',
        'wizards/initial_stock_wizard_views.xml',  # Définit action_initial_stock_wizard - DOIT ÊTRE AVANT menus.xml
        'wizards/import_flexible_inventory_wizard_views.xml',  # Import flexible Excel/CSV
        'wizards/stock_accounts_config_wizard_views.xml',
        # Vues de base (utilisent les actions wizards)
        'views/stock_inventory_views.xml',  # Utilise action_import_inventory_wizard
        # Actions dashboard et reports (définissent les actions)
        'views/dashboard_home_views.xml',  # Définit action_stockex_dashboard_home
        'views/dashboard_home_form_view.xml',
        'views/stock_reports_views.xml',  # Définit action_stock_quant_report, etc.
        'views/analytics_dashboard_views.xml',  # Définit action_inventory_analysis
        'reports/inventory_report.xml',  # Définit action_report_inventory
        # Menus (utilisent toutes les actions)
        'views/menus.xml',  # Utilise toutes les actions
        # Vues complémentaires
        'views/mobile_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'stockex/static/src/css/dashboard.css',
            'stockex/static/src/css/cleanup_wizard.css',
            'stockex/static/src/js/analytics_dashboard.js',
        ],
        'web.assets_frontend': [
            'stockex/static/src/css/mobile.css',
            'stockex/static/src/js/barcode-scanner.js',
            'stockex/static/src/js/mobile-app.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'web_icon': 'stockex/static/description/icon.png'
}

