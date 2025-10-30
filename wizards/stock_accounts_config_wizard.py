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
    account_311_id = fields.Many2one('account.account', string='311 - Marchandises A')
    account_603_id = fields.Many2one('account.account', string='603 - Variation stocks marchandises')
    account_321_id = fields.Many2one('account.account', string='321 - Matières A')
    account_6031_id = fields.Many2one('account.account', string='6031 - Variation stocks matières')
    account_33_id = fields.Many2one('account.account', string='33 - Autres approvisionnements')
    account_6032_id = fields.Many2one('account.account', string='6032 - Variation autres approv.')
    account_351_id = fields.Many2one('account.account', string='351 - Produits finis')
    account_7131_id = fields.Many2one('account.account', string='7131 - Variation stocks produits')
    
    # Messages
    message = fields.Html(string='Résultat', readonly=True)
    
    def action_search_accounts(self):
        """Recherche automatique des comptes dans le plan comptable."""
        self.ensure_one()
        
        Account = self.env['account.account']
        found_accounts = {}
        missing_accounts = []
        
        # Liste des comptes à rechercher
        accounts_to_find = {
            'account_311_id': ['311', '3110', '31100'],
            'account_603_id': ['603', '6030', '60300'],
            'account_321_id': ['321', '3210', '32100'],
            'account_6031_id': ['6031', '60310'],
            'account_33_id': ['33', '330', '3300'],
            'account_6032_id': ['6032', '60320'],
            'account_351_id': ['351', '3510', '35100'],
            'account_7131_id': ['7131', '71310'],
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
        
        return self.write({
            'state': 'config',
            'message': message,
        })
    
    def action_configure_categories(self):
        """Configure les catégories avec les comptes sélectionnés."""
        self.ensure_one()
        
        Category = self.env['product.category']
        configured_count = 0
        errors = []
        
        # Configuration Marchandises
        if self.account_311_id and self.account_603_id:
            category = Category.search([('name', '=', 'Marchandises')], limit=1)
            if category:
                category.write({
                    'property_stock_valuation_account_id': self.account_311_id.id,
                    'property_stock_account_input_categ_id': self.account_603_id.id,
                    'property_stock_account_output_categ_id': self.account_603_id.id,
                })
                configured_count += 1
                _logger.info(f"✅ Marchandises configurée avec 311 et 603")
        else:
            errors.append("Marchandises : Comptes 311 ou 603 manquants")
        
        # Configuration Matières Premières
        if self.account_321_id and self.account_6031_id:
            category = Category.search([('name', '=', 'Matières Premières')], limit=1)
            if category:
                category.write({
                    'property_stock_valuation_account_id': self.account_321_id.id,
                    'property_stock_account_input_categ_id': self.account_6031_id.id,
                    'property_stock_account_output_categ_id': self.account_6031_id.id,
                })
                configured_count += 1
                _logger.info(f"✅ Matières Premières configurée avec 321 et 6031")
        else:
            errors.append("Matières Premières : Comptes 321 ou 6031 manquants")
        
        # Configuration Fournitures
        if self.account_33_id and self.account_6032_id:
            category = Category.search([('name', '=', 'Fournitures')], limit=1)
            if category:
                category.write({
                    'property_stock_valuation_account_id': self.account_33_id.id,
                    'property_stock_account_input_categ_id': self.account_6032_id.id,
                    'property_stock_account_output_categ_id': self.account_6032_id.id,
                })
                configured_count += 1
                _logger.info(f"✅ Fournitures configurée avec 33 et 6032")
        else:
            errors.append("Fournitures : Comptes 33 ou 6032 manquants")
        
        # Configuration Produits Finis
        if self.account_351_id and self.account_7131_id:
            category = Category.search([('name', '=', 'Produits Finis')], limit=1)
            if category:
                category.write({
                    'property_stock_valuation_account_id': self.account_351_id.id,
                    'property_stock_account_input_categ_id': self.account_7131_id.id,
                    'property_stock_account_output_categ_id': self.account_7131_id.id,
                })
                configured_count += 1
                _logger.info(f"✅ Produits Finis configurée avec 351 et 7131")
        else:
            errors.append("Produits Finis : Comptes 351 ou 7131 manquants")
        
        # Message de résultat
        if configured_count > 0:
            message = f"""
            <div style="padding: 15px; background: #d4edda; border-left: 4px solid #28a745;">
                <h4 style="color: #155724;">✅ Configuration Réussie</h4>
                <p><strong>{configured_count}</strong> catégorie(s) configurée(s) avec les comptes OHADA.</p>
                <p>Les catégories suivantes ont été mises à jour :</p>
                <ul>
                    {('<li>Marchandises (311/603)</li>' if self.account_311_id and self.account_603_id else '')}
                    {('<li>Matières Premières (321/6031)</li>' if self.account_321_id and self.account_6031_id else '')}
                    {('<li>Fournitures (33/6032)</li>' if self.account_33_id and self.account_6032_id else '')}
                    {('<li>Produits Finis (351/7131)</li>' if self.account_351_id and self.account_7131_id else '')}
                </ul>
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
        
        return self.write({
            'state': 'done',
            'message': message,
        })
    
    def action_close(self):
        """Ferme le wizard."""
        return {'type': 'ir.actions.act_window_close'}
