"""
NScripter Processor
Handles translation for NScripter games (.nscript, .txt, .dat files)
"""

import os
import re
import struct
from typing import Dict, List, Tuple, Any


class NScripterProcessor:
    """Processor for NScripter engine games"""
    
    def __init__(self):
        self.supported_extensions = ['.txt', '.nscript', '.dat']
        
        # NScripter command patterns
        self.text_patterns = [
            # Message text in quotes
            r'"([^"]*[ひらがなカタカナ漢字々〆ヵヶ一-龯][^"]*)"',
            r"'([^']*[ひらがなカタカナ漢字々〆ヵヶ一-龯][^']*)'",
            
            # Text commands
            r'text\s+"([^"]*)"',
            r'mes\s+"([^"]*)"',
            r'say\s+"([^"]*)"',
            
            # Menu choices
            r'menu\s+"([^"]*)"',
            r'choice\s+"([^"]*)"',
            r'select\s+"([^"]*)"',
            
            # Character names
            r'name\s+"([^"]*)"',
            r'setname\s+"([^"]*)"',
            
            # Window text
            r'window\s+"([^"]*)"',
            r'caption\s+"([^"]*)"',
            
            # Variables with Japanese text
            r'\$([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*"([^"]*[ひらがなカタカナ漢字々〆ヵヶ一-龯][^"]*)"',
            
            # Direct Japanese text at line start
            r'^([ひらがなカタカナ漢字々〆ヵヶ一-龯][^\n\r]*)',
            
            # Text in brackets
            r'\[([^\]]*[ひらがなカタカナ漢字々〆ヵヶ一-龯][^\]]*)\]',
            
            # NScripter specific commands
            r'print\s+"([^"]*)"',
            r'puttext\s+"([^"]*)"',
            r'drawtext\s+"([^"]*)"',
        ]
        
        # Common NScripter file signatures
        self.nscripter_signatures = [
            b'NScripter',
            b'ONScripter',
            b'\x1a\x1a\x1a\x1a',  # Common dat file signature
        ]
    
    def detect_nscripter_project(self, directory: str) -> bool:
        """Detect if directory contains an NScripter project"""
        
        # Check for NScripter indicators
        nscripter_indicators = [
            'nscript.exe',
            'onscripter.exe',
            'nscripter.exe',
            '0.txt',
            '00.txt',
            'nscript.dat',
            'arc.nsa',
            'default.ttf'
        ]
        
        for indicator in nscripter_indicators:
            if os.path.exists(os.path.join(directory, indicator)):
                return True
        
        # Check for numbered text files (common in NScripter)
        numbered_files = 0
        for i in range(100):
            filename = f"{i}.txt"
            if os.path.exists(os.path.join(directory, filename)):
                numbered_files += 1
                if numbered_files >= 3:  # Multiple numbered files indicate NScripter
                    return True
        
        # Check for .nscript files
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(('.nscript', '.dat')):
                    return True
        
        return False
    
    def find_nscripter_text_files(self, directory: str) -> List[str]:
        """Find all NScripter text files"""
        
        text_files = []
        
        # Search for script files
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                
                if file.lower().endswith('.txt'):
                    if self.might_contain_japanese(file_path):
                        text_files.append(file_path)
                
                elif file.lower().endswith('.nscript'):
                    text_files.append(file_path)
                
                elif file.lower().endswith('.dat'):
                    if self._is_nscripter_dat(file_path):
                        text_files.append(file_path)
        
        return text_files
    
    def might_contain_japanese(self, file_path: str) -> bool:
        """Check if file might contain Japanese text"""
        try:
            # Try different encodings
            for encoding in ['utf-8', 'shift_jis', 'cp932']:
                try:
                    with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                        content = f.read(1024)
                    
                    japanese_pattern = r'[ひらがなカタカナ漢字々〆ヵヶ一-龯]'
                    if re.search(japanese_pattern, content):
                        return True
                except Exception:
                    continue
            
            return False
            
        except Exception:
            return False
    
    def _is_nscripter_dat(self, file_path: str) -> bool:
        """Check if .dat file is an NScripter data file"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(16)
                
            for signature in self.nscripter_signatures:
                if signature in header:
                    return True
            
            return False
            
        except Exception:
            return False
    
    def extract_translatable_text(self, file_path: str) -> List[Tuple[str, str, str]]:
        """Extract translatable text from NScripter files"""
        
        if file_path.lower().endswith('.dat'):
            return self._extract_from_dat_file(file_path)
        else:
            return self._extract_from_text_file(file_path)
    
    def _extract_from_text_file(self, file_path: str) -> List[Tuple[str, str, str]]:
        """Extract text from .txt or .nscript files"""
        
        texts = []
        
        try:
            # Try different encodings
            content = None
            for encoding in ['utf-8', 'shift_jis', 'cp932']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if not content:
                return texts
            
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith(';'):  # Skip empty lines and comments
                    continue
                
                # Try each pattern
                for pattern in self.text_patterns:
                    matches = re.findall(pattern, line, re.MULTILINE)
                    
                    if isinstance(matches[0] if matches else None, tuple):
                        # Handle patterns that return tuples (variable assignments)
                        for match_tuple in matches:
                            for match in match_tuple[1:]:  # Skip variable name
                                if self._is_japanese_text(match):
                                    key = f"line_{line_num}_{len(texts)}"
                                    texts.append((key, match, file_path))
                    else:
                        # Handle patterns that return strings
                        for match in matches:
                            if self._is_japanese_text(match):
                                key = f"line_{line_num}_{len(texts)}"
                                texts.append((key, match, file_path))
        
        except Exception as e:
            print(f"Error extracting from NScripter file {file_path}: {e}")
        
        return texts
    
    def _extract_from_dat_file(self, file_path: str) -> List[Tuple[str, str, str]]:
        """Extract text from .dat files (simplified implementation)"""
        
        texts = []
        
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # Try to decode as text with different encodings
            for encoding in ['shift_jis', 'cp932', 'utf-8']:
                try:
                    text_content = data.decode(encoding, errors='ignore')
                    
                    # Look for Japanese text patterns
                    japanese_pattern = r'[ひらがなカタカナ漢字々〆ヵヶ一-龯][^\x00-\x1f\x7f-\x9f]*'
                    matches = re.findall(japanese_pattern, text_content)
                    
                    for i, match in enumerate(matches):
                        if len(match.strip()) >= 2:
                            key = f"dat_{i}"
                            texts.append((key, match.strip(), file_path))
                    
                    break  # Use first successful encoding
                    
                except Exception:
                    continue
        
        except Exception as e:
            print(f"Error extracting from NScripter DAT file {file_path}: {e}")
        
        return texts
    
    def _is_japanese_text(self, text: str) -> bool:
        """Check if text contains Japanese characters"""
        if not text or len(text.strip()) < 2:
            return False
        
        japanese_pattern = r'[ひらがなカタカナ漢字々〆ヵヶ一-龯]'
        return bool(re.search(japanese_pattern, text))
    
    def create_translation_file(self, original_file: str, translations: Dict[str, str], 
                              output_dir: str, target_language: str):
        """Create translated file for NScripter"""
        
        # Determine output path
        rel_path = os.path.basename(original_file)
        lang_code = self._get_language_code(target_language)
        base_name = os.path.splitext(rel_path)[0]
        ext = os.path.splitext(rel_path)[1]
        
        output_file = os.path.join(output_dir, f"{base_name}_{lang_code}{ext}")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        try:
            if original_file.lower().endswith('.dat'):
                # For .dat files, create a text file instead
                output_file = os.path.join(output_dir, f"{base_name}_{lang_code}.txt")
                with open(output_file, 'w', encoding='utf-8') as f:
                    for key, translation in translations.items():
                        f.write(f"{key}: {translation}\n")
            else:
                # Read original file
                content = None
                for encoding in ['utf-8', 'shift_jis', 'cp932']:
                    try:
                        with open(original_file, 'r', encoding=encoding) as f:
                            content = f.read()
                        break
                    except UnicodeDecodeError:
                        continue
                
                if not content:
                    return
                
                # Apply translations
                translated_content = content
                original_texts = self.extract_translatable_text(original_file)
                
                for key, translation in translations.items():
                    for orig_key, orig_text, _ in original_texts:
                        if orig_key == key:
                            translated_content = translated_content.replace(orig_text, translation)
                            break
                
                # Save translated file
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(translated_content)
                
        except Exception as e:
            print(f"Error creating NScripter translation file: {e}")
    
    def _get_language_code(self, language: str) -> str:
        """Get language code for file naming"""
        language_codes = {
            'English': 'en',
            'Russian': 'ru',
            'Spanish': 'es',
            'French': 'fr',
            'German': 'de',
            'Chinese': 'zh',
            'Korean': 'ko'
        }
        return language_codes.get(language, 'en')
    
    def get_file_stats(self, file_path: str) -> Dict[str, Any]:
        """Get statistics for an NScripter file"""
        
        try:
            file_size = os.path.getsize(file_path)
            texts = self.extract_translatable_text(file_path)
            
            japanese_texts = [text for key, text, path in texts if self._is_japanese_text(text)]
            
            # Estimate tokens
            total_chars = sum(len(text) for text in japanese_texts)
            estimated_tokens = total_chars // 3
            
            needs_translation = len(japanese_texts) > 0
            
            return {
                'file_size': file_size,
                'total_text_entries': len(texts),
                'japanese_text_entries': len(japanese_texts),
                'estimated_tokens': estimated_tokens,
                'needs_translation': needs_translation,
                'file_type': 'NScripter'
            }
            
        except Exception as e:
            return {
                'file_size': 0,
                'total_text_entries': 0,
                'japanese_text_entries': 0,
                'estimated_tokens': 0,
                'needs_translation': False,
                'error': str(e)
            }
