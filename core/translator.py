"""
Translation Manager
Handles the translation process for RPG Maker MV/MZ games, Ren'Py games, Unity projects, 
Wolf RPG Editor, KiriKiri, and NScripter games
"""

import os
import json
import glob
import threading
import time
from typing import Dict, List, Any, Optional, Tuple
from PyQt5.QtCore import QThread, pyqtSignal
from core.api_client import APIClient
from core.file_processor import FileProcessor
from core.renpy_processor import RenpyProcessor
from core.unity_processor import UnityProcessor
from core.wolf_processor import WolfProcessor
from core.kirikiri_processor import KiriKiriProcessor
from core.nscripter_processor import NScripterProcessor
from core.livemaker_processor import LiveMakerProcessor
from core.tyranobuilder_processor import TyranoBuilderProcessor
from core.srpg_studio_processor import SRPGStudioProcessor
from core.lune_processor import LuneProcessor
from core.regex_processor import RegexProcessor


class TranslationManager(QThread):
    """Manages the translation process"""
    
    # Signals for UI updates
    progress_updated = pyqtSignal(int, int, str)  # current, total, filename
    log_message = pyqtSignal(str)
    translation_complete = pyqtSignal(str, str)  # original, translated
    error_occurred = pyqtSignal(str)
    
    def __init__(self, config: Dict[str, Any], input_dir: str, output_dir: str):
        super().__init__()
        
        self.config = config
        self.input_dir = input_dir
        self.output_dir = output_dir
        
        self.api_client = APIClient(config)
        self.file_processor = FileProcessor()
        self.renpy_processor = RenpyProcessor()
        self.unity_processor = UnityProcessor()
        self.wolf_processor = WolfProcessor()
        self.kirikiri_processor = KiriKiriProcessor()
        self.nscripter_processor = NScripterProcessor()
        self.livemaker_processor = LiveMakerProcessor()
        self.tyranobuilder_processor = TyranoBuilderProcessor()
        self.srpg_studio_processor = SRPGStudioProcessor()
        self.lune_processor = LuneProcessor()
        self.regex_processor = RegexProcessor()
        
        # Detect project type
        self.is_renpy_project = self.renpy_processor.detect_renpy_project(input_dir)
        self.is_unity_project = self.unity_processor.detect_unity_project(input_dir)
        self.is_wolf_project = self.wolf_processor.detect_wolf_project(input_dir)
        self.is_kirikiri_project = self.kirikiri_processor.detect_kirikiri_project(input_dir)
        self.is_nscripter_project = self.nscripter_processor.detect_nscripter_project(input_dir)
        self.is_livemaker_project = len(self.livemaker_processor.find_livemaker_files(input_dir)) > 0
        self.is_tyranobuilder_project = len(self.tyranobuilder_processor.find_tyranobuilder_files(input_dir)) > 0
        self.is_srpg_studio_project = len(self.srpg_studio_processor.find_srpg_studio_files(input_dir)) > 0
        self.is_lune_project = len(self.lune_processor.find_lune_files(input_dir)) > 0
        self.is_regex_project = len(self.regex_processor.find_regex_files(input_dir)) > 0
        
        if self.is_renpy_project:
            self.project_type = "Ren'Py"
        elif self.is_unity_project:
            self.project_type = "Unity"
        elif self.is_wolf_project:
            self.project_type = "Wolf RPG Editor"
        elif self.is_kirikiri_project:
            self.project_type = "KiriKiri"
        elif self.is_nscripter_project:
            self.project_type = "NScripter"
        elif self.is_livemaker_project:
            self.project_type = "Live Maker"
        elif self.is_tyranobuilder_project:
            self.project_type = "TyranoBuilder"
        elif self.is_srpg_studio_project:
            self.project_type = "SRPG Studio"
        elif self.is_lune_project:
            self.project_type = "Lune"
        elif self.is_regex_project:
            self.project_type = "Regex"
        else:
            self.project_type = "RPG Maker"
        
        self.is_paused = False
        self.is_stopped = False
        self.current_file = 0
        self.total_files = 0
        
        # Thread control
        self.file_threads = int(config.get('fileThreads', 1))
        self.translation_threads = int(config.get('threads', 1))
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    def run(self):
        """Main translation process"""
        try:
            self.log_message.emit(f"Starting translation process for {self.project_type} project...")
            
            # Handle different project types
            if self.is_unity_project:
                self.process_unity_project(self.input_dir, self.output_dir, self.config['target_language'])
            elif self.is_wolf_project:
                self.process_wolf_project(self.input_dir, self.output_dir, self.config['target_language'])
            elif self.is_kirikiri_project:
                self.process_kirikiri_project(self.input_dir, self.output_dir, self.config['target_language'])
            elif self.is_nscripter_project:
                self.process_nscripter_project(self.input_dir, self.output_dir, self.config['target_language'])
            elif self.is_livemaker_project:
                self.process_livemaker_project(self.input_dir, self.output_dir, self.config['target_language'])
            elif self.is_tyranobuilder_project:
                self.process_tyranobuilder_project(self.input_dir, self.output_dir, self.config['target_language'])
            elif self.is_srpg_studio_project:
                self.process_srpg_studio_project(self.input_dir, self.output_dir, self.config['target_language'])
            elif self.is_lune_project:
                self.process_lune_project(self.input_dir, self.output_dir, self.config['target_language'])
            elif self.is_regex_project:
                self.process_regex_project(self.input_dir, self.output_dir, self.config['target_language'])
            else:
                # Handle Ren'Py and RPG Maker with file-based approach
                if self.is_renpy_project:
                    files_to_process = self.find_rpy_files()
                    file_type = ".rpy files"
                else:
                    files_to_process = self.find_json_files()
                    file_type = "JSON files"
                
                if not files_to_process:
                    self.log_message.emit(f"No {file_type} found to translate")
                    return
                
                self.total_files = len(files_to_process)
                self.log_message.emit(f"Found {self.total_files} {file_type} to process")
                
                # Process files
                for i, file_path in enumerate(files_to_process):
                    if self.is_stopped:
                        break
                    
                    while self.is_paused and not self.is_stopped:
                        time.sleep(0.1)
                    
                    self.current_file = i + 1
                    filename = os.path.basename(file_path)
                    
                    self.progress_updated.emit(self.current_file, self.total_files, filename)
                    self.log_message.emit(f"Processing: {filename}")
                    
                    try:
                        if self.is_renpy_project:
                            self.process_rpy_file(file_path)
                        else:
                            self.process_json_file(file_path)
                        self.log_message.emit(f"Completed: {filename}")
                    except Exception as e:
                        error_msg = f"Error processing {filename}: {str(e)}"
                        self.log_message.emit(error_msg)
                        self.error_occurred.emit(error_msg)
            
            if not self.is_stopped:
                self.log_message.emit("Translation process completed successfully!")
            else:
                self.log_message.emit("Translation process was stopped")
                
        except Exception as e:
            error_msg = f"Critical error in translation process: {str(e)}"
            self.log_message.emit(error_msg)
            self.error_occurred.emit(error_msg)
    
    def find_json_files(self) -> List[str]:
        """Find all JSON files in the input directory"""
        json_files = []
        
        # Common RPG Maker file patterns
        patterns = [
            "**/*.json",
            "**/Map*.json",
            "**/data/*.json"
        ]
        
        # Exclude system files that shouldn't be translated
        exclude_patterns = [
            "System.json",
            "Tilesets.json",
            "Animations.json",
            "States.json",
            "Skills.json",
            "Items.json",
            "Weapons.json",
            "Armors.json",
            "Enemies.json",
            "Troops.json",
            "Classes.json",
            "Actors.json"
        ]
        
        for pattern in patterns:
            search_path = os.path.join(self.input_dir, pattern)
            found_files = glob.glob(search_path, recursive=True)
            
            for file_path in found_files:
                filename = os.path.basename(file_path)
                
                # Skip excluded files
                if any(exclude in filename for exclude in exclude_patterns):
                    continue
                
                # Only add if not already in list
                if file_path not in json_files:
                    json_files.append(file_path)
        
        return sorted(json_files)
    
    def find_rpy_files(self) -> List[str]:
        """Find all .rpy files in the game directory"""
        return self.renpy_processor.find_rpy_files(self.input_dir)
    
    def process_json_file(self, file_path: str):
        """Process a single JSON file (RPG Maker)"""
        return self.process_file(file_path)
    
    def process_rpy_file(self, file_path: str):
        """Process a single .rpy file (Ren'Py)"""
        try:
            # Check if file needs translation
            if not self.renpy_processor.needs_translation(file_path):
                self.log_message.emit(f"Skipping {os.path.basename(file_path)} - no translatable content")
                return
            
            # Extract translatable text
            translatable_texts = self.renpy_processor.extract_translatable_text(file_path)
            
            if not translatable_texts:
                self.log_message.emit(f"No translatable text found in {os.path.basename(file_path)}")
                return
            
            # Convert to simple list for translation
            texts_to_translate = [text for text, context, line_num in translatable_texts]
            
            self.log_message.emit(f"Found {len(texts_to_translate)} strings to translate in {os.path.basename(file_path)}")
            
            # Translate the texts
            translated_texts = self.translate_texts(texts_to_translate)
            
            # Create translation mapping
            translation_map = {}
            for i, (original_text, context, line_num) in enumerate(translatable_texts):
                if i < len(translated_texts):
                    translation_map[original_text] = translated_texts[i]
                    self.log_message.emit(f"Line {line_num}: '{original_text[:50]}...' -> '{translated_texts[i][:50]}...'")
            
            # Create Ren'Py translation file
            game_dir = os.path.join(self.input_dir, 'game')
            target_language = self.config.get('language', 'English')
            
            translation_file = self.renpy_processor.create_translation_file(
                file_path, translation_map, target_language, game_dir
            )
            
            self.log_message.emit(f"Created translation file: {translation_file}")
            
        except Exception as e:
            raise Exception(f"Failed to process Ren'Py file {file_path}: {str(e)}")
    
    def process_file(self, file_path: str):
        """Process a single JSON file"""
        try:
            # Read the JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if file needs translation
            if not self.file_processor.needs_translation(data):
                self.log_message.emit(f"Skipping {os.path.basename(file_path)} - no translatable content")
                return
            
            # Extract translatable text
            translatable_texts = self.file_processor.extract_translatable_text(data)
            
            if not translatable_texts:
                self.log_message.emit(f"No translatable text found in {os.path.basename(file_path)}")
                return
            
            # Translate the texts
            translated_texts = self.translate_texts(translatable_texts)
            
            # Apply translations back to data
            translated_data = self.file_processor.apply_translations(data, translated_texts)
            
            # Save translated file
            output_path = self.get_output_path(file_path)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(translated_data, f, ensure_ascii=False, indent=2)
            
            self.log_message.emit(f"Saved translated file: {output_path}")
            
        except Exception as e:
            raise Exception(f"Failed to process file {file_path}: {str(e)}")
    
    def translate_texts(self, texts: List[str]) -> List[str]:
        """Translate a list of texts using the API"""
        batch_size = int(self.config.get('batchsize', 10))
        translated_texts = []
        
        self.log_message.emit(f"Starting translation of {len(texts)} text strings in batches of {batch_size}")
        
        # Process texts in batches
        for i in range(0, len(texts), batch_size):
            if self.is_stopped:
                break
                
            while self.is_paused and not self.is_stopped:
                time.sleep(0.1)
            
            batch = texts[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(texts) + batch_size - 1) // batch_size
            
            self.log_message.emit(f"Processing batch {batch_num}/{total_batches} ({len(batch)} strings)")
            
            # Log first few lines being translated for debugging
            if len(batch) > 0:
                preview = batch[0][:100] + "..." if len(batch[0]) > 100 else batch[0]
                self.log_message.emit(f"Translating: {preview}")
            
            try:
                # Prepare batch for translation
                batch_dict = {f"Line{j+1}": text for j, text in enumerate(batch)}
                
                # Get translation from API
                self.log_message.emit(f"Sending request to {self.config.get('model', 'API')}...")
                translated_batch = self.api_client.translate_batch(batch_dict)
                
                # Extract translated texts in order
                successful_translations = 0
                for j in range(len(batch)):
                    key = f"Line{j+1}"
                    if key in translated_batch:
                        translated_text = translated_batch[key]
                        translated_texts.append(translated_text)
                        successful_translations += 1
                        
                        # Log translation preview for first item in batch
                        if j == 0:
                            preview = translated_text[:100] + "..." if len(translated_text) > 100 else translated_text
                            self.log_message.emit(f"Translation result: {preview}")
                    else:
                        # Fallback to original if translation failed
                        translated_texts.append(batch[j])
                        self.log_message.emit(f"Translation failed for: {batch[j][:50]}...")
                
                self.log_message.emit(f"Batch completed: {successful_translations}/{len(batch)} translations successful")
                
                # Small delay to avoid hitting rate limits
                time.sleep(0.1)
                
            except Exception as e:
                error_msg = str(e)
                self.log_message.emit(f"Batch translation error: {error_msg}")
                
                # Check for specific error types
                if "rate limit" in error_msg.lower():
                    self.log_message.emit("Rate limit detected - waiting 60 seconds...")
                    time.sleep(60)
                elif "quota" in error_msg.lower():
                    self.log_message.emit("API quota exceeded - stopping translation")
                    self.is_stopped = True
                    break
                elif "unauthorized" in error_msg.lower():
                    self.log_message.emit("API key invalid or unauthorized - stopping translation")
                    self.is_stopped = True
                    break
                
                # Add original texts as fallback
                translated_texts.extend(batch)
        
        self.log_message.emit(f"Translation completed: {len(translated_texts)} strings processed")
        return translated_texts
    
    def get_output_path(self, input_path: str) -> str:
        """Get output path for translated file"""
        rel_path = os.path.relpath(input_path, self.input_dir)
        return os.path.join(self.output_dir, rel_path)
    
    def pause(self):
        """Pause the translation process"""
        self.is_paused = True
    
    def resume(self):
        """Resume the translation process"""
        self.is_paused = False
    
    def stop(self):
        """Stop the translation process"""
        self.is_stopped = True
        self.is_paused = False
    
    def detect_unity_project(self, game_dir: str) -> bool:
        """Detect if this is a Unity project"""
        unity_processor = UnityProcessor()
        return unity_processor.detect_unity_project(game_dir)
    
    def process_unity_project(self, game_dir: str, output_dir: str, target_language: str):
        """Process Unity localization files"""
        try:
            unity_processor = UnityProcessor()
            
            # Extract translatable texts
            self.log_message.emit("Extracting texts from Unity localization files...")
            translatable_files = unity_processor.find_unity_text_files(game_dir)
            
            if not translatable_files:
                self.log_message.emit("No Unity localization files found")
                return
            
            self.log_message.emit(f"Found {len(translatable_files)} localization files")
            
            for file_path in translatable_files:
                if self.is_stopped:
                    break
                
                while self.is_paused and not self.is_stopped:
                    time.sleep(0.1)
                
                filename = os.path.basename(file_path)
                self.log_message.emit(f"Processing Unity file: {filename}")
                
                # Extract texts
                texts_to_translate = unity_processor.extract_translatable_text(file_path)
                
                if not texts_to_translate:
                    self.log_message.emit(f"No translatable texts found in {filename}")
                    continue
                
                self.log_message.emit(f"Found {len(texts_to_translate)} translatable texts in {filename}")
                
                # Translate texts
                text_list = [text for key, text, file_path in texts_to_translate]
                translated_texts = self.translate_texts(text_list)
                
                # Create translation mapping
                translation_map = {}
                for i, (key, text, _) in enumerate(texts_to_translate):
                    if i < len(translated_texts):
                        translation_map[key] = translated_texts[i]
                
                # Apply translations and save
                unity_processor.create_translation_file(file_path, translation_map, output_dir, target_language)
                self.log_message.emit(f"Saved translated file: {filename}")
                
        except Exception as e:
            self.log_message.emit(f"Error processing Unity project: {str(e)}")
            raise
    
    def process_wolf_project(self, game_dir: str, output_dir: str, target_language: str):
        """Process Wolf RPG Editor files"""
        try:
            wolf_processor = WolfProcessor()
            
            self.log_message.emit("Extracting texts from Wolf RPG Editor files...")
            wolf_files = wolf_processor.find_wolf_text_files(game_dir)
            
            if not wolf_files:
                self.log_message.emit("No Wolf RPG Editor files found")
                return
            
            self.log_message.emit(f"Found {len(wolf_files)} Wolf files")
            
            for file_path in wolf_files:
                if self.is_stopped:
                    break
                
                while self.is_paused and not self.is_stopped:
                    time.sleep(0.1)
                
                filename = os.path.basename(file_path)
                self.log_message.emit(f"Processing Wolf file: {filename}")
                
                texts_to_translate = wolf_processor.extract_translatable_text(file_path)
                
                if not texts_to_translate:
                    self.log_message.emit(f"No translatable texts found in {filename}")
                    continue
                
                self.log_message.emit(f"Found {len(texts_to_translate)} translatable texts in {filename}")
                
                text_list = [text for key, text, file_path in texts_to_translate]
                translated_texts = self.translate_texts(text_list)
                
                translation_map = {}
                for i, (key, text, _) in enumerate(texts_to_translate):
                    if i < len(translated_texts):
                        translation_map[key] = translated_texts[i]
                
                wolf_processor.create_translation_file(file_path, translation_map, output_dir, target_language)
                self.log_message.emit(f"Saved translated file: {filename}")
                
        except Exception as e:
            self.log_message.emit(f"Error processing Wolf project: {str(e)}")
            raise
    
    def process_kirikiri_project(self, game_dir: str, output_dir: str, target_language: str):
        """Process KiriKiri files"""
        try:
            kirikiri_processor = KiriKiriProcessor()
            
            self.log_message.emit("Extracting texts from KiriKiri files...")
            kirikiri_files = kirikiri_processor.find_kirikiri_text_files(game_dir)
            
            if not kirikiri_files:
                self.log_message.emit("No KiriKiri files found")
                return
            
            self.log_message.emit(f"Found {len(kirikiri_files)} KiriKiri files")
            
            for file_path in kirikiri_files:
                if self.is_stopped:
                    break
                
                while self.is_paused and not self.is_stopped:
                    time.sleep(0.1)
                
                filename = os.path.basename(file_path)
                self.log_message.emit(f"Processing KiriKiri file: {filename}")
                
                texts_to_translate = kirikiri_processor.extract_translatable_text(file_path)
                
                if not texts_to_translate:
                    self.log_message.emit(f"No translatable texts found in {filename}")
                    continue
                
                self.log_message.emit(f"Found {len(texts_to_translate)} translatable texts in {filename}")
                
                text_list = [text for key, text, file_path in texts_to_translate]
                translated_texts = self.translate_texts(text_list)
                
                translation_map = {}
                for i, (key, text, _) in enumerate(texts_to_translate):
                    if i < len(translated_texts):
                        translation_map[key] = translated_texts[i]
                
                kirikiri_processor.create_translation_file(file_path, translation_map, output_dir, target_language)
                self.log_message.emit(f"Saved translated file: {filename}")
                
        except Exception as e:
            self.log_message.emit(f"Error processing KiriKiri project: {str(e)}")
            raise
    
    def process_nscripter_project(self, game_dir: str, output_dir: str, target_language: str):
        """Process NScripter files"""
        try:
            nscripter_processor = NScripterProcessor()
            
            self.log_message.emit("Extracting texts from NScripter files...")
            nscripter_files = nscripter_processor.find_nscripter_text_files(game_dir)
            
            if not nscripter_files:
                self.log_message.emit("No NScripter files found")
                return
            
            self.log_message.emit(f"Found {len(nscripter_files)} NScripter files")
            
            for file_path in nscripter_files:
                if self.is_stopped:
                    break
                
                while self.is_paused and not self.is_stopped:
                    time.sleep(0.1)
                
                filename = os.path.basename(file_path)
                self.log_message.emit(f"Processing NScripter file: {filename}")
                
                texts_to_translate = nscripter_processor.extract_translatable_text(file_path)
                
                if not texts_to_translate:
                    self.log_message.emit(f"No translatable texts found in {filename}")
                    continue
                
                self.log_message.emit(f"Found {len(texts_to_translate)} translatable texts in {filename}")
                
                text_list = [text for key, text, file_path in texts_to_translate]
                translated_texts = self.translate_texts(text_list)
                
                translation_map = {}
                for i, (key, text, _) in enumerate(texts_to_translate):
                    if i < len(translated_texts):
                        translation_map[key] = translated_texts[i]
                
                nscripter_processor.create_translation_file(file_path, translation_map, output_dir, target_language)
                self.log_message.emit(f"Saved translated file: {filename}")
                
        except Exception as e:
            self.log_message.emit(f"Error processing NScripter project: {str(e)}")
            raise
    
    def process_livemaker_project(self, game_dir: str, output_dir: str, target_language: str):
        """Process Live Maker project files"""
        try:
            livemaker_processor = self.livemaker_processor
            files_to_process = livemaker_processor.find_livemaker_files(game_dir)
            
            if not files_to_process:
                self.log_message.emit("No Live Maker files found to translate")
                return
            
            self.total_files = len(files_to_process)
            self.log_message.emit(f"Found {self.total_files} Live Maker files to process")
            
            os.makedirs(output_dir, exist_ok=True)
            
            for i, file_path in enumerate(files_to_process):
                if self.is_stopped:
                    break
                
                while self.is_paused and not self.is_stopped:
                    time.sleep(0.1)
                
                self.current_file = i + 1
                self.progress_updated.emit(self.current_file, self.total_files, os.path.basename(file_path))
                
                filename = os.path.basename(file_path)
                self.log_message.emit(f"Processing Live Maker file: {filename}")
                
                texts_to_translate = livemaker_processor.extract_translatable_text(file_path)
                
                if not texts_to_translate:
                    self.log_message.emit(f"No translatable texts found in {filename}")
                    continue
                
                self.log_message.emit(f"Found {len(texts_to_translate)} translatable texts in {filename}")
                
                text_list = [text for text, context, text_type in texts_to_translate]
                translated_texts = self.translate_texts(text_list)
                
                # Create translation file
                translation_data = []
                for i, (original, context, text_type) in enumerate(texts_to_translate):
                    translation = translated_texts[i] if i < len(translated_texts) else original
                    translation_data.append((original, translation, context))
                
                output_file = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}_translation.json")
                livemaker_processor.create_translation_file(translation_data, output_file)
                self.log_message.emit(f"Saved translated file: {os.path.basename(output_file)}")
                
        except Exception as e:
            self.log_message.emit(f"Error processing Live Maker project: {str(e)}")
            raise
    
    def process_tyranobuilder_project(self, game_dir: str, output_dir: str, target_language: str):
        """Process TyranoBuilder project files"""
        try:
            tyranobuilder_processor = self.tyranobuilder_processor
            files_to_process = tyranobuilder_processor.find_tyranobuilder_files(game_dir)
            
            if not files_to_process:
                self.log_message.emit("No TyranoBuilder files found to translate")
                return
            
            self.total_files = len(files_to_process)
            self.log_message.emit(f"Found {self.total_files} TyranoBuilder files to process")
            
            os.makedirs(output_dir, exist_ok=True)
            
            for i, file_path in enumerate(files_to_process):
                if self.is_stopped:
                    break
                
                while self.is_paused and not self.is_stopped:
                    time.sleep(0.1)
                
                self.current_file = i + 1
                self.progress_updated.emit(self.current_file, self.total_files, os.path.basename(file_path))
                
                filename = os.path.basename(file_path)
                self.log_message.emit(f"Processing TyranoBuilder file: {filename}")
                
                texts_to_translate = tyranobuilder_processor.extract_translatable_text(file_path)
                
                if not texts_to_translate:
                    self.log_message.emit(f"No translatable texts found in {filename}")
                    continue
                
                self.log_message.emit(f"Found {len(texts_to_translate)} translatable texts in {filename}")
                
                text_list = [text for text, context, text_type in texts_to_translate]
                translated_texts = self.translate_texts(text_list)
                
                # Create translation file
                translation_data = []
                for i, (original, context, text_type) in enumerate(texts_to_translate):
                    translation = translated_texts[i] if i < len(translated_texts) else original
                    translation_data.append((original, translation, context))
                
                output_file = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}_translation.json")
                tyranobuilder_processor.create_translation_file(translation_data, output_file)
                self.log_message.emit(f"Saved translated file: {os.path.basename(output_file)}")
                
        except Exception as e:
            self.log_message.emit(f"Error processing TyranoBuilder project: {str(e)}")
            raise
    
    def process_srpg_studio_project(self, game_dir: str, output_dir: str, target_language: str):
        """Process SRPG Studio project files"""
        try:
            srpg_processor = self.srpg_studio_processor
            files_to_process = srpg_processor.find_srpg_studio_files(game_dir)
            
            if not files_to_process:
                self.log_message.emit("No SRPG Studio files found to translate")
                return
            
            self.total_files = len(files_to_process)
            self.log_message.emit(f"Found {self.total_files} SRPG Studio files to process")
            
            os.makedirs(output_dir, exist_ok=True)
            
            for i, file_path in enumerate(files_to_process):
                if self.is_stopped:
                    break
                
                while self.is_paused and not self.is_stopped:
                    time.sleep(0.1)
                
                self.current_file = i + 1
                self.progress_updated.emit(self.current_file, self.total_files, os.path.basename(file_path))
                
                filename = os.path.basename(file_path)
                self.log_message.emit(f"Processing SRPG Studio file: {filename}")
                
                texts_to_translate = srpg_processor.extract_translatable_text(file_path)
                
                if not texts_to_translate:
                    self.log_message.emit(f"No translatable texts found in {filename}")
                    continue
                
                self.log_message.emit(f"Found {len(texts_to_translate)} translatable texts in {filename}")
                
                text_list = [text for text, context, text_type in texts_to_translate]
                translated_texts = self.translate_texts(text_list)
                
                # Create translation file
                translation_data = []
                for i, (original, context, text_type) in enumerate(texts_to_translate):
                    translation = translated_texts[i] if i < len(translated_texts) else original
                    translation_data.append((original, translation, context))
                
                output_file = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}_translation.json")
                srpg_processor.create_translation_file(translation_data, output_file)
                self.log_message.emit(f"Saved translated file: {os.path.basename(output_file)}")
                
        except Exception as e:
            self.log_message.emit(f"Error processing SRPG Studio project: {str(e)}")
            raise
    
    def process_lune_project(self, game_dir: str, output_dir: str, target_language: str):
        """Process Lune project files"""
        try:
            lune_processor = self.lune_processor
            files_to_process = lune_processor.find_lune_files(game_dir)
            
            if not files_to_process:
                self.log_message.emit("No Lune files found to translate")
                return
            
            self.total_files = len(files_to_process)
            self.log_message.emit(f"Found {self.total_files} Lune files to process")
            
            os.makedirs(output_dir, exist_ok=True)
            
            for i, file_path in enumerate(files_to_process):
                if self.is_stopped:
                    break
                
                while self.is_paused and not self.is_stopped:
                    time.sleep(0.1)
                
                self.current_file = i + 1
                self.progress_updated.emit(self.current_file, self.total_files, os.path.basename(file_path))
                
                filename = os.path.basename(file_path)
                self.log_message.emit(f"Processing Lune file: {filename}")
                
                texts_to_translate = lune_processor.extract_translatable_text(file_path)
                
                if not texts_to_translate:
                    self.log_message.emit(f"No translatable texts found in {filename}")
                    continue
                
                self.log_message.emit(f"Found {len(texts_to_translate)} translatable texts in {filename}")
                
                text_list = [text for text, context, text_type in texts_to_translate]
                translated_texts = self.translate_texts(text_list)
                
                # Create translation file
                translation_data = []
                for i, (original, context, text_type) in enumerate(texts_to_translate):
                    translation = translated_texts[i] if i < len(translated_texts) else original
                    translation_data.append((original, translation, context))
                
                output_file = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}_translation.json")
                lune_processor.create_translation_file(translation_data, output_file)
                self.log_message.emit(f"Saved translated file: {os.path.basename(output_file)}")
                
        except Exception as e:
            self.log_message.emit(f"Error processing Lune project: {str(e)}")
            raise
    
    def process_regex_project(self, game_dir: str, output_dir: str, target_language: str):
        """Process Regex project files"""
        try:
            regex_processor = self.regex_processor
            files_to_process = regex_processor.find_regex_files(game_dir)
            
            if not files_to_process:
                self.log_message.emit("No Regex files found to translate")
                return
            
            self.total_files = len(files_to_process)
            self.log_message.emit(f"Found {self.total_files} Regex files to process")
            
            os.makedirs(output_dir, exist_ok=True)
            
            for i, file_path in enumerate(files_to_process):
                if self.is_stopped:
                    break
                
                while self.is_paused and not self.is_stopped:
                    time.sleep(0.1)
                
                self.current_file = i + 1
                self.progress_updated.emit(self.current_file, self.total_files, os.path.basename(file_path))
                
                filename = os.path.basename(file_path)
                self.log_message.emit(f"Processing Regex file: {filename}")
                
                texts_to_translate = regex_processor.extract_translatable_text(file_path)
                
                if not texts_to_translate:
                    self.log_message.emit(f"No translatable texts found in {filename}")
                    continue
                
                self.log_message.emit(f"Found {len(texts_to_translate)} translatable texts in {filename}")
                
                text_list = [text for text, context, text_type in texts_to_translate]
                translated_texts = self.translate_texts(text_list)
                
                # Create translation file
                translation_data = []
                for i, (original, context, text_type) in enumerate(texts_to_translate):
                    translation = translated_texts[i] if i < len(translated_texts) else original
                    translation_data.append((original, translation, context))
                
                output_file = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}_translation.json")
                regex_processor.create_translation_file(translation_data, output_file)
                self.log_message.emit(f"Saved translated file: {os.path.basename(output_file)}")
                
        except Exception as e:
            self.log_message.emit(f"Error processing Regex project: {str(e)}")
            raise
