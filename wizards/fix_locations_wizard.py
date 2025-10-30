# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class FixLocationsWizard(models.TransientModel):
    """Assistant pour corriger les emplacements et les stocks."""
    _name = 'stockex.fix.locations.wizard'
    _description = 'Corriger les Emplacements'
    
    inventory_id = fields.Many2one(
        comodel_name='stockex.stock.inventory',
        string='Inventaire',
        required=True
    )
    
    bad_locations_count = fields.Integer(
        string='Emplacements à corriger',
        compute='_compute_bad_locations'
    )
    
    bad_locations_info = fields.Html(
        string='Détails',
        compute='_compute_bad_locations'
    )
    
    @api.depends('inventory_id')
    def _compute_bad_locations(self):
        """Compte les emplacements qui ne sont pas de type 'internal'."""
        for wizard in self:
            if not wizard.inventory_id:
                wizard.bad_locations_count = 0
                wizard.bad_locations_info = ""
                continue
            
            # Compter les emplacements non-internal
            bad_locations = {}
            for line in wizard.inventory_id.line_ids:
                if line.location_id and line.location_id.usage != 'internal':
                    loc_name = line.location_id.complete_name
                    if loc_name not in bad_locations:
                        bad_locations[loc_name] = {
                            'id': line.location_id.id,
                            'usage': line.location_id.usage,
                            'count': 0
                        }
                    bad_locations[loc_name]['count'] += 1
            
            wizard.bad_locations_count = sum(loc['count'] for loc in bad_locations.values())
            
            # Construire le HTML
            if bad_locations:
                html = "<table class='table table-sm'>"
                html += "<thead><tr><th>Emplacement</th><th>Type</th><th>Nb lignes</th></tr></thead>"
                html += "<tbody>"
                for loc_name, info in sorted(bad_locations.items(), key=lambda x: -x[1]['count'])[:20]:
                    html += f"<tr><td>{loc_name}</td><td>{info['usage']}</td><td>{info['count']}</td></tr>"
                html += "</tbody></table>"
                wizard.bad_locations_info = html
            else:
                wizard.bad_locations_info = "<p class='text-success'>✅ Tous les emplacements sont corrects !</p>"
    
    def action_fix_locations(self):
        """Corrige les emplacements en les convertissant en type 'internal'."""
        self.ensure_one()
        
        fixed_count = 0
        errors = []
        
        # Parcourir toutes les lignes
        for line in self.inventory_id.line_ids:
            try:
                if line.location_id and line.location_id.usage != 'internal':
                    # Convertir l'emplacement en 'internal'
                    _logger.info(f"Conversion emplacement {line.location_id.name}: {line.location_id.usage} → internal")
                    line.location_id.write({'usage': 'internal'})
                    fixed_count += 1
                    
            except Exception as e:
                errors.append(f"Emplacement {line.location_id.name}: {str(e)}")
                _logger.error(f"Erreur conversion emplacement {line.location_id.name}: {e}")
        
        # Message de résultat
        message = f"✅ {fixed_count} emplacements convertis en type 'internal'"
        if errors:
            message += f"\n\n❌ Erreurs ({len(errors)}):\n" + "\n".join(errors[:10])
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Correction des Emplacements',
                'message': message,
                'type': 'success' if not errors else 'warning',
                'sticky': False,
            }
        }
    
    def action_revalidate_inventory(self):
        """Corrige les emplacements puis revalide l'inventaire."""
        self.ensure_one()
        
        # Corriger les emplacements
        self.action_fix_locations()
        
        # Mettre l'inventaire en brouillon
        if self.inventory_id.state == 'done':
            self.inventory_id.write({'state': 'draft'})
        
        # Revalider
        self.inventory_id.action_validate()
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stockex.stock.inventory',
            'res_id': self.inventory_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
