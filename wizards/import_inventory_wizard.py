# -*- coding: utf-8 -*-

import base64
import csv
import io
import logging

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ImportInventoryWizard(models.TransientModel):
    _name = 'stockex.import.inventory.wizard'
    _description = 'Assistant d\'Import d\'Inventaire CSV'

    name = fields.Char(
        string='Nom de l\'inventaire',
        required=True,
        default='Import CSV',
        help='Nom descriptif pour identifier cet inventaire'
    )
    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.today,
        help='Date de réalisation de l\'inventaire'
    )
    file = fields.Binary(
        string='Fichier CSV',
        required=True,
        help='Fichier CSV contenant les données d\'inventaire'
    )
    filename = fields.Char(
        string='Nom du fichier',
        help='Nom du fichier CSV importé'
    )
    
    separator = fields.Selection(
        selection=[(',', 'Virgule (,)'), (';', 'Point-virgule (;)'), ('\t', 'Tabulation')],
        string='Séparateur',
        default=',',
        required=True,
        help='Séparateur de colonnes utilisé dans le fichier CSV'
    )
    decimal_separator = fields.Selection(
        selection=[(',', 'Virgule (,)'), ('.', 'Point (.)')],
        string='Séparateur décimal',
        default=',',
        required=True,
        help='Séparateur décimal pour les nombres (virgule ou point)'
    )
    create_missing_products = fields.Boolean(
        string='Créer les produits manquants',
        default=True,
        help='Si coché, les produits non trouvés seront créés automatiquement'
    )
    create_missing_locations = fields.Boolean(
        string='Créer les emplacements manquants',
        default=True,
        help='Si coché, les emplacements non trouvés seront créés automatiquement'
    )
    update_product_prices = fields.Boolean(
        string='Mettre à jour les prix produits',
        default=False,
        help='Si coché, les prix standards des produits seront mis à jour'
    )
    
    # Statistiques après prévisualisation
    preview_done = fields.Boolean(string='Prévisualisation effectuée', default=False)
    total_lines = fields.Integer(string='Nombre total de lignes', readonly=True)
    valid_lines = fields.Integer(string='Lignes valides', readonly=True)
    error_lines = fields.Integer(string='Lignes avec erreurs', readonly=True)
    preview_log = fields.Text(string='Log de prévisualisation', readonly=True)

    def _get_or_create_uom(self, uom_code):
        """Récupère ou crée une unité de mesure.
        
        Mapping:
        - PC (Pièce) → Units (Unité)
        - KG → kg
        - L → L (Litre)
        - M → m (Mètre)
        """
        # Mapping des codes CSV vers noms Odoo
        uom_mapping = {
            'PC': 'Units',
            'PCS': 'Units',
            'PIECE': 'Units',
            'UNITE': 'Units',
            'KG': 'kg',
            'L': 'L',
            'M': 'm',
            'M2': 'm²',
            'M3': 'm³',
        }
        
        # Récupérer le nom Odoo correspondant
        uom_name = uom_mapping.get(uom_code.upper().strip(), 'Units')
        
        # Chercher l'UOM
        uom = self.env['uom.uom'].search([('name', '=', uom_name)], limit=1)
        
        if not uom:
            # Fallback: chercher la catégorie Unit pour créer une nouvelle UOM
            category_unit = self.env['uom.category'].search([('name', '=', 'Unit')], limit=1)
            if not category_unit:
                # Créer la catégorie si elle n'existe pas
                category_unit = self.env['uom.category'].create({'name': 'Unit'})
            
            # Créer l'UOM
            uom = self.env['uom.uom'].create({
                'name': uom_name,
                'category_id': category_unit.id,
                'factor': 1.0,
                'uom_type': 'reference',
                'rounding': 0.01,
            })
        
        return uom

    def _clean_number(self, value):
        """Nettoie et convertit une valeur numérique du CSV."""
        if not value or value.strip() in ['-', '']:
            return 0.0
        
        try:
            # Enlever les espaces (séparateur de milliers)
            value = str(value).strip().replace(' ', '')
            
            # Remplacer le séparateur décimal si nécessaire
            if self.decimal_separator == ',':
                value = value.replace(',', '.')
            
            return float(value)
        except (ValueError, AttributeError):
            return 0.0

    def _parse_csv(self):
        """Parse le fichier CSV et retourne les lignes."""
        if not self.file:
            raise UserError("Veuillez sélectionner un fichier CSV.")
        
        try:
            # Décoder le fichier
            csv_data = base64.b64decode(self.file)
            csv_file = io.StringIO(csv_data.decode('utf-8'))
            
            # Lire le CSV
            reader = csv.DictReader(csv_file, delimiter=self.separator)
            
            # Nettoyer les noms de colonnes (supprimer espaces avant/après)
            lines = []
            for row in reader:
                cleaned_row = {key.strip(): value for key, value in row.items()}
                lines.append(cleaned_row)
            
            return lines
            
        except Exception as e:
            raise UserError(f"Erreur lors de la lecture du fichier CSV : {str(e)}")

    def action_preview(self):
        """Prévisualise l'import sans créer de données."""
        self.ensure_one()
        
        lines = self._parse_csv()
        total = len(lines)
        valid = 0
        errors = 0
        log_messages = []
        
        log_messages.append(f"=== PRÉVISUALISATION DE L'IMPORT ===\n")
        log_messages.append(f"Fichier : {self.filename}")
        log_messages.append(f"Total lignes : {total}\n")
        
        # Vérifier la structure
        if lines:
            expected_cols = ['wh_type_code', 'wh_type_id', 'wh_code', 'wharehouse', 
                           'product_default_code', 'product_id', 'uom', 'quantity', 'standard_price']
            first_line_keys = list(lines[0].keys())
            
            # Nettoyer les espaces dans les clés
            first_line_keys = [k.strip() for k in first_line_keys]
            
            log_messages.append(f"Colonnes détectées : {', '.join(first_line_keys[:5])}...")
        
        # Analyser un échantillon
        sample_size = min(100, total)
        for i, line in enumerate(lines[:sample_size]):
            try:
                # Vérifier les champs obligatoires (accepter quantité 0)
                product_code = line.get('product_default_code', '').strip()
                warehouse = line.get('wharehouse', '').strip()
                quantity = self._clean_number(line.get('quantity', '0'))
                
                if product_code and warehouse:
                    valid += 1
                else:
                    errors += 1
                    if errors <= 10:  # Limiter les messages d'erreur
                        log_messages.append(f"❌ Ligne {i+2}: Produit ou emplacement manquant")
                        
            except Exception as e:
                errors += 1
                if errors <= 10:
                    log_messages.append(f"❌ Ligne {i+2}: {str(e)}")
        
        # Statistiques
        log_messages.append(f"\n=== RÉSULTATS ===")
        log_messages.append(f"✅ Lignes valides : {valid}/{sample_size} (échantillon)")
        log_messages.append(f"❌ Lignes avec erreurs : {errors}/{sample_size}")
        log_messages.append(f"\n⚠️  Estimation sur fichier complet :")
        log_messages.append(f"   Lignes valides estimées : ~{int(valid * total / sample_size)}")
        log_messages.append(f"   Lignes erreurs estimées : ~{int(errors * total / sample_size)}")
        
        # Mettre à jour le wizard
        self.write({
            'preview_done': True,
            'total_lines': total,
            'valid_lines': int(valid * total / sample_size),
            'error_lines': int(errors * total / sample_size),
            'preview_log': '\n'.join(log_messages)
        })
        
        # Retourner le même wizard
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stockex.import.inventory.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def action_import(self):
        """Lance l'import réel des données."""
        self.ensure_one()
        
        if not self.preview_done:
            raise UserError("Veuillez d'abord effectuer une prévisualisation de l'import.")
        
        lines = self._parse_csv()
        
        # Générer un nom unique avec timestamp si nécessaire
        inventory_name = self.name
        existing = self.env['stockex.stock.inventory'].search([('name', '=', inventory_name)])
        if existing:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            inventory_name = f"{self.name} ({timestamp})"
        
        # Créer l'inventaire
        inventory = self.env['stockex.stock.inventory'].create({
            'name': inventory_name,
            'date': self.date,
            'description': f'Import CSV - {self.filename}\nLignes importées : {len(lines)}'
        })
        
        # Dictionnaires de cache
        warehouses_cache = {}
        products_cache = {}
        parent_warehouses_cache = {}
        
        imported = 0
        skipped = 0
        errors_detail = []
        
        for i, line in enumerate(lines):
            try:
                # Extraire les données
                product_code = line.get('product_default_code', '').strip()
                product_name = line.get('product_id', '').strip()
                warehouse_name = line.get('wharehouse', '').strip()
                quantity = self._clean_number(line.get('quantity', '0'))
                standard_price = self._clean_number(line.get('standard_price', '0'))
                uom_name = line.get('uom', 'PC').strip()
                
                # Vérifier les données obligatoires (accepter quantité 0)
                if not product_code or not warehouse_name:
                    skipped += 1
                    errors_detail.append(f"Ligne {i+2}: Produit ou emplacement manquant")
                    continue
                
                # Récupérer les infos de l'emplacement parent
                parent_location_code = line.get('wh_type_code', '').strip()
                parent_location_name = line.get('wh_type_id', '').strip()
                wh_code = line.get('wh_code', '').strip()
                
                # Récupérer ou créer l'entrepôt
                if warehouse_name not in warehouses_cache:
                    # Rechercher l'entrepôt par code ou nom
                    warehouse = self.env['stock.warehouse'].search([
                        '|',
                        ('code', '=', wh_code if wh_code else warehouse_name[:5].upper()),
                        ('name', '=', warehouse_name)
                    ], limit=1)
                    
                    if not warehouse and self.create_missing_locations:
                        # Créer ou récupérer l'entrepôt parent
                        parent_warehouse_id = None
                        if parent_location_code and parent_location_name:
                            if parent_location_code not in parent_warehouses_cache:
                                parent_warehouse = self.env['stock.warehouse'].search([
                                    '|',
                                    ('code', '=', parent_location_code),
                                    ('name', '=', parent_location_name)
                                ], limit=1)
                                
                                if not parent_warehouse:
                                    # Créer l'entrepôt parent
                                    parent_warehouse = self.env['stock.warehouse'].create({
                                        'name': parent_location_name,
                                        'code': parent_location_code[:5].upper(),
                                        'company_id': self.env.company.id,
                                    })
                                
                                parent_warehouses_cache[parent_location_code] = parent_warehouse.id if parent_warehouse else False
                            
                            parent_warehouse_id = parent_warehouses_cache.get(parent_location_code)
                        
                        # Créer l'entrepôt
                        warehouse = self.env['stock.warehouse'].create({
                            'name': warehouse_name,
                            'code': wh_code[:5].upper() if wh_code else warehouse_name[:5].upper(),
                            'company_id': self.env.company.id,
                            'parent_id': parent_warehouse_id if parent_warehouse_id else False,
                        })
                    
                    # Stocker l'emplacement de stock de l'entrepôt (lot_stock_id)
                    warehouses_cache[warehouse_name] = warehouse.lot_stock_id.id if warehouse else False
                
                location_id = warehouses_cache.get(warehouse_name)
                if not location_id:
                    skipped += 1
                    errors_detail.append(f"Ligne {i+2}: Entrepôt '{warehouse_name}' non trouvé")
                    continue
                
                # Récupérer ou créer le produit
                if product_code not in products_cache:
                    product = self.env['product.product'].search([
                        ('default_code', '=', product_code)
                    ], limit=1)
                    
                    if not product and self.create_missing_products:
                        # Récupérer ou créer l'UOM (PC → Units)
                        uom = self._get_or_create_uom(uom_name)
                        
                        # Ne pas spécifier le type, laisser la valeur par défaut d'Odoo
                        product = self.env['product.product'].create({
                            'name': product_name or product_code,
                            'default_code': product_code,
                            # 'type': laissé vide pour utiliser la valeur par défaut
                            'standard_price': standard_price,
                            'uom_id': uom.id,
                            'uom_po_id': uom.id,
                        })
                    
                    products_cache[product_code] = product.id if product else False
                
                product_id = products_cache.get(product_code)
                if not product_id:
                    skipped += 1
                    errors_detail.append(f"Ligne {i+2}: Produit '{product_code}' non trouvé")
                    continue
                
                # Mettre à jour le prix SI l'option est cochée (en dehors du cache)
                if self.update_product_prices and standard_price > 0:
                    product = self.env['product.product'].browse(product_id)
                    if product.standard_price != standard_price:
                        product.write({'standard_price': standard_price})
                
                # Créer la ligne d'inventaire
                # La quantité théorique sera calculée automatiquement par le modèle
                self.env['stockex.stock.inventory.line'].create({
                    'inventory_id': inventory.id,
                    'product_id': product_id,
                    'location_id': location_id,
                    'product_qty': quantity,  # Quantité inventoriée (du CSV)
                })
                
                imported += 1
                
                # Commit par batch tous les 500 enregistrements pour éviter timeout
                if imported % 500 == 0:
                    self.env.cr.commit()
                    
            except Exception as e:
                skipped += 1
                import traceback
                error_msg = f"Ligne {i+2}: {str(e)}"
                errors_detail.append(error_msg)
                _logger.error(f"{error_msg}\n{traceback.format_exc()}")
        
        # Message de confirmation
        message = f"Import terminé avec succès !\n\n"
        message += f"✅ Lignes importées : {imported}\n"
        message += f"⚠️  Lignes ignorées : {skipped}\n"
        if errors_detail[:5]:  # Afficher max 5 premières erreurs
            message += f"\nPremières erreurs :\n" + "\n".join(errors_detail[:5])
        
        # Ajouter le résumé dans la description de l'inventaire
        inventory.write({
            'description': inventory.description + f"\n\n{message}"
        })
        
        # Retourner vers l'inventaire créé
        return {
            'type': 'ir.actions.act_window',
            'name': 'Inventaire Importé',
            'res_model': 'stockex.stock.inventory',
            'view_mode': 'form',
            'res_id': inventory.id,
            'target': 'current',
        }
