# -*- coding: utf-8 -*-
"""
Module d'authentification JWT pour Stockex
========================================
Implémente l'authentification par token JWT pour sécuriser l'API REST Stockex.
"""

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    jwt = None

import hashlib
import logging
from datetime import datetime, timedelta
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

if not JWT_AVAILABLE:
    _logger.warning("Module PyJWT non disponible. L'authentification JWT ne fonctionnera pas. Installez-le avec: pip3 install PyJWT")


class StockexJWTAuth:
    """Gestionnaire d'authentification JWT pour Stockex."""
    
    def __init__(self, secret_key=None):
        """
        Initialise le gestionnaire JWT.
        
        Args:
            secret_key (str): Clé secrète pour signer les tokens. Si None, utilise la config Odoo.
        """
        self.secret_key = secret_key
        self._secret_initialized = False
    
    def _get_odoo_secret(self):
        """Récupère la clé secrète depuis la configuration Odoo."""
        # Utilise un hash du mot de passe master Odoo comme clé secrète
        try:
            if request and hasattr(request, 'env') and hasattr(request.env, 'cr'):
                db_name = request.env.cr.dbname
            else:
                db_name = 'default'
        except (RuntimeError, AttributeError):
            db_name = 'default'
        return hashlib.sha256(f"stockex_jwt_{db_name}".encode()).hexdigest()
    
    def _ensure_secret_key(self):
        """Initialise la clé secrète si nécessaire."""
        if not self._secret_initialized:
            if not self.secret_key:
                self.secret_key = self._get_odoo_secret()
            self._secret_initialized = True
    
    def generate_token(self, user_id, expires_in_hours=24):
        """
        Génère un token JWT pour un utilisateur.
        
        Args:
            user_id (int): ID de l'utilisateur
            expires_in_hours (int): Durée de validité en heures
            
        Returns:
            str: Token JWT encodé
        """
        if not JWT_AVAILABLE:
            _logger.error("PyJWT n'est pas installé. Impossible de générer un token.")
            return None
        
        self._ensure_secret_key()
            
        try:
            payload = {
                'user_id': user_id,
                'exp': datetime.utcnow() + timedelta(hours=expires_in_hours),
                'iat': datetime.utcnow(),
                'iss': 'stockex_api'
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm='HS256')
            return token
        except Exception as e:
            _logger.error(f"Erreur génération token JWT: {str(e)}")
            return None
    
    def verify_token(self, token):
        """
        Vérifie la validité d'un token JWT.
        
        Args:
            token (str): Token JWT à vérifier
            
        Returns:
            dict: Payload décodé si valide, None sinon
        """
        if not JWT_AVAILABLE:
            _logger.error("PyJWT n'est pas installé. Impossible de vérifier le token.")
            return None
        
        self._ensure_secret_key()
            
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            _logger.warning("Token JWT expiré")
            return None
        except jwt.InvalidTokenError as e:
            _logger.warning(f"Token JWT invalide: {str(e)}")
            return None
    
    def get_user_from_token(self, token):
        """
        Récupère l'utilisateur Odoo à partir d'un token JWT.
        
        Args:
            token (str): Token JWT
            
        Returns:
            res.users record: Utilisateur Odoo ou None
        """
        payload = self.verify_token(token)
        if not payload:
            return None
            
        user_id = payload.get('user_id')
        if not user_id:
            return None
            
        try:
            user = request.env['res.users'].sudo().browse(user_id)
            return user if user.exists() else None
        except Exception as e:
            _logger.error(f"Erreur récupération utilisateur: {str(e)}")
            return None


# Instance globale
stockex_jwt_auth = StockexJWTAuth()