"""
Optimized RPG Maker File Editor for Large Files
Handles CommonEvents.json and other large RPG Maker files efficiently
"""

import json
import re
import os
from pathlib import Path
from typing import Dict, List, Any, Set, Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QListWidget, QListWidgetItem, QGroupBox, QProgressBar,
    QFileDialog, QMessageBox, QSpinBox, QApplication,
    QComboBox, QCheckBox, QSplitter, QAbstractItemView
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QTextCursor, QTextCharFormat, QColor


class TextProcessingThread(QThread):
    """Background thread for processing large text files"""
    progress_updated = pyqtSignal(int, str)
    chunk_processed = pyqtSignal(int, list)  # chunk_index, text_entries
    finished_processing = pyqtSignal(int)  # total_entries
    
    def __init__(self, file_data, enabled_codes, chunk_size=100):
        super().__init__()
        self.file_data = file_data
        self.enabled_codes = enabled_codes
        self.chunk_size = chunk_size
        self.japanese_pattern = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+')
        
    def run(self):
        """Process file data in chunks - flexible for any JSON structure"""
        try:
            total_entries = 0
            
            # Handle different file structures
            events_to_process = []
            
            if isinstance(self.file_data, dict):
                # Check for Map files (events field)
                if 'events' in self.file_data and isinstance(self.file_data['events'], list):
                    # Map file structure - process events
                    events_to_process = [event for event in self.file_data['events'] if event is not None]
                    self.progress_updated.emit(10, f"Detected Map file with {len(events_to_process)} events")
                
                # Check for CommonEvents structure
                elif 'data' in self.file_data and isinstance(self.file_data['data'], list):
                    # Standard RPG Maker structure (CommonEvents, etc)
                    events_to_process = [event for event in self.file_data['data'] if event is not None]
                    self.progress_updated.emit(10, f"Detected data file with {len(events_to_process)} events")
                
                # Check for direct event list at root
                elif 'list' in self.file_data and isinstance(self.file_data['list'], list):
                    # Single event structure
                    events_to_process = [self.file_data]
                    self.progress_updated.emit(10, "Detected single event structure")
                
                else:
                    # Treat the entire dict as a single event-like structure
                    events_to_process = [self.file_data]
                    self.progress_updated.emit(10, "Detected custom structure")
                    
            elif isinstance(self.file_data, list):
                # File is a direct array
                events_to_process = [event for event in self.file_data if event is not None]
                self.progress_updated.emit(10, f"Detected array with {len(events_to_process)} items")
            
            if not events_to_process:
                self.progress_updated.emit(100, "No processable events found")
                self.finished_processing.emit(0)
                return
            
            total_events = len(events_to_process)
            self.progress_updated.emit(0, f"Processing {total_events} events...")
            
            for i in range(0, total_events, self.chunk_size):
                chunk = events_to_process[i:i + self.chunk_size]
                chunk_entries = []
                
                for event_index, event in enumerate(chunk):
                    if isinstance(event, dict):
                        # Try different ways to extract text from the event
                        event_id = event.get('id', i + event_index)
                        event_name = event.get('name', f'Event {event_id}')
                        
                        # Handle Map files - events have pages with lists
                        if 'pages' in event and isinstance(event['pages'], list):
                            for page_index, page in enumerate(event['pages']):
                                if isinstance(page, dict) and 'list' in page and isinstance(page['list'], list):
                                    self._process_event_list(page['list'], event_id, f"{event_name} (Page {page_index})", chunk_entries)
                        
                        # Look for event lists (standard RPG Maker structure - CommonEvents, etc.)
                        elif 'list' in event and isinstance(event['list'], list):
                            self._process_event_list(event['list'], event_id, event_name, chunk_entries)
                        
                        # Also look for any text directly in the event object (names, descriptions, etc.)
                        self._process_object_text(event, event_id, event_name, chunk_entries)
                
                # Emit chunk results
                if chunk_entries:
                    self.chunk_processed.emit(i // self.chunk_size, chunk_entries)
                    total_entries += len(chunk_entries)
                
                # Update progress
                progress = int((i + len(chunk)) / total_events * 100)
                self.progress_updated.emit(progress, f"Processed {i + len(chunk)}/{total_events} events...")
                
                # Allow GUI to update
                self.msleep(10)
            
            self.progress_updated.emit(100, f"Processing complete! Found {total_entries} text entries")
            self.finished_processing.emit(total_entries)
            
        except Exception as e:
            self.progress_updated.emit(0, f"Processing error: {str(e)}")
            self.finished_processing.emit(0)
    
    def _process_event_list(self, event_list, event_id, event_name, chunk_entries):
        """Process RPG Maker event command list"""
        for cmd_index, command in enumerate(event_list):
            if isinstance(command, dict):
                code = command.get('code', 0)
                # Skip technical code 0 (contains internal technical names, not translatable content)
                if code != 0 and code in self.enabled_codes:
                    parameters = command.get('parameters', [])
                    self._process_parameters(parameters, event_id, event_name, cmd_index, code, chunk_entries)
    
    def _process_parameters(self, parameters, event_id, event_name, cmd_index, code, chunk_entries):
        """Process parameters list, handling nested arrays"""
        for param_index, param in enumerate(parameters):
            if isinstance(param, str) and self.japanese_pattern.search(param):
                # Determine path based on file structure
                if "Page" in event_name:
                    # Map file structure
                    path = f'events[{event_id}].pages[0].list[{cmd_index}].parameters[{param_index}]'
                else:
                    # CommonEvents or other structure
                    path = f'data[{event_id}].list[{cmd_index}].parameters[{param_index}]'
                    
                chunk_entries.append({
                    'event_id': event_id,
                    'event_name': event_name,
                    'command_index': cmd_index,
                    'parameter_index': param_index,
                    'code': code,
                    'original_text': param,
                    'translated_text': param,
                    'path': path
                })
            elif isinstance(param, list):
                # Handle nested parameter lists (like choices in event code 102)
                for sub_index, sub_param in enumerate(param):
                    if isinstance(sub_param, str) and self.japanese_pattern.search(sub_param):
                        # Determine path based on file structure
                        if "Page" in event_name:
                            path = f'events[{event_id}].pages[0].list[{cmd_index}].parameters[{param_index}][{sub_index}]'
                        else:
                            path = f'data[{event_id}].list[{cmd_index}].parameters[{param_index}][{sub_index}]'
                            
                        chunk_entries.append({
                            'event_id': event_id,
                            'event_name': event_name,
                            'command_index': cmd_index,
                            'parameter_index': f"{param_index}[{sub_index}]",
                            'code': code,
                            'original_text': sub_param,
                            'translated_text': sub_param,
                            'path': path
                        })
    
    def _process_object_text(self, obj, event_id, event_name, chunk_entries):
        """Process text fields directly in object"""
        text_fields = ['name', 'nickname', 'description', 'message', 'note', 'text']
        for field in text_fields:
            if field in obj and isinstance(obj[field], str) and self.japanese_pattern.search(obj[field]):
                chunk_entries.append({
                    'event_id': event_id,
                    'event_name': event_name,
                    'command_index': -1,
                    'parameter_index': -1,
                    'code': 0,
                    'original_text': obj[field],
                    'translated_text': obj[field],
                    'path': f'data[{event_id}].{field}'
                })


class LargeFileRPGEditor(QWidget):
    """Optimized RPG Maker file editor for large files"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize attributes
        self.current_file = None
        self.file_data = None
        self.text_entries = []
        self.enabled_codes = {401, 405, 102}  # Default codes
        self.chunk_size = 100
        
        # Initialize UI
        self.setup_ui()
        
        # Auto-save timer
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(30000)  # Auto-save every 30 seconds
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # File selection section
        file_section = QGroupBox("📁 File Selection")
        file_layout = QVBoxLayout(file_section)
        
        # File path and browse
        file_row = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("padding: 5px; background-color: #f0f0f0; border-radius: 3px;")
        file_row.addWidget(self.file_label)
        
        browse_btn = QPushButton("📂 Browse File")
        browse_btn.clicked.connect(self.browse_file)
        file_row.addWidget(browse_btn)
        file_layout.addLayout(file_row)
        
        # Chunk size control
        chunk_row = QHBoxLayout()
        chunk_row.addWidget(QLabel("Chunk Size:"))
        self.chunk_spinbox = QSpinBox()
        self.chunk_spinbox.setRange(50, 1000)
        self.chunk_spinbox.setValue(100)
        self.chunk_spinbox.setSuffix(" events")
        self.chunk_spinbox.valueChanged.connect(self.update_chunk_size)
        chunk_row.addWidget(self.chunk_spinbox)
        
        load_btn = QPushButton("🔄 Load & Process File")
        load_btn.clicked.connect(self.load_and_process_file)
        chunk_row.addWidget(load_btn)
        
        diagnose_btn = QPushButton("🔍 Diagnose File")
        diagnose_btn.clicked.connect(self.diagnose_file)
        chunk_row.addWidget(diagnose_btn)
        
        file_layout.addLayout(chunk_row)
        layout.addWidget(file_section)
        
        # Progress section
        progress_section = QGroupBox("📊 Processing Progress")
        progress_layout = QVBoxLayout(progress_section)
        
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready to load file")
        progress_layout.addWidget(self.status_label)
        
        layout.addWidget(progress_section)
        
        # Code selection section
        codes_section = QGroupBox("🎮 Event Codes")
        codes_layout = QVBoxLayout(codes_section)
        
        # Quick presets
        presets_row = QHBoxLayout()
        recommended_btn = QPushButton("Recommended Only")
        recommended_btn.clicked.connect(lambda: self.set_code_preset([401, 405, 102, 101]))
        presets_row.addWidget(recommended_btn)
        
        dialogue_btn = QPushButton("Dialogue Only")
        dialogue_btn.clicked.connect(lambda: self.set_code_preset([401, 405, 101]))
        presets_row.addWidget(dialogue_btn)
        
        all_btn = QPushButton("All Codes")
        all_btn.clicked.connect(lambda: self.set_code_preset([401, 405, 102, 101, 408, 122, 355, 357, 657, 356, 320, 324, 111, 108]))
        presets_row.addWidget(all_btn)
        
        codes_layout.addLayout(presets_row)
        
        # Individual code checkboxes
        individual_codes_label = QLabel("Individual Code Selection:")
        individual_codes_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        codes_layout.addWidget(individual_codes_label)
        
        # Create checkboxes for common RPG Maker codes
        self.code_checkboxes = {}
        code_descriptions = {
            # Main Dialogue Codes (Recommended)
            401: "Show Text (main dialogue)",
            405: "Show Text (scrolling)",
            102: "Show Choices",
            
            # Optional Codes
            101: "Character Names",
            408: "Comments (⚠️ High Cost)",
            
            # Variable Codes
            122: "Control Variables",
            
            # Other Event Codes
            355: "Scripts",
            357: "Picture Text",
            657: "Picture Text Extended",
            356: "Plugin Commands",
            320: "Change Name Input",
            324: "Change Nickname",
            111: "Conditional Branch",
            108: "Comments"
        }
        
        # Create grid layout for checkboxes
        checkbox_widget = QWidget()
        checkbox_layout = QVBoxLayout(checkbox_widget)
        
        row_layout = None
        for i, (code, description) in enumerate(code_descriptions.items()):
            if i % 3 == 0:  # New row every 3 items
                row_layout = QHBoxLayout()
                checkbox_layout.addLayout(row_layout)
            
            checkbox = QCheckBox(f"{code}: {description}")
            checkbox.setChecked(code in [401, 405, 102, 101])  # Default recommended codes + names
            checkbox.stateChanged.connect(self.update_enabled_codes)
            self.code_checkboxes[code] = checkbox
            row_layout.addWidget(checkbox)
        
        codes_layout.addWidget(checkbox_widget)
        layout.addWidget(codes_section)
        
        # Main content area
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Text entries list
        entries_section = QGroupBox("📝 Text Entries")
        entries_layout = QVBoxLayout(entries_section)
        
        # Multi-selection toolbar (Aegisub-style)
        selection_toolbar = QHBoxLayout()
        
        self.copy_selected_btn = QPushButton("📋 Copy Selected")
        self.copy_selected_btn.clicked.connect(self.copy_selected_entries)
        self.copy_selected_btn.setEnabled(False)
        selection_toolbar.addWidget(self.copy_selected_btn)
        
        self.paste_selected_btn = QPushButton("📥 Paste to Selected")
        self.paste_selected_btn.clicked.connect(self.paste_to_selected_entries)
        self.paste_selected_btn.setEnabled(False)
        selection_toolbar.addWidget(self.paste_selected_btn)
        
        # Filter options
        self.filter_rpg_codes = QCheckBox("Filter RPG codes")
        self.filter_rpg_codes.setChecked(True)
        self.filter_rpg_codes.setToolTip("Remove RPG Maker formatting codes (\\C[n], \\., \\^, etc.) when copying")
        selection_toolbar.addWidget(self.filter_rpg_codes)
        
        selection_toolbar.addStretch()
        
        # Selection info
        self.selection_info = QLabel("No selection")
        self.selection_info.setStyleSheet("color: #666; font-style: italic;")
        selection_toolbar.addWidget(self.selection_info)
        
        entries_layout.addLayout(selection_toolbar)
        
        self.entries_list = QListWidget()
        self.entries_list.setSelectionMode(QAbstractItemView.ExtendedSelection)  # Enable multi-selection
        self.entries_list.currentItemChanged.connect(self.on_entry_selected)
        self.entries_list.itemSelectionChanged.connect(self.on_selection_changed)
        entries_layout.addWidget(self.entries_list)
        
        content_splitter.addWidget(entries_section)
        
        # Text editor section
        editor_section = QGroupBox("✏️ Text Editor")
        editor_layout = QVBoxLayout(editor_section)
        
        # Original text (read-only)
        editor_layout.addWidget(QLabel("Original Text:"))
        self.original_text = QTextEdit()
        self.original_text.setReadOnly(True)
        self.original_text.setMaximumHeight(100)
        editor_layout.addWidget(self.original_text)
        
        # Translated text (editable)
        editor_layout.addWidget(QLabel("Translated Text:"))
        self.translated_text = QTextEdit()
        self.translated_text.textChanged.connect(self.on_text_changed)
        self.translated_text.setMaximumHeight(100)
        editor_layout.addWidget(self.translated_text)
        
        # Context info
        self.context_label = QLabel("No entry selected")
        self.context_label.setStyleSheet("color: #666; font-style: italic;")
        editor_layout.addWidget(self.context_label)
        
        # Save button
        save_btn = QPushButton("💾 Save Changes")
        save_btn.clicked.connect(self.save_file)
        editor_layout.addWidget(save_btn)
        
        content_splitter.addWidget(editor_section)
        layout.addWidget(content_splitter)
        
    def browse_file(self):
        """Browse for a single RPG Maker file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select RPG Maker File",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            self.current_file = file_path
            self.file_label.setText(f"Selected: {Path(file_path).name}")
            
    def update_chunk_size(self, value):
        """Update chunk size for processing"""
        self.chunk_size = value
        
    def set_code_preset(self, codes):
        """Set a preset of event codes"""
        self.enabled_codes = set(codes)
        # Update checkboxes to match preset
        for code, checkbox in self.code_checkboxes.items():
            checkbox.setChecked(code in codes)
        self.status_label.setText(f"Event codes set: {sorted(codes)}")
        
    def update_enabled_codes(self):
        """Update enabled codes based on checkbox states"""
        self.enabled_codes = set()
        for code, checkbox in self.code_checkboxes.items():
            if checkbox.isChecked():
                self.enabled_codes.add(code)
        
        self.status_label.setText(f"Event codes selected: {sorted(self.enabled_codes)}")
        
    def diagnose_file(self):
        """Diagnose file format and structure"""
        if not self.current_file:
            QMessageBox.warning(self, "Warning", "Please select a file first")
            return
        
        try:
            file_path = Path(self.current_file)
            file_size = file_path.stat().st_size
            
            # Read first part of file to check format
            with open(self.current_file, 'r', encoding='utf-8') as f:
                first_chunk = f.read(1000)
            
            # Basic analysis
            analysis = f"File: {file_path.name}\n"
            analysis += f"Size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)\n"
            analysis += f"First 100 chars: {first_chunk[:100]!r}\n"
            
            # Try to parse as JSON
            try:
                with open(self.current_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                analysis += f"✅ Valid JSON format\n"
                analysis += f"Type: {type(data).__name__}\n"
                
                if isinstance(data, dict):
                    analysis += f"Keys: {list(data.keys())[:10]}\n"
                    if 'data' in data:
                        analysis += f"Data array length: {len(data['data']) if isinstance(data['data'], list) else 'N/A'}\n"
                elif isinstance(data, list):
                    analysis += f"Array length: {len(data)}\n"
                    
            except json.JSONDecodeError as e:
                analysis += f"❌ JSON Error: {e}\n"
            
            QMessageBox.information(self, "File Diagnosis", analysis)
            
        except Exception as e:
            QMessageBox.critical(self, "Diagnosis Error", f"Error analyzing file: {e}")
    
    def load_and_process_file(self):
        """Load and process the selected file with flexible format support"""
        if not self.current_file:
            QMessageBox.warning(self, "Warning", "Please select a file first")
            return
        
        try:
            self.status_label.setText("🔄 Loading file...")
            self.progress_bar.setValue(0)
            QApplication.processEvents()
            
            # Read file with multiple encoding attempts
            file_content = None
            encodings = ['utf-8', 'utf-8-sig', 'cp1252', 'latin1']
            
            for encoding in encodings:
                try:
                    with open(self.current_file, 'r', encoding=encoding) as f:
                        file_content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if file_content is None:
                raise Exception("Could not decode file with any supported encoding")
            
            # Parse JSON with better error handling
            try:
                self.file_data = json.loads(file_content)
            except json.JSONDecodeError as e:
                # Try to fix common JSON issues and be more flexible
                file_content = file_content.strip()
                if not file_content:
                    raise Exception("File is empty")
                
                # Try parsing again with more details
                raise Exception(f"JSON parsing failed: {e.msg} at line {e.lineno}")
            
            # Accept any valid JSON structure (dict or list)
            if not isinstance(self.file_data, (dict, list)):
                raise Exception("File content is not valid JSON (must be object or array)")
            
            # Handle different RPG Maker file structures
            if isinstance(self.file_data, dict):
                # Most RPG Maker files have 'data' field, but not all
                if 'data' in self.file_data:
                    self.status_label.setText("✅ Standard RPG Maker file format detected")
                else:
                    # Accept files without 'data' field - might be plugins, system files, etc.
                    self.status_label.setText("✅ RPG Maker file format detected (non-standard structure)")
            else:
                # Some files might be arrays
                self.status_label.setText("✅ JSON array format detected")
            
            # Start background processing
            self.start_background_processing()
            
        except FileNotFoundError:
            self.status_label.setText("❌ File not found")
            QMessageBox.critical(self, "Error", f"File not found: {self.current_file}")
        except PermissionError:
            self.status_label.setText("❌ Permission denied")
            QMessageBox.critical(self, "Error", f"Permission denied accessing: {self.current_file}")
        except json.JSONDecodeError as e:
            self.status_label.setText("❌ Invalid JSON format")
            error_details = f"JSON Error:\n{str(e)}\n\nThis might be caused by:\n"
            error_details += "• Corrupted file\n• Non-standard JSON format\n• File too large for memory\n• Binary data in text file"
            QMessageBox.critical(self, "JSON Parse Error", error_details)
        except Exception as e:
            self.status_label.setText("❌ Error loading file")
            error_msg = str(e)
            QMessageBox.critical(self, "Load Error", f"Error loading file:\n{error_msg}")
            
    def start_background_processing(self):
        """Start background processing thread"""
        self.text_entries = []
        self.entries_list.clear()
        
        self.processing_thread = TextProcessingThread(
            self.file_data, self.enabled_codes, self.chunk_size
        )
        self.processing_thread.progress_updated.connect(self.on_progress_updated)
        self.processing_thread.chunk_processed.connect(self.on_chunk_processed)
        self.processing_thread.finished_processing.connect(self.on_processing_finished)
        self.processing_thread.start()
        
    def on_progress_updated(self, progress, message):
        """Handle progress updates"""
        self.progress_bar.setValue(progress)
        self.status_label.setText(message)
        
    def on_chunk_processed(self, chunk_index, entries):
        """Handle processed chunk"""
        # Group identical texts together
        text_groups = {}
        
        for entry in entries:
            original_text = entry['original_text']
            if original_text not in text_groups:
                text_groups[original_text] = {
                    'main_entry': entry,
                    'duplicates': []
                }
            else:
                text_groups[original_text]['duplicates'].append(entry)
        
        # Add grouped entries
        for text, group in text_groups.items():
            main_entry = group['main_entry']
            duplicates = group['duplicates']
            
            # Add duplicate info to main entry
            main_entry['duplicates'] = duplicates
            main_entry['duplicate_count'] = len(duplicates)
            
            self.text_entries.append(main_entry)
            
            # Create display text
            display_text = f"[{main_entry['code']}] {text[:50]}"
            if len(duplicates) > 0:
                display_text += f" (x{len(duplicates) + 1})"
            if len(text) > 50:
                display_text += "..."
            
            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, len(self.text_entries) - 1)
            self.entries_list.addItem(item)
        
    def on_processing_finished(self, total_entries):
        """Handle processing completion"""
        self.status_label.setText(f"✅ Processing complete! Found {total_entries} text entries")
        self.progress_bar.setValue(100)
        
    def on_entry_selected(self, current, previous):
        """Handle entry selection"""
        if current is None:
            return
            
        entry_index = current.data(Qt.UserRole)
        if 0 <= entry_index < len(self.text_entries):
            entry = self.text_entries[entry_index]
            
            # Update editor
            self.original_text.setText(entry['original_text'])
            self.translated_text.setText(entry['translated_text'])
            
            # Update context
            context = f"Event: {entry['event_name']} (ID: {entry['event_id']}) | "
            context += f"Code: {entry['code']} | Path: {entry['path']}"
            self.context_label.setText(context)
    
    def on_text_changed(self):
        """Handle text changes in editor"""
        current_item = self.entries_list.currentItem()
        if current_item is None:
            return
            
        entry_index = current_item.data(Qt.UserRole)
        if 0 <= entry_index < len(self.text_entries):
            new_text = self.translated_text.toPlainText()
            entry = self.text_entries[entry_index]
            
            # Update the main entry
            entry['translated_text'] = new_text
            
            # Update all duplicates if they exist
            if 'duplicates' in entry:
                for duplicate in entry['duplicates']:
                    duplicate['translated_text'] = new_text
    
    def auto_save(self):
        """Auto-save functionality"""
        if self.current_file and self.file_data:
            try:
                # Create backup
                backup_path = self.current_file + '.autosave'
                with open(backup_path, 'w', encoding='utf-8') as f:
                    json.dump(self.file_data, f, ensure_ascii=False, indent=2)
            except Exception:
                pass  # Silent fail for auto-save
    
    def save_file(self):
        """Save changes to file"""
        if not self.current_file or not self.file_data:
            QMessageBox.warning(self, "Warning", "No file loaded")
            return
        
        try:
            # Apply changes to file data
            for entry in self.text_entries:
                if entry['translated_text'] != entry['original_text']:
                    # Update main entry
                    self._update_file_data(entry)
                    
                    # Update all duplicates if they exist
                    if 'duplicates' in entry:
                        for duplicate in entry['duplicates']:
                            if duplicate['translated_text'] != duplicate['original_text']:
                                self._update_file_data(duplicate)
            
            # Create backup
            backup_path = self.current_file + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(self.file_data, f, ensure_ascii=False, indent=2)
            
            # Save main file
            with open(self.current_file, 'w', encoding='utf-8') as f:
                json.dump(self.file_data, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(self, "Success", 
                                  f"File saved successfully!\nBackup created: {backup_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Error saving file: {e}")
    
    def _update_file_data(self, entry):
        """Update file data with translated text"""
        try:
            # Handle different file structures
            if isinstance(self.file_data, dict):
                # Map files - events field
                if 'events' in self.file_data and isinstance(self.file_data['events'], list):
                    events_array = self.file_data['events']
                    if entry['event_id'] < len(events_array) and events_array[entry['event_id']]:
                        event = events_array[entry['event_id']]
                        self._update_event_data(event, entry)
                
                # CommonEvents - data field  
                elif 'data' in self.file_data and isinstance(self.file_data['data'], list):
                    data_array = self.file_data['data']
                    if entry['event_id'] < len(data_array) and data_array[entry['event_id']]:
                        event = data_array[entry['event_id']]
                        self._update_event_data(event, entry)
                
                # Single event structure
                elif 'list' in self.file_data:
                    self._update_event_data(self.file_data, entry)
                    
        except Exception as e:
            print(f"Error updating file data: {e}")
    
    def _update_event_data(self, event, entry):
        """Update event data with translated text"""
        try:
            # Handle Map files with pages
            if 'pages' in event and isinstance(event['pages'], list):
                for page in event['pages']:
                    if isinstance(page, dict) and 'list' in page:
                        self._update_command_list(page['list'], entry)
            
            # Handle direct event list
            elif 'list' in event and isinstance(event['list'], list):
                self._update_command_list(event['list'], entry)
                
        except Exception as e:
            print(f"Error updating event data: {e}")
    
    def _update_command_list(self, command_list, entry):
        """Update command list with translated text"""
        try:
            command_index = entry.get('command_index', -1)
            parameter_index = entry.get('parameter_index', -1)
            
            # Ensure indices are integers
            if isinstance(command_index, str):
                command_index = int(command_index) if command_index.isdigit() else -1
            if isinstance(parameter_index, str):
                parameter_index = int(parameter_index) if parameter_index.isdigit() else -1
            
            if (command_index >= 0 and 
                command_index < len(command_list)):
                
                command = command_list[command_index]
                if isinstance(command, dict) and 'parameters' in command:
                    params = command['parameters']
                    if (isinstance(params, list) and 
                        parameter_index >= 0 and 
                        parameter_index < len(params)):
                        
                        params[parameter_index] = entry['translated_text']
                        
        except Exception as e:
            print(f"Error updating command list: {e}")
    
    def on_selection_changed(self):
        """Handle selection change in entries list"""
        selected_items = self.entries_list.selectedItems()
        count = len(selected_items)
        
        if count == 0:
            self.selection_info.setText("No selection")
            self.copy_selected_btn.setEnabled(False)
            self.paste_selected_btn.setEnabled(False)
        elif count == 1:
            self.selection_info.setText("1 entry selected")
            self.copy_selected_btn.setEnabled(True)
            self.paste_selected_btn.setEnabled(QApplication.clipboard().mimeData().hasText())
        else:
            self.selection_info.setText(f"{count} entries selected")
            self.copy_selected_btn.setEnabled(True)
            self.paste_selected_btn.setEnabled(QApplication.clipboard().mimeData().hasText())
    
    def copy_selected_entries(self):
        """Copy selected entries to clipboard (Aegisub-style)"""
        selected_items = self.entries_list.selectedItems()
        if not selected_items:
            return
        
        copied_texts = []
        for item in selected_items:
            entry_index = item.data(Qt.UserRole)
            if 0 <= entry_index < len(self.text_entries):
                entry = self.text_entries[entry_index]
                text = entry['original_text']
                
                # Filter RPG Maker codes if option is enabled
                if self.filter_rpg_codes.isChecked():
                    text = self.filter_rpg_maker_codes(text)
                
                copied_texts.append(text)
        
        # Join texts with newlines
        clipboard_text = '\n'.join(copied_texts)
        QApplication.clipboard().setText(clipboard_text)
        
        count = len(copied_texts)
        QMessageBox.information(self, "Copied", 
                              f"Copied {count} text{'s' if count != 1 else ''} to clipboard!")
    
    def paste_to_selected_entries(self):
        """Paste clipboard text to selected entries (Aegisub-style)"""
        selected_items = self.entries_list.selectedItems()
        if not selected_items:
            return
        
        clipboard_text = QApplication.clipboard().text()
        if not clipboard_text:
            return
        
        # Split clipboard text by lines
        lines = clipboard_text.strip().split('\n')
        
        # Match lines to selected entries
        updated_count = 0
        for i, item in enumerate(selected_items):
            if i < len(lines):
                entry_index = item.data(Qt.UserRole)
                if 0 <= entry_index < len(self.text_entries):
                    entry = self.text_entries[entry_index]
                    new_text = lines[i].strip()
                    
                    # If we filtered codes during copy, merge back with original structure
                    if self.filter_rpg_codes.isChecked():
                        new_text = self.merge_with_original_codes(entry['original_text'], new_text)
                    
                    # Update the entry
                    entry['translated_text'] = new_text
                    
                    # Update list item display
                    display_text = f"[{entry['code']}] {new_text[:50]}{'...' if len(new_text) > 50 else ''}"
                    item.setText(display_text)
                    
                    # Mark as modified
                    item.setData(Qt.UserRole + 1, True)  # Modified flag
                    
                    updated_count += 1
        
        QMessageBox.information(self, "Pasted", 
                              f"Updated {updated_count} text{'s' if updated_count != 1 else ''}!")
        
        # Update current editor if one of the pasted entries is selected
        current_item = self.entries_list.currentItem()
        if current_item in selected_items:
            entry_index = current_item.data(Qt.UserRole)
            if 0 <= entry_index < len(self.text_entries):
                entry = self.text_entries[entry_index]
                self.translated_text.setPlainText(entry.get('translated_text', entry['original_text']))
    
    def merge_with_original_codes(self, original: str, translated: str) -> str:
        """Merge translated text with original RPG codes"""
        if not original or not translated:
            return translated
        
        # Simple strategy: try to detect if original has codes and preserve them
        # If original has no codes, just return translated
        if not re.search(r'\\[CNVGIFSP\.\^\!><\|\{\}\\]', original):
            return translated
        
        # Extract codes pattern from original and apply to translated
        # This is a basic approach - extract leading and trailing codes
        
        # Find leading codes
        leading_match = re.match(r'^((?:\\[CNVGIFSP]\[\d*\]|\\[\.\^\!><\|\{\}\\])*)', original)
        leading_codes = leading_match.group(1) if leading_match else ""
        
        # Find trailing codes
        trailing_match = re.search(r'((?:\\[CNVGIFSP]\[\d*\]|\\[\.\^\!><\|\{\}\\])*)$', original)
        trailing_codes = trailing_match.group(1) if trailing_match else ""
        
        # Remove those codes from original to get the middle text structure
        middle_original = original
        if leading_codes:
            middle_original = middle_original[len(leading_codes):]
        if trailing_codes:
            middle_original = middle_original[:-len(trailing_codes)] if trailing_codes else middle_original
        
        # Find any codes in the middle
        middle_codes = re.findall(r'\\[CNVGIFSP]\[\d*\]|\\[\.\^\!><\|\{\}\\]', middle_original)
        
        # For simple case, just preserve leading and trailing codes
        result = leading_codes + translated + trailing_codes
        
        return result
    
    def filter_rpg_maker_codes(self, text: str) -> str:
        """Remove RPG Maker formatting codes from text"""
        if not text:
            return text
        
        # Common RPG Maker codes to filter (order matters)
        patterns = [
            r'\\C\[\d+\]',       # Color codes like \C[27]
            r'\\N\[\d+\]',       # Name codes
            r'\\V\[\d+\]',       # Variable codes
            r'\\G',              # Gold symbol
            r'\\I\[\d+\]',       # Item icons
            r'\\P\[\d+\]',       # Party member names
            r'\\FS\[\d+\]',      # Font size
            r'\\\.',             # Wait code \.
            r'\\\^',             # Close message
            r'\\!',              # Wait for input
            r'\\>',              # Speed up
            r'\\<',              # Speed down
            r'\\\|',             # Pause
            r'\\\{',             # Text bigger
            r'\\}',              # Text smaller
            r'\\\\',             # Double backslash (any remaining escapes)
        ]
        
        cleaned_text = text
        for pattern in patterns:
            cleaned_text = re.sub(pattern, '', cleaned_text)
        
        # Clean up multiple spaces and trim
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        return cleaned_text
