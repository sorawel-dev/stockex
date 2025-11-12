# -*- coding: utf-8 -*-
"""
Contrôleur Mobile PWA - Stockex
================================
Interface mobile optimisée pour inventaire terrain avec mode offline.

Features:
- PWA (Progressive Web App)
- Scan codes-barres (QuaggaJS)
- Mode offline (Service Worker + IndexedDB)
- Interface tactile optimisée
- Synchronisation automatique
"""

import json
import logging
import os
from odoo import http, fields
from odoo.http import request, Response
from odoo.modules.module import get_module_path

_logger = logging.getLogger(__name__)


class StockexMobileController(http.Controller):
    """Contrôleur pour application mobile PWA."""
    
    # ========== PAGES PRINCIPALES ==========
    
    @http.route('/stockex/mobile', type='http', auth='user', website=True)
    def mobile_home(self, **kwargs):
        """Page d'accueil mobile PWA."""
        return request.render('stockex.mobile_home', {
            'page_title': 'Stockex Mobile',
        })
    
    @http.route('/stockex/mobile/offline', type='http', auth='public', website=True)
    def mobile_offline(self, **kwargs):
        """Page affichée quand offline sans cache."""
        return request.render('stockex.mobile_offline', {
            'page_title': 'Mode Hors Ligne',
        })
    
    @http.route('/stockex/mobile/new', type='http', auth='user', website=True)
    def mobile_new_inventory(self, **kwargs):
        """Créer un nouvel inventaire mobile."""
        # Liste des emplacements pour sélection
        locations = request.env['stock.location'].search([
            ('usage', '=', 'internal'),
        ], order='complete_name')
        
        return request.render('stockex.mobile_new_inventory', {
            'page_title': 'Nouvel Inventaire',
            'locations': locations,
        })
    
    @http.route('/stockex/mobile/scan', type='http', auth='user', website=True)
    def mobile_scan(self, inventory_id=None, **kwargs):
        """Interface de scan de codes-barres."""
        inventory = None
        if inventory_id:
            inventory = request.env['stockex.stock.inventory'].browse(int(inventory_id))
        
        return request.render('stockex.mobile_scan', {
            'page_title': 'Scanner Code-Barres',
            'inventory': inventory,
        })
    
    @http.route('/stockex/mobile/inventory/<int:inventory_id>', type='http', auth='user', website=True)
    def mobile_inventory_detail(self, inventory_id, **kwargs):
        """Détail d'un inventaire mobile."""
        inventory = request.env['stockex.stock.inventory'].browse(inventory_id)
        
        if not inventory.exists():
            return request.render('stockex.mobile_error', {
                'error_message': 'Inventaire introuvable',
            })
        
        return request.render('stockex.mobile_inventory_detail', {
            'page_title': f'Inventaire {inventory.name}',
            'inventory': inventory,
        })
    
    # ========== API JSON MOBILE ==========
    
    @http.route('/api/mobile/inventory/create', type='http', auth='user', methods=['POST'], csrf=False)
    def mobile_create_inventory(self, **params):
        """Crée un nouvel inventaire depuis l'interface mobile."""
        try:
            location_id = int(params.get('location_id'))
            date = params.get('date')
            
            if not location_id:
                return request.redirect('/stockex/mobile?error=missing_location')
            
            # Créer l'inventaire
            inventory = request.env['stockex.stock.inventory'].create({
                'location_id': location_id,
                'date': date or fields.Date.today(),
                'state': 'draft',
            })
            
            # Rediriger vers la page de scan pour cet inventaire
            return request.redirect(f'/stockex/mobile/scan?inventory_id={inventory.id}')
            
        except Exception as e:
            _logger.error(f"Erreur création inventaire mobile: {str(e)}", exc_info=True)
            return request.redirect(f'/stockex/mobile?error={str(e)}')
    
    @http.route('/api/mobile/inventories/sync', type='json', auth='user', methods=['POST'], csrf=False)
    def sync_inventories(self, **params):
        """Synchronise les inventaires locaux (offline) vers serveur.
        
        Body JSON:
        {
            "inventories": [
                {
                    "local_id": "temp-123",
                    "location_id": 8,
                    "date": "2025-10-28",
                    "lines": [
                        {
                            "product_id": 42,
                            "product_qty": 100,
                            "standard_price": 1000
                        }
                    ]
                }
            ]
        }
        """
        try:
            inventories_data = params.get('inventories', [])
            if not inventories_data:
                return {
                    'success': False,
                    'error': 'Aucun inventaire à synchroniser',
                }
            
            synced = []
            errors = []
            
            for inv_data in inventories_data:
                try:
                    # Valider les données requises
                    if not inv_data.get('location_id'):
                        raise ValueError("location_id requis")
                    
                    # Créer l'inventaire sur le serveur
                    inventory_vals = {
                        'location_id': inv_data['location_id'],
                        'date': inv_data.get('date') or fields.Date.today(),
                        'state': 'draft',
                    }
                    
                    inventory = request.env['stockex.stock.inventory'].create(inventory_vals)
                    _logger.info(f"✅ Inventaire créé: {inventory.name} (ID: {inventory.id})")
                    
                    # Créer les lignes
                    lines_created = 0
                    for line_data in inv_data.get('lines', []):
                        if not line_data.get('product_id'):
                            continue
                            
                        request.env['stockex.stock.inventory.line'].create({
                            'inventory_id': inventory.id,
                            'product_id': line_data['product_id'],
                            'product_qty': line_data.get('product_qty', 0) or line_data.get('real_qty', 0),
                            'standard_price': line_data.get('standard_price', 0),
                        })
                        lines_created += 1
                    
                    _logger.info(f"✅ {lines_created} lignes créées pour {inventory.name}")
                    
                    synced.append({
                        'local_id': inv_data.get('local_id'),
                        'server_id': inventory.id,
                        'name': inventory.name,
                        'lines_count': lines_created,
                    })
                    
                except Exception as e:
                    error_msg = str(e)
                    _logger.error(f"❌ Erreur sync inventaire {inv_data.get('local_id')}: {error_msg}", exc_info=True)
                    errors.append({
                        'local_id': inv_data.get('local_id'),
                        'error': error_msg,
                    })
            
            return {
                'success': True,
                'synced': synced,
                'errors': errors,
                'total': len(inventories_data),
                'synced_count': len(synced),
                'error_count': len(errors),
            }
            
        except Exception as e:
            _logger.error(f"Erreur globale sync: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
            }
    
    @http.route('/api/mobile/products/search', type='json', auth='user', methods=['POST'])
    def mobile_search_product(self, **params):
        """Recherche produit par code-barres ou référence.
        
        Body JSON:
        {
            "barcode": "1234567890",
            "or": "reference": "ABC-001"
        }
        """
        try:
            barcode = params.get('barcode')
            reference = params.get('reference')
            
            domain = [('type', '=', 'product')]
            
            if barcode:
                domain.append(('barcode', '=', barcode))
            elif reference:
                domain.append(('default_code', '=', reference))
            else:
                return {'error': True, 'message': 'barcode ou reference requis'}
            
            product = request.env['product.product'].search(domain, limit=1)
            
            if not product:
                return {
                    'found': False,
                    'message': 'Produit introuvable',
                }
            
            return {
                'found': True,
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'code': product.default_code,
                    'barcode': product.barcode,
                    'uom': product.uom_id.name,
                    'uom_id': product.uom_id.id,
                    'standard_price': product.standard_price,
                    'tracking': product.tracking,
                    'image_url': f'/web/image/product.product/{product.id}/image_128' if product.image_128 else None,
                },
            }
            
        except Exception as e:
            _logger.error(f"Erreur recherche produit: {str(e)}", exc_info=True)
            return {'error': True, 'message': str(e)}
    
    @http.route('/api/mobile/inventory/add-line', type='json', auth='user', methods=['POST'])
    def mobile_add_line(self, **params):
        """Ajoute une ligne à un inventaire mobile.
        
        Body JSON:
        {
            "inventory_id": 42,
            "product_id": 89,
            "real_qty": 100,
            "photo_data": "data:image/jpeg;base64,..." (optionnel)
        }
        """
        try:
            inventory_id = params.get('inventory_id')
            product_id = params.get('product_id')
            real_qty = params.get('real_qty', 0)
            
            if not inventory_id or not product_id:
                return {'error': True, 'message': 'inventory_id et product_id requis'}
            
            inventory = request.env['stockex.stock.inventory'].browse(inventory_id)
            
            if not inventory.exists():
                return {'error': True, 'message': 'Inventaire introuvable'}
            
            # Vérifie si ligne existe déjà
            existing_line = request.env['stockex.stock.inventory.line'].search([
                ('inventory_id', '=', inventory_id),
                ('product_id', '=', product_id),
            ], limit=1)
            
            if existing_line:
                # Met à jour la quantité
                existing_line.write({'real_qty': real_qty})
                line = existing_line
            else:
                # Crée nouvelle ligne
                line = request.env['stockex.stock.inventory.line'].create({
                    'inventory_id': inventory_id,
                    'product_id': product_id,
                    'real_qty': real_qty,
                })
            
            # TODO: Gérer photo_data si fourni
            
            return {
                'success': True,
                'line': {
                    'id': line.id,
                    'product_name': line.product_id.name,
                    'theoretical_qty': line.theoretical_qty,
                    'real_qty': line.real_qty,
                    'difference': line.difference,
                },
            }
            
        except Exception as e:
            _logger.error(f"Erreur ajout ligne: {str(e)}", exc_info=True)
            return {'error': True, 'message': str(e)}
    
    @http.route('/api/mobile/inventory/<int:inventory_id>/lines', type='json', auth='user', methods=['GET'])
    def mobile_get_lines(self, inventory_id, **params):
        """Récupère les lignes d'un inventaire pour affichage mobile."""
        try:
            inventory = request.env['stockex.stock.inventory'].browse(inventory_id)
            
            if not inventory.exists():
                return {'error': True, 'message': 'Inventaire introuvable'}
            
            lines = [{
                'id': line.id,
                'product_id': line.product_id.id,
                'product_name': line.product_id.name,
                'product_code': line.product_id.default_code,
                'theoretical_qty': line.theoretical_qty,
                'real_qty': line.real_qty,
                'difference': line.difference,
                'uom': line.product_id.uom_id.name,
            } for line in inventory.inventory_line_ids]
            
            return {
                'success': True,
                'inventory': {
                    'id': inventory.id,
                    'name': inventory.name,
                    'state': inventory.state,
                    'total_lines': len(lines),
                },
                'lines': lines,
            }
            
        except Exception as e:
            _logger.error(f"Erreur récupération lignes: {str(e)}", exc_info=True)
            return {'error': True, 'message': str(e)}
    
    # ========== MANIFEST & SERVICE WORKER ==========
    
    @http.route('/stockex/manifest.json', type='http', auth='public')
    def manifest(self, **kwargs):
        """Retourne le manifest PWA."""
        manifest_path = get_module_path('stockex')
        manifest_file = os.path.join(manifest_path, 'static', 'manifest.json')
        
        try:
            with open(manifest_file, 'r') as f:
                manifest_data = f.read()
            
            return Response(
                manifest_data,
                content_type='application/manifest+json',
                headers={'Cache-Control': 'max-age=3600'},
            )
        except FileNotFoundError:
            # Manifest inline si fichier non trouvé
            manifest_json = {
                "name": "Stockex Mobile",
                "short_name": "Stockex",
                "start_url": "/stockex/mobile",
                "display": "standalone",
                "background_color": "#ffffff",
                "theme_color": "#00A09D",
                "icons": [
                    {
                        "src": "/stockex/static/img/icon-192x192.png",
                        "sizes": "192x192",
                        "type": "image/png"
                    }
                ]
            }
            
            return Response(
                json.dumps(manifest_json),
                content_type='application/manifest+json',
            )
    
    @http.route('/stockex/sw.js', type='http', auth='public')
    def service_worker(self, **kwargs):
        """Retourne le Service Worker JavaScript."""
        sw_path = get_module_path('stockex')
        sw_file = os.path.join(sw_path, 'static', 'src', 'js', 'service-worker.js')
        
        try:
            with open(sw_file, 'r') as f:
                sw_code = f.read()
            
            return Response(
                sw_code,
                content_type='application/javascript',
                headers={'Service-Worker-Allowed': '/stockex/'},
            )
        except FileNotFoundError:
            return Response(
                "// Service Worker not found",
                content_type='application/javascript',
                status=404,
            )
