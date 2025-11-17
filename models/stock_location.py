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
    
    # Entrepôt associé (calculé)
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Entrepôt',
        compute='_compute_warehouse_id',
        store=True
    )

    eneo_region_id = fields.Many2one(
        'stockex.eneo.region',
        string='Région Électrique ENEO',
        compute='_compute_eneo_region_id',
        store=True
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
    
    # Champs pour Smart Buttons
    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        related='company_id.currency_id',
        store=True,
        readonly=True
    )
    stock_value = fields.Monetary(
        string='Valeur du stock',
        currency_field='currency_id',
        compute='_compute_stock_value',
        store=False
    )
    move_count = fields.Integer(
        string='Mouvements',
        compute='_compute_move_count',
        store=False
    )
    quant_count = fields.Integer(
        string='Articles en stock',
        compute='_compute_quant_count',
        store=False
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
    
    @api.depends('name', 'complete_name', 'location_id', 'location_id.name')
    def _compute_display_name(self):
        """Calcule un libellé explicite: CODE_ENTREPÔT | Nom complet."""
        for record in self:
            # Trouver l'entrepôt via la racine view_location_id
            warehouse = False
            loc = record
            try:
                while loc:
                    warehouse = self.env['stock.warehouse'].search([('view_location_id', '=', loc.id)], limit=1)
                    if warehouse:
                        break
                    loc = loc.location_id
            except Exception:
                warehouse = False
            base = record.complete_name or record.name
            if warehouse and warehouse.code and base:
                record.display_name = f"{warehouse.code} | {base}"
            else:
                record.display_name = base
    
    @api.depends('location_id', 'location_id.name')
    def _compute_warehouse_id(self):
        """Détermine l'entrepôt auquel appartient l'emplacement (via view_location_id)."""
        for rec in self:
            rec.warehouse_id = False
            loc = rec
            try:
                while loc:
                    wh = self.env['stock.warehouse'].search([('view_location_id', '=', loc.id)], limit=1)
                    if wh:
                        rec.warehouse_id = wh
                        break
                    loc = loc.location_id
            except Exception:
                rec.warehouse_id = False
    
    @api.depends('warehouse_id', 'warehouse_id.eneo_region_id')
    def _compute_eneo_region_id(self):
        for rec in self:
            rec.eneo_region_id = rec.warehouse_id.eneo_region_id if rec.warehouse_id else False

    @api.onchange('warehouse_id')
    def _onchange_warehouse_city(self):
        """Met à jour automatiquement la ville de l'emplacement avec celle de l'entrepôt."""
        if self.warehouse_id and self.warehouse_id.city and not self.city:
            self.city = self.warehouse_id.city
    
    @api.model_create_multi
    def create(self, vals_list):
        """Hérite la ville de l'entrepôt à la création si non spécifiée."""
        for vals in vals_list:
            # Si la ville n'est pas spécifiée, essayer de la récupérer de l'entrepôt
            if not vals.get('city'):
                # Chercher l'entrepôt via location_id
                if vals.get('location_id'):
                    location = self.browse(vals['location_id'])
                    warehouse = False
                    loc = location
                    try:
                        while loc:
                            wh = self.env['stock.warehouse'].search([('view_location_id', '=', loc.id)], limit=1)
                            if wh:
                                warehouse = wh
                                break
                            loc = loc.location_id
                    except Exception:
                        warehouse = False
                    
                    if warehouse and warehouse.city:
                        vals['city'] = warehouse.city
        
        return super(StockLocation, self).create(vals_list)
    
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
    
    def _compute_quant_count(self):
        for rec in self:
            domain = [('location_id', 'child_of', rec.id), ('quantity', '>', 0)]
            rec.quant_count = self.env['stock.quant'].search_count(domain)
    
    def _compute_move_count(self):
        for rec in self:
            domain = ['|', ('location_id', 'child_of', rec.id), ('location_dest_id', 'child_of', rec.id), ('state', '=', 'done')]
            # Note: 'state' filter applies to moves; handled by concatenating domain properly
            domain = ['|', ('location_id', 'child_of', rec.id), ('location_dest_id', 'child_of', rec.id)] + [('state', '=', 'done')]
            rec.move_count = self.env['stock.move'].search_count(domain)
    
    def _compute_stock_value(self):
        for rec in self:
            total = 0.0
            quants = self.env['stock.quant'].search([('location_id', 'child_of', rec.id), ('quantity', '>', 0)])
            for q in quants:
                total += (q.quantity or 0.0) * (q.product_id.standard_price or 0.0)
            rec.stock_value = total
    
    def action_open_stock_value(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Valorisation du stock',
            'res_model': 'product.product',
            'view_mode': 'list,form',
            'domain': [('qty_available', '!=', 0)],
            'context': {
                'search_default_real_stock_available': 1,
                'location': self.id,
            },
        }
    
    def action_open_moves(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Mouvements de stock',
            'res_model': 'stock.move',
            'view_mode': 'list,form,pivot,graph',
            'domain': ['|', ('location_id', 'child_of', self.id), ('location_dest_id', 'child_of', self.id)],
            'context': {
                'search_default_done': 1,
            },
        }
    
    def action_open_quants(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Articles en stock',
            'res_model': 'stock.quant',
            'view_mode': 'list,form',
            'domain': [('location_id', 'child_of', self.id), ('quantity', '>', 0)],
            'context': {
                'search_default_productgroup': 1,
                'search_default_locationgroup': 1,
            },
        }
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
