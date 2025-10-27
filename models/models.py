# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class StockWarehouse(models.Model):
    """Héritage de stock.warehouse pour ajouter une hiérarchie d'entrepôts"""
    _inherit = 'stock.warehouse'
    
    # Code entrepôt (ancien "nom court")
    warehouse_code = fields.Char(
        string='Code Entrepôt',
        size=10,
        index=True,
        help='Code unique de l\'entrepôt (ex: WH-ABJ-001, WH-YOP-002)'
    )
    
    parent_id = fields.Many2one(
        comodel_name='stock.warehouse',
        string='Entrepôt Parent',
        ondelete='restrict',
        index=True,
        help='Entrepôt parent pour créer une hiérarchie d\'entrepôts'
    )
    child_ids = fields.One2many(
        comodel_name='stock.warehouse',
        inverse_name='parent_id',
        string='Entrepôts Enfants',
        help='Entrepôts dépendant de cet entrepôt'
    )
    child_count = fields.Integer(
        string='Nombre d\'enfants',
        compute='_compute_child_count',
        store=True
    )
    
    # Champs de géolocalisation
    latitude = fields.Float(
        string='Latitude',
        digits=(10, 7),
        help='Latitude GPS de l\'entrepôt (ex: 5.3599517)'
    )
    longitude = fields.Float(
        string='Longitude',
        digits=(10, 7),
        help='Longitude GPS de l\'entrepôt (ex: -4.0082563)'
    )
    coordinates = fields.Char(
        string='Coordonnées GPS',
        compute='_compute_coordinates',
        store=False,
        help='Coordonnées au format "Latitude, Longitude"'
    )
    google_maps_url = fields.Char(
        string='Lien Google Maps',
        compute='_compute_google_maps_url',
        store=False
    )
    
    # Informations de contact
    address = fields.Text(string='Adresse complète')
    city = fields.Char(string='Ville')
    phone = fields.Char(string='Téléphone')
    email = fields.Char(string='Email')
    
    def _generate_warehouse_code(self, name):
        """
        Génère un diminutif intelligent du nom de l'entrepôt.
        
        Args:
            name (str): Nom de l'entrepôt
            
        Returns:
            str: Code diminutif (max 5 caractères)
        
        Exemples:
            - "Abidjan" → "ABIDJ"
            - "Entrepôt Central" → "EC"
            - "Grand Bassam Site Nord" → "GBSN"
        """
        if not name:
            return 'WH'
        
        name = name.strip()
        words = name.split()
        
        if len(words) == 1:
            # Un seul mot : prendre les 5 premiers caractères
            code = name[:5].upper()
        else:
            # Plusieurs mots : prendre la première lettre de chaque mot (max 5)
            code = ''.join([word[0].upper() for word in words[:5] if word])
            # Si le code est trop court, compléter avec les premières lettres du premier mot
            if len(code) < 3 and words:
                code = (words[0][:3] + code).upper()[:5]
        
        return code
    
    @api.onchange('name')
    def _onchange_name_generate_code(self):
        """Génère automatiquement le code (diminutif) lors de la saisie du nom."""
        if self.name and not self.code:
            self.code = self._generate_warehouse_code(self.name)
    
    @api.model_create_multi
    def create(self, vals_list):
        """Génère automatiquement le code si non fourni lors de la création."""
        for vals in vals_list:
            if vals.get('name') and not vals.get('code'):
                vals['code'] = self._generate_warehouse_code(vals['name'])
        return super().create(vals_list)
    
    def write(self, vals):
        """Met à jour le code si le nom change et que le code n'est pas explicitement fourni."""
        if 'name' in vals and 'code' not in vals:
            for warehouse in self:
                # Regénérer le code si le nom change
                new_code = self._generate_warehouse_code(vals['name'])
                vals['code'] = new_code
        return super().write(vals)
    
    @api.depends('child_ids')
    def _compute_child_count(self):
        """Calcule le nombre d'entrepôts enfants."""
        for warehouse in self:
            warehouse.child_count = len(warehouse.child_ids)
    
    @api.depends('latitude', 'longitude')
    def _compute_coordinates(self):
        """Calcule les coordonnées GPS au format texte."""
        for warehouse in self:
            if warehouse.latitude and warehouse.longitude:
                warehouse.coordinates = f"{warehouse.latitude}, {warehouse.longitude}"
            else:
                warehouse.coordinates = False
    
    @api.depends('latitude', 'longitude')
    def _compute_google_maps_url(self):
        """Génère l'URL Google Maps."""
        for warehouse in self:
            if warehouse.latitude and warehouse.longitude:
                warehouse.google_maps_url = f"https://www.google.com/maps?q={warehouse.latitude},{warehouse.longitude}"
            else:
                warehouse.google_maps_url = False
    
    def action_open_map(self):
        """Ouvre Google Maps dans un nouvel onglet."""
        self.ensure_one()
        if not self.google_maps_url:
            raise UserError("Veuillez renseigner les coordonnées GPS de cet entrepôt.")
        return {
            'type': 'ir.actions.act_url',
            'url': self.google_maps_url,
            'target': 'new',
        }


class StockInventory(models.Model):
    _name = 'stockex.stock.inventory'
    _description = 'Inventaire de Stock'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'
    _rec_name = 'name'
    _rec_names_search = ['name']

    name = fields.Char(
        string='Référence',
        required=True,
        default='Nouveau',
        index=True,
        copy=False,
        tracking=True
    )
    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.today,
        index=True,
        tracking=True
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Brouillon'),
            ('in_progress', 'En cours'),
            ('pending_approval', 'En attente d\'approbation'),
            ('approved', 'Approuvé'),
            ('done', 'Validé'),
            ('cancel', 'Annulé')
        ],
        string='État',
        default='draft',
        required=True,
        copy=False,
        tracking=True,
        index=True
    )
    description = fields.Text(string='Notes')
    location_id = fields.Many2one(
        comodel_name='stock.location',
        string='Emplacement',
        index=True,
        tracking=True
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Société',
        required=True,
        default=lambda self: self.env.company,
        index=True
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsable',
        required=True,
        default=lambda self: self.env.user,
        index=True,
        tracking=True
    )
    approver_id = fields.Many2one(
        comodel_name='res.users',
        string='Approbateur',
        tracking=True,
        help='Utilisateur qui a approuvé l\'inventaire'
    )
    approval_date = fields.Datetime(
        string='Date d\'approbation',
        readonly=True,
        tracking=True
    )
    validator_id = fields.Many2one(
        comodel_name='res.users',
        string='Validateur',
        tracking=True,
        help='Utilisateur qui a validé l\'inventaire'
    )
    validation_date = fields.Datetime(
        string='Date de validation',
        readonly=True,
        tracking=True
    )
    line_ids = fields.One2many(
        comodel_name='stockex.stock.inventory.line',
        inverse_name='inventory_id',
        string='Lignes'
    )
    
    _sql_constraints = [
        ('name_company_uniq', 'unique(name, company_id)', 
         'La référence doit être unique par société !'),
    ]
    
    def unlink(self):
        """Empêcher la suppression des inventaires validés."""
        for inventory in self:
            if inventory.state == 'done':
                raise UserError(
                    f"🚫 Impossible de supprimer l'inventaire '{inventory.name}'.\n\n"
                    f"L'inventaire a été validé le {inventory.validation_date.strftime('%d/%m/%Y à %H:%M') if inventory.validation_date else 'N/A'}.\n"
                    f"Les stocks Odoo ont déjà été mis à jour.\n\n"
                    f"❌ Un inventaire validé ne peut jamais être supprimé pour des raisons de traçabilité et d'audit.\n\n"
                    f"💡 Si vous devez corriger des erreurs :\n"
                    f"   - Créez un nouvel inventaire correctif\n"
                    f"   - Documentez les changements dans les notes"
                )
            elif inventory.state == 'approved':
                raise UserError(
                    f"🚫 Impossible de supprimer l'inventaire '{inventory.name}'.\n\n"
                    f"L'inventaire a été approuvé le {inventory.approval_date.strftime('%d/%m/%Y à %H:%M') if inventory.approval_date else 'N/A'}.\n"
                    f"Vous devez d'abord le rejeter avant de pouvoir le supprimer."
                )
        return super(StockInventory, self).unlink()
    
    def action_start(self):
        """Démarre l'inventaire."""
        if not self.line_ids:
            raise UserError("Vous devez ajouter au moins une ligne avant de démarrer l'inventaire.")
        return self.write({'state': 'in_progress'})
    
    def action_request_approval(self):
        """Demande l'approbation de l'inventaire."""
        if not self.line_ids:
            raise UserError("Impossible de demander l'approbation d'un inventaire sans lignes.")
        
        # Créer une activité pour le manager
        manager = self.user_id.parent_id or self.env.ref('base.user_admin')
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            user_id=manager.id,
            summary=f"Approbation d'inventaire : {self.name}",
            note=f"Merci d'approuver l'inventaire {self.name} du {self.date}"
        )
        
        return self.write({'state': 'pending_approval'})
    
    def action_approve(self):
        """Approuve l'inventaire."""
        self.write({
            'state': 'approved',
            'approver_id': self.env.user.id,
            'approval_date': fields.Datetime.now()
        })
        
        # Marquer l'activité comme terminée
        activity = self.activity_ids.filtered(lambda a: a.user_id == self.env.user)
        if activity:
            activity.action_done()
        
        return True
    
    def action_reject(self):
        """Rejette l'inventaire et le remet en brouillon."""
        # Marquer l'activité comme annulée
        activity = self.activity_ids.filtered(lambda a: a.user_id == self.env.user)
        if activity:
            activity.unlink()
        
        return self.write({'state': 'draft'})
    
    def action_validate(self):
        """Valide l'inventaire et met à jour les stocks Odoo."""
        for inventory in self:
            if not inventory.line_ids:
                raise UserError("Impossible de valider un inventaire sans lignes.")
            
            # Mettre à jour les stocks Odoo
            inventory._update_odoo_stock()
        
        return self.write({
            'state': 'done',
            'validator_id': self.env.user.id,
            'validation_date': fields.Datetime.now()
        })
    
    def _update_odoo_stock(self):
        """Met à jour les stocks Odoo avec les quantités de l'inventaire."""
        self.ensure_one()
        
        StockQuant = self.env['stock.quant']
        adjusted_count = 0
        errors = []
        skipped_no_data = 0
        skipped_bad_location = 0
        skipped_qty_zero = 0
        
        _logger.info(f"Début mise à jour stocks pour inventaire {self.name} - {len(self.line_ids)} lignes")
        
        for line in self.line_ids:
            try:
                if not line.product_id or not line.location_id:
                    skipped_no_data += 1
                    _logger.warning(f"Ligne sans produit ou emplacement ignorée")
                    continue
                
                # Vérifier que l'emplacement est de type interne
                if line.location_id.usage != 'internal':
                    skipped_bad_location += 1
                    _logger.warning(f"Ligne {line.id}: Emplacement '{line.location_id.complete_name}' (usage={line.location_id.usage}) ignoré - pas de type 'internal'")
                    errors.append(f"Emplacement '{line.location_id.name}' n'est pas de type 'internal' (type: {line.location_id.usage})")
                    continue
                
                # Trouver ou créer le quant avec company_id
                quant = StockQuant.search([
                    ('product_id', '=', line.product_id.id),
                    ('location_id', '=', line.location_id.id),
                    ('company_id', '=', self.company_id.id),
                ], limit=1)
                
                if quant:
                    # Mettre à jour la quantité existante
                    _logger.info(f"MAJ quant {line.product_id.default_code} @ {line.location_id.name}: {quant.quantity} → {line.product_qty}")
                    quant.inventory_quantity = line.product_qty
                    quant.inventory_quantity_set = True
                    quant.action_apply_inventory()
                    adjusted_count += 1
                else:
                    # Créer un nouveau quant si nécessaire
                    if line.product_qty != 0:  # Créer même pour quantités négatives
                        _logger.info(f"Création quant {line.product_id.default_code} @ {line.location_id.name}: 0 → {line.product_qty}")
                        new_quant = StockQuant.create({
                            'product_id': line.product_id.id,
                            'location_id': line.location_id.id,
                            'company_id': self.company_id.id,
                            'inventory_quantity': line.product_qty,
                            'inventory_quantity_set': True,
                        })
                        new_quant.action_apply_inventory()
                        adjusted_count += 1
                    else:
                        skipped_qty_zero += 1
                        
            except Exception as e:
                error_msg = f"Produit {line.product_id.default_code} @ {line.location_id.name}: {str(e)}"
                errors.append(error_msg)
                _logger.error(f"Erreur mise à jour stock {line.product_id.display_name} @ {line.location_id.name}: {e}", exc_info=True)
        
        # Statistiques détaillées
        stats = f"""
📊 Statistiques de mise à jour:
- Total lignes: {len(self.line_ids)}
- ✅ Ajustements réussis: {adjusted_count}
- ⚠️ Ignorées (emplacement non 'internal'): {skipped_bad_location}
- ⚠️ Ignorées (sans données): {skipped_no_data}
- ⚠️ Ignorées (quantité = 0): {skipped_qty_zero}
- ❌ Erreurs: {len(errors)}
"""
        
        # Message de confirmation
        message = f"✅ Stocks mis à jour : {adjusted_count} ajustements effectués sur {len(self.line_ids)} lignes"
        message += stats
        
        if errors:
            message += f"\n\n⚠️ Détails des erreurs ({len(errors)}):\n" + "\n".join(errors[:20])
        
        self.message_post(body=message)
        _logger.info(f"Fin mise à jour stocks: {adjusted_count} ajustements, {skipped_bad_location} emplacements non-internal, {len(errors)} erreurs")
        
        return adjusted_count
    
    def action_cancel(self):
        """Annule l'inventaire."""
        return self.write({'state': 'cancel'})
    
    def action_draft(self):
        """Remet l'inventaire en brouillon."""
        return self.write({'state': 'draft'})
    
    def name_get(self):
        """Affichage personnalisé du nom."""
        result = []
        for record in self:
            name = f"{record.name} - {record.date}"
            if record.location_id:
                name += f" ({record.location_id.name})"
            result.append((record.id, name))
        return result
    
    @api.model_create_multi
    def create(self, vals_list):
        """Génère automatiquement la référence si elle n'est pas fournie."""
        for vals in vals_list:
            if vals.get('name', 'Nouveau') == 'Nouveau' or not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code('stockex.stock.inventory') or 'Nouveau'
        return super().create(vals_list)
    
    def action_export_excel(self):
        """Exporter l'inventaire en Excel."""
        self.ensure_one()
        
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
            from openpyxl.utils import get_column_letter
            import base64
            from io import BytesIO
        except ImportError:
            raise UserError("La bibliothèque openpyxl est requise pour l'export Excel.")
        
        # Créer le workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Inventaire"
        
        # Styles
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=12)
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # En-tête du document
        ws['A1'] = f"INVENTAIRE DE STOCK - {self.name}"
        ws['A1'].font = Font(bold=True, size=14)
        ws.merge_cells('A1:J1')
        
        ws['A2'] = f"Date: {self.date}"
        ws['A3'] = f"Responsable: {self.user_id.name}"
        ws['A4'] = f"Société: {self.company_id.name}"
        ws['A5'] = f"État: {dict(self._fields['state'].selection).get(self.state)}"
        
        # En-têtes colonnes (ligne 7)
        headers = [
            'Produit',
            'Référence',
            'Catégorie',
            'Emplacement',
            'Qté Théorique',
            'Qté Réelle',
            'Écart',
            'Prix Standard (FCFA)',
            'Valeur Écart (FCFA)',
            'UdM'
        ]
        
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=7, column=col_num, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.border = border
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        # Données
        row_num = 8
        total_theoretical = 0
        total_real = 0
        total_difference_value = 0
        
        for line in self.line_ids:
            ws.cell(row=row_num, column=1, value=line.product_id.name or '')
            ws.cell(row=row_num, column=2, value=line.product_id.default_code or '')
            ws.cell(row=row_num, column=3, value=line.product_id.categ_id.name or '')
            ws.cell(row=row_num, column=4, value=line.location_id.display_name or '')
            ws.cell(row=row_num, column=5, value=line.theoretical_qty)
            ws.cell(row=row_num, column=6, value=line.product_qty)
            ws.cell(row=row_num, column=7, value=line.difference)
            ws.cell(row=row_num, column=8, value=line.standard_price)
            
            diff_value = line.difference * line.standard_price
            ws.cell(row=row_num, column=9, value=diff_value)
            ws.cell(row=row_num, column=10, value=line.product_uom_id.name or '')
            
            # Bordures
            for col in range(1, 11):
                ws.cell(row=row_num, column=col).border = border
            
            # Colorer les écarts
            diff_cell = ws.cell(row=row_num, column=7)
            if line.difference > 0:
                diff_cell.font = Font(color="008000", bold=True)  # Vert
            elif line.difference < 0:
                diff_cell.font = Font(color="FF0000", bold=True)  # Rouge
            
            total_theoretical += line.theoretical_qty
            total_real += line.product_qty
            total_difference_value += diff_value
            row_num += 1
        
        # Ligne totaux
        row_num += 1
        ws.cell(row=row_num, column=1, value="TOTAUX").font = Font(bold=True)
        ws.cell(row=row_num, column=5, value=total_theoretical).font = Font(bold=True)
        ws.cell(row=row_num, column=6, value=total_real).font = Font(bold=True)
        ws.cell(row=row_num, column=7, value=total_real - total_theoretical).font = Font(bold=True)
        ws.cell(row=row_num, column=9, value=total_difference_value).font = Font(bold=True)
        
        for col in range(1, 11):
            ws.cell(row=row_num, column=col).fill = PatternFill(start_color="E0E0E0", end_color="E0E0E0", fill_type="solid")
        
        # Ajuster largeur colonnes
        column_widths = [30, 15, 20, 35, 15, 15, 12, 15, 15, 10]
        for i, width in enumerate(column_widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = width
        
        # Sauvegarder en mémoire
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        # Créer l'attachement
        attachment = self.env['ir.attachment'].create({
            'name': f'Inventaire_{self.name.replace("/", "_")}.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
    
    def action_print_pdf(self):
        """Imprimer l'inventaire en PDF."""
        self.ensure_one()
        return self.env.ref('stockex.action_report_inventory').report_action(self)
    
    @api.model
    def _send_inventory_reminders(self):
        """Envoie des rappels pour les inventaires en cours depuis plus de 7 jours."""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=7)
        old_inventories = self.search([
            ('state', 'in', ['in_progress', 'pending_approval']),
            ('create_date', '<=', cutoff_date)
        ])
        
        for inventory in old_inventories:
            # Créer une activité de rappel
            inventory.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=inventory.user_id.id,
                summary=f"Rappel: Inventaire en attente - {inventory.name}",
                note=f"L'inventaire {inventory.name} est en cours depuis plus de 7 jours. Merci de le finaliser.",
                date_deadline=fields.Date.today()
            )
            
            _logger.info(f"Rappel envoyé pour inventaire {inventory.name}")
        
        return True


class StockInventoryLine(models.Model):
    _name = 'stockex.stock.inventory.line'
    _description = 'Ligne d\'inventaire'
    _order = 'product_id, id'
    _rec_name = 'product_id'
    
    inventory_id = fields.Many2one(
        comodel_name='stockex.stock.inventory',
        string='Inventaire',
        required=True,
        ondelete='cascade',
        index=True
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Produit',
        required=True,
        index=True
    )
    product_barcode = fields.Char(
        string='Code-barres',
        related='product_id.barcode',
        readonly=True,
        help='Code-barres du produit pour scan mobile'
    )
    scanned_barcode = fields.Char(
        string='Code-barres scanné',
        help='Code-barres scanné pour recherche rapide de produit'
    )
    theoretical_qty = fields.Float(
        string='Quantité théorique',
        digits='Product Unit of Measure',
        readonly=True,
        compute='_compute_theoretical_qty',
        store=True
    )
    product_qty = fields.Float(
        string='Quantité réelle',
        digits='Product Unit of Measure',
        default=0.0
    )
    difference = fields.Float(
        string='Différence',
        compute='_compute_difference',
        store=True,
        digits='Product Unit of Measure',
        readonly=True
    )
    difference_display = fields.Html(
        string='Écart',
        compute='_compute_difference_display',
        readonly=True
    )
    location_id = fields.Many2one(
        comodel_name='stock.location',
        string='Emplacement',
        index=True
    )
    standard_price = fields.Float(
        string='Prix unitaire',
        digits='Product Price',
        help='Prix unitaire du produit au moment de l\'inventaire'
    )
    product_uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Unité de Mesure',
        related='product_id.uom_id',
        readonly=True
    )
    
    # Pièces jointes et photos
    image_1 = fields.Binary(
        string='Photo 1',
        attachment=True,
        help='Première photo du produit compté'
    )
    image_2 = fields.Binary(
        string='Photo 2',
        attachment=True,
        help='Deuxième photo du produit compté'
    )
    image_3 = fields.Binary(
        string='Photo 3',
        attachment=True,
        help='Troisième photo du produit compté'
    )
    note = fields.Text(
        string='Remarques',
        help='Notes ou observations sur cette ligne d\'inventaire'
    )
    
    @api.depends('product_id', 'location_id')
    def _compute_theoretical_qty(self):
        """Calcule la quantité théorique depuis le stock Odoo."""
        # Préparer l'ensemble des lignes pertinentes (avec produit et emplacement)
        lines = self.filtered(lambda l: l.product_id and l.location_id)

        # Initialiser les lignes sans données requises à 0
        for line in (self - lines):
            line.theoretical_qty = 0.0

        if not lines:
            return

        product_ids = list(set(lines.mapped('product_id').ids))
        location_ids = list(set(lines.mapped('location_id').ids))

        # Agréger en une seule requête SQL
        groups = self.env['stock.quant'].read_group(
            domain=[
                ('product_id', 'in', product_ids),
                ('location_id', 'in', location_ids),
            ],
            fields=['quantity:sum', 'reserved_quantity:sum'],
            groupby=['product_id', 'location_id'],
        )

        # Construire un mapping (product_id, location_id) -> quantity - reserved
        qty_map = {}
        for g in groups:
            prod_id = g['product_id'][0]
            loc_id = g['location_id'][0]
            qty = g.get('quantity_sum', 0.0) or 0.0
            reserved = g.get('reserved_quantity_sum', 0.0) or 0.0
            qty_map[(prod_id, loc_id)] = qty - reserved

        for line in lines:
            line.theoretical_qty = qty_map.get((line.product_id.id, line.location_id.id), 0.0)
    
    @api.depends('theoretical_qty', 'product_qty')
    def _compute_difference(self):
        """Calcule la différence entre la quantité réelle et théorique."""
        for line in self:
            line.difference = line.product_qty - line.theoretical_qty
    
    @api.depends('difference')
    def _compute_difference_display(self):
        """Affiche la différence en couleur selon le signe."""
        for line in self:
            diff = line.difference
            if diff < 0:
                color = 'red'
                icon = '⚠️'
            elif diff > 0:
                color = 'green'
                icon = '✓'
            else:
                color = 'gray'
                icon = '='
            line.difference_display = f'<span style="color: {color}; font-weight: bold;">{icon} {diff:,.2f}</span>'
    
    @api.onchange('scanned_barcode')
    def _onchange_scanned_barcode(self):
        """Recherche le produit par code-barres scanné."""
        if self.scanned_barcode:
            product = self.env['product.product'].search([
                ('barcode', '=', self.scanned_barcode)
            ], limit=1)
            if product:
                self.product_id = product.id
                self.scanned_barcode = False  # Reset après scan
            else:
                return {
                    'warning': {
                        'title': 'Code-barres non trouvé',
                        'message': f"Aucun produit trouvé avec le code-barres '{self.scanned_barcode}'"
                    }
                }
    
    @api.constrains('product_id', 'inventory_id')
    def _check_product_uniqueness(self):
        """Vérifie qu'un produit n'apparaît qu'une seule fois par inventaire."""
        for line in self:
            domain = [
                ('inventory_id', '=', line.inventory_id.id),
                ('product_id', '=', line.product_id.id),
                ('id', '!=', line.id)
            ]
            if line.location_id:
                domain.append(('location_id', '=', line.location_id.id))
            if self.search_count(domain) > 0:
                raise UserError(
                    f"Le produit '{line.product_id.display_name}' est déjà présent dans cet inventaire "
                    f"pour cet emplacement."
                )

