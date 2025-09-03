"""
Ren'Py File Processor
Handles extraction and application of translatable text from .rpy files
"""

import os
import re
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path


class RenpyProcessor:
    """Processes Ren'Py .rpy files for translation"""
    
    def __init__(self):
        # Patterns for Japanese text detection
        self.japanese_pattern = re.compile(r'[ひらがなカタカナ漢字\u3040-\u309f\u30a0-\u30ff\u4e00-\u9faf]+')
        
        # Patterns for extracting translatable strings
        self.dialogue_patterns = [
            # Basic dialogue: character "text"
            re.compile(r'^(\s*)(\w+)\s+"([^"]+)"', re.MULTILINE),
            # Narrator text: "text"
            re.compile(r'^(\s*)"([^"]+)"(?:\s*$)', re.MULTILINE),
            # Say statement: $ renpy.say(character, "text")
            re.compile(r'^(\s*)\$\s*renpy\.say\([^,]+,\s*"([^"]+)"\)', re.MULTILINE),
            # Menu choices: "choice text"
            re.compile(r'^(\s*)"([^"]+)"\s*:', re.MULTILINE),
        ]
        
        # Patterns for strings that should be translated
        self.translatable_patterns = [
            # Window titles, descriptions, etc.
            re.compile(r'(title|description|tooltip|label)\s*=\s*"([^"]+)"'),
            # Text variables
            re.compile(r'(\w+_text)\s*=\s*"([^"]+)"'),
            # UI strings
            re.compile(r'(ui\.text)\s*\(\s*"([^"]+)"\s*\)'),
        ]
        
        # Patterns to exclude from translation
        self.exclude_patterns = [
            re.compile(r'#.*'),  # Comments
            re.compile(r'image\s+\w+\s*='),  # Image definitions
            re.compile(r'define\s+\w+\s*='),  # Variable definitions (unless text)
            re.compile(r'transform\s+\w+'),  # Transform definitions
            re.compile(r'screen\s+\w+'),  # Screen definitions (header)
            re.compile(r'label\s+\w+'),  # Label definitions
            re.compile(r'init\s+'),  # Init blocks
        ]
    
    def detect_renpy_project(self, directory: str) -> bool:
        """Detect if directory contains a Ren'Py project"""
        game_dir = os.path.join(directory, 'game')
        
        if not os.path.exists(game_dir):
            return False
        
        # Look for common Ren'Py files
        renpy_indicators = [
            'script.rpy',
            'options.rpy',
            'gui.rpy',
            'screens.rpy'
        ]
        
        for indicator in renpy_indicators:
            if os.path.exists(os.path.join(game_dir, indicator)):
                return True
        
        # Check for any .rpy files
        for file in os.listdir(game_dir):
            if file.endswith('.rpy'):
                return True
        
        return False
    
    def find_rpy_files(self, directory: str) -> List[str]:
        """Find all .rpy files in the game directory"""
        game_dir = os.path.join(directory, 'game')
        
        if not os.path.exists(game_dir):
            return []
        
        rpy_files = []
        
        # Recursively find .rpy files
        for root, dirs, files in os.walk(game_dir):
            # Skip tl directory to avoid processing existing translations
            if 'tl' in dirs:
                dirs.remove('tl')
            
            for file in files:
                if file.endswith('.rpy'):
                    file_path = os.path.join(root, file)
                    rpy_files.append(file_path)
        
        return sorted(rpy_files)
    
    def needs_translation(self, file_path: str) -> bool:
        """Check if the .rpy file contains translatable Japanese text"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return bool(self.japanese_pattern.search(content))
        
        except Exception:
            return False
    
    def extract_translatable_text(self, file_path: str) -> List[Tuple[str, str, int]]:
        """
        Extract translatable text from .rpy file
        Returns list of (original_text, context, line_number)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            translatable_texts = []
            
            for line_num, line in enumerate(lines, 1):
                # Skip excluded patterns
                if any(pattern.search(line) for pattern in self.exclude_patterns):
                    continue
                
                # Extract dialogue
                for pattern in self.dialogue_patterns:
                    matches = pattern.findall(line)
                    for match in matches:
                        if len(match) >= 2:
                            text = match[-1]  # Last group is always the text
                            if self.japanese_pattern.search(text):
                                context = f"dialogue_{line_num}"
                                translatable_texts.append((text, context, line_num))
                
                # Extract other translatable strings
                for pattern in self.translatable_patterns:
                    matches = pattern.findall(line)
                    for match in matches:
                        if len(match) >= 2:
                            text = match[1]
                            if self.japanese_pattern.search(text):
                                context = f"string_{match[0]}_{line_num}"
                                translatable_texts.append((text, context, line_num))
            
            return translatable_texts
        
        except Exception as e:
            raise Exception(f"Failed to extract text from {file_path}: {str(e)}")
    
    def create_translation_file(self, original_file: str, translations: Dict[str, str], 
                              target_language: str, game_dir: str) -> str:
        """
        Create Ren'Py translation file in tl/[language] directory
        """
        try:
            # Get relative path from game directory
            rel_path = os.path.relpath(original_file, game_dir)
            
            # Create tl directory structure
            language_code = self._get_language_code(target_language)
            tl_dir = os.path.join(game_dir, 'tl', language_code)
            os.makedirs(tl_dir, exist_ok=True)
            
            # Create translation file path
            base_name = os.path.splitext(os.path.basename(rel_path))[0]
            translation_file = os.path.join(tl_dir, f"{base_name}.rpy")
            
            # Generate translation content
            content = self._generate_translation_content(original_file, translations, target_language)
            
            # Write translation file
            with open(translation_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return translation_file
        
        except Exception as e:
            raise Exception(f"Failed to create translation file: {str(e)}")
    
    def _get_language_code(self, language: str) -> str:
        """Get Ren'Py language code from language name"""
        language_codes = {
            'English': 'english',
            'en': 'english',
            '简体中文': 'schinese',
            'zh-CN': 'schinese',
            '繁體中文': 'tchinese', 
            'zh-TW': 'tchinese',
            '한국어': 'korean',
            'ko-KR': 'korean',
            'Русский': 'russian',
            'ru-RU': 'russian',
            'Español': 'spanish',
            'es-ES': 'spanish',
            'Français': 'french',
            'fr-FR': 'french',
            'Deutsch': 'german',
            'de-DE': 'german',
            'Italiano': 'italian',
            'it-IT': 'italian',
            'Português': 'portuguese',
            'pt-BR': 'portuguese'
        }
        
        return language_codes.get(language, language.lower().replace('-', '').replace('_', ''))
    
    def _generate_translation_content(self, original_file: str, translations: Dict[str, str], 
                                    target_language: str) -> str:
        """Generate Ren'Py translation file content"""
        
        try:
            with open(original_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Create header
            rel_path = os.path.basename(original_file)
            language_code = self._get_language_code(target_language)
            
            content = f'''# Translation file for {rel_path}
# Generated by Eroge Translation Tool
# Language: {target_language} ({language_code})

translate {language_code}:

'''
            
            # Process each line and add translations
            current_label = None
            translation_counter = 0
            
            for line_num, line in enumerate(lines, 1):
                stripped_line = line.strip()
                
                # Track current label for context
                label_match = re.match(r'label\s+(\w+)', stripped_line)
                if label_match:
                    current_label = label_match.group(1)
                    continue
                
                # Find translatable strings in this line
                found_translation = False
                
                # Check dialogue patterns
                for pattern in self.dialogue_patterns:
                    match = pattern.search(line)
                    if match and len(match.groups()) >= 2:
                        original_text = match.groups()[-1]
                        
                        if original_text in translations:
                            translation_counter += 1
                            
                            # Generate translation block
                            if current_label:
                                block_id = f"{current_label}_{translation_counter:03d}"
                            else:
                                block_id = f"line_{line_num:03d}"
                            
                            content += f'    # {rel_path}:{line_num}\n'
                            content += f'    old "{self._escape_string(original_text)}"\n'
                            content += f'    new "{self._escape_string(translations[original_text])}"\n\n'
                            
                            found_translation = True
                            break
                
                # Check other translatable patterns if no dialogue found
                if not found_translation:
                    for pattern in self.translatable_patterns:
                        matches = pattern.findall(line)
                        for match in matches:
                            if len(match) >= 2:
                                original_text = match[1]
                                
                                if original_text in translations:
                                    translation_counter += 1
                                    
                                    block_id = f"string_{line_num:03d}"
                                    
                                    content += f'    # {rel_path}:{line_num}\n'
                                    content += f'    old "{self._escape_string(original_text)}"\n'
                                    content += f'    new "{self._escape_string(translations[original_text])}"\n\n'
            
            return content
        
        except Exception as e:
            raise Exception(f"Failed to generate translation content: {str(e)}")
    
    def _escape_string(self, text: str) -> str:
        """Escape string for Ren'Py format"""
        # Escape quotes and backslashes
        text = text.replace('\\', '\\\\')
        text = text.replace('"', '\\"')
        return text
    
    def get_file_stats(self, file_path: str) -> Dict[str, Any]:
        """Get statistics about a .rpy file"""
        try:
            translatable_texts = self.extract_translatable_text(file_path)
            
            japanese_texts = [text for text, _, _ in translatable_texts 
                            if self.japanese_pattern.search(text)]
            
            return {
                'total_text_entries': len(translatable_texts),
                'japanese_text_entries': len(japanese_texts),
                'needs_translation': len(japanese_texts) > 0,
                'file_size': os.path.getsize(file_path),
                'estimated_tokens': sum(len(text) // 4 for text, _, _ in japanese_texts)
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'needs_translation': False
            }
    
    def validate_translation_file(self, file_path: str) -> Tuple[bool, str]:
        """Validate Ren'Py translation file syntax"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic syntax checks
            if not re.search(r'translate\s+\w+:', content):
                return False, "Missing translate block"
            
            # Check for balanced quotes
            in_string = False
            escape_next = False
            
            for char in content:
                if escape_next:
                    escape_next = False
                    continue
                
                if char == '\\':
                    escape_next = True
                    continue
                
                if char == '"':
                    in_string = not in_string
            
            if in_string:
                return False, "Unbalanced quotes detected"
            
            return True, "Translation file is valid"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
