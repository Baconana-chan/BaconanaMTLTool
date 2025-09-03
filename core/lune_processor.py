"""
Lune Engine processor
Handles Lune Engine (.l) game files
Used in games like Shinsetsu Ryouki no Ori
"""

import os
import re
import json
import struct
from typing import List, Tuple, Dict
import logging

class LuneProcessor:
    """Processor for Lune engine games"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def find_lune_files(self, directory: str) -> List[str]:
        """Find Lune script files"""
        lune_files = []
        
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.l'):
                    file_path = os.path.join(root, file)
                    lune_files.append(file_path)
        
        return sorted(lune_files)
    
    def extract_translatable_text(self, file_path: str) -> List[Tuple[str, str, str]]:
        """Extract translatable text from Lune files"""
        texts = []
        
        try:
            # Lune .l files can be binary or text
            # Try to detect format first
            if self._is_binary_file(file_path):
                texts = self._process_binary_lune_file(file_path)
            else:
                texts = self._process_text_lune_file(file_path)
            
        except Exception as e:
            self.logger.error(f"Error processing Lune file {file_path}: {e}")
        
        return texts
    
    def _is_binary_file(self, file_path: str) -> bool:
        """Check if file is binary format"""
        try:
            with open(file_path, 'rb') as f:
                # Read first few bytes to check for binary markers
                header = f.read(16)
                
            # Check for common binary patterns
            # Binary files often have null bytes or non-printable characters
            null_count = header.count(b'\x00')
            if null_count > 2:
                return True
            
            # Try to decode as text
            try:
                header.decode('utf-8')
                return False
            except UnicodeDecodeError:
                try:
                    header.decode('shift-jis')
                    return False
                except UnicodeDecodeError:
                    return True
                    
        except Exception:
            return False
    
    def _process_binary_lune_file(self, file_path: str) -> List[Tuple[str, str, str]]:
        """Process binary Lune file"""
        texts = []
        
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # Look for text patterns in binary data
            # Lune often uses Shift-JIS encoding
            text_pattern = re.compile(rb'[\x81-\x9F\xE0-\xFC][\x40-\x7E\x80-\xFC]+')
            
            for match in text_pattern.finditer(data):
                try:
                    text_bytes = match.group()
                    
                    # Try different encodings
                    for encoding in ['shift-jis', 'cp932', 'utf-8']:
                        try:
                            text = text_bytes.decode(encoding)
                            
                            if self._is_translatable_text(text):
                                offset = match.start()
                                texts.append((text, f"offset_{offset}", "dialogue"))
                            break
                        except UnicodeDecodeError:
                            continue
                            
                except Exception:
                    continue
            
            # Look for longer text strings (possible dialogue)
            long_text_pattern = re.compile(rb'[\x20-\x7E\x81-\x9F\xE0-\xFC][\x20-\x7E\x40-\xFC]{10,}')
            
            for match in long_text_pattern.finditer(data):
                try:
                    text_bytes = match.group()
                    
                    for encoding in ['shift-jis', 'cp932', 'utf-8']:
                        try:
                            text = text_bytes.decode(encoding)
                            
                            if self._is_translatable_text(text):
                                offset = match.start()
                                texts.append((text, f"offset_{offset}_long", "dialogue"))
                            break
                        except UnicodeDecodeError:
                            continue
                            
                except Exception:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error processing binary Lune file: {e}")
        
        return texts
    
    def _process_text_lune_file(self, file_path: str) -> List[Tuple[str, str, str]]:
        """Process text-based Lune file"""
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
            
            # Parse Lune script syntax
            line_num = 0
            current_speaker = ""
            
            for line in content.split('\n'):
                line_num += 1
                original_line = line.strip()
                
                if not original_line or original_line.startswith(('///', ';')):
                    continue
                
                # Look for Lune-specific patterns
                # Character names might be in format: [Character]
                speaker_match = re.match(r'\[([^\]]+)\]', original_line)
                if speaker_match:
                    speaker = speaker_match.group(1)
                    if self._is_translatable_text(speaker):
                        texts.append((speaker, f"line_{line_num}_speaker", "character"))
                        current_speaker = speaker
                    continue
                
                # Dialogue text
                # Remove Lune commands and formatting
                clean_line = self._clean_lune_text(original_line)
                
                if self._is_translatable_text(clean_line):
                    context = f"line_{line_num}"
                    if current_speaker:
                        context += f"_speaker_{current_speaker}"
                    texts.append((clean_line, context, "dialogue"))
            
        except Exception as e:
            self.logger.error(f"Error processing text Lune file: {e}")
        
        return texts
    
    def _clean_lune_text(self, text: str) -> str:
        """Clean Lune script formatting"""
        # Remove common Lune commands
        # This is based on common visual novel engine patterns
        text = re.sub(r'\\[a-zA-Z]+\[[^\]]*\]', '', text)  # \command[params]
        text = re.sub(r'<[^>]+>', '', text)  # <tags>
        text = re.sub(r'\{[^}]+\}', '', text)  # {commands}
        text = re.sub(r'\[[^\]]*\]', '', text)  # [tags]
        
        return text.strip()
    
    def _is_translatable_text(self, text: str) -> bool:
        """Check if text is worth translating"""
        if not text or len(text.strip()) < 3:
            return False
        
        # Check for Japanese characters
        japanese_pattern = r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]'
        if not re.search(japanese_pattern, text):
            return False
        
        # Filter out system commands and file names
        if text.lower().startswith(('load', 'save', 'jump', 'call', 'return')):
            return False
        
        if text.lower().endswith(('.wav', '.mp3', '.ogg', '.jpg', '.png', '.gif')):
            return False
        
        return True
    
    def create_translation_file(self, texts: List[Tuple[str, str, str]], output_path: str):
        """Create translation file for Lune texts"""
        translation_data = []
        
        for original, context, text_type in texts:
            translation_data.append({
                'original': original,
                'translation': '',
                'context': context,
                'type': text_type,
                'notes': 'Lune Engine format'
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(translation_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Created Lune translation file: {output_path}")
    
    def apply_translations(self, original_file: str, translation_file: str, output_file: str):
        """Apply translations back to Lune files"""
        try:
            # Load translations
            with open(translation_file, 'r', encoding='utf-8') as f:
                translations = json.load(f)
            
            # Create translation dictionary
            trans_dict = {}
            for item in translations:
                if item['translation'].strip():
                    trans_dict[item['original']] = item['translation']
            
            # Apply based on file type
            if self._is_binary_file(original_file):
                self._apply_binary_translations(original_file, trans_dict, output_file)
            else:
                self._apply_text_translations(original_file, trans_dict, output_file)
            
        except Exception as e:
            self.logger.error(f"Error applying Lune translations: {e}")
    
    def _apply_text_translations(self, original_file: str, trans_dict: dict, output_file: str):
        """Apply translations to text Lune file"""
        try:
            # Read original file
            encodings = ['shift-jis', 'utf-8', 'cp932']
            content = None
            used_encoding = 'shift-jis'  # Default for Lune
            
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
                content = content.replace(original, translation)
            
            # Write translated file
            with open(output_file, 'w', encoding=used_encoding) as f:
                f.write(content)
            
            self.logger.info(f"Applied text translations to: {output_file}")
            
        except Exception as e:
            self.logger.error(f"Error applying text translations: {e}")
    
    def _apply_binary_translations(self, original_file: str, trans_dict: dict, output_file: str):
        """Apply translations to binary Lune file"""
        try:
            with open(original_file, 'rb') as f:
                data = bytearray(f.read())
            
            # Apply translations to binary data
            for original, translation in trans_dict.items():
                try:
                    # Try different encodings
                    for encoding in ['shift-jis', 'cp932', 'utf-8']:
                        try:
                            original_bytes = original.encode(encoding)
                            translation_bytes = translation.encode(encoding)
                            
                            # Only replace if lengths are similar to avoid corruption
                            if len(translation_bytes) <= len(original_bytes) + 10:
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
