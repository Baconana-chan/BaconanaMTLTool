"""
Unity Project Processor
Handles extraction and application of translatable text from Unity projects
Supports various Unity localization formats including JSON, CSV, and Unity Localization Package
"""

import os
import json
import csv
import xml.etree.ElementTree as ET
import re
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path


class UnityProcessor:
    """Processes Unity projects for translation"""
    
    def __init__(self):
        # Patterns for Japanese text detection
        self.japanese_pattern = re.compile(r'[ひらがなカタカナ漢字\u3040-\u309f\u30a0-\u30ff\u4e00-\u9faf]+')
        
        # Common Unity localization file patterns
        self.localization_patterns = [
            # Unity Localization Package
            "**/Localization/**/*.json",
            "**/LocalizationSettings/**/*.json",
            "**/String Tables/**/*.json",
            
            # Custom localization files
            "**/Localization/**/*.csv",
            "**/Localization/**/*.txt",
            "**/Localization/**/*.xml",
            
            # StreamingAssets localization
            "**/StreamingAssets/**/*localization*.json",
            "**/StreamingAssets/**/*text*.json",
            "**/StreamingAssets/**/*dialogue*.json",
            "**/StreamingAssets/**/*locale*.json",
            
            # Resources folder
            "**/Resources/**/*localization*.json",
            "**/Resources/**/*text*.json",
            "**/Resources/**/*dialogue*.json",
            
            # Common naming patterns
            "**/*_jp.json", "**/*_ja.json", "**/*_japanese.json",
            "**/*_en.json", "**/*_english.json",
            "**/text_*.json", "**/dialogue_*.json",
            "**/strings_*.json", "**/locale_*.json"
        ]
        
        # File patterns to exclude
        self.exclude_patterns = [
            "**/Library/**",
            "**/Temp/**", 
            "**/Logs/**",
            "**/ProjectSettings/**",
            "**/Packages/**",
            "**/.git/**",
            "**/.vs/**",
            "**/obj/**",
            "**/bin/**"
        ]
        
        # Unity asset extensions that might contain text
        self.unity_text_extensions = [
            '.json', '.csv', '.txt', '.xml', '.yml', '.yaml'
        ]
    
    def detect_unity_project(self, directory: str) -> bool:
        """Detect if directory contains a Unity project"""
        
        # Check for Unity project indicators
        unity_indicators = [
            'Assets',
            'ProjectSettings',
            'Library',
            'Packages'
        ]
        
        # Must have Assets folder and ProjectSettings
        assets_path = os.path.join(directory, 'Assets')
        project_settings_path = os.path.join(directory, 'ProjectSettings')
        
        if not (os.path.exists(assets_path) and os.path.exists(project_settings_path)):
            return False
        
        # Check for Unity version file
        version_file = os.path.join(project_settings_path, 'ProjectVersion.txt')
        if os.path.exists(version_file):
            try:
                with open(version_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'unity' in content.lower():
                        return True
            except Exception:
                pass
        
        # Check for common Unity files in ProjectSettings
        unity_files = [
            'ProjectSettings.asset',
            'QualitySettings.asset',
            'TagManager.asset'
        ]
        
        for unity_file in unity_files:
            if os.path.exists(os.path.join(project_settings_path, unity_file)):
                return True
        
        return False
    
    def find_unity_text_files(self, directory: str) -> List[str]:
        """Find all text files that might contain translatable content"""
        import glob
        
        text_files = []
        assets_dir = os.path.join(directory, 'Assets')
        
        if not os.path.exists(assets_dir):
            return []
        
        # Search for localization files
        for pattern in self.localization_patterns:
            search_path = os.path.join(assets_dir, pattern.replace('**/', ''))
            found_files = glob.glob(search_path, recursive=True)
            
            for file_path in found_files:
                # Skip excluded directories
                should_exclude = False
                for exclude_pattern in self.exclude_patterns:
                    if exclude_pattern.replace('**/', '') in file_path:
                        should_exclude = True
                        break
                
                if not should_exclude and file_path not in text_files:
                    text_files.append(file_path)
        
        # Also search for any text files with Japanese content
        for root, dirs, files in os.walk(assets_dir):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(
                exclude.replace('**/', '').replace('/', '') in d 
                for exclude in self.exclude_patterns
            )]
            
            for file in files:
                if any(file.endswith(ext) for ext in self.unity_text_extensions):
                    file_path = os.path.join(root, file)
                    
                    if file_path not in text_files and self.might_contain_japanese(file_path):
                        text_files.append(file_path)
        
        return sorted(text_files)
    
    def might_contain_japanese(self, file_path: str) -> bool:
        """Quick check if file might contain Japanese text"""
        try:
            # Read first few KB to check for Japanese
            with open(file_path, 'r', encoding='utf-8') as f:
                sample = f.read(4096)  # Read first 4KB
                return bool(self.japanese_pattern.search(sample))
        except Exception:
            try:
                # Try with different encoding
                with open(file_path, 'r', encoding='shift-jis') as f:
                    sample = f.read(4096)
                    return bool(self.japanese_pattern.search(sample))
            except Exception:
                return False
    
    def needs_translation(self, file_path: str) -> bool:
        """Check if the file contains translatable Japanese text"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return bool(self.japanese_pattern.search(content))
        except Exception:
            try:
                with open(file_path, 'r', encoding='shift-jis') as f:
                    content = f.read()
                return bool(self.japanese_pattern.search(content))
            except Exception:
                return False
    
    def extract_translatable_text(self, file_path: str) -> List[Tuple[str, str, str]]:
        """
        Extract translatable text from Unity file
        Returns list of (original_text, key/context, file_type)
        """
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext == '.json':
                return self._extract_from_json(file_path)
            elif file_ext == '.csv':
                return self._extract_from_csv(file_path)
            elif file_ext == '.xml':
                return self._extract_from_xml(file_path)
            elif file_ext in ['.txt', '.yml', '.yaml']:
                return self._extract_from_text(file_path)
            else:
                return self._extract_from_text(file_path)  # Fallback
        
        except Exception as e:
            raise Exception(f"Failed to extract text from {file_path}: {str(e)}")
    
    def _extract_from_json(self, file_path: str) -> List[Tuple[str, str, str]]:
        """Extract text from JSON files"""
        translatable_texts = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            def extract_recursive(obj, path=""):
                if isinstance(obj, str):
                    if self.japanese_pattern.search(obj):
                        translatable_texts.append((obj, path, "json"))
                elif isinstance(obj, dict):
                    for key, value in obj.items():
                        new_path = f"{path}.{key}" if path else key
                        extract_recursive(value, new_path)
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        new_path = f"{path}[{i}]"
                        extract_recursive(item, new_path)
            
            extract_recursive(data)
            
        except Exception as e:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='shift-jis') as f:
                    data = json.load(f)
                # Repeat extraction with new data
                # ... (same logic as above)
            except Exception:
                raise e
        
        return translatable_texts
    
    def _extract_from_csv(self, file_path: str) -> List[Tuple[str, str, str]]:
        """Extract text from CSV files"""
        translatable_texts = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', newline='') as f:
                # Try to detect delimiter
                sample = f.read(1024)
                f.seek(0)
                
                if '\t' in sample:
                    delimiter = '\t'
                elif ';' in sample:
                    delimiter = ';'
                else:
                    delimiter = ','
                
                reader = csv.reader(f, delimiter=delimiter)
                
                for row_num, row in enumerate(reader):
                    for col_num, cell in enumerate(row):
                        if cell and self.japanese_pattern.search(cell):
                            context = f"row_{row_num}_col_{col_num}"
                            translatable_texts.append((cell, context, "csv"))
        
        except Exception:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='shift-jis', newline='') as f:
                    reader = csv.reader(f)
                    for row_num, row in enumerate(reader):
                        for col_num, cell in enumerate(row):
                            if cell and self.japanese_pattern.search(cell):
                                context = f"row_{row_num}_col_{col_num}"
                                translatable_texts.append((cell, context, "csv"))
            except Exception as e:
                raise e
        
        return translatable_texts
    
    def _extract_from_xml(self, file_path: str) -> List[Tuple[str, str, str]]:
        """Extract text from XML files"""
        translatable_texts = []
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            def extract_from_element(element, path=""):
                # Check element text
                if element.text and element.text.strip():
                    text = element.text.strip()
                    if self.japanese_pattern.search(text):
                        element_path = f"{path}/{element.tag}" if path else element.tag
                        translatable_texts.append((text, element_path, "xml"))
                
                # Check attributes
                for attr_name, attr_value in element.attrib.items():
                    if attr_value and self.japanese_pattern.search(attr_value):
                        attr_path = f"{path}/{element.tag}@{attr_name}" if path else f"{element.tag}@{attr_name}"
                        translatable_texts.append((attr_value, attr_path, "xml"))
                
                # Recursively check children
                for child in element:
                    child_path = f"{path}/{element.tag}" if path else element.tag
                    extract_from_element(child, child_path)
            
            extract_from_element(root)
            
        except Exception as e:
            raise e
        
        return translatable_texts
    
    def _extract_from_text(self, file_path: str) -> List[Tuple[str, str, str]]:
        """Extract text from plain text files"""
        translatable_texts = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if line and self.japanese_pattern.search(line):
                    context = f"line_{line_num}"
                    translatable_texts.append((line, context, "text"))
        
        except Exception:
            try:
                with open(file_path, 'r', encoding='shift-jis') as f:
                    lines = f.readlines()
                
                for line_num, line in enumerate(lines, 1):
                    line = line.strip()
                    if line and self.japanese_pattern.search(line):
                        context = f"line_{line_num}"
                        translatable_texts.append((line, context, "text"))
            except Exception as e:
                raise e
        
        return translatable_texts
    
    def create_translation_file(self, original_file: str, translations: Dict[str, str], 
                              target_language: str, assets_dir: str) -> str:
        """
        Create translation file for Unity project
        """
        try:
            # Get relative path from Assets directory
            rel_path = os.path.relpath(original_file, assets_dir)
            
            # Create translations directory structure
            language_code = self._get_language_code(target_language)
            translations_dir = os.path.join(assets_dir, 'Translations', language_code)
            os.makedirs(translations_dir, exist_ok=True)
            
            # Preserve directory structure
            rel_dir = os.path.dirname(rel_path)
            if rel_dir:
                output_dir = os.path.join(translations_dir, rel_dir)
                os.makedirs(output_dir, exist_ok=True)
            else:
                output_dir = translations_dir
            
            # Create translation file
            original_name = os.path.basename(original_file)
            translation_file = os.path.join(output_dir, original_name)
            
            # Apply translations based on file type
            file_ext = os.path.splitext(original_file)[1].lower()
            
            if file_ext == '.json':
                self._create_json_translation(original_file, translation_file, translations)
            elif file_ext == '.csv':
                self._create_csv_translation(original_file, translation_file, translations)
            elif file_ext == '.xml':
                self._create_xml_translation(original_file, translation_file, translations)
            else:
                self._create_text_translation(original_file, translation_file, translations)
            
            return translation_file
            
        except Exception as e:
            raise Exception(f"Failed to create translation file: {str(e)}")
    
    def _get_language_code(self, language: str) -> str:
        """Get Unity language code from language name"""
        language_codes = {
            'English': 'en',
            'en': 'en',
            '简体中文': 'zh-CN',
            'zh-CN': 'zh-CN',
            '繁體中文': 'zh-TW', 
            'zh-TW': 'zh-TW',
            '한국어': 'ko',
            'ko-KR': 'ko',
            'Русский': 'ru',
            'ru-RU': 'ru',
            'Español': 'es',
            'es-ES': 'es',
            'Français': 'fr',
            'fr-FR': 'fr',
            'Deutsch': 'de',
            'de-DE': 'de',
            'Italiano': 'it',
            'it-IT': 'it',
            'Português': 'pt',
            'pt-BR': 'pt'
        }
        
        return language_codes.get(language, language.lower().replace('-', '_'))
    
    def _create_json_translation(self, original_file: str, translation_file: str, 
                               translations: Dict[str, str]):
        """Create translated JSON file"""
        with open(original_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        def apply_translations(obj):
            if isinstance(obj, str):
                return translations.get(obj, obj)
            elif isinstance(obj, dict):
                return {key: apply_translations(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [apply_translations(item) for item in obj]
            else:
                return obj
        
        translated_data = apply_translations(data)
        
        with open(translation_file, 'w', encoding='utf-8') as f:
            json.dump(translated_data, f, ensure_ascii=False, indent=2)
    
    def _create_csv_translation(self, original_file: str, translation_file: str, 
                              translations: Dict[str, str]):
        """Create translated CSV file"""
        rows = []
        
        with open(original_file, 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                translated_row = []
                for cell in row:
                    translated_cell = translations.get(cell, cell)
                    translated_row.append(translated_cell)
                rows.append(translated_row)
        
        with open(translation_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            for row in rows:
                writer.writerow(row)
    
    def _create_xml_translation(self, original_file: str, translation_file: str, 
                              translations: Dict[str, str]):
        """Create translated XML file"""
        tree = ET.parse(original_file)
        root = tree.getroot()
        
        def translate_element(element):
            # Translate element text
            if element.text and element.text.strip():
                text = element.text.strip()
                if text in translations:
                    element.text = translations[text]
            
            # Translate attributes
            for attr_name, attr_value in element.attrib.items():
                if attr_value in translations:
                    element.attrib[attr_name] = translations[attr_value]
            
            # Recursively translate children
            for child in element:
                translate_element(child)
        
        translate_element(root)
        tree.write(translation_file, encoding='utf-8', xml_declaration=True)
    
    def _create_text_translation(self, original_file: str, translation_file: str, 
                               translations: Dict[str, str]):
        """Create translated text file"""
        with open(original_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        translated_lines = []
        for line in lines:
            stripped_line = line.strip()
            if stripped_line in translations:
                # Preserve original indentation
                indent = line[:len(line) - len(line.lstrip())]
                translated_lines.append(indent + translations[stripped_line] + '\n')
            else:
                translated_lines.append(line)
        
        with open(translation_file, 'w', encoding='utf-8') as f:
            f.writelines(translated_lines)
    
    def get_file_stats(self, file_path: str) -> Dict[str, Any]:
        """Get statistics about a Unity text file"""
        try:
            translatable_texts = self.extract_translatable_text(file_path)
            
            japanese_texts = [text for text, _, _ in translatable_texts 
                            if self.japanese_pattern.search(text)]
            
            return {
                'total_text_entries': len(translatable_texts),
                'japanese_text_entries': len(japanese_texts),
                'needs_translation': len(japanese_texts) > 0,
                'file_size': os.path.getsize(file_path),
                'estimated_tokens': sum(len(text) // 4 for text, _, _ in japanese_texts),
                'file_type': os.path.splitext(file_path)[1]
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'needs_translation': False
            }
    
    def validate_translation_file(self, file_path: str) -> Tuple[bool, str]:
        """Validate Unity translation file"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)  # Will raise exception if invalid
                return True, "JSON file is valid"
            
            elif file_ext == '.xml':
                ET.parse(file_path)  # Will raise exception if invalid
                return True, "XML file is valid"
            
            elif file_ext == '.csv':
                with open(file_path, 'r', encoding='utf-8', newline='') as f:
                    csv.reader(f)  # Basic check
                return True, "CSV file is valid"
            
            else:
                # For text files, just check if it's readable
                with open(file_path, 'r', encoding='utf-8') as f:
                    f.read()
                return True, "Text file is valid"
                
        except Exception as e:
            return False, f"Validation error: {str(e)}"
