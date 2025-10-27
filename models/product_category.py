# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductCategory(models.Model):
    """Extension du modèle product.category pour ajouter un champ code."""
    _inherit = 'product.category'
    
    code = fields.Char(
        string='Code',
        help='Code court pour identifier rapidement la catégorie',
        index=True,
        copy=False,
        tracking=True
    )
    
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 
         'Le code de la catégorie doit être unique !')
    ]
    
    @api.constrains('code')
    def _check_code_format(self):
        """Valide le format du code (optionnel)."""
        for record in self:
            if record.code:
                # Enlever les espaces en début et fin
                record.code = record.code.strip().upper()
                
                # Vérifier que le code ne contient que des caractères alphanumériques
                if not record.code.replace('_', '').replace('-', '').isalnum():
                    raise ValidationError(
                        _("Le code ne peut contenir que des lettres, chiffres, tirets (-) et underscores (_).")
                    )
    
    def name_get(self):
        """Affiche le code avec le nom si disponible."""
        result = []
        for record in self:
            if record.code:
                name = f"[{record.code}] {record.complete_name}"
            else:
                name = record.complete_name
            result.append((record.id, name))
        return result
    
    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        """Recherche par code ou nom."""
        domain = domain or []
        if name:
            # Rechercher par code d'abord, puis par nom
            domain = ['|', ('code', operator, name), ('name', operator, name)]
        return self._search(domain, limit=limit, order=order)
