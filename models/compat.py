# -*- coding: utf-8 -*-

"""
Module de Compatibilité Odoo 18/19
===================================

Ce module gère les différences potentielles entre Odoo 18 et Odoo 19
pour assurer une compatibilité transparente.
"""

import logging
from odoo import release

_logger = logging.getLogger(__name__)

# Détection de la version d'Odoo
ODOO_VERSION = release.version_info[0]
ODOO_VERSION_FULL = '.'.join(map(str, release.version_info[:2]))

IS_ODOO_18 = ODOO_VERSION == 18
IS_ODOO_19 = ODOO_VERSION >= 19

_logger.info(f"Stockex: Détection version Odoo {ODOO_VERSION_FULL}")


def get_compatible_widget(widget_name):
    """
    Retourne le nom du widget compatible avec la version d'Odoo.
    
    Args:
        widget_name (str): Nom du widget demandé
        
    Returns:
        str: Nom du widget compatible
    """
    # Pour l'instant, les widgets sont identiques entre 18 et 19
    # Cette fonction est prête pour d'éventuelles adaptations futures
    
    if IS_ODOO_19 and widget_name in ['statusbar', 'badge']:
        # Si Odoo 19 change les noms de widgets, adapter ici
        return widget_name
    
    return widget_name


def get_compatible_field_type(field_type):
    """
    Retourne le type de champ compatible avec la version d'Odoo.
    
    Args:
        field_type (str): Type de champ demandé
        
    Returns:
        str: Type de champ compatible
    """
    # Les types de champs sont identiques entre 18 et 19
    # Cette fonction est prête pour d'éventuelles adaptations futures
    return field_type


def check_module_compatibility(module_name):
    """
    Vérifie si un module est compatible avec la version d'Odoo.
    
    Args:
        module_name (str): Nom du module à vérifier
        
    Returns:
        bool: True si compatible, False sinon
    """
    # Modules requis pour Stockex
    required_modules = {
        'base': True,  # Toujours présent
        'mail': True,  # Toujours présent
        'stock': True,  # Module standard
        'product': True,  # Module standard
        'account': True,  # Module standard
    }
    
    return required_modules.get(module_name, True)


def get_python_dependencies():
    """
    Retourne la liste des dépendances Python par version.
    
    Returns:
        list: Liste des packages Python requis
    """
    dependencies = [
        'openpyxl',  # Import Excel
        'python-barcode',  # Génération codes-barres
    ]
    
    optional_dependencies = [
        'requests',  # Pour Kobo Collect (optionnel)
    ]
    
    return {
        'required': dependencies,
        'optional': optional_dependencies
    }


def check_python_dependencies():
    """
    Vérifie que toutes les dépendances Python sont installées.
    
    Returns:
        dict: Statut des dépendances
    """
    deps = get_python_dependencies()
    status = {
        'required': {},
        'optional': {}
    }
    
    # Vérifier dépendances requises
    for dep in deps['required']:
        try:
            if dep == 'python-barcode':
                __import__('barcode')
            else:
                __import__(dep)
            status['required'][dep] = True
        except ImportError:
            status['required'][dep] = False
            _logger.warning(f"Dépendance requise manquante: {dep}")
    
    # Vérifier dépendances optionnelles
    for dep in deps['optional']:
        try:
            __import__(dep)
            status['optional'][dep] = True
        except ImportError:
            status['optional'][dep] = False
            _logger.info(f"Dépendance optionnelle non installée: {dep}")
    
    return status


def log_compatibility_info():
    """
    Enregistre les informations de compatibilité dans les logs.
    """
    _logger.info("="*60)
    _logger.info("Stockex - Informations de Compatibilité")
    _logger.info("="*60)
    _logger.info(f"Version Odoo détectée: {ODOO_VERSION_FULL}")
    _logger.info(f"Odoo 18: {IS_ODOO_18}")
    _logger.info(f"Odoo 19: {IS_ODOO_19}")
    
    # Vérifier dépendances Python
    deps_status = check_python_dependencies()
    
    _logger.info("-"*60)
    _logger.info("Dépendances Python Requises:")
    for dep, installed in deps_status['required'].items():
        status = "✅ OK" if installed else "❌ MANQUANT"
        _logger.info(f"  {dep}: {status}")
    
    _logger.info("-"*60)
    _logger.info("Dépendances Python Optionnelles:")
    for dep, installed in deps_status['optional'].items():
        status = "✅ Installé" if installed else "⚠️ Non installé"
        _logger.info(f"  {dep}: {status}")
    
    _logger.info("="*60)
    
    # Vérifier si toutes les dépendances requises sont présentes
    all_required_ok = all(deps_status['required'].values())
    if not all_required_ok:
        _logger.warning(
            "⚠️ ATTENTION: Certaines dépendances requises sont manquantes. "
            "Le module peut ne pas fonctionner correctement."
        )
    else:
        _logger.info("✅ Toutes les dépendances requises sont installées.")
    
    return all_required_ok


# Exécuter la vérification au chargement du module
if __name__ != '__main__':
    log_compatibility_info()
