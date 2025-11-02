# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class StockAccountsConfigWizard(models.TransientModel):
    """Assistant de configuration des comptes de stock pour les catégories."""
    _name = 'stockex.stock.accounts.config.wizard'
    _description = 'Configuration des Comptes de Stock OHADA'
    
    state = fields.Selection([
        ('search', 'Recherche des Comptes'),
        ('config', 'Configuration'),
        ('done', 'Terminé'),
    ], default='search', string='État')
    
    # Comptes trouvés automatiquement
    account_31_id = fields.Many2one('account.account', string='31 - Marchandises')
    account_311_id = fields.Many2one('account.account', string='311 - Marchandises A')
    account_603_id = fields.Many2one('account.account', string='603 - Variation stocks marchandises')
    account_32_id = fields.Many2one('account.account', string='32 - Matières premières')
    account_321_id = fields.Many2one('account.account', string='321 - Matières A')
    account_6031_id = fields.Many2one('account.account', string='6031 - Variation stocks matières')
    account_33_id = fields.Many2one('account.account', string='33 - Autres approvisionnements')
    account_6032_id = fields.Many2one('account.account', string='6032 - Variation autres approv.')
    account_35_id = fields.Many2one('account.account', string='35 - Produits')
    account_351_id = fields.Many2one('account.account', string='351 - Produits finis')
    account_713_id = fields.Many2one('account.account', string='713 - Variation stocks produits')
    account_7131_id = fields.Many2one('account.account', string='7131 - Variation stocks produits finis')
    account_381_id = fields.Many2one('account.account', string='381 - Écarts prix (Mali)')
    account_658_id = fields.Many2one('account.account', string='658 - Charges diverses')
    
    # Messages
    message = fields.Html(string='Résultat', readonly=True)
    
    def action_search_accounts(self):
        """Recherche automatique des comptes dans le plan comptable."""
        self.ensure_one()
        
        Account = self.env['account.account']
        found_accounts = {}
        missing_accounts = []
        
        # Liste des comptes à rechercher (ordre: comptes principaux d'abord)
        accounts_to_find = {
            # Comptes de valorisation (Classe 3)
            'account_31_id': ['31', '310', '3100'],
            'account_311_id': ['311', '3110', '31100'],
            'account_32_id': ['32', '320', '3200'],
            'account_321_id': ['321', '3210', '32100'],
            'account_33_id': ['33', '330', '3300'],
            'account_35_id': ['35', '350', '3500'],
            'account_351_id': ['351', '3510', '35100'],
            # Comptes de variation (Classe 6 et 7)
            'account_603_id': ['603', '6030', '60300'],
            'account_6031_id': ['6031', '60310'],
            'account_6032_id': ['6032', '60320'],
            'account_713_id': ['713', '7130', '71300'],
            'account_7131_id': ['7131', '71310'],
            # Comptes d'écart de prix
            'account_381_id': ['381', '3810', '38100'],
            'account_658_id': ['658', '6580', '65800'],
        }
        
        # Rechercher chaque compte par code
        for field_name, codes in accounts_to_find.items():
            account = None
            for code in codes:
                account = Account.search([('code', '=', code)], limit=1)
                if account:
                    break
            
            if account:
                found_accounts[field_name] = account.id
                _logger.info(f"✅ Compte trouvé: {code} - {account.name}")
            else:
                missing_accounts.append(codes[0])
                _logger.warning(f"⚠️ Compte non trouvé: {', '.join(codes)}")
        
        # Mettre à jour le wizard
        self.write(found_accounts)
        
        # Générer le message
        if missing_accounts:
            message = f"""
            <div style="padding: 15px; background: #fff3cd; border-left: 4px solid #ffc107;">
                <h4 style="color: #856404;">⚠️ Comptes Manquants</h4>
                <p>Les comptes suivants n'ont pas été trouvés dans votre plan comptable :</p>
                <ul>
                    {''.join([f'<li><strong>{code}</strong></li>' for code in missing_accounts])}
                </ul>
                <p><strong>Actions recommandées :</strong></p>
                <ol>
                    <li>Créez ces comptes dans votre plan comptable</li>
                    <li>Ou sélectionnez manuellement des comptes équivalents ci-dessous</li>
                </ol>
            </div>
            <div style="padding: 15px; background: #d4edda; border-left: 4px solid #28a745; margin-top: 15px;">
                <h4 style="color: #155724;">✅ Comptes Trouvés</h4>
                <p>{len(found_accounts)} compte(s) trouvé(s) automatiquement.</p>
            </div>
            """
        else:
            message = """
            <div style="padding: 15px; background: #d4edda; border-left: 4px solid #28a745;">
                <h4 style="color: #155724;">✅ Tous les Comptes Trouvés</h4>
                <p>Tous les comptes OHADA ont été trouvés dans votre plan comptable.</p>
                <p>Cliquez sur <strong>"Configurer les Catégories"</strong> pour appliquer la configuration.</p>
            </div>
            """
        
        self.write({
            'state': 'config',
            'message': message,
        })
        
        # Retourner l'action pour garder le wizard ouvert
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stockex.stock.accounts.config.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }
    
    def action_configure_categories(self):
        """Configure les catégories avec les comptes sélectionnés selon recommandations OHADA."""
        self.ensure_one()
        
        Category = self.env['product.category']
        configured_categories = []  # Liste des catégories configurées
        inherited_count = 0
        skipped_count = 0
        errors = []
        
        # Compte d'écart de prix par défaut (priorité: 381 > 658)
        price_diff_account = self.account_381_id or self.account_658_id
        
        # Configuration Marchandises (Priorité: 31 > 311)
        valuation_account = self.account_31_id or self.account_311_id
        if valuation_account and self.account_603_id:
            category = Category.search([('name', '=', 'Marchandises')], limit=1)
            if category:
                vals = {
                    'property_stock_valuation_account_id': valuation_account.id,
                    'property_stock_account_input_categ_id': self.account_603_id.id,
                    'property_stock_account_output_categ_id': self.account_603_id.id,
                }
                if price_diff_account:
                    vals['property_account_creditor_price_difference_categ'] = price_diff_account.id
                category.write(vals)
                configured_categories.append(category.id)
                _logger.info(f"✅ Marchandises configurée avec {valuation_account.code}/603")
        else:
            errors.append("Marchandises : Comptes 31 (ou 311) ou 603 manquants")
        
        # Configuration Matières Premières (Priorité: 32 > 321)
        valuation_account = self.account_32_id or self.account_321_id
        if valuation_account and self.account_6031_id:
            category = Category.search([('name', '=', 'Matières Premières')], limit=1)
            if category:
                vals = {
                    'property_stock_valuation_account_id': valuation_account.id,
                    'property_stock_account_input_categ_id': self.account_6031_id.id,
                    'property_stock_account_output_categ_id': self.account_6031_id.id,
                }
                if price_diff_account:
                    vals['property_account_creditor_price_difference_categ'] = price_diff_account.id
                category.write(vals)
                configured_categories.append(category.id)
                _logger.info(f"✅ Matières Premières configurée avec {valuation_account.code}/6031")
        else:
            errors.append("Matières Premières : Comptes 32 (ou 321) ou 6031 manquants")
        
        # Configuration Fournitures
        if self.account_33_id and self.account_6032_id:
            category = Category.search([('name', '=', 'Fournitures')], limit=1)
            if category:
                vals = {
                    'property_stock_valuation_account_id': self.account_33_id.id,
                    'property_stock_account_input_categ_id': self.account_6032_id.id,
                    'property_stock_account_output_categ_id': self.account_6032_id.id,
                }
                if price_diff_account:
                    vals['property_account_creditor_price_difference_categ'] = price_diff_account.id
                category.write(vals)
                configured_categories.append(category.id)
                _logger.info(f"✅ Fournitures configurée avec 33/6032")
        else:
            errors.append("Fournitures : Comptes 33 ou 6032 manquants")
        
        # Configuration Produits Finis (Priorité: 35 > 351 et 713 > 7131)
        valuation_account = self.account_35_id or self.account_351_id
        variation_account = self.account_713_id or self.account_7131_id
        if valuation_account and variation_account:
            category = Category.search([('name', '=', 'Produits Finis')], limit=1)
            if category:
                vals = {
                    'property_stock_valuation_account_id': valuation_account.id,
                    'property_stock_account_input_categ_id': variation_account.id,
                    'property_stock_account_output_categ_id': variation_account.id,
                }
                if price_diff_account:
                    vals['property_account_creditor_price_difference_categ'] = price_diff_account.id
                category.write(vals)
                configured_categories.append(category.id)
                _logger.info(f"✅ Produits Finis configurée avec {valuation_account.code}/{variation_account.code}")
        else:
            errors.append("Produits Finis : Comptes 35 (ou 351) ou 713 (ou 7131) manquants")
        
        # Configurer toutes les autres catégories avec les comptes par défaut
        # Les catégories sans configuration héritent de leur parent
        all_categories = Category.search([])
        default_valuation = self.account_31_id or self.account_311_id  # Compte par défaut
        default_variation = self.account_603_id  # Compte par défaut
        
        for category in all_categories:
            # Skip les catégories déjà configurées dans les étapes précédentes
            if category.id in configured_categories:
                continue
            
            # Vérifier si la catégorie a déjà une configuration explicite
            if category.property_stock_valuation_account_id:
                continue  # Déjà configurée
            
            # Déterminer les comptes à utiliser (parent ou défaut)
            valuation_to_use = None
            variation_to_use = None
            source = None
            
            # Si la catégorie a un parent configuré, utiliser ses comptes
            if category.parent_id and category.parent_id.property_stock_valuation_account_id:
                valuation_to_use = category.parent_id.property_stock_valuation_account_id
                variation_to_use = category.parent_id.property_stock_account_input_categ_id
                source = f"parent ({category.parent_id.name})"
                inherited_count += 1
            # Sinon, utiliser les comptes par défaut
            elif default_valuation and default_variation:
                valuation_to_use = default_valuation
                variation_to_use = default_variation
                source = "défaut"
            
            # Appliquer la configuration
            if valuation_to_use and variation_to_use:
                vals = {
                    'property_stock_valuation_account_id': valuation_to_use.id,
                    'property_stock_account_input_categ_id': variation_to_use.id,
                    'property_stock_account_output_categ_id': variation_to_use.id,
                }
                if price_diff_account:
                    vals['property_account_creditor_price_difference_categ'] = price_diff_account.id
                category.write(vals)
                configured_categories.append(category.id)
                _logger.info(f"✅ {category.name} configurée avec comptes {source}")
            else:
                skipped_count += 1
                _logger.warning(f"⚠️ {category.name} non configurée (comptes manquants)")
        
        # Message de résultat
        configured_count = len(configured_categories)
        if configured_count > 0 or inherited_count > 0:
            message = f"""
            <div style="padding: 15px; background: #d4edda; border-left: 4px solid #28a745;">
                <h4 style="color: #155724;">✅ Configuration Réussie</h4>
                <p><strong>{configured_count}</strong> catégorie(s) configurée(s) explicitement avec les comptes OHADA.</p>
                {(f'<p><strong>{inherited_count}</strong> catégorie(s) ont hérité des comptes de leur parent.</p>' if inherited_count > 0 else '')}
                <p>Les catégories principales ont été mises à jour :</p>
                <ul>
                    {('<li>Marchandises (31/603)</li>' if self.account_31_id and self.account_603_id else '')}
                    {('<li>Matières Premières (32/6031)</li>' if self.account_32_id and self.account_6031_id else '')}
                    {('<li>Fournitures (33/6032)</li>' if self.account_33_id and self.account_6032_id else '')}
                    {('<li>Produits Finis (35/713)</li>' if self.account_35_id and self.account_713_id else '')}
                </ul>
                <p style="margin-top: 10px;"><em>Note: Toutes les catégories ont été configurées explicitement pour éviter les erreurs de validation.</em></p>
            </div>
            """
            
            if skipped_count > 0:
                message += f"""
                <div style="padding: 15px; background: #e7f3ff; border-left: 4px solid #2196F3; margin-top: 15px;">
                    <h4 style="color: #0d47a1;">ℹ️ Héritage Automatique</h4>
                    <p><strong>{skipped_count}</strong> catégorie(s) sans configuration explicite.</p>
                    <p>Ces catégories hériteront automatiquement des comptes de leur parent si elles en ont un.</p>
                </div>
                """
            
            if errors:
                message += f"""
                <div style="padding: 15px; background: #fff3cd; border-left: 4px solid #ffc107; margin-top: 15px;">
                    <h4 style="color: #856404;">⚠️ Catégories Non Configurées</h4>
                    <ul>
                        {''.join([f'<li>{error}</li>' for error in errors])}
                    </ul>
                </div>
                """
        else:
            message = """
            <div style="padding: 15px; background: #f8d7da; border-left: 4px solid #dc3545;">
                <h4 style="color: #721c24;">❌ Échec de la Configuration</h4>
                <p>Aucune catégorie n'a pu être configurée. Vérifiez que les comptes existent.</p>
            </div>
            """
        
        self.write({
            'state': 'done',
            'message': message,
        })
        
        # Retourner l'action pour garder le wizard ouvert et afficher le résultat
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stockex.stock.accounts.config.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }
    
    def action_close(self):
        """Ferme le wizard."""
        return {'type': 'ir.actions.act_window_close'}
