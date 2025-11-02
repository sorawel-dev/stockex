# -*- coding: utf-8 -*-

import logging
from odoo import models, api

_logger = logging.getLogger(__name__)


class ProductCategoryAutoConfig(models.Model):
    """Extension du modèle product.category pour auto-configuration des comptes."""
    _inherit = 'product.category'
    
    @api.model
    def _auto_configure_stock_accounts(self):
        """
        Configure automatiquement les comptes de stock pour toutes les catégories
        qui n'ont pas de configuration explicite.
        
        Cette méthode peut être appelée manuellement ou via un cron.
        """
        _logger.info("🔍 Début de l'auto-configuration des comptes de stock...")
        
        # Récupérer les comptes par défaut
        Account = self.env['account.account']
        
        # Chercher le compte de valorisation (priorité: 31 > 311)
        default_valuation = Account.search([('code', '=', '31')], limit=1)
        if not default_valuation:
            default_valuation = Account.search([('code', '=', '311')], limit=1)
        
        # Chercher le compte de variation (priorité: 603 > 6030)
        default_variation = Account.search([('code', '=', '603')], limit=1)
        if not default_variation:
            default_variation = Account.search([('code', '=', '6030')], limit=1)
        
        if not default_valuation or not default_variation:
            _logger.warning("⚠️ Comptes par défaut non trouvés (31/311 ou 603/6030)")
            return {
                'configured': 0,
                'skipped': 0,
                'error': 'Comptes par défaut manquants'
            }
        
        _logger.info(f"✅ Comptes par défaut: {default_valuation.code}/{default_variation.code}")
        
        # Récupérer toutes les catégories
        all_categories = self.search([])
        configured_count = 0
        skipped_count = 0
        
        for category in all_categories:
            # Vérifier si la catégorie a déjà une configuration complète
            if (category.property_stock_valuation_account_id and 
                category.property_stock_account_input_categ_id and 
                category.property_stock_account_output_categ_id):
                skipped_count += 1
                continue
            
            # Déterminer les comptes à utiliser
            valuation_account = None
            variation_account = None
            source = None
            
            # Si la catégorie a un parent configuré, utiliser ses comptes
            if category.parent_id and category.parent_id.property_stock_valuation_account_id:
                valuation_account = category.parent_id.property_stock_valuation_account_id
                variation_account = category.parent_id.property_stock_account_input_categ_id
                source = f"parent ({category.parent_id.name})"
            # Sinon, utiliser les comptes par défaut
            else:
                valuation_account = default_valuation
                variation_account = default_variation
                source = "défaut"
            
            # Appliquer la configuration
            try:
                category.write({
                    'property_stock_valuation_account_id': valuation_account.id,
                    'property_stock_account_input_categ_id': variation_account.id,
                    'property_stock_account_output_categ_id': variation_account.id,
                })
                configured_count += 1
                _logger.info(f"✅ {category.name} configurée avec comptes {source}")
            except Exception as e:
                _logger.error(f"❌ Erreur pour {category.name}: {str(e)}")
        
        _logger.info(f"📊 Auto-configuration terminée: {configured_count} configurées, {skipped_count} déjà OK")
        
        return {
            'configured': configured_count,
            'skipped': skipped_count,
            'total': len(all_categories)
        }
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create pour auto-configurer les nouvelles catégories."""
        categories = super(ProductCategoryAutoConfig, self).create(vals_list)
        
        # Traiter chaque catégorie créée
        for category in categories:
            # Si la catégorie n'a pas de comptes configurés
            if category.property_stock_valuation_account_id:
                continue
            # Récupérer les comptes par défaut
            Account = self.env['account.account']
            default_valuation = Account.search([('code', '=', '31')], limit=1)
            if not default_valuation:
                default_valuation = Account.search([('code', '=', '311')], limit=1)
            
            default_variation = Account.search([('code', '=', '603')], limit=1)
            if not default_variation:
                default_variation = Account.search([('code', '=', '6030')], limit=1)
            
            # Si la catégorie a un parent, utiliser ses comptes
            if category.parent_id and category.parent_id.property_stock_valuation_account_id:
                category.write({
                    'property_stock_valuation_account_id': category.parent_id.property_stock_valuation_account_id.id,
                    'property_stock_account_input_categ_id': category.parent_id.property_stock_account_input_categ_id.id,
                    'property_stock_account_output_categ_id': category.parent_id.property_stock_account_output_categ_id.id,
                })
                _logger.info(f"✅ Nouvelle catégorie {category.name} configurée avec comptes du parent")
            # Sinon, utiliser les comptes par défaut
            elif default_valuation and default_variation:
                category.write({
                    'property_stock_valuation_account_id': default_valuation.id,
                    'property_stock_account_input_categ_id': default_variation.id,
                    'property_stock_account_output_categ_id': default_variation.id,
                })
                _logger.info(f"✅ Nouvelle catégorie {category.name} configurée avec comptes par défaut")
        
        return categories
