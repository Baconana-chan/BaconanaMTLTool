"""
Wolf RPG Editor Processor
Handles translation for Wolf RPG Editor games (.txt files and .wolf archives)
"""

import os
import re
import struct
import zlib
from typing import Dict, List, Tuple, Any, Optional
import tempfile
import shutil


class WolfProcessor:
    """Processor for Wolf RPG Editor games"""
    
    def __init__(self):
        self.supported_extensions = ['.txt', '.wolf']
        
        # Common Wolf RPG Editor text patterns
        self.text_patterns = [
            # Message text
            r'\\msg\[([^\]]+)\]',
            r'\\m\[([^\]]+)\]',
            
            # Choice text
            r'\\choice\[([^\]]+)\]',
            r'\\c\[([^\]]+)\]',
            
            # Character names
            r'\\name\[([^\]]+)\]',
            r'\\n\[([^\]]+)\]',
            
            # Description text
            r'\\desc\[([^\]]+)\]',
            r'\\d\[([^\]]+)\]',
            
            # Direct Japanese text (enclosed in quotes)
            r'"([^"]*[ひらがなカタカナ漢字々〆ヵヶ一-龯][^"]*)"',
            r"'([^']*[ひらがなカタカナ漢字々〆ヵヶ一-龯][^']*)'",
            
            # Text without quotes but with Japanese characters
            r'([ひらがなカタカナ漢字々〆ヵヶ一-龯][^\n\r\t,;:{}()[\]]*)',
        ]
        
        # Wolf archive magic numbers
        self.wolf_magic = b'DX\x00\x00'
        
    def detect_wolf_project(self, directory: str) -> bool:
        """Detect if directory contains a Wolf RPG Editor project"""
        
        # Check for Wolf RPG Editor indicators
        wolf_indicators = [
            'Game.exe',
            'Game.dat',
            'Config.exe',
            'Data',
            'BGM',
            'Picture',
            'Sound'
        ]
        
        indicator_count = 0
        for indicator in wolf_indicators:
            if os.path.exists(os.path.join(directory, indicator)):
                indicator_count += 1
        
        # Need at least 3 indicators for positive detection
        if indicator_count >= 3:
            return True
        
        # Check for .wolf files
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.wolf'):
                    return True
        
        # Check for characteristic text files
        data_dir = os.path.join(directory, 'Data')
        if os.path.exists(data_dir):
            for file in os.listdir(data_dir):
                if file.lower().endswith('.txt'):
                    file_path = os.path.join(data_dir, file)
                    if self.might_contain_japanese(file_path):
                        return True
        
        return False
    
    def find_wolf_text_files(self, directory: str) -> List[str]:
        """Find all Wolf RPG Editor text files"""
        
        text_files = []
        
        # Common Wolf RPG Editor directories
        search_dirs = [
            directory,
            os.path.join(directory, 'Data'),
            os.path.join(directory, 'Text'),
            os.path.join(directory, 'Script'),
            os.path.join(directory, 'Event'),
        ]
        
        for search_dir in search_dirs:
            if not os.path.exists(search_dir):
                continue
                
            for root, dirs, files in os.walk(search_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    if file.lower().endswith('.txt'):
                        if self.might_contain_japanese(file_path):
                            text_files.append(file_path)
                    
                    elif file.lower().endswith('.wolf'):
                        text_files.append(file_path)
        
        return text_files
    
    def might_contain_japanese(self, file_path: str) -> bool:
        """Check if file might contain Japanese text"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(1024)  # Read first 1KB
                
            # Check for Japanese characters
            japanese_pattern = r'[ひらがなカタカナ漢字々〆ヵヶ一-龯]'
            return bool(re.search(japanese_pattern, content))
            
        except Exception:
            try:
                # Try Shift-JIS encoding
                with open(file_path, 'r', encoding='shift_jis', errors='ignore') as f:
                    content = f.read(1024)
                    
                japanese_pattern = r'[ひらがなカタカナ漢字々〆ヵヶ一-龯]'
                return bool(re.search(japanese_pattern, content))
            except Exception:
                return False
    
    def extract_translatable_text(self, file_path: str) -> List[Tuple[str, str, str]]:
        """Extract translatable text from Wolf RPG Editor files"""
        
        if file_path.lower().endswith('.wolf'):
            return self._extract_from_wolf_archive(file_path)
        else:
            return self._extract_from_text_file(file_path)
    
    def _extract_from_text_file(self, file_path: str) -> List[Tuple[str, str, str]]:
        """Extract text from .txt files"""
        
        texts = []
        
        try:
            # Try UTF-8 first
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Fallback to Shift-JIS
            with open(file_path, 'r', encoding='shift_jis', errors='ignore') as f:
                content = f.read()
        
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            # Try each pattern
            for pattern in self.text_patterns:
                matches = re.findall(pattern, line)
                for match in matches:
                    if self._is_japanese_text(match):
                        key = f"line_{line_num}_{len(texts)}"
                        texts.append((key, match, file_path))
        
        return texts
    
    def _extract_from_wolf_archive(self, file_path: str) -> List[Tuple[str, str, str]]:
        """Extract text from .wolf archive files"""
        
        texts = []
        temp_dir = None
        
        try:
            # Extract wolf archive to temporary directory
            temp_dir = tempfile.mkdtemp(prefix="wolf_extract_")
            
            if self._extract_wolf_archive(file_path, temp_dir):
                # Process extracted files
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        extracted_file = os.path.join(root, file)
                        if file.lower().endswith('.txt'):
                            file_texts = self._extract_from_text_file(extracted_file)
                            texts.extend(file_texts)
            
        except Exception as e:
            print(f"Error extracting Wolf archive {file_path}: {e}")
        
        finally:
            # Cleanup
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        return texts
    
    def _extract_wolf_archive(self, wolf_file: str, output_dir: str) -> bool:
        """Extract Wolf RPG Editor archive file"""
        
        try:
            with open(wolf_file, 'rb') as f:
                # Check magic number
                magic = f.read(4)
                if magic != self.wolf_magic:
                    return False
                
                # Read archive header
                file_count = struct.unpack('<I', f.read(4))[0]
                
                # Read file entries
                files = []
                for i in range(file_count):
                    # Read filename length
                    name_len = struct.unpack('<I', f.read(4))[0]
                    
                    # Read filename
                    filename = f.read(name_len).decode('shift_jis', errors='ignore')
                    
                    # Read file size and offset
                    file_size = struct.unpack('<I', f.read(4))[0]
                    file_offset = struct.unpack('<I', f.read(4))[0]
                    
                    files.append({
                        'name': filename,
                        'size': file_size,
                        'offset': file_offset
                    })
                
                # Extract files
                for file_info in files:
                    f.seek(file_info['offset'])
                    file_data = f.read(file_info['size'])
                    
                    # Try to decompress if it's compressed
                    try:
                        file_data = zlib.decompress(file_data)
                    except zlib.error:
                        pass  # Not compressed
                    
                    # Save file
                    output_path = os.path.join(output_dir, file_info['name'])
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    
                    with open(output_path, 'wb') as out_f:
                        out_f.write(file_data)
                
                return True
                
        except Exception as e:
            print(f"Error extracting Wolf archive: {e}")
            return False
    
    def _is_japanese_text(self, text: str) -> bool:
        """Check if text contains Japanese characters"""
        if not text or len(text.strip()) < 2:
            return False
        
        japanese_pattern = r'[ひらがなカタカナ漢字々〆ヵヶ一-龯]'
        return bool(re.search(japanese_pattern, text))
    
    def create_translation_file(self, original_file: str, translations: Dict[str, str], 
                              output_dir: str, target_language: str):
        """Create translated file for Wolf RPG Editor"""
        
        # Determine output path
        rel_path = os.path.basename(original_file)
        lang_code = self._get_language_code(target_language)
        
        if original_file.lower().endswith('.wolf'):
            output_file = os.path.join(output_dir, f"{rel_path[:-5]}_{lang_code}.wolf")
            # For .wolf files, we would need to recreate the archive
            # For now, extract and create text files
            base_name = os.path.splitext(rel_path)[0]
            output_file = os.path.join(output_dir, f"{base_name}_{lang_code}.txt")
        else:
            base_name = os.path.splitext(rel_path)[0]
            output_file = os.path.join(output_dir, f"{base_name}_{lang_code}.txt")
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        try:
            # Read original file
            try:
                with open(original_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                with open(original_file, 'r', encoding='shift_jis', errors='ignore') as f:
                    content = f.read()
            
            # Apply translations
            translated_content = content
            for key, translation in translations.items():
                # Find the original text and replace it
                # This is a simplified approach
                lines = translated_content.split('\n')
                for i, line in enumerate(lines):
                    for pattern in self.text_patterns:
                        if re.search(pattern, line):
                            # Replace Japanese text with translation
                            for original_key, original_text, _ in self.extract_translatable_text(original_file):
                                if original_key == key and original_text in line:
                                    lines[i] = line.replace(original_text, translation)
                                    break
                
                translated_content = '\n'.join(lines)
            
            # Save translated file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(translated_content)
                
        except Exception as e:
            print(f"Error creating Wolf translation file: {e}")
    
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
        """Get statistics for a Wolf RPG Editor file"""
        
        try:
            file_size = os.path.getsize(file_path)
            texts = self.extract_translatable_text(file_path)
            
            japanese_texts = [text for key, text, path in texts if self._is_japanese_text(text)]
            
            # Estimate tokens (rough)
            total_chars = sum(len(text) for text in japanese_texts)
            estimated_tokens = total_chars // 3  # Rough estimate for Japanese
            
            needs_translation = len(japanese_texts) > 0
            
            return {
                'file_size': file_size,
                'total_text_entries': len(texts),
                'japanese_text_entries': len(japanese_texts),
                'estimated_tokens': estimated_tokens,
                'needs_translation': needs_translation,
                'file_type': 'Wolf RPG Editor'
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
