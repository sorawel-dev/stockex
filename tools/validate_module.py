#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de validation automatique du module Odoo Stockex
Détecte les erreurs avant l'installation pour gagner du temps
"""

import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict
import re

class Color:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class ModuleValidator:
    def __init__(self, module_path):
        self.module_path = Path(module_path)
        self.errors = []
        self.warnings = []
        self.info = []
        
        # Stockage des définitions
        self.defined_actions = set()
        self.defined_menus = set()
        self.defined_views = set()
        self.defined_models = set()
        
        # Stockage des références
        self.action_references = []
        self.menu_references = []
        self.view_references = []
        
        # Ordre de chargement
        self.load_order = []
        
    def log_error(self, file, line, message):
        self.errors.append({
            'file': file,
            'line': line,
            'message': message,
            'severity': 'ERROR'
        })
        
    def log_warning(self, file, line, message):
        self.warnings.append({
            'file': file,
            'line': line,
            'message': message,
            'severity': 'WARNING'
        })
        
    def log_info(self, message):
        self.info.append(message)
    
    def validate_xml_syntax(self, xml_file):
        """Valide la syntaxe XML"""
        try:
            ET.parse(xml_file)
            return True
        except ET.ParseError as e:
            self.log_error(
                str(xml_file.relative_to(self.module_path)),
                e.position[0] if hasattr(e, 'position') else 0,
                f"Erreur XML: {str(e)}"
            )
            return False
    
    def extract_definitions(self, xml_file):
        """Extrait les définitions (actions, menus, vues)"""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            for record in root.findall('.//record'):
                record_id = record.get('id')
                model = record.get('model')
                
                if record_id:
                    full_id = f"stockex.{record_id}"
                    
                    if model == 'ir.actions.act_window':
                        self.defined_actions.add(record_id)
                        self.defined_actions.add(full_id)
                    elif model == 'ir.ui.view':
                        self.defined_views.add(record_id)
                        self.defined_views.add(full_id)
            
            for menuitem in root.findall('.//menuitem'):
                menu_id = menuitem.get('id')
                if menu_id:
                    self.defined_menus.add(menu_id)
                    self.defined_menus.add(f"stockex.{menu_id}")
                    
        except Exception as e:
            self.log_warning(
                str(xml_file.relative_to(self.module_path)),
                0,
                f"Erreur extraction définitions: {str(e)}"
            )
    
    def extract_references(self, xml_file):
        """Extrait les références utilisées"""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Références aux actions dans les menus
            for menuitem in root.findall('.//menuitem'):
                action = menuitem.get('action')
                if action:
                    self.action_references.append({
                        'file': xml_file,
                        'action': action,
                        'type': 'menu'
                    })
            
            # Références aux vues (inherit_id)
            for record in root.findall('.//record[@model="ir.ui.view"]'):
                for field in record.findall('.//field[@name="inherit_id"]'):
                    ref = field.get('ref')
                    if ref:
                        self.view_references.append({
                            'file': xml_file,
                            'view': ref,
                            'type': 'inherit'
                        })
            
            # Actions dans boutons/liens %(action)d
            content = xml_file.read_text(encoding='utf-8')
            action_pattern = r'%\((\w+)\)d'
            for match in re.finditer(action_pattern, content):
                action_name = match.group(1)
                self.action_references.append({
                    'file': xml_file,
                    'action': action_name,
                    'type': 'button'
                })
                
        except Exception as e:
            self.log_warning(
                str(xml_file.relative_to(self.module_path)),
                0,
                f"Erreur extraction références: {str(e)}"
            )
    
    def validate_odoo18_syntax(self, xml_file):
        """Vérifie la syntaxe Odoo 18"""
        try:
            content = xml_file.read_text(encoding='utf-8')
            
            # Vérifier <tree> au lieu de <list>
            if '<tree' in content and 'inherit_id' not in content:
                line_num = content[:content.index('<tree')].count('\n') + 1
                self.log_error(
                    str(xml_file.relative_to(self.module_path)),
                    line_num,
                    "Utiliser <list> au lieu de <tree> pour Odoo 18"
                )
            
            # Vérifier xpath //tree
            if '//tree' in content:
                line_num = content[:content.index('//tree')].count('\n') + 1
                self.log_error(
                    str(xml_file.relative_to(self.module_path)),
                    line_num,
                    "Utiliser //list au lieu de //tree dans xpath pour Odoo 18"
                )
            
            # Vérifier boutons sans name
            tree = ET.parse(xml_file)
            root = tree.getroot()
            for button in root.findall('.//button[@type]'):
                if button.get('type') in ['action', 'object'] and not button.get('name'):
                    self.log_error(
                        str(xml_file.relative_to(self.module_path)),
                        0,
                        f"Bouton de type '{button.get('type')}' sans attribut 'name'"
                    )
                    
        except Exception as e:
            pass
    
    def check_load_order(self):
        """Vérifie l'ordre de chargement du manifest"""
        manifest_file = self.module_path / '__manifest__.py'
        if not manifest_file.exists():
            self.log_error('__manifest__.py', 0, "Fichier manifest introuvable")
            return
        
        try:
            content = manifest_file.read_text(encoding='utf-8')
            
            # Extraire l'ordre des fichiers data
            data_match = re.search(r"'data':\s*\[(.*?)\]", content, re.DOTALL)
            if data_match:
                data_section = data_match.group(1)
                file_pattern = r"'([^']+\.xml)'"
                
                self.load_order = re.findall(file_pattern, data_section)
                
                # Vérifier que les actions sont avant les menus
                action_files = [f for f in self.load_order if 'action' in f or 'dashboard' in f or 'report' in f]
                menu_index = next((i for i, f in enumerate(self.load_order) if 'menus.xml' in f), -1)
                
                if menu_index >= 0:
                    for action_file in action_files:
                        action_index = self.load_order.index(action_file)
                        if action_index > menu_index:
                            self.log_error(
                                '__manifest__.py',
                                0,
                                f"'{action_file}' devrait être chargé AVANT 'menus.xml'"
                            )
                            
        except Exception as e:
            self.log_error('__manifest__.py', 0, f"Erreur analyse manifest: {str(e)}")
    
    def validate_references(self):
        """Valide que toutes les références existent"""
        # Vérifier les actions
        for ref in self.action_references:
            action = ref['action']
            if action not in self.defined_actions and f"stockex.{action}" not in self.defined_actions:
                self.log_error(
                    str(ref['file'].relative_to(self.module_path)),
                    0,
                    f"Action '{action}' référencée mais non définie"
                )
        
        # Vérifier les vues
        for ref in self.view_references:
            view = ref['view']
            # Ignorer les refs externes (stock.*, base.*, etc.)
            if not view.startswith(('stock.', 'base.', 'product.', 'account.')):
                if view not in self.defined_views and f"stockex.{view}" not in self.defined_views:
                    self.log_error(
                        str(ref['file'].relative_to(self.module_path)),
                        0,
                        f"Vue '{view}' référencée mais non définie"
                    )
    
    def run(self):
        """Lance toutes les validations"""
        print(f"{Color.BOLD}{Color.CYAN}🔍 Validation du module Stockex...{Color.RESET}\n")
        
        # 1. Collecter tous les fichiers XML
        xml_files = list(self.module_path.rglob('*.xml'))
        xml_files = [f for f in xml_files if '__pycache__' not in str(f)]
        
        print(f"{Color.BLUE}📁 {len(xml_files)} fichiers XML trouvés{Color.RESET}\n")
        
        # 2. Première passe: validation syntaxe et extraction définitions
        print(f"{Color.YELLOW}⚙️  Phase 1: Validation syntaxe XML...{Color.RESET}")
        valid_files = []
        for xml_file in xml_files:
            if self.validate_xml_syntax(xml_file):
                valid_files.append(xml_file)
                self.extract_definitions(xml_file)
        
        print(f"   {Color.GREEN}✓{Color.RESET} {len(valid_files)}/{len(xml_files)} fichiers XML valides\n")
        
        # 3. Vérification syntaxe Odoo 18
        print(f"{Color.YELLOW}⚙️  Phase 2: Vérification syntaxe Odoo 18...{Color.RESET}")
        for xml_file in valid_files:
            self.validate_odoo18_syntax(xml_file)
        print(f"   {Color.GREEN}✓{Color.RESET} Vérification terminée\n")
        
        # 4. Extraction références
        print(f"{Color.YELLOW}⚙️  Phase 3: Extraction des références...{Color.RESET}")
        for xml_file in valid_files:
            self.extract_references(xml_file)
        
        print(f"   {Color.GREEN}✓{Color.RESET} {len(self.defined_actions)} actions définies")
        print(f"   {Color.GREEN}✓{Color.RESET} {len(self.defined_views)} vues définies")
        print(f"   {Color.GREEN}✓{Color.RESET} {len(self.defined_menus)} menus définis\n")
        
        # 5. Vérification ordre de chargement
        print(f"{Color.YELLOW}⚙️  Phase 4: Vérification ordre de chargement...{Color.RESET}")
        self.check_load_order()
        print(f"   {Color.GREEN}✓{Color.RESET} Ordre vérifié\n")
        
        # 6. Validation références
        print(f"{Color.YELLOW}⚙️  Phase 5: Validation des références...{Color.RESET}")
        self.validate_references()
        print(f"   {Color.GREEN}✓{Color.RESET} Références vérifiées\n")
        
        # 7. Affichage résultats
        self.print_results()
        
        return len(self.errors) == 0
    
    def print_results(self):
        """Affiche le rapport final"""
        print(f"\n{Color.BOLD}{'='*70}{Color.RESET}")
        print(f"{Color.BOLD}{Color.CYAN}📊 RAPPORT DE VALIDATION{Color.RESET}")
        print(f"{Color.BOLD}{'='*70}{Color.RESET}\n")
        
        # Erreurs
        if self.errors:
            print(f"{Color.BOLD}{Color.RED}❌ ERREURS ({len(self.errors)}){Color.RESET}\n")
            for i, error in enumerate(self.errors, 1):
                print(f"{Color.RED}  {i}. {error['file']}:{error['line']}{Color.RESET}")
                print(f"     {error['message']}\n")
        else:
            print(f"{Color.BOLD}{Color.GREEN}✅ Aucune erreur trouvée{Color.RESET}\n")
        
        # Avertissements
        if self.warnings:
            print(f"{Color.BOLD}{Color.YELLOW}⚠️  AVERTISSEMENTS ({len(self.warnings)}){Color.RESET}\n")
            for i, warning in enumerate(self.warnings, 1):
                print(f"{Color.YELLOW}  {i}. {warning['file']}:{warning['line']}{Color.RESET}")
                print(f"     {warning['message']}\n")
        
        # Résumé
        print(f"{Color.BOLD}{'='*70}{Color.RESET}")
        if len(self.errors) == 0:
            print(f"{Color.BOLD}{Color.GREEN}✅ MODULE PRÊT POUR L'INSTALLATION !{Color.RESET}")
        else:
            print(f"{Color.BOLD}{Color.RED}❌ CORRIGEZ LES ERREURS AVANT D'INSTALLER{Color.RESET}")
        print(f"{Color.BOLD}{'='*70}{Color.RESET}\n")

if __name__ == '__main__':
    module_path = Path(__file__).parent.parent
    validator = ModuleValidator(module_path)
    
    success = validator.run()
    sys.exit(0 if success else 1)
