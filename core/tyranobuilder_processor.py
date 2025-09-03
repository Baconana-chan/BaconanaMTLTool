"""
TyranoBuilder processor
Handles TyranoBuilder (.ks, .tjs) game files
"""

import os
import re
import json
from typing import List, Tuple, Dict
import logging

class TyranoBuilderProcessor:
    """Processor for TyranoBuilder engine games"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def find_tyranobuilder_files(self, directory: str) -> List[str]:
        """Find TyranoBuilder script files"""
        tb_files = []
        
        for root, _, files in os.walk(directory):
            for file in files:
                # TyranoBuilder uses .ks files (similar to KiriKiri but different syntax)
                # Also .tjs files for TyranoScript
                if file.lower().endswith(('.ks', '.tjs')) and not file.startswith('.'):
                    file_path = os.path.join(root, file)
                    
                    # Check if it's actually TyranoBuilder by looking for specific tags
                    if self._is_tyranobuilder_file(file_path):
                        tb_files.append(file_path)
        
        return sorted(tb_files)
    
    def _is_tyranobuilder_file(self, file_path: str) -> bool:
        """Check if file is TyranoBuilder format by looking for specific tags"""
        try:
            encodings = ['utf-8', 'shift-jis', 'cp932']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read(1000)  # Read first 1000 chars
                    
                    # TyranoBuilder specific tags
                    tyranobuilder_tags = [
                        '@', '[', ']',  # Basic TyranoScript syntax
                        'tyrano', 'title', 'start',
                        'chara_new', 'chara_show', 'chara_hide',
                        'bg', 'playse', 'playbgm',
                        'wait', 'l', 'p', 'r'
                    ]
                    
                    # Check for TyranoBuilder patterns
                    tyrano_patterns = [
                        r'\[([^\]]+)\]',  # TyranoScript tags
                        r'@(\w+)',       # @ commands
                        r'#(\w+)',       # Character names
                    ]
                    
                    for pattern in tyrano_patterns:
                        if re.search(pattern, content):
                            return True
                    
                    break
                except UnicodeDecodeError:
                    continue
            
        except Exception:
            pass
        
        return False
    
    def extract_translatable_text(self, file_path: str) -> List[Tuple[str, str, str]]:
        """Extract translatable text from TyranoBuilder files"""
        texts = []
        
        try:
            encodings = ['utf-8', 'shift-jis', 'cp932']
            content = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if not content:
                return texts
            
            line_num = 0
            current_character = ""
            
            for line in content.split('\n'):
                line_num += 1
                original_line = line.strip()
                
                if not original_line or original_line.startswith(';'):
                    continue
                
                # Character name detection
                chara_match = re.match(r'#([^#\n]+)', original_line)
                if chara_match:
                    character_name = chara_match.group(1).strip()
                    if self._is_translatable_text(character_name):
                        texts.append((character_name, f"line_{line_num}", "character"))
                        current_character = character_name
                    continue
                
                # TyranoScript commands
                if original_line.startswith('[') or original_line.startswith('@'):
                    # Extract text from TyranoScript tags
                    tag_texts = self._extract_from_tags(original_line, line_num)
                    texts.extend(tag_texts)
                    continue
                
                # Regular dialogue text (not starting with special characters)
                if not original_line.startswith(('[', '@', '*', '&')):
                    # Remove ruby text and other formatting
                    clean_text = self._clean_dialogue_text(original_line)
                    
                    if self._is_translatable_text(clean_text):
                        context = f"line_{line_num}"
                        if current_character:
                            context += f"_char_{current_character}"
                        texts.append((clean_text, context, "dialogue"))
            
        except Exception as e:
            self.logger.error(f"Error processing TyranoBuilder file {file_path}: {e}")
        
        return texts
    
    def _extract_from_tags(self, line: str, line_num: int) -> List[Tuple[str, str, str]]:
        """Extract text from TyranoScript tags"""
        texts = []
        
        # Common TyranoScript tags that contain text
        text_patterns = [
            r'\[chara_new\s+.*?name="([^"]+)"',  # Character registration
            r'\[bg\s+.*?storage="([^"]+)"',      # Background names
            r'\[playse\s+.*?storage="([^"]+)"',  # Sound effect names
            r'\[playbgm\s+.*?storage="([^"]+)"', # Music names
            r'\[button\s+.*?text="([^"]+)"',     # Button text
            r'\[link\s+.*?text="([^"]+)"',       # Link text
            r'\[font\s+.*?\]([^[]+)',            # Font formatted text
            r'text="([^"]+)"',                   # Generic text attribute
            r'name="([^"]+)"',                   # Name attributes
        ]
        
        for pattern in text_patterns:
            matches = re.finditer(pattern, line, re.IGNORECASE)
            for match in matches:
                text = match.group(1).strip()
                if self._is_translatable_text(text):
                    texts.append((text, f"line_{line_num}_tag", "ui"))
        
        return texts
    
    def _clean_dialogue_text(self, text: str) -> str:
        """Clean dialogue text from TyranoBuilder formatting"""
        # Remove ruby text [ruby text=読み]漢字[/ruby]
        text = re.sub(r'\[ruby[^\]]*\]([^\[]+)\[/ruby\]', r'\1', text)
        
        # Remove other formatting tags
        text = re.sub(r'\[/?[^\]]+\]', '', text)
        
        # Remove control characters
        text = re.sub(r'[@#&*]', '', text)
        
        return text.strip()
    
    def _is_translatable_text(self, text: str) -> bool:
        """Check if text is worth translating"""
        if not text or len(text.strip()) < 2:
            return False
        
        # Check for Japanese characters
        japanese_pattern = r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]'
        if not re.search(japanese_pattern, text):
            return False
        
        # Filter out file names and system strings
        if text.lower().endswith(('.jpg', '.png', '.gif', '.wav', '.mp3', '.ogg')):
            return False
        
        system_strings = [
            'true', 'false', 'null', 'undefined',
            'auto', 'skip', 'save', 'load', 'config'
        ]
        
        if text.lower() in system_strings:
            return False
        
        return True
    
    def create_translation_file(self, texts: List[Tuple[str, str, str]], output_path: str):
        """Create translation file for TyranoBuilder texts"""
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
        
        self.logger.info(f"Created TyranoBuilder translation file: {output_path}")
    
    def apply_translations(self, original_file: str, translation_file: str, output_file: str):
        """Apply translations back to TyranoBuilder files"""
        try:
            # Load translations
            with open(translation_file, 'r', encoding='utf-8') as f:
                translations = json.load(f)
            
            # Create translation dictionary
            trans_dict = {}
            for item in translations:
                if item['translation'].strip():
                    trans_dict[item['original']] = item['translation']
            
            # Read original file
            encodings = ['utf-8', 'shift-jis', 'cp932']
            content = None
            used_encoding = 'utf-8'
            
            for encoding in encodings:
                try:
                    with open(original_file, 'r', encoding=encoding) as f:
                        content = f.read()
                    used_encoding = encoding
                    break
                except UnicodeDecodeError:
                    continue
            
            if not content:
                return
            
            # Apply translations line by line to preserve formatting
            lines = content.split('\n')
            translated_lines = []
            
            for line in lines:
                translated_line = line
                
                # Apply translations
                for original, translation in trans_dict.items():
                    # Use word boundary matching where possible
                    if original in line:
                        translated_line = translated_line.replace(original, translation)
                
                translated_lines.append(translated_line)
            
            # Write translated file
            translated_content = '\n'.join(translated_lines)
            with open(output_file, 'w', encoding=used_encoding) as f:
                f.write(translated_content)
            
            self.logger.info(f"Applied TyranoBuilder translations to: {output_file}")
            
        except Exception as e:
            self.logger.error(f"Error applying TyranoBuilder translations: {e}")
