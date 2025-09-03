"""
Regex Engine processor
Handles Regex engine (.txt) game files
Used in games like Narcissu (fan adaptations)
"""

import os
import re
import json
from typing import List, Tuple
import logging

class RegexProcessor:
    """Processor for Regex engine games"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def find_regex_files(self, directory: str) -> List[str]:
        """Find Regex script files"""
        regex_files = []
        
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.txt'):
                    file_path = os.path.join(root, file)
                    
                    # Check if it's actually a Regex engine file
                    if self._is_regex_engine_file(file_path):
                        regex_files.append(file_path)
        
        return sorted(regex_files)
    
    def _is_regex_engine_file(self, file_path: str) -> bool:
        """Check if file is Regex engine format"""
        try:
            encodings = ['utf-8', 'shift-jis', 'cp932']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read(1000)  # Read first 1000 chars
                    
                    # Look for Regex engine patterns
                    # Regex engine often has specific command structures
                    regex_patterns = [
                        r'^#[A-Z_]+',        # Commands starting with #
                        r'@[a-zA-Z_]+',      # @ commands
                        r'\$[a-zA-Z_]+',     # $ variables
                        r'%[a-zA-Z_]+',      # % variables
                        r'\\[a-zA-Z]+',      # Escape sequences
                    ]
                    
                    pattern_count = 0
                    for pattern in regex_patterns:
                        if re.search(pattern, content, re.MULTILINE):
                            pattern_count += 1
                    
                    # If we find multiple patterns, likely Regex engine
                    if pattern_count >= 2:
                        return True
                    
                    # Also check for typical visual novel text patterns
                    if re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', content):
                        # Has Japanese text, check for simple dialogue format
                        lines = content.split('\n')[:20]  # Check first 20 lines
                        dialogue_lines = 0
                        for line in lines:
                            line = line.strip()
                            if line and not line.startswith(('#', '//', ';')):
                                if re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', line):
                                    dialogue_lines += 1
                        
                        if dialogue_lines >= 3:
                            return True
                    
                    break
                except UnicodeDecodeError:
                    continue
                    
        except Exception:
            pass
        
        return False
    
    def extract_translatable_text(self, file_path: str) -> List[Tuple[str, str, str]]:
        """Extract translatable text from Regex files"""
        texts = []
        
        try:
            # Try different encodings
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
            current_speaker = ""
            in_dialogue_block = False
            
            for line in content.split('\n'):
                line_num += 1
                original_line = line.strip()
                
                if not original_line:
                    continue
                
                # Skip comments
                if original_line.startswith(('#', '//', ';', '*')):
                    continue
                
                # Character name detection
                # Format: [Character] or {Character} or Character:
                speaker_patterns = [
                    r'^\[([^\]]+)\]',     # [Speaker]
                    r'^\{([^}]+)\}',      # {Speaker}
                    r'^([^:]+):',         # Speaker:
                    r'^「([^」]+)」',      # 「Speaker」
                ]
                
                speaker_found = False
                for pattern in speaker_patterns:
                    match = re.match(pattern, original_line)
                    if match:
                        speaker = match.group(1).strip()
                        if self._is_translatable_text(speaker):
                            texts.append((speaker, f"line_{line_num}_speaker", "character"))
                            current_speaker = speaker
                        speaker_found = True
                        break
                
                if speaker_found:
                    continue
                
                # Command detection
                if original_line.startswith(('@', '$', '%', '\\')):
                    # Extract text from commands
                    command_texts = self._extract_from_commands(original_line, line_num)
                    texts.extend(command_texts)
                    continue
                
                # Regular dialogue text
                clean_text = self._clean_regex_text(original_line)
                
                if self._is_translatable_text(clean_text):
                    context = f"line_{line_num}"
                    if current_speaker:
                        context += f"_speaker_{current_speaker}"
                    texts.append((clean_text, context, "dialogue"))
            
        except Exception as e:
            self.logger.error(f"Error processing Regex file {file_path}: {e}")
        
        return texts
    
    def _extract_from_commands(self, line: str, line_num: int) -> List[Tuple[str, str, str]]:
        """Extract text from Regex engine commands"""
        texts = []
        
        # Common command patterns that contain text
        command_patterns = [
            r'@message\s+"([^"]+)"',     # @message "text"
            r'@say\s+"([^"]+)"',         # @say "text"
            r'@text\s+"([^"]+)"',        # @text "text"
            r'@choice\s+"([^"]+)"',      # @choice "text"
            r'@name\s+"([^"]+)"',        # @name "text"
            r'"([^"]+)"',                # Any quoted text
            r"'([^']+)'",                # Single quoted text
        ]
        
        for pattern in command_patterns:
            matches = re.finditer(pattern, line, re.IGNORECASE)
            for match in matches:
                text = match.group(1).strip()
                if self._is_translatable_text(text):
                    texts.append((text, f"line_{line_num}_cmd", "ui"))
        
        return texts
    
    def _clean_regex_text(self, text: str) -> str:
        """Clean Regex engine formatting"""
        # Remove common formatting
        text = re.sub(r'\\[a-zA-Z]', '', text)  # \n, \r, etc.
        text = re.sub(r'\{[^}]*\}', '', text)   # {commands}
        text = re.sub(r'\[[^\]]*\]', '', text)  # [tags]
        text = re.sub(r'<[^>]*>', '', text)     # <tags>
        
        # Remove ruby text patterns
        text = re.sub(r'([^\(]+)\([^\)]+\)', r'\1', text)  # 漢字(かんじ) -> 漢字
        
        return text.strip()
    
    def _is_translatable_text(self, text: str) -> bool:
        """Check if text is worth translating"""
        if not text or len(text.strip()) < 2:
            return False
        
        # Check for Japanese characters
        japanese_pattern = r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]'
        if not re.search(japanese_pattern, text):
            return False
        
        # Filter out system commands
        system_commands = [
            'load', 'save', 'jump', 'call', 'return', 'end',
            'if', 'else', 'endif', 'while', 'endwhile',
            'true', 'false', 'null'
        ]
        
        if text.lower() in system_commands:
            return False
        
        # Filter out file names
        if text.lower().endswith(('.wav', '.mp3', '.ogg', '.jpg', '.png', '.gif', '.bmp')):
            return False
        
        return True
    
    def create_translation_file(self, texts: List[Tuple[str, str, str]], output_path: str):
        """Create translation file for Regex texts"""
        translation_data = []
        
        for original, context, text_type in texts:
            translation_data.append({
                'original': original,
                'translation': '',
                'context': context,
                'type': text_type,
                'notes': 'Regex Engine format'
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(translation_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Created Regex translation file: {output_path}")
    
    def apply_translations(self, original_file: str, translation_file: str, output_file: str):
        """Apply translations back to Regex files"""
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
            
            # Apply translations
            for original, translation in trans_dict.items():
                # Use word boundary matching when possible
                escaped_original = re.escape(original)
                content = re.sub(escaped_original, translation, content)
            
            # Write translated file
            with open(output_file, 'w', encoding=used_encoding) as f:
                f.write(content)
            
            self.logger.info(f"Applied Regex translations to: {output_file}")
            
        except Exception as e:
            self.logger.error(f"Error applying Regex translations: {e}")
