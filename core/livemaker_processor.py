"""
Live Maker Engine processor
Handles Live Maker (.lm, .lsb, .lsc) game files
"""

import os
import re
import json
import struct
from typing import List, Tuple, Dict, Any
import logging

class LiveMakerProcessor:
    """Processor for Live Maker engine games"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def find_livemaker_files(self, directory: str) -> List[str]:
        """Find Live Maker script files"""
        lm_files = []
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(('.lsb', '.lsc', '.lm')):
                    file_path = os.path.join(root, file)
                    lm_files.append(file_path)
        
        return sorted(lm_files)
    
    def extract_translatable_text(self, file_path: str) -> List[Tuple[str, str, str]]:
        """Extract translatable text from Live Maker files"""
        texts = []
        
        try:
            # Determine file type and process accordingly
            if file_path.lower().endswith('.lsb'):
                texts = self._process_lsb_file(file_path)
            elif file_path.lower().endswith('.lsc'):
                texts = self._process_lsc_file(file_path)
            elif file_path.lower().endswith('.lm'):
                texts = self._process_lm_file(file_path)
            
        except Exception as e:
            self.logger.error(f"Error processing Live Maker file {file_path}: {e}")
        
        return texts
    
    def _process_lsb_file(self, file_path: str) -> List[Tuple[str, str, str]]:
        """Process Live Maker binary script file (.lsb)"""
        texts = []
        
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
                
            # Live Maker uses Shift-JIS encoding typically
            # Look for text patterns in the binary data
            text_pattern = re.compile(rb'[\x81-\x9F\xE0-\xFC][\x40-\x7E\x80-\xFC]+|[\x20-\x7E]+')
            
            for match in text_pattern.finditer(data):
                try:
                    # Try to decode as Shift-JIS first, then UTF-8
                    text_bytes = match.group()
                    
                    try:
                        text = text_bytes.decode('shift-jis')
                    except UnicodeDecodeError:
                        try:
                            text = text_bytes.decode('utf-8')
                        except UnicodeDecodeError:
                            continue
                    
                    # Filter out non-Japanese text and system strings
                    if self._is_translatable_text(text):
                        offset = match.start()
                        texts.append((text, f"offset_{offset}", "dialogue"))
                        
                except Exception:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error processing LSB file {file_path}: {e}")
        
        return texts
    
    def _process_lsc_file(self, file_path: str) -> List[Tuple[str, str, str]]:
        """Process Live Maker script file (.lsc)"""
        texts = []
        
        try:
            # Try different encodings
            encodings = ['shift-jis', 'utf-8', 'cp932']
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
            
            # Live Maker script patterns
            # Text messages often appear in quotes or after specific commands
            patterns = [
                r'"([^"]+)"',  # Quoted text
                r'msg\s+"([^"]+)"',  # Message command
                r'say\s+"([^"]+)"',  # Say command
                r'text\s+"([^"]+)"',  # Text command
                r'choice\s+"([^"]+)"',  # Choice options
            ]
            
            line_num = 0
            for line in content.split('\n'):
                line_num += 1
                line = line.strip()
                
                for pattern in patterns:
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        text = match.group(1)
                        if self._is_translatable_text(text):
                            texts.append((text, f"line_{line_num}", "dialogue"))
            
        except Exception as e:
            self.logger.error(f"Error processing LSC file {file_path}: {e}")
        
        return texts
    
    def _process_lm_file(self, file_path: str) -> List[Tuple[str, str, str]]:
        """Process Live Maker project file (.lm)"""
        texts = []
        
        try:
            # .lm files are usually text-based project files
            encodings = ['shift-jis', 'utf-8', 'cp932']
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
            
            # Look for text entries in project files
            patterns = [
                r'title\s*=\s*"([^"]+)"',  # Game title
                r'name\s*=\s*"([^"]+)"',   # Character names
                r'text\s*=\s*"([^"]+)"',   # Text entries
            ]
            
            line_num = 0
            for line in content.split('\n'):
                line_num += 1
                line = line.strip()
                
                for pattern in patterns:
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        text = match.group(1)
                        if self._is_translatable_text(text):
                            texts.append((text, f"line_{line_num}", "ui"))
            
        except Exception as e:
            self.logger.error(f"Error processing LM file {file_path}: {e}")
        
        return texts
    
    def _is_translatable_text(self, text: str) -> bool:
        """Check if text is worth translating"""
        if not text or len(text.strip()) < 2:
            return False
        
        # Check for Japanese characters
        japanese_pattern = r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]'
        if not re.search(japanese_pattern, text):
            return False
        
        # Filter out common system strings
        system_strings = [
            'null', 'true', 'false', 'undefined',
            'script', 'function', 'var', 'if', 'else',
            'for', 'while', 'return', 'break', 'continue'
        ]
        
        if text.lower() in system_strings:
            return False
        
        return True
    
    def create_translation_file(self, texts: List[Tuple[str, str, str]], output_path: str):
        """Create translation file for Live Maker texts"""
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
        
        self.logger.info(f"Created Live Maker translation file: {output_path}")
    
    def apply_translations(self, original_file: str, translation_file: str, output_file: str):
        """Apply translations back to Live Maker files"""
        try:
            # Load translations
            with open(translation_file, 'r', encoding='utf-8') as f:
                translations = json.load(f)
            
            # Create translation dictionary
            trans_dict = {}
            for item in translations:
                if item['translation'].strip():
                    trans_dict[item['original']] = item['translation']
            
            # Apply translations based on file type
            if original_file.lower().endswith('.lsb'):
                self._apply_lsb_translations(original_file, trans_dict, output_file)
            elif original_file.lower().endswith(('.lsc', '.lm')):
                self._apply_text_translations(original_file, trans_dict, output_file)
            
        except Exception as e:
            self.logger.error(f"Error applying translations: {e}")
    
    def _apply_text_translations(self, original_file: str, trans_dict: Dict[str, str], output_file: str):
        """Apply translations to text-based Live Maker files"""
        try:
            # Read original file
            encodings = ['shift-jis', 'utf-8', 'cp932']
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
                # Escape special regex characters
                escaped_original = re.escape(original)
                content = re.sub(escaped_original, translation, content)
            
            # Write translated file
            with open(output_file, 'w', encoding=used_encoding) as f:
                f.write(content)
            
            self.logger.info(f"Applied translations to: {output_file}")
            
        except Exception as e:
            self.logger.error(f"Error applying text translations: {e}")
    
    def _apply_lsb_translations(self, original_file: str, trans_dict: Dict[str, str], output_file: str):
        """Apply translations to binary Live Maker files"""
        try:
            with open(original_file, 'rb') as f:
                data = bytearray(f.read())
            
            # Apply translations to binary data
            for original, translation in trans_dict.items():
                try:
                    # Try both Shift-JIS and UTF-8
                    for encoding in ['shift-jis', 'utf-8']:
                        try:
                            original_bytes = original.encode(encoding)
                            translation_bytes = translation.encode(encoding)
                            
                            # Replace in binary data
                            data = data.replace(original_bytes, translation_bytes)
                            break
                        except UnicodeEncodeError:
                            continue
                except Exception:
                    continue
            
            # Write translated file
            with open(output_file, 'wb') as f:
                f.write(data)
            
            self.logger.info(f"Applied binary translations to: {output_file}")
            
        except Exception as e:
            self.logger.error(f"Error applying binary translations: {e}")
