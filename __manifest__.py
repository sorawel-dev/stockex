# -*- coding: utf-8 -*-
# pyright: reportUnusedExpression=false
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
    'depends': ['base', 'mail', 'stock', 'stock_account', 'product', 'account'],
    'external_dependencies': {
        'python': ['openpyxl'],
    },
    'category': 'Inventory/Inventory',
    'version': '19.0.10.0.0',
    'data': [
        'security/stockex_security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/remove_dashboard.xml',
        'data/stock_accounts_ohada.xml',
        # 'data/product_categories_config.xml',  # Désactivé : auto-configuration gère les catégories
        'data/auto_configure_categories.xml',
        'data/cron_jobs.xml',
        'data/kobo_config_data.xml',  # Configuration Kobo Collect par défaut
        'data/eneo_region_data.xml',
        'data/eneo_network_data.xml',
        'views/res_config_settings_views.xml',
        'views/stock_warehouse_views.xml',
        'views/stock_location_views.xml',
        'views/eneo_network_views.xml',
        'views/product_category_views.xml',
        'views/product_category_config_views.xml',
        'views/product_views.xml',  # Hérite vue liste produits pour masquer colonnes
        'views/kobo_config_views.xml',
        # Vues de base (avant les wizards)
        'views/stock_inventory_views.xml',
        'views/stock_reports_views.xml',
        'views/stock_analysis_views.xml',
        'views/stock_analysis_pivot_views.xml',  # Tableau croisé dynamique puissant
        'views/depreciation_report_views.xml',
        'views/lot_tracking_views.xml',  # Définit action_stock_lot_expiring
        'views/inventory_dashboard_views.xml',  # Dashboard moderne OWL
        'reports/inventory_report.xml',
        # Menus (AVANT les wizards pour que menu_stockex_reporting existe)
        'views/menus.xml',
        # Wizards (APRÈS menus - peuvent référencer menu_stockex_reporting)
        'wizards/import_method_wizard_views.xml',
        'wizards/import_inventory_wizard_views.xml',
        'wizards/import_excel_wizard_views.xml',
        'wizards/import_kobo_wizard_views.xml',
        'wizards/fix_locations_wizard_views.xml',
        'wizards/fix_product_types_wizard_views.xml',
        'wizards/cancel_inventory_wizard_views.xml',
        'wizards/import_flexible_inventory_wizard_views.xml',
        'wizards/stock_accounts_config_wizard_views.xml',
        'wizards/warehouse_valuation_export_wizard_views.xml',
        'wizards/stock_valuation_date_wizard_views.xml',
        'wizards/initial_stock_wizard_views.xml',
        # Vues complémentaires
        'views/mobile_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'stockex/static/src/css/cleanup_wizard.css',
            'stockex/static/src/css/inventory_dashboard.css',
            'stockex/static/src/js/inventory_dashboard.js',
            'stockex/static/src/xml/inventory_dashboard.xml',
            'stockex/static/src/js/minio_upload.js',
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
    'web_icon': 'stockex/static/description/icon.png',
}