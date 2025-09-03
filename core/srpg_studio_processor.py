"""
SRPG Studio processor
Handles SRPG Studio (.json, .js) game files
"""

import os
import re
import json
from typing import List, Tuple, Dict
import logging

class SRPGStudioProcessor:
    """Processor for SRPG Studio engine games"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def find_srpg_studio_files(self, directory: str) -> List[str]:
        """Find SRPG Studio data files"""
        srpg_files = []
        
        # SRPG Studio typically uses these file patterns
        target_patterns = [
            'mapinfo.json',
            'eventcommand.json', 
            'message.json',
            'stringtable.json',
            'scenario*.json',
            'event*.json',
            'data/*.json',
            'script/*.js'
        ]
        
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Check against patterns
                for pattern in target_patterns:
                    if '*' in pattern:
                        # Handle wildcard patterns
                        base_pattern = pattern.replace('*', '.*')
                        if re.match(base_pattern, os.path.relpath(file_path, directory).replace('\\', '/')):
                            if self._is_srpg_studio_file(file_path):
                                srpg_files.append(file_path)
                            break
                    else:
                        # Exact match
                        if file.lower() == pattern.lower():
                            if self._is_srpg_studio_file(file_path):
                                srpg_files.append(file_path)
                            break
        
        return sorted(srpg_files)
    
    def _is_srpg_studio_file(self, file_path: str) -> bool:
        """Check if file is SRPG Studio format"""
        try:
            if file_path.lower().endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check for SRPG Studio specific structure
                srpg_indicators = [
                    'mapdata', 'eventdata', 'messagedata',
                    'unitdata', 'classdata', 'itemdata',
                    'skilldata', 'weapondata', 'armordata'
                ]
                
                if isinstance(data, dict):
                    for key in data.keys():
                        if any(indicator in key.lower() for indicator in srpg_indicators):
                            return True
                
                if isinstance(data, list) and data:
                    # Check first item structure
                    first_item = data[0]
                    if isinstance(first_item, dict):
                        common_fields = ['id', 'name', 'description', 'message']
                        if any(field in first_item for field in common_fields):
                            return True
            
            elif file_path.lower().endswith('.js'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(500)  # Read first 500 chars
                
                # Check for SRPG Studio JavaScript patterns
                js_patterns = [
                    'SRPG', 'MapData', 'EventData', 'MessageData',
                    'Game_Unit', 'Game_Map', 'Scene_'
                ]
                
                for pattern in js_patterns:
                    if pattern in content:
                        return True
        
        except Exception:
            pass
        
        return False
    
    def extract_translatable_text(self, file_path: str) -> List[Tuple[str, str, str]]:
        """Extract translatable text from SRPG Studio files"""
        texts = []
        
        try:
            if file_path.lower().endswith('.json'):
                texts = self._process_json_file(file_path)
            elif file_path.lower().endswith('.js'):
                texts = self._process_js_file(file_path)
            
        except Exception as e:
            self.logger.error(f"Error processing SRPG Studio file {file_path}: {e}")
        
        return texts
    
    def _process_json_file(self, file_path: str) -> List[Tuple[str, str, str]]:
        """Process SRPG Studio JSON file"""
        texts = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Process different data structures
            if isinstance(data, dict):
                texts.extend(self._extract_from_dict(data, file_path))
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    if isinstance(item, dict):
                        item_texts = self._extract_from_dict(item, f"{file_path}[{i}]")
                        texts.extend(item_texts)
            
        except Exception as e:
            self.logger.error(f"Error processing JSON file {file_path}: {e}")
        
        return texts
    
    def _extract_from_dict(self, data: dict, context_prefix: str) -> List[Tuple[str, str, str]]:
        """Extract text from dictionary structure"""
        texts = []
        
        # Common text fields in SRPG Studio
        text_fields = [
            'name', 'description', 'message', 'text',
            'title', 'subtitle', 'content', 'dialogue',
            'option', 'choice', 'comment', 'note'
        ]
        
        def extract_recursive(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    if isinstance(value, str) and self._is_translatable_text(value):
                        # Determine text type based on field name
                        text_type = "dialogue"
                        if key.lower() in ['name', 'title']:
                            text_type = "name"
                        elif key.lower() in ['description', 'note', 'comment']:
                            text_type = "description"
                        elif key.lower() in ['option', 'choice']:
                            text_type = "choice"
                        
                        texts.append((value, f"{context_prefix}.{current_path}", text_type))
                    
                    elif isinstance(value, (dict, list)):
                        extract_recursive(value, current_path)
            
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    current_path = f"{path}[{i}]"
                    extract_recursive(item, current_path)
        
        extract_recursive(data)
        return texts
    
    def _process_js_file(self, file_path: str) -> List[Tuple[str, str, str]]:
        """Process SRPG Studio JavaScript file"""
        texts = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract strings from JavaScript
            # Look for quoted strings that contain Japanese text
            string_patterns = [
                r'"([^"]*)"',      # Double quoted strings
                r"'([^']*)'",      # Single quoted strings
                r'`([^`]*)`',      # Template literals
            ]
            
            line_num = 0
            for line in content.split('\n'):
                line_num += 1
                
                for pattern in string_patterns:
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        text = match.group(1)
                        if self._is_translatable_text(text):
                            texts.append((text, f"line_{line_num}", "code"))
            
        except Exception as e:
            self.logger.error(f"Error processing JS file {file_path}: {e}")
        
        return texts
    
    def _is_translatable_text(self, text: str) -> bool:
        """Check if text is worth translating"""
        if not text or len(text.strip()) < 2:
            return False
        
        # Check for Japanese characters
        japanese_pattern = r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]'
        if not re.search(japanese_pattern, text):
            return False
        
        # Filter out code-like strings
        code_patterns = [
            r'^[a-zA-Z_][a-zA-Z0-9_]*$',  # Variable names
            r'^\d+$',                     # Numbers only
            r'^[.\/\\]+$',               # Paths
            r'^#[0-9a-fA-F]+$',          # Hex colors
        ]
        
        for pattern in code_patterns:
            if re.match(pattern, text):
                return False
        
        # Filter out common system strings
        system_strings = [
            'true', 'false', 'null', 'undefined',
            'function', 'var', 'let', 'const',
            'if', 'else', 'for', 'while', 'return'
        ]
        
        if text.lower() in system_strings:
            return False
        
        return True
    
    def create_translation_file(self, texts: List[Tuple[str, str, str]], output_path: str):
        """Create translation file for SRPG Studio texts"""
        translation_data = []
        
        for original, context, text_type in texts:
            translation_data.append({
                'original': original,
                'translation': '',
                'context': context,
                'type': text_type,
                'notes': ''
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(translation_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Created SRPG Studio translation file: {output_path}")
    
    def apply_translations(self, original_file: str, translation_file: str, output_file: str):
        """Apply translations back to SRPG Studio files"""
        try:
            # Load translations
            with open(translation_file, 'r', encoding='utf-8') as f:
                translations = json.load(f)
            
            # Create translation dictionary
            trans_dict = {}
            for item in translations:
                if item['translation'].strip():
                    trans_dict[item['original']] = item['translation']
            
            if original_file.lower().endswith('.json'):
                self._apply_json_translations(original_file, trans_dict, output_file)
            elif original_file.lower().endswith('.js'):
                self._apply_js_translations(original_file, trans_dict, output_file)
            
        except Exception as e:
            self.logger.error(f"Error applying SRPG Studio translations: {e}")
    
    def _apply_json_translations(self, original_file: str, trans_dict: dict, output_file: str):
        """Apply translations to JSON file"""
        try:
            with open(original_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Recursively apply translations
            def translate_recursive(obj):
                if isinstance(obj, dict):
                    return {key: translate_recursive(value) for key, value in obj.items()}
                elif isinstance(obj, list):
                    return [translate_recursive(item) for item in obj]
                elif isinstance(obj, str) and obj in trans_dict:
                    return trans_dict[obj]
                else:
                    return obj
            
            translated_data = translate_recursive(data)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(translated_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Applied JSON translations to: {output_file}")
            
        except Exception as e:
            self.logger.error(f"Error applying JSON translations: {e}")
    
    def _apply_js_translations(self, original_file: str, trans_dict: dict, output_file: str):
        """Apply translations to JavaScript file"""
        try:
            with open(original_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Apply translations
            for original, translation in trans_dict.items():
                # Escape special regex characters
                escaped_original = re.escape(original)
                content = re.sub(escaped_original, translation, content)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"Applied JS translations to: {output_file}")
            
        except Exception as e:
            self.logger.error(f"Error applying JS translations: {e}")
