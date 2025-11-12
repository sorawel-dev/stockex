# -*- coding: utf-8 -*-

import logging
import json
from datetime import datetime
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ImportKoboWizard(models.TransientModel):
    """Wizard pour importer les données depuis Kobo Collect."""
    _name = 'stockex.import.kobo.wizard'
    _description = 'Import Kobo Collect'
    
    name = fields.Char(
        string='Nom de l\'Inventaire',
        required=True,
        default=lambda self: f"Inventaire Kobo {fields.Date.today()}"
    )
    
    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.today
    )
    
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Société',
        required=True,
        default=lambda self: self.env.company
    )
    
    config_id = fields.Many2one(
        comodel_name='stockex.kobo.config',
        string='Configuration Kobo',
        required=True,
        domain="[('active', '=', True), ('company_id', '=', company_id)]"
    )
    
    import_mode = fields.Selection(
        selection=[
            ('new_only', 'Nouvelles Soumissions Uniquement'),
            ('all', 'Toutes les Soumissions'),
            ('date_range', 'Plage de Dates'),
        ],
        string='Mode d\'Import',
        default='new_only',
        required=True
    )
    
    date_from = fields.Date(
        string='Date Début',
        help='Importer les soumissions à partir de cette date'
    )
    
    date_to = fields.Date(
        string='Date Fin',
        help='Importer les soumissions jusqu\'à cette date'
    )
    
    # Options
    create_missing_products = fields.Boolean(
        string='Créer les Produits Manquants',
        default=True,
        related='config_id.create_missing_products',
        readonly=False
    )
    
    create_missing_locations = fields.Boolean(
        string='Créer les Emplacements Manquants',
        default=True,
        related='config_id.create_missing_locations',
        readonly=False
    )
    
    update_product_prices = fields.Boolean(
        string='Mettre à Jour les Prix',
        default=True
    )
    
    import_geolocation = fields.Boolean(
        string='Importer la Géolocalisation',
        default=True
    )
    
    auto_validate = fields.Boolean(
        string='Valider Automatiquement',
        default=False,
        related='config_id.auto_validate',
        readonly=False
    )
    
    # Preview
    submissions_count = fields.Integer(
        string='Soumissions à Importer',
        compute='_compute_submissions_preview'
    )
    
    preview_html = fields.Html(
        string='Aperçu',
        compute='_compute_submissions_preview'
    )
    
    @api.depends('config_id', 'import_mode', 'date_from', 'date_to')
    def _compute_submissions_preview(self):
        """Calcule un aperçu des soumissions à importer."""
        for wizard in self:
            if not wizard.config_id:
                wizard.submissions_count = 0
                wizard.preview_html = "<p class='text-muted'>Sélectionnez une configuration Kobo</p>"
                continue
            
            # Simuler pour l'instant
            wizard.submissions_count = 0
            wizard.preview_html = f"""
            <div class='alert alert-info'>
                <h5>Configuration : {wizard.config_id.name}</h5>
                <ul>
                    <li><strong>Formulaire :</strong> {wizard.config_id.form_name or wizard.config_id.form_id}</li>
                    <li><strong>URL :</strong> {wizard.config_id.kobo_url}</li>
                    <li><strong>Mode :</strong> {dict(wizard._fields['import_mode'].selection).get(wizard.import_mode)}</li>
                </ul>
                <p class='text-warning'>⏳ Connexion à Kobo... Cliquez sur "Synchroniser" pour récupérer les données.</p>
            </div>
            """
    
    def action_sync_kobo(self):
        """Synchronise avec Kobo et récupère les soumissions."""
        self.ensure_one()
        
        if not self.config_id:
            raise UserError("Veuillez sélectionner une configuration Kobo.")
        
        try:
            import requests
            
            headers = {
                'Authorization': f'Token {self.config_id.api_token}',
                'Accept': 'application/json'
            }
            
            # Récupérer les soumissions
            url = f"{self.config_id.kobo_url}/api/v2/assets/{self.config_id.form_id}/data/?format=json"
            
            params = {}
            if self.import_mode == 'new_only' and self.config_id.last_submission_id:
                params['query'] = json.dumps({'_id': {'$gt': self.config_id.last_submission_id}})
            elif self.import_mode == 'date_range' and self.date_from:
                params['query'] = json.dumps({
                    '_submission_time': {
                        '$gte': self.date_from.strftime('%Y-%m-%d'),
                        '$lte': (self.date_to or fields.Date.today()).strftime('%Y-%m-%d')
                    }
                })
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                # Tolérance aux réponses non-JSON (HTML du DRF)
                try:
                    data = response.json()
                except Exception:
                    ct = response.headers.get('Content-Type') or 'n/a'
                    preview = (response.text or '')[:300].strip()
                    raise UserError(
                        "Réponse non-JSON de l'API Kobo.\n"
                        f"Content-Type: {ct}\n"
                        f"URL testée: {url}\n"
                        "Vérifiez l'UID, le token et que l'API renvoie bien du JSON (?format=json).\n"
                        f"Aperçu: {preview}"
                    )
                submissions = data.get('results', [])
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': '✅ Synchronisation Réussie',
                        'message': f"{len(submissions)} soumission(s) trouvée(s)",
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise UserError(
                    f"Erreur lors de la synchronisation:\n"
                    f"Code: {response.status_code}\n"
                    f"Message: {response.text}"
                )
                
        except ImportError:
            raise UserError(
                "Le module 'requests' n'est pas installé.\n"
                "Installez-le avec : pip3 install requests"
            )
        except Exception as e:
            raise UserError(f"Erreur lors de la synchronisation:\n{str(e)}")
    
    def action_import(self):
        """Importe les données depuis Kobo et crée l'inventaire."""
        self.ensure_one()
        
        if not self.config_id:
            raise UserError("Veuillez sélectionner une configuration Kobo.")
        
        try:
            import requests
            
            headers = {
                'Authorization': f'Token {self.config_id.api_token}',
                'Accept': 'application/json'
            }
            
            # Récupérer les soumissions
            url = f"{self.config_id.kobo_url}/api/v2/assets/{self.config_id.form_id}/data/?format=json"
            
            params = {}
            if self.import_mode == 'new_only' and self.config_id.last_submission_id:
                params['query'] = json.dumps({'_id': {'$gt': self.config_id.last_submission_id}})
            elif self.import_mode == 'date_range' and self.date_from:
                params['query'] = json.dumps({
                    '_submission_time': {
                        '$gte': self.date_from.strftime('%Y-%m-%d'),
                        '$lte': (self.date_to or fields.Date.today()).strftime('%Y-%m-%d')
                    }
                })
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code != 200:
                raise UserError(
                    f"Erreur lors de la récupération des données:\n"
                    f"Code: {response.status_code}\n"
                    f"Message: {response.text}"
                )
            
            try:
                data = response.json()
            except Exception:
                ct = response.headers.get('Content-Type') or 'n/a'
                preview = (response.text or '')[:300].strip()
                raise UserError(
                    "Réponse non-JSON de l'API Kobo.\n"
                    f"Content-Type: {ct}\n"
                    "Vérifiez l'UID, le token et que l'API renvoie bien du JSON (?format=json).\n"
                    f"Aperçu: {preview}"
                )
            submissions = data.get('results', [])
            
            if not submissions:
                raise UserError("Aucune soumission à importer.")
            
            # Créer l'inventaire
            inventory = self._create_inventory_from_submissions(submissions)
            
            # Mettre à jour la configuration
            if submissions:
                last_id = max(s.get('_id', 0) for s in submissions)
                self.config_id.write({
                    'last_sync': fields.Datetime.now(),
                    'last_submission_id': last_id,
                })
            
            # Auto-validation si demandé
            if self.auto_validate and inventory.line_ids:
                inventory.action_validate()
            
            return {
                'type': 'ir.actions.act_window',
                'name': 'Inventaire Importé',
                'res_model': 'stockex.stock.inventory',
                'res_id': inventory.id,
                'view_mode': 'form',
                'target': 'current',
            }
            
        except ImportError:
            raise UserError(
                "Le module 'requests' n'est pas installé.\n"
                "Installez-le avec : pip3 install requests"
            )
        except Exception as e:
            _logger.error(f"Erreur import Kobo: {e}", exc_info=True)
            raise UserError(f"Erreur lors de l'import:\n{str(e)}")
    
    def _download_kobo_attachment(self, submission, attachment_filename):
        """Télécharge une pièce jointe depuis Kobo avec authentification.
        
        Args:
            submission: Dictionnaire de la soumission Kobo (contient _attachments)
            attachment_filename: Nom du fichier de la pièce jointe (ex: 1762608570518.jpg)
            
        Returns:
            tuple: (file_content (bytes), filename (str)) ou (None, None) si erreur
        """
        if not attachment_filename:
            return None, None
            
        try:
            import requests
            import base64
            from PIL import Image
            from io import BytesIO
            
            # Chercher l'attachment correspondant dans _attachments
            attachments = submission.get('_attachments', [])
            target_attachment = None
            
            _logger.info(f"Recherche attachment '{attachment_filename}' parmi {len(attachments)} attachments")
            
            for att in attachments:
                basename = att.get('media_file_basename', '')
                fullname = att.get('filename', '')
                _logger.debug(f"Checking: basename={basename}, fullname={fullname}")
                # Matcher par media_file_basename (nom de fichier uniquement)
                if basename == attachment_filename:
                    target_attachment = att
                    _logger.info(f"Match trouvé par basename: {basename}")
                    break
                # Fallback: matcher si le filename complet contient notre nom
                if attachment_filename in fullname:
                    target_attachment = att
                    _logger.info(f"Match trouvé par fullname: {fullname}")
                    break
            
            if not target_attachment:
                _logger.warning(f"Attachment {attachment_filename} non trouvé dans _attachments")
                return None, None
            
            # Récupérer l'URL de téléchargement
            download_url = target_attachment.get('download_medium_url') or target_attachment.get('download_url')
            if not download_url:
                _logger.warning(f"Pas d'URL de téléchargement pour {attachment_filename}")
                return None, None
            
            # Headers d'authentification
            headers = {
                'Authorization': f'Token {self.config_id.api_token}',
            }
            
            # Télécharger le fichier
            file_response = requests.get(download_url, headers=headers, timeout=60)
            
            if file_response.status_code == 200:
                # Compresser l'image si c'est une image et si la compression est activée
                file_content = file_response.content
                if self.config_id.compress_photos and attachment_filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    try:
                        # Charger l'image
                        img = Image.open(BytesIO(file_content))
                        
                        # Convertir en RGB si nécessaire (pour PNG avec transparence)
                        if img.mode in ('RGBA', 'LA', 'P'):
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            if img.mode == 'P':
                                img = img.convert('RGBA')
                            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                            img = background
                        
                        # Redimensionner si l'image est trop grande
                        max_dimension = self.config_id.photo_max_size or 1600
                        if max(img.size) > max_dimension:
                            ratio = max_dimension / max(img.size)
                            new_size = tuple(int(dim * ratio) for dim in img.size)
                            # Utiliser LANCZOS pour la meilleure qualité de redimensionnement
                            img = img.resize(new_size, Image.Resampling.LANCZOS)
                        
                        # Compresser en JPEG avec qualité configurable et optimisations
                        quality = max(70, min(95, self.config_id.photo_quality or 90))  # Limiter entre 70-95
                        output = BytesIO()
                        # optimize=True pour une compression optimale
                        # progressive=True pour chargement progressif (meilleure expérience)
                        img.save(output, format='JPEG', quality=quality, optimize=True, progressive=True)
                        file_content = output.getvalue()
                        
                        # Changer l'extension en .jpg
                        attachment_filename = attachment_filename.rsplit('.', 1)[0] + '.jpg'
                        
                        original_size = len(file_response.content) / 1024
                        compressed_size = len(file_content) / 1024
                        _logger.info(f"Image compressée: {attachment_filename} ({original_size:.1f}KB → {compressed_size:.1f}KB, gain: {100*(1-compressed_size/original_size):.1f}%)")
                        
                    except Exception as e:
                        _logger.warning(f"Impossible de compresser {attachment_filename}: {e}")
                        # Garder le fichier original en cas d'erreur
                        file_content = file_response.content
                
                return file_content, attachment_filename
            else:
                _logger.warning(f"Erreur téléchargement {attachment_filename}: {file_response.status_code}")
                return None, None
                
        except Exception as e:
            _logger.error(f"Erreur lors du téléchargement de {attachment_filename}: {e}")
            return None, None
    
    def _create_inventory_from_submissions(self, submissions):
        """Crée un inventaire à partir des soumissions Kobo."""
        # Créer l'inventaire
        inventory = self.env['stockex.stock.inventory'].create({
            'name': self.name,
            'date': self.date,
            'company_id': self.company_id.id,
            'user_id': self.env.user.id,
            'state': 'draft',
            'description': f'Import Kobo Collect - {len(submissions)} soumissions\nFormulaire: {self.config_id.form_name or self.config_id.form_id}'
        })
        
        # Caches
        products_cache = {}
        locations_cache = {}
        warehouses_cache = {}
        categories_cache = {}
        
        imported = 0
        skipped = 0
        errors_detail = []
        
        # Mapping des champs depuis la configuration
        cfg = self.config_id
        field_product_code = cfg.mapping_product_code or 'Code d\'article'
        field_product_name = cfg.mapping_product_name or 'Nom du Materiel'
        field_quantity = cfg.mapping_quantity or 'Quantité'
        field_location = cfg.mapping_location or 'MAGASIN'
        field_warehouse = cfg.mapping_warehouse or 'EMPLACEMENT'
        field_category = cfg.mapping_category or 'category'
        field_price = cfg.mapping_price or 'unit_price'
        field_brand = cfg.mapping_brand or 'Marque'
        field_product_type = cfg.mapping_product_type or 'Type d\'article'
        field_gps_lat = cfg.mapping_gps_lat or '_Coordonnées géographiques_latitude'
        field_gps_lon = cfg.mapping_gps_lon or '_Coordonnées géographiques_longitude'
        field_gps_alt = cfg.mapping_gps_alt or '_Coordonnées géographiques_altitude'
        field_photo_url = cfg.mapping_photo_url or 'Ajouter une photo du material_URL'
        field_label_url = cfg.mapping_label_url or 'Ajouter une photo de l\'etiquette d\'inventaire ENEO_URL'
        field_submission_time = cfg.mapping_submission_time or '_submission_time'
        field_submission_id = cfg.mapping_submission_id or '_id'
        
        for i, submission in enumerate(submissions):
            try:
                # Extraire les données selon le mapping
                product_code = str(submission.get(field_product_code, '')).strip()
                product_name = str(submission.get(field_product_name, '')).strip()
                location_name = str(submission.get(field_location, '')).strip()
                warehouse_name = str(submission.get(field_warehouse, '')).strip()
                
                if not product_code:
                    skipped += 1
                    errors_detail.append(f"Soumission {i+1}: Code produit manquant")
                    continue
                
                # Quantité
                try:
                    quantity = float(submission.get(field_quantity, 0))
                except:
                    quantity = 0.0
                
                # Prix
                try:
                    price = float(submission.get(field_price, 0))
                except:
                    price = 0.0
                
                # Marque
                brand = str(submission.get(field_brand, '')).strip()
                
                # Type d'article (sérialisé ou non)
                product_type_str = str(submission.get(field_product_type, '')).strip()
                is_serialized = 'sérialisé' in product_type_str.lower()
                
                # GPS - Gestion spéciale pour _geolocation qui est un tableau [lat, lon]
                gps_lat = gps_lon = gps_alt = None
                if self.import_geolocation:
                    try:
                        # Si le champ GPS est _geolocation (tableau)
                        if '_geolocation' in str(field_gps_lat).lower():
                            geoloc = submission.get('_geolocation', [])
                            if isinstance(geoloc, list) and len(geoloc) >= 2:
                                gps_lat = float(geoloc[0])
                                gps_lon = float(geoloc[1])
                        else:
                            # Sinon, utiliser les champs séparés
                            gps_lat = float(submission.get(field_gps_lat, 0))
                            gps_lon = float(submission.get(field_gps_lon, 0))
                            if field_gps_alt:
                                gps_alt = float(submission.get(field_gps_alt, 0))
                    except:
                        pass
                
                # URLs des photos
                photo_url = str(submission.get(field_photo_url, '')).strip()
                label_url = str(submission.get(field_label_url, '')).strip()
                
                # Catégorie
                category_name = str(submission.get(field_category, '')).strip()
                category_id = None
                if category_name and category_name not in categories_cache:
                    category = self.env['product.category'].search([('name', '=', category_name)], limit=1)
                    if not category and self.create_missing_products:
                        category = self.env['product.category'].create({'name': category_name})
                    categories_cache[category_name] = category.id if category else False
                category_id = categories_cache.get(category_name)
                
                # Emplacement (location_id)
                # Chercher d'abord par le magasin principal
                location_key = f"{location_name}|{warehouse_name}"
                if location_key not in locations_cache:
                    # Option 1: Chercher un entrepôt par nom exact
                    warehouse = self.env['stock.warehouse'].search([
                        '|',
                        ('name', '=', location_name),
                        ('name', 'ilike', location_name)
                    ], limit=1)
                    
                    if not warehouse and self.create_missing_locations:
                        # Créer un nouvel entrepôt
                        code = location_name[:5].upper().replace(' ', '')
                        # Vérifier que le code n'existe pas déjà
                        existing_code = self.env['stock.warehouse'].search([('code', '=', code)], limit=1)
                        if existing_code:
                            code = f"{code}{self.env['stock.warehouse'].search_count([])+1}"
                        
                        warehouse = self.env['stock.warehouse'].create({
                            'name': location_name,
                            'code': code,
                            'company_id': self.company_id.id,
                        })
                    
                    if warehouse:
                        # Si on a un sous-emplacement spécifique
                        if warehouse_name and warehouse_name != location_name:
                            # Chercher ou créer un sous-emplacement
                            sub_location = self.env['stock.location'].search([
                                ('name', '=', warehouse_name),
                                ('location_id', '=', warehouse.lot_stock_id.id)
                            ], limit=1)
                            
                            if not sub_location and self.create_missing_locations:
                                sub_location = self.env['stock.location'].create({
                                    'name': warehouse_name,
                                    'location_id': warehouse.lot_stock_id.id,
                                    'usage': 'internal',
                                    'company_id': self.company_id.id,
                                })
                            
                            locations_cache[location_key] = sub_location.id if sub_location else warehouse.lot_stock_id.id
                        else:
                            locations_cache[location_key] = warehouse.lot_stock_id.id
                    else:
                        locations_cache[location_key] = False
                
                location_id = locations_cache.get(location_key)
                if not location_id:
                    skipped += 1
                    errors_detail.append(f"Soumission {i+1}: Emplacement '{location_name}' non créé")
                    continue
                
                # Produit
                if product_code not in products_cache:
                    product = self.env['product.product'].search([('default_code', '=', product_code)], limit=1)
                    
                    if not product and self.create_missing_products:
                        product_vals = {
                            'name': product_name or product_code,
                            'default_code': product_code,
                            'type': 'product',
                            'categ_id': category_id if category_id else self.env.ref('product.product_category_all').id,
                            'standard_price': price if price > 0 else 0.0,
                        }
                        
                        # Ajouter la marque si disponible
                        if brand:
                            # Chercher ou créer un attribut "Marque" (optionnel)
                            product_vals['description'] = f"Marque: {brand}"
                        
                        # Tracking pour articles sérialisés
                        if is_serialized:
                            product_vals['tracking'] = 'serial'
                        
                        product = self.env['product.product'].create(product_vals)
                        
                    elif product and self.update_product_prices and price > 0:
                        product.write({'standard_price': price})
                    
                    products_cache[product_code] = product.id if product else False
                
                product_id = products_cache.get(product_code)
                if not product_id:
                    skipped += 1
                    errors_detail.append(f"Soumission {i+1}: Produit '{product_code}' non créé")
                    continue
                
                # Créer la ligne d'inventaire
                line_vals = {
                    'inventory_id': inventory.id,
                    'product_id': product_id,
                    'location_id': location_id,
                    'product_qty': quantity,
                    'standard_price': price if price > 0 else 0.0,
                }
                
                # Ajouter les coordonnées GPS si disponibles
                if gps_lat and gps_lon and location_id:
                    try:
                        loc_rec = self.env['stock.location'].browse(location_id)
                        if loc_rec:
                            vals = {'latitude': gps_lat, 'longitude': gps_lon}
                            loc_rec.write(vals)
                    except Exception as e:
                        _logger.warning(f"Impossible de mettre à jour les coordonnées GPS de l'emplacement: {e}")
                line = self.env['stockex.stock.inventory.line'].create(line_vals)
                
                # Télécharger et attacher les photos (si activé)
                photos_attached = []
                if self.config_id.download_photos:
                    if photo_url:
                        file_content, filename = self._download_kobo_attachment(submission, photo_url)
                        if file_content and filename:
                            import base64
                            line.write({'image_1': base64.b64encode(file_content)})
                            size_kb = len(file_content) / 1024
                            photos_attached.append(f"✅ Photo produit intégrée ({size_kb:.1f} KB)")
                        else:
                            photos_attached.append(f"⚠️ Photo produit non disponible: {photo_url}")
                    
                    if label_url:
                        file_content, filename = self._download_kobo_attachment(submission, label_url)
                        if file_content and filename:
                            import base64
                            line.write({'image_2': base64.b64encode(file_content)})
                            size_kb = len(file_content) / 1024
                            photos_attached.append(f"✅ Étiquette intégrée ({size_kb:.1f} KB)")
                        else:
                            photos_attached.append(f"⚠️ Étiquette non disponible: {label_url}")
                else:
                    # Téléchargement désactivé, stocker juste les URLs
                    if photo_url:
                        photos_attached.append(f"🔗 Photo produit: {photo_url}")
                    if label_url:
                        photos_attached.append(f"🔗 Étiquette: {label_url}")
                
                # Ajouter une note avec les informations supplémentaires
                notes = []
                if gps_lat and gps_lon:
                    notes.append(f"GPS: {gps_lat}, {gps_lon}")
                    if gps_alt is not None:
                        notes.append(f"Alt: {gps_alt}")
                if brand:
                    notes.append(f"Marque: {brand}")
                if product_type_str:
                    notes.append(f"Type: {product_type_str}")
                if warehouse_name:
                    notes.append(f"Emplacement détaillé: {warehouse_name}")
                if photos_attached:
                    notes.extend(photos_attached)
                
                if notes:
                    line.write({'note': '\n'.join(notes)})
                
                imported += 1
                
            except Exception as e:
                skipped += 1
                errors_detail.append(f"Soumission {i+1}: {str(e)}")
                _logger.error(f"Erreur import soumission {i+1}: {e}", exc_info=True)
        
        # Message de résultat
        message = f"✅ Import Kobo terminé\n\n"
        message += f"📊 Statistiques:\n"
        message += f"- Total soumissions: {len(submissions)}\n"
        message += f"- ✅ Importées: {imported}\n"
        message += f"- ⚠️ Ignorées: {skipped}\n"
        
        if errors_detail:
            message += f"\n⚠️ Détails des erreurs (premières 10):\n" + "\n".join(errors_detail[:10])
            if len(errors_detail) > 10:
                message += f"\n... et {len(errors_detail) - 10} autres erreurs"
        
        inventory.message_post(body=message)
        
        return inventory
