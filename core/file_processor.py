"""
File Processor for RPG Maker MV/MZ JSON files
Handles extraction and application of translatable text
"""

import json
import os
import re
from typing import Dict, List, Any, Union, Set


class FileProcessor:
    """Processes RPG Maker JSON files for translation"""
    
    def __init__(self):
        # Patterns for Japanese text detection
        self.japanese_pattern = re.compile(r'[\\u3040-\\u309f\\u30a0-\\u30ff\\u4e00-\\u9faf]')
        
        # Text fields that commonly contain translatable content
        self.translatable_fields = {
            'name',           # Character names
            'nickname',       # Character nicknames  
            'description',    # Item descriptions
            'message',        # Dialog messages
            'note',           # Notes
            'text',           # General text
            'title',          # Titles
            'displayName',    # Display names
            'content',        # Content
            'label',          # Labels
            'tooltip'         # Tooltips
        }
        
        # Event command codes that contain text
        self.text_command_codes = {
            101,  # Show Text
            102,  # Show Choices
            103,  # Input Number
            104,  # Select Item
            105,  # Show Scrolling Text
            108,  # Comment
            111,  # Conditional Branch (text)
            117,  # Common Event
            118,  # Label
            119,  # Jump to Label
            122,  # Control Variables (text)
            355,  # Script (sometimes contains text)
            356,  # Script (continued)
        }
    
    def needs_translation(self, data: Any) -> bool:
        """Check if the file contains translatable Japanese text"""
        return self._contains_japanese_text(data)
    
    def _contains_japanese_text(self, obj: Any) -> bool:
        """Recursively check if object contains Japanese text"""
        if isinstance(obj, str):
            return bool(self.japanese_pattern.search(obj))
        elif isinstance(obj, dict):
            return any(self._contains_japanese_text(value) for value in obj.values())
        elif isinstance(obj, list):
            return any(self._contains_japanese_text(item) for item in obj)
        return False
    
    def extract_translatable_text(self, data: Any) -> List[str]:
        """Extract all translatable text from the data structure"""
        texts = []
        self._extract_text_recursive(data, texts)
        
        # Remove duplicates while preserving order
        unique_texts = []
        seen = set()
        for text in texts:
            if text not in seen and text.strip():
                unique_texts.append(text)
                seen.add(text)
        
        return unique_texts
    
    def _extract_text_recursive(self, obj: Any, texts: List[str], path: str = ""):
        """Recursively extract translatable text"""
        if isinstance(obj, str):
            if self.japanese_pattern.search(obj):
                texts.append(obj)
        
        elif isinstance(obj, dict):
            # Handle RPG Maker event lists
            if 'list' in obj and isinstance(obj['list'], list):
                self._extract_from_event_list(obj['list'], texts)
            
            # Handle regular dictionary fields
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                
                # Check if this is a translatable field
                if key.lower() in self.translatable_fields:
                    if isinstance(value, str) and self.japanese_pattern.search(value):
                        texts.append(value)
                else:
                    self._extract_text_recursive(value, texts, current_path)
        
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                current_path = f"{path}[{i}]" if path else f"[{i}]"
                self._extract_text_recursive(item, texts, current_path)
    
    def _extract_from_event_list(self, event_list: List[Dict[str, Any]], texts: List[str]):
        """Extract text from RPG Maker event command list"""
        for event in event_list:
            if not isinstance(event, dict):
                continue
            
            code = event.get('code', 0)
            parameters = event.get('parameters', [])
            
            # Handle different event command types
            if code in self.text_command_codes:
                for param in parameters:
                    if isinstance(param, str) and self.japanese_pattern.search(param):
                        texts.append(param)
                    elif isinstance(param, list):
                        # Handle nested parameter lists
                        for sub_param in param:
                            if isinstance(sub_param, str) and self.japanese_pattern.search(sub_param):
                                texts.append(sub_param)
    
    def apply_translations(self, data: Any, translations: Dict[str, str]) -> Any:
        """Apply translations back to the data structure"""
        # Create a mapping from original to translated text
        original_texts = self.extract_translatable_text(data)
        translation_map = {}
        
        # Map original texts to translations
        for i, original in enumerate(original_texts):
            if i < len(translations):
                translation_map[original] = translations[i]
        
        # Apply translations
        return self._apply_translations_recursive(data, translation_map)
    
    def _apply_translations_recursive(self, obj: Any, translation_map: Dict[str, str]) -> Any:
        """Recursively apply translations to data structure"""
        if isinstance(obj, str):
            return translation_map.get(obj, obj)
        
        elif isinstance(obj, dict):
            result = {}
            for key, value in obj.items():
                if key.lower() in self.translatable_fields and isinstance(value, str):
                    result[key] = translation_map.get(value, value)
                else:
                    result[key] = self._apply_translations_recursive(value, translation_map)
            return result
        
        elif isinstance(obj, list):
            return [self._apply_translations_recursive(item, translation_map) for item in obj]
        
        else:
            return obj
    
    def detect_encoding(self, file_path: str) -> str:
        """Detect file encoding"""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                # Simple encoding detection without chardet dependency
                try:
                    raw_data.decode('utf-8')
                    return 'utf-8'
                except UnicodeDecodeError:
                    try:
                        raw_data.decode('shift-jis')
                        return 'shift-jis'
                    except UnicodeDecodeError:
                        return 'utf-8'  # Default fallback
        except Exception:
            return 'utf-8'
    
    def load_json_file(self, file_path: str) -> Dict[str, Any]:
        """Load JSON file with proper encoding detection"""
        encoding = self.detect_encoding(file_path)
        
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return json.load(f)
        except UnicodeDecodeError:
            # Fallback to utf-8 if detected encoding fails
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    def save_json_file(self, file_path: str, data: Dict[str, Any]):
        """Save JSON file with proper formatting"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def create_backup(self, file_path: str) -> str:
        """Create backup of original file"""
        backup_path = f"{file_path}.backup"
        
        try:
            import shutil
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception as e:
            raise Exception(f"Failed to create backup: {str(e)}")
    
    def validate_json_structure(self, data: Any) -> tuple[bool, str]:
        """Validate JSON structure for RPG Maker compatibility"""
        try:
            # Basic structure validation
            if not isinstance(data, (dict, list)):
                return False, "Invalid JSON structure: must be object or array"
            
            # Check for common RPG Maker fields
            if isinstance(data, dict):
                # Check if it looks like a map file
                if 'data' in data and 'events' in data:
                    if not isinstance(data['data'], list):
                        return False, "Map data must be an array"
                    if not isinstance(data['events'], list):
                        return False, "Map events must be an array"
            
            return True, "JSON structure is valid"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def get_file_stats(self, file_path: str) -> Dict[str, Any]:
        """Get statistics about a JSON file"""
        try:
            data = self.load_json_file(file_path)
            texts = self.extract_translatable_text(data)
            
            japanese_texts = [text for text in texts if self.japanese_pattern.search(text)]
            
            return {
                'total_text_entries': len(texts),
                'japanese_text_entries': len(japanese_texts),
                'needs_translation': len(japanese_texts) > 0,
                'file_size': os.path.getsize(file_path),
                'estimated_tokens': sum(len(text) // 4 for text in japanese_texts)
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'needs_translation': False
            }
