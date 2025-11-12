# -*- coding: utf-8 -*-
"""
API REST pour Module Stockex
============================
Fournit des endpoints REST pour l'accès externe aux fonctionnalités d'inventaire.

Endpoints disponibles:
- GET    /api/stockex/inventories - Liste des inventaires
- GET    /api/stockex/inventories/<id> - Détail d'un inventaire
- POST   /api/stockex/inventories - Créer un inventaire
- PUT    /api/stockex/inventories/<id> - Modifier un inventaire
- DELETE /api/stockex/inventories/<id> - Supprimer un inventaire
- GET    /api/stockex/products - Liste des produits
- GET    /api/stockex/locations - Liste des emplacements
"""

import json
import logging
from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


class StockexAPIController(http.Controller):
    """Contrôleur API REST pour Stockex."""
    
    def _get_user_from_token(self, token):
        """Valide le token API et retourne l'utilisateur."""
        # TODO: Implémenter validation JWT/OAuth2
        # Pour l'instant, utilise la session Odoo standard
        return request.env.user
    
    def _json_response(self, data, status=200):
        """Retourne une réponse JSON formatée."""
        return Response(
            json.dumps(data, default=str, ensure_ascii=False),
            status=status,
            mimetype='application/json',
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            }
        )
    
    def _error_response(self, message, status=400):
        """Retourne une réponse d'erreur JSON."""
        return self._json_response({
            'error': True,
            'message': message
        }, status=status)
    
    # ========== INVENTAIRES ==========
    
    @http.route('/api/stockex/inventories', type='http', auth='user', methods=['GET'], csrf=False)
    def list_inventories(self, **params):
        """Liste tous les inventaires avec filtres optionnels.
        
        Params:
            - state: Filtrer par état (draft, in_progress, etc.)
            - location_id: Filtrer par emplacement
            - date_from: Date début (YYYY-MM-DD)
            - date_to: Date fin (YYYY-MM-DD)
            - limit: Nombre max de résultats (défaut: 100)
            - offset: Décalage pour pagination (défaut: 0)
        """
        try:
            domain = []
            
            if params.get('state'):
                domain.append(('state', '=', params['state']))
            
            if params.get('location_id'):
                domain.append(('location_id', '=', int(params['location_id'])))
            
            if params.get('date_from'):
                domain.append(('date', '>=', params['date_from']))
            
            if params.get('date_to'):
                domain.append(('date', '<=', params['date_to']))
            
            limit = int(params.get('limit', 100))
            offset = int(params.get('offset', 0))
            
            inventories = request.env['stockex.stock.inventory'].search(
                domain,
                limit=limit,
                offset=offset,
                order='date desc'
            )
            
            data = {
                'total': request.env['stockex.stock.inventory'].search_count(domain),
                'limit': limit,
                'offset': offset,
                'inventories': [{
                    'id': inv.id,
                    'name': inv.name,
                    'date': inv.date.isoformat() if inv.date else None,
                    'location_id': inv.location_id.id,
                    'location_name': inv.location_id.complete_name,
                    'state': inv.state,
                    'state_display': dict(inv._fields['state'].selection).get(inv.state),
                    'total_lines': len(inv.inventory_line_ids),
                    'total_difference_value': inv.total_difference_value,
                    'user_id': inv.user_id.id,
                    'user_name': inv.user_id.name,
                } for inv in inventories]
            }
            
            return self._json_response(data)
            
        except Exception as e:
            _logger.error(f"Erreur API list_inventories: {str(e)}", exc_info=True)
            return self._error_response(str(e), status=500)
    
    @http.route('/api/stockex/inventories/<int:inventory_id>', type='http', auth='user', methods=['GET'], csrf=False)
    def get_inventory(self, inventory_id, **params):
        """Récupère les détails d'un inventaire spécifique.
        
        Params:
            - include_lines: Inclure les lignes (true/false, défaut: true)
        """
        try:
            inventory = request.env['stockex.stock.inventory'].browse(inventory_id)
            
            if not inventory.exists():
                return self._error_response("Inventaire introuvable", status=404)
            
            include_lines = params.get('include_lines', 'true').lower() == 'true'
            
            data = {
                'id': inventory.id,
                'name': inventory.name,
                'date': inventory.date.isoformat() if inventory.date else None,
                'location_id': inventory.location_id.id,
                'location_name': inventory.location_id.complete_name,
                'state': inventory.state,
                'state_display': dict(inventory._fields['state'].selection).get(inventory.state),
                'total_lines': len(inventory.inventory_line_ids),
                'total_difference_value': inventory.total_difference_value,
                'user_id': inventory.user_id.id,
                'user_name': inventory.user_id.name,
                'company_id': inventory.company_id.id,
                'company_name': inventory.company_id.name,
            }
            
            if include_lines:
                data['lines'] = [{
                    'id': line.id,
                    'product_id': line.product_id.id,
                    'product_code': line.product_id.default_code,
                    'product_name': line.product_id.name,
                    'theoretical_qty': line.theoretical_qty,
                    'real_qty': line.real_qty,
                    'difference': line.difference,
                    'standard_price': line.standard_price,
                    'difference_value': line.difference_value,
                    'state': line.state,
                } for line in inventory.inventory_line_ids]
            
            return self._json_response(data)
            
        except Exception as e:
            _logger.error(f"Erreur API get_inventory: {str(e)}", exc_info=True)
            return self._error_response(str(e), status=500)
    
    @http.route('/api/stockex/inventories', type='json', auth='user', methods=['POST'], csrf=False)
    def create_inventory(self, **params):
        """Crée un nouvel inventaire.
        
        Body JSON:
        {
            "location_id": 1,
            "date": "2025-10-28",
            "lines": [
                {
                    "product_id": 10,
                    "real_qty": 100
                }
            ]
        }
        """
        try:
            # Validation
            if not params.get('location_id'):
                return {'error': True, 'message': 'location_id requis'}
            
            # Création inventaire
            inventory_vals = {
                'location_id': params['location_id'],
                'date': params.get('date'),
            }
            
            inventory = request.env['stockex.stock.inventory'].create(inventory_vals)
            
            # Ajout des lignes si fournies
            if params.get('lines'):
                for line_data in params['lines']:
                    request.env['stockex.stock.inventory.line'].create({
                        'inventory_id': inventory.id,
                        'product_id': line_data['product_id'],
                        'real_qty': line_data.get('real_qty', 0),
                    })
            
            return {
                'success': True,
                'inventory_id': inventory.id,
                'name': inventory.name,
            }
            
        except Exception as e:
            _logger.error(f"Erreur API create_inventory: {str(e)}", exc_info=True)
            return {'error': True, 'message': str(e)}
    
    # ========== PRODUITS ==========
    
    @http.route('/api/stockex/products', type='http', auth='user', methods=['GET'], csrf=False)
    def list_products(self, **params):
        """Liste les produits stockables.
        
        Params:
            - search: Recherche par nom ou code
            - category_id: Filtrer par catégorie
            - limit: Nombre max (défaut: 100)
        """
        try:
            domain = [('type', '=', 'product')]
            
            if params.get('search'):
                search = params['search']
                domain.append('|')
                domain.append(('name', 'ilike', search))
                domain.append(('default_code', 'ilike', search))
            
            if params.get('category_id'):
                domain.append(('categ_id', '=', int(params['category_id'])))
            
            limit = int(params.get('limit', 100))
            
            products = request.env['product.product'].search(domain, limit=limit)
            
            data = {
                'total': request.env['product.product'].search_count(domain),
                'products': [{
                    'id': p.id,
                    'code': p.default_code,
                    'name': p.name,
                    'category_id': p.categ_id.id,
                    'category_name': p.categ_id.name,
                    'uom_id': p.uom_id.id,
                    'uom_name': p.uom_id.name,
                    'standard_price': p.standard_price,
                    'barcode': p.barcode,
                } for p in products]
            }
            
            return self._json_response(data)
            
        except Exception as e:
            _logger.error(f"Erreur API list_products: {str(e)}", exc_info=True)
            return self._error_response(str(e), status=500)
    
    # ========== EMPLACEMENTS ==========
    
    @http.route('/api/stockex/locations', type='http', auth='user', methods=['GET'], csrf=False)
    def list_locations(self, **params):
        """Liste les emplacements internes.
        
        Params:
            - warehouse_id: Filtrer par entrepôt
        """
        try:
            domain = [('usage', '=', 'internal')]
            
            if params.get('warehouse_id'):
                warehouse = request.env['stock.warehouse'].browse(int(params['warehouse_id']))
                domain.append(('id', 'child_of', warehouse.view_location_id.id))
            
            locations = request.env['stock.location'].search(domain)
            
            data = {
                'total': len(locations),
                'locations': [{
                    'id': loc.id,
                    'name': loc.name,
                    'complete_name': loc.complete_name,
                    'barcode': loc.barcode,
                    'parent_id': loc.location_id.id if loc.location_id else None,
                } for loc in locations]
            }
            
            return self._json_response(data)
            
        except Exception as e:
            _logger.error(f"Erreur API list_locations: {str(e)}", exc_info=True)
            return self._error_response(str(e), status=500)
    
    # ========== KPIs & ANALYTICS ==========
    
    @http.route('/api/stockex/kpis', type='http', auth='user', methods=['GET'], csrf=False)
    def get_kpis(self, **params):
        """Récupère les KPIs globaux du module.
        
        Params:
            - period: Période (today, week, month, year)
        """
        try:
            summary_model = request.env['stockex.inventory.summary']
            
            # Récupérer l'enregistrement par défaut
            summary = summary_model.search([], limit=1)
            if not summary:
                summary = summary_model.create({})
            
            # Récupération KPIs depuis le summary
            kpis = {
                'total_inventories': summary.total_inventories,
                'total_inventories_done': summary.total_inventories_done,
                'total_products': summary.total_products_all,
                'total_quantity': summary.total_quantity_all,
                'total_value': summary.total_value_all,
                'current_stock_value': summary.current_stock_value,
            }
            
            return self._json_response(kpis)
            
        except Exception as e:
            _logger.error(f"Erreur API get_kpis: {str(e)}", exc_info=True)
            return self._error_response(str(e), status=500)
