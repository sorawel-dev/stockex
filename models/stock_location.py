# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class StockLocation(models.Model):
    _inherit = 'stock.location'
    
    # Champ personnalisé pour l'affichage
    display_name = fields.Char(
        string='Nom Complet',
        compute='_compute_display_name',
        store=False
    )
    
    # Code-barres pour l'emplacement
    barcode = fields.Char(
        string='Code-barres',
        copy=False,
        index=True,
        help='Code-barres unique pour identifier l\'emplacement'
    )
    
    barcode_image = fields.Binary(
        string='Image Code-barres',
        compute='_compute_barcode_image',
        store=False,
        help='Image du code-barres générée automatiquement'
    )

    # Champs de géolocalisation
    latitude = fields.Float(
        string='Latitude',
        digits=(10, 7),
        help='Latitude GPS de l\'emplacement (ex: 5.3599517)'
    )
    longitude = fields.Float(
        string='Longitude',
        digits=(10, 7),
        help='Longitude GPS de l\'emplacement (ex: -4.0082563)'
    )
    address = fields.Text(
        string='Adresse',
        help='Adresse complète de l\'emplacement'
    )
    city = fields.Char(
        string='Ville',
        help='Ville de l\'emplacement'
    )
    country_id = fields.Many2one(
        comodel_name='res.country',
        string='Pays',
        help='Pays de l\'emplacement'
    )
    phone = fields.Char(
        string='Téléphone',
        help='Numéro de téléphone de l\'emplacement'
    )
    email = fields.Char(
        string='Email',
        help='Email de contact pour l\'emplacement'
    )
    
    # Champ calculé pour afficher les coordonnées
    coordinates = fields.Char(
        string='Coordonnées GPS',
        compute='_compute_coordinates',
        store=False,
        help='Coordonnées GPS au format "Latitude, Longitude"'
    )
    google_maps_url = fields.Char(
        string='Google Maps',
        compute='_compute_google_maps_url',
        store=False,
        help='Lien vers Google Maps'
    )
    
    @api.depends('barcode')
    def _compute_barcode_image(self):
        """Génère l'image du code-barres."""
        for location in self:
            if location.barcode:
                try:
                    import barcode
                    from barcode.writer import ImageWriter
                    from io import BytesIO
                    import base64
                    
                    # Générer le code-barres EAN13 ou Code128
                    code128 = barcode.get('code128', location.barcode, writer=ImageWriter())
                    buffer = BytesIO()
                    code128.write(buffer)
                    location.barcode_image = base64.b64encode(buffer.getvalue())
                except ImportError:
                    location.barcode_image = False
                    _logger.warning("Module 'python-barcode' non installé. Installez avec: pip install python-barcode")
                except Exception as e:
                    location.barcode_image = False
                    _logger.error(f"Erreur génération code-barres: {e}")
            else:
                location.barcode_image = False
    
    def action_generate_barcode(self):
        """Génère automatiquement un code-barres unique."""
        self.ensure_one()
        
        if self.barcode:
            raise UserError("Cet emplacement a déjà un code-barres. Supprimez-le d'abord pour en générer un nouveau.")
        
        # Générer un code-barres unique basé sur l'ID
        # Format: LOC + ID sur 10 chiffres
        barcode = f"LOC{str(self.id).zfill(10)}"
        
        # Vérifier l'unicité
        existing = self.search([('barcode', '=', barcode), ('id', '!=', self.id)])
        if existing:
            # Ajouter un suffixe aléatoire
            import random
            barcode = f"LOC{str(self.id).zfill(8)}{random.randint(10, 99)}"
        
        self.write({'barcode': barcode})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Code-barres généré',
                'message': f"Code-barres généré : {barcode}",
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_print_barcode_labels(self):
        """Imprime les étiquettes de codes-barres."""
        # Cette action peut être liée à un rapport QWeb
        return self.env.ref('stockex.action_report_location_barcode').report_action(self)
    
    @api.depends('name', 'location_id', 'location_id.complete_name', 'location_id.warehouse_id', 'warehouse_id')
    def _compute_complete_name(self):
        """Surcharge pour formater le nom au format {DIMINUTIF}/{CODE ENTREPOT}/{Stock}."""
        for location in self:
            # Rechercher l'entrepôt associé
            warehouse = location.warehouse_id
            if not warehouse and location.location_id:
                warehouse = location.location_id.warehouse_id
            
            if warehouse and location.usage == 'internal':
                # Format: {DIMINUTIF}/{CODE ENTREPOT}/{Nom Emplacement}
                diminutif = warehouse.code or 'WH'
                code_entrepot = warehouse.warehouse_code or ''
                
                if code_entrepot:
                    # Construire le chemin avec le format personnalisé
                    if location.location_id and location.location_id.usage == 'view':
                        # Emplacement principal sous l'entrepôt
                        location.complete_name = f"{diminutif}/{code_entrepot}/{location.name}"
                    elif location.location_id and location.location_id != warehouse.view_location_id:
                        # Sous-emplacement : ajouter au chemin parent
                        parent_path = location.location_id.complete_name or location.location_id.name
                        if parent_path.startswith(f"{diminutif}/"):
                            location.complete_name = f"{parent_path}/{location.name}"
                        else:
                            location.complete_name = f"{diminutif}/{code_entrepot}/{location.name}"
                    else:
                        location.complete_name = f"{diminutif}/{code_entrepot}/{location.name}"
                else:
                    # Pas de code entrepôt, utiliser seulement le diminutif
                    if location.location_id:
                        parent_name = location.location_id.complete_name or location.location_id.name
                        location.complete_name = f"{parent_name}/{location.name}"
                    else:
                        location.complete_name = location.name
            else:
                # Pour les autres types d'emplacements, utiliser le comportement standard
                if location.location_id:
                    parent_name = location.location_id.complete_name or location.location_id.name
                    location.complete_name = f"{parent_name}/{location.name}"
                else:
                    location.complete_name = location.name
    
    @api.depends('name', 'complete_name')
    def _compute_display_name(self):
        """Calcule le nom d'affichage avec le complete_name formaté."""
        for record in self:
            record.display_name = record.complete_name or record.name
    
    @api.depends('latitude', 'longitude')
    def _compute_coordinates(self):
        """Calcule les coordonnées au format lisible."""
        for record in self:
            if record.latitude and record.longitude:
                record.coordinates = f"{record.latitude}, {record.longitude}"
            else:
                record.coordinates = False
    
    @api.depends('latitude', 'longitude')
    def _compute_google_maps_url(self):
        """Génère l'URL Google Maps."""
        for record in self:
            if record.latitude and record.longitude:
                record.google_maps_url = f"https://www.google.com/maps?q={record.latitude},{record.longitude}"
            else:
                record.google_maps_url = False
    
    def action_open_map(self):
        """Ouvre Google Maps dans un nouvel onglet."""
        self.ensure_one()
        if not self.latitude or not self.longitude:
            from odoo.exceptions import UserError
            raise UserError("Les coordonnées GPS ne sont pas définies pour cet emplacement.")
        
        return {
            'type': 'ir.actions.act_url',
            'url': self.google_maps_url,
            'target': 'new',
        }
