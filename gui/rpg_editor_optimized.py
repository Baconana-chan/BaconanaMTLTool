"""
Optimized RPG Maker File Editor for Large Files
Handles massive files like CommonEvents with lazy loading and chunked processing
"""

import json
import re
import os
from typing import Dict, List, Any, Optional, Tuple, Set
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QTextEdit, QLabel, QComboBox, QSpinBox, QProgressBar,
                           QGroupBox, QCheckBox, QSplitter, QListWidget, 
                           QListWidgetItem, QMessageBox, QApplication, QLineEdit,
                           QScrollArea, QTabWidget, QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor, QFont


class LargeFileProcessor(QThread):
    """Background processor for large RPG Maker files"""
    
    progress_updated = pyqtSignal(int, str)
    chunk_processed = pyqtSignal(int, dict, list)  # chunk_id, events, japanese_texts
    processing_finished = pyqtSignal(dict)  # statistics
    
    def __init__(self, file_path: str, enabled_codes: Set[int], chunk_size: int = 100):
        super().__init__()
        self.file_path = file_path
        self.enabled_codes = enabled_codes
        self.chunk_size = chunk_size
        self.japanese_pattern = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+')
        self.is_cancelled = False
        
    def run(self):
        """Process file in chunks to handle large files efficiently"""
        try:
            self.progress_updated.emit(0, "Loading file...")
            
            # Load file
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, dict) or 'data' not in data:
                self.progress_updated.emit(100, "Invalid file format")
                return
            
            events_data = data['data']
            if not isinstance(events_data, list):
                self.progress_updated.emit(100, "Invalid events data format")
                return
            
            # Filter out None entries
            valid_events = [event for event in events_data if event is not None]
            total_events = len(valid_events)
            
            self.progress_updated.emit(10, f"Processing {total_events} events...")
            
            # Process in chunks
            chunks_processed = 0
            total_chunks = (total_events + self.chunk_size - 1) // self.chunk_size
            total_texts = 0
            total_relevant_events = 0
            
            for i in range(0, total_events, self.chunk_size):
                if self.is_cancelled:
                    break
                
                chunk = valid_events[i:i + self.chunk_size]
                chunk_texts = []
                relevant_events = []
                
                for event in chunk:
                    if self.is_cancelled:
                        break
                    
                    if not isinstance(event, dict) or 'list' not in event:
                        continue
                    
                    event_list = event.get('list', [])
                    if not isinstance(event_list, list):
                        continue
                    
                    # Check if event contains relevant codes
                    has_relevant_codes = False
                    event_texts = []
                    
                    for cmd in event_list:
                        if not isinstance(cmd, dict):
                            continue
                        
                        code = cmd.get('code', 0)
                        if code in self.enabled_codes:
                            has_relevant_codes = True
                            parameters = cmd.get('parameters', [])
                            
                            # Extract Japanese text from parameters
                            for param in parameters:
                                if isinstance(param, str) and self.japanese_pattern.search(param):
                                    event_texts.append(param)
                                elif isinstance(param, list):
                                    for sub_param in param:
                                        if isinstance(sub_param, str) and self.japanese_pattern.search(sub_param):
                                            event_texts.append(sub_param)
                    
                    if has_relevant_codes:
                        relevant_events.append(event)
                        chunk_texts.extend(event_texts)
                        total_relevant_events += 1
                
                chunks_processed += 1
                progress = 10 + (chunks_processed / total_chunks) * 80
                
                self.progress_updated.emit(int(progress), 
                    f"Chunk {chunks_processed}/{total_chunks} - Found {len(chunk_texts)} texts")
                
                total_texts += len(chunk_texts)
                
                # Emit chunk data
                self.chunk_processed.emit(chunks_processed - 1, 
                    {'events': relevant_events, 'start_index': i}, chunk_texts)
                
                # Allow UI updates
                QApplication.processEvents()
            
            # Emit final statistics
            stats = {
                'total_events': total_events,
                'relevant_events': total_relevant_events,
                'total_texts': total_texts,
                'chunks_processed': chunks_processed
            }
            
            self.progress_updated.emit(100, f"Completed! Found {total_texts} texts in {total_relevant_events} events")
            self.processing_finished.emit(stats)
            
        except Exception as e:
            self.progress_updated.emit(100, f"Error: {str(e)}")
    
    def cancel(self):
        """Cancel processing"""
        self.is_cancelled = True


class OptimizedRPGEditor(QWidget):
    """Optimized RPG Maker file editor for large files like CommonEvents"""
    
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.file_data = None
        self.events_chunks = {}  # chunk_id -> events data
        self.japanese_texts = []  # All found Japanese texts
        self.enabled_codes = {401, 405, 102}  # Default codes
        self.processor = None
        self.current_chunk = 0
        self.search_results = []
        self.current_search_index = 0
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the optimized editor UI"""
        layout = QVBoxLayout(self)
        
        # File selection and options
        file_group = QGroupBox("📁 Large File Editor (Optimized for CommonEvents)")
        file_layout = QVBoxLayout(file_group)
        
        # File selection
        file_select_layout = QHBoxLayout()
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Select RPG Maker JSON file (Map001.json, CommonEvents.json, etc.)")
        file_select_layout.addWidget(QLabel("File:"))
        file_select_layout.addWidget(self.file_path_edit)
        
        self.browse_file_btn = QPushButton("📂 Browse File")
        self.browse_file_btn.clicked.connect(self.browse_file)
        file_select_layout.addWidget(self.browse_file_btn)
        file_layout.addLayout(file_select_layout)
        
        # Processing options
        options_layout = QHBoxLayout()
        options_layout.addWidget(QLabel("Chunk Size:"))
        self.chunk_size_spin = QSpinBox()
        self.chunk_size_spin.setRange(50, 500)
        self.chunk_size_spin.setValue(100)
        self.chunk_size_spin.setToolTip("Events processed at once (lower = less memory, slower)")
        options_layout.addWidget(self.chunk_size_spin)
        
        self.load_file_btn = QPushButton("🔄 Load & Process File")
        self.load_file_btn.clicked.connect(self.load_file)
        self.load_file_btn.setEnabled(False)
        options_layout.addWidget(self.load_file_btn)
        
        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.clicked.connect(self.cancel_processing)
        self.cancel_btn.setEnabled(False)
        options_layout.addWidget(self.cancel_btn)
        
        options_layout.addStretch()
        file_layout.addLayout(options_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        file_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("Ready to load file")
        file_layout.addWidget(self.progress_label)
        
        layout.addWidget(file_group)
        
        # Event codes selection (compact)
        codes_group = QGroupBox("🎮 Event Codes Filter")
        codes_layout = QHBoxLayout(codes_group)
        
        # Quick presets
        preset_layout = QVBoxLayout()
        preset_layout.addWidget(QLabel("Quick Presets:"))
        
        self.preset_dialogue_btn = QPushButton("💬 Dialogue Only")
        self.preset_dialogue_btn.clicked.connect(lambda: self.set_codes_preset({401, 405}))
        preset_layout.addWidget(self.preset_dialogue_btn)
        
        self.preset_recommended_btn = QPushButton("⭐ Recommended")
        self.preset_recommended_btn.clicked.connect(lambda: self.set_codes_preset({401, 405, 102}))
        preset_layout.addWidget(self.preset_recommended_btn)
        
        self.preset_all_btn = QPushButton("🔧 All Codes")
        self.preset_all_btn.clicked.connect(lambda: self.set_codes_preset({401, 405, 102, 103, 104, 111, 355, 356}))
        preset_layout.addWidget(self.preset_all_btn)
        
        codes_layout.addLayout(preset_layout)
        
        # Individual checkboxes (compact grid)
        from core.rpg_maker_processor import RPGMakerProcessor
        rpg_processor = RPGMakerProcessor()
        
        checkboxes_widget = QWidget()
        checkboxes_layout = QVBoxLayout(checkboxes_widget)
        checkboxes_layout.addWidget(QLabel("Individual Codes:"))
        
        self.code_checkboxes = {}
        codes_per_row = 3
        row_layout = None
        
        for i, (code, info) in enumerate(rpg_processor.available_codes.items()):
            if i % codes_per_row == 0:
                row_layout = QHBoxLayout()
                checkboxes_layout.addLayout(row_layout)
            
            checkbox = QCheckBox(f"{code}: {info.name[:15]}...")
            checkbox.setChecked(code in self.enabled_codes)
            checkbox.toggled.connect(self.update_enabled_codes)
            checkbox.setToolTip(f"{code}: {info.name} - {info.description}")
            self.code_checkboxes[code] = checkbox
            row_layout.addWidget(checkbox)
        
        codes_scroll = QScrollArea()
        codes_scroll.setWidget(checkboxes_widget)
        codes_scroll.setMaximumHeight(150)
        codes_layout.addWidget(codes_scroll)
        
        layout.addWidget(codes_group)
        
        # Main content area with splitter
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Left panel: Events list and navigation
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Statistics and navigation
        stats_layout = QHBoxLayout()
        self.stats_label = QLabel("No file loaded")
        stats_layout.addWidget(self.stats_label)
        stats_layout.addStretch()
        left_layout.addLayout(stats_layout)
        
        # Search functionality
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search in Japanese texts...")
        self.search_edit.returnPressed.connect(self.search_texts)
        search_layout.addWidget(self.search_edit)
        
        self.search_btn = QPushButton("🔍")
        self.search_btn.clicked.connect(self.search_texts)
        search_layout.addWidget(self.search_btn)
        
        self.search_next_btn = QPushButton("⬇️")
        self.search_next_btn.clicked.connect(self.search_next)
        self.search_next_btn.setEnabled(False)
        search_layout.addWidget(self.search_next_btn)
        
        self.search_prev_btn = QPushButton("⬆️")
        self.search_prev_btn.clicked.connect(self.search_previous)
        self.search_prev_btn.setEnabled(False)
        search_layout.addWidget(self.search_prev_btn)
        
        left_layout.addLayout(search_layout)
        
        # Events list
        self.events_list = QListWidget()
        self.events_list.itemClicked.connect(self.on_event_selected)
        left_layout.addWidget(self.events_list)
        
        left_panel.setMaximumWidth(400)
        content_splitter.addWidget(left_panel)
        
        # Right panel: Text editor
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Editor header
        editor_header = QHBoxLayout()
        self.editor_title = QLabel("Select an event to edit")
        self.editor_title.setFont(QFont("", 12, QFont.Bold))
        editor_header.addWidget(self.editor_title)
        editor_header.addStretch()
        
        self.save_btn = QPushButton("💾 Save Changes")
        self.save_btn.clicked.connect(self.save_changes)
        self.save_btn.setEnabled(False)
        editor_header.addWidget(self.save_btn)
        
        right_layout.addLayout(editor_header)
        
        # Text editor with syntax highlighting
        self.text_editor = QTextEdit()
        self.text_editor.setFont(QFont("Consolas", 10))
        self.text_editor.textChanged.connect(self.on_text_changed)
        right_layout.addWidget(self.text_editor)
        
        # Translation helper
        translation_layout = QHBoxLayout()
        translation_layout.addWidget(QLabel("Quick Translation:"))
        self.translation_edit = QLineEdit()
        self.translation_edit.setPlaceholderText("Enter translation for selected text...")
        translation_layout.addWidget(self.translation_edit)
        
        self.apply_translation_btn = QPushButton("✅ Apply")
        self.apply_translation_btn.clicked.connect(self.apply_translation)
        translation_layout.addWidget(self.apply_translation_btn)
        
        right_layout.addLayout(translation_layout)
        
        content_splitter.addWidget(right_panel)
        content_splitter.setSizes([400, 800])
        
        layout.addWidget(content_splitter)
    
    def browse_file(self):
        """Browse for RPG Maker JSON file"""
        from PyQt5.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select RPG Maker JSON File", 
            "", "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            self.file_path_edit.setText(file_path)
            self.load_file_btn.setEnabled(True)
    
    def set_codes_preset(self, codes: Set[int]):
        """Set event codes preset"""
        self.enabled_codes = codes.copy()
        # Update checkboxes
        for code, checkbox in self.code_checkboxes.items():
            checkbox.setChecked(code in self.enabled_codes)
    
    def update_enabled_codes(self):
        """Update enabled codes from checkboxes"""
        self.enabled_codes = set()
        for code, checkbox in self.code_checkboxes.items():
            if checkbox.isChecked():
                self.enabled_codes.add(code)
    
    def load_file(self):
        """Load and process RPG Maker file"""
        file_path = self.file_path_edit.text().strip()
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self, "Error", "Please select a valid file")
            return
        
        if not self.enabled_codes:
            QMessageBox.warning(self, "Error", "Please select at least one event code")
            return
        
        self.current_file = file_path
        self.events_chunks.clear()
        self.japanese_texts.clear()
        self.events_list.clear()
        self.text_editor.clear()
        
        # Setup progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.load_file_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        
        # Start background processing
        chunk_size = self.chunk_size_spin.value()
        self.processor = LargeFileProcessor(file_path, self.enabled_codes, chunk_size)
        self.processor.progress_updated.connect(self.on_progress_updated)
        self.processor.chunk_processed.connect(self.on_chunk_processed)
        self.processor.processing_finished.connect(self.on_processing_finished)
        self.processor.start()
    
    def cancel_processing(self):
        """Cancel file processing"""
        if self.processor:
            self.processor.cancel()
            self.processor.wait()
        
        self.progress_bar.setVisible(False)
        self.load_file_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.progress_label.setText("Processing cancelled")
    
    def on_progress_updated(self, progress: int, message: str):
        """Handle progress updates"""
        self.progress_bar.setValue(progress)
        self.progress_label.setText(message)
    
    def on_chunk_processed(self, chunk_id: int, chunk_data: dict, texts: List[str]):
        """Handle processed chunk"""
        self.events_chunks[chunk_id] = chunk_data
        self.japanese_texts.extend(texts)
        
        # Add events to list
        events = chunk_data['events']
        start_index = chunk_data['start_index']
        
        for i, event in enumerate(events):
            event_id = event.get('id', start_index + i)
            event_name = event.get('name', f'Event {event_id}')
            
            item = QListWidgetItem(f"Event {event_id}: {event_name}")
            item.setData(Qt.UserRole, {'chunk_id': chunk_id, 'event_index': i, 'event': event})
            self.events_list.addItem(item)
    
    def on_processing_finished(self, stats: dict):
        """Handle processing completion"""
        self.progress_bar.setVisible(False)
        self.load_file_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        
        self.stats_label.setText(
            f"📊 {stats['relevant_events']} events | {stats['total_texts']} texts | "
            f"{stats['chunks_processed']} chunks processed"
        )
        
        self.save_btn.setEnabled(True)
        QMessageBox.information(self, "Success", 
            f"File processed successfully!\n\n"
            f"Found {stats['total_texts']} Japanese texts in {stats['relevant_events']} events\n"
            f"Processed in {stats['chunks_processed']} chunks")
    
    def on_event_selected(self, item: QListWidgetItem):
        """Handle event selection"""
        data = item.data(Qt.UserRole)
        if not data:
            return
        
        event = data['event']
        self.current_event_data = data
        
        # Display event in editor
        self.editor_title.setText(f"Event {event.get('id', '?')}: {event.get('name', 'Unnamed')}")
        
        # Extract and format Japanese texts from event
        event_list = event.get('list', [])
        formatted_text = self.format_event_for_editing(event_list)
        
        self.text_editor.blockSignals(True)
        self.text_editor.clear()
        self.text_editor.setPlainText(formatted_text)
        self.highlight_japanese_text()
        self.text_editor.blockSignals(False)
    
    def format_event_for_editing(self, event_list: List[dict]) -> str:
        """Format event commands for editing"""
        lines = []
        lines.append("# RPG Maker Event Commands (Edit Japanese text below)")
        lines.append("# Changes will be automatically applied to the original structure")
        lines.append("")
        
        for i, cmd in enumerate(event_list):
            if not isinstance(cmd, dict):
                continue
            
            code = cmd.get('code', 0)
            if code not in self.enabled_codes:
                continue
            
            parameters = cmd.get('parameters', [])
            lines.append(f"## Command {i}: Code {code}")
            
            for j, param in enumerate(parameters):
                if isinstance(param, str) and re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+', param):
                    lines.append(f"TEXT_{i}_{j}: {param}")
                elif isinstance(param, list):
                    for k, sub_param in enumerate(param):
                        if isinstance(sub_param, str) and re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+', sub_param):
                            lines.append(f"TEXT_{i}_{j}_{k}: {sub_param}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def highlight_japanese_text(self):
        """Highlight Japanese text in the editor"""
        cursor = self.text_editor.textCursor()
        format_japanese = QTextCharFormat()
        format_japanese.setBackground(QColor(255, 255, 0, 100))  # Light yellow
        format_japanese.setForeground(QColor(0, 0, 139))  # Dark blue
        
        text = self.text_editor.toPlainText()
        japanese_pattern = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+')
        
        for match in japanese_pattern.finditer(text):
            cursor.setPosition(match.start())
            cursor.setPosition(match.end(), QTextCursor.KeepAnchor)
            cursor.setCharFormat(format_japanese)
    
    def search_texts(self):
        """Search in Japanese texts"""
        search_term = self.search_edit.text().strip()
        if not search_term:
            return
        
        self.search_results.clear()
        self.current_search_index = 0
        
        # Search in events list
        for i in range(self.events_list.count()):
            item = self.events_list.item(i)
            data = item.data(Qt.UserRole)
            if data:
                event = data['event']
                event_list = event.get('list', [])
                
                for cmd in event_list:
                    if not isinstance(cmd, dict):
                        continue
                    
                    parameters = cmd.get('parameters', [])
                    for param in parameters:
                        if isinstance(param, str) and search_term.lower() in param.lower():
                            self.search_results.append((i, item, param))
                        elif isinstance(param, list):
                            for sub_param in param:
                                if isinstance(sub_param, str) and search_term.lower() in sub_param.lower():
                                    self.search_results.append((i, item, sub_param))
        
        if self.search_results:
            self.search_next_btn.setEnabled(True)
            self.search_prev_btn.setEnabled(True)
            self.progress_label.setText(f"Found {len(self.search_results)} matches")
            self.search_next()
        else:
            self.progress_label.setText("No matches found")
    
    def search_next(self):
        """Go to next search result"""
        if not self.search_results:
            return
        
        if self.current_search_index >= len(self.search_results):
            self.current_search_index = 0
        
        index, item, text = self.search_results[self.current_search_index]
        self.events_list.setCurrentRow(index)
        self.on_event_selected(item)
        
        self.progress_label.setText(f"Match {self.current_search_index + 1}/{len(self.search_results)}: {text[:50]}...")
        self.current_search_index += 1
    
    def search_previous(self):
        """Go to previous search result"""
        if not self.search_results:
            return
        
        self.current_search_index -= 2
        if self.current_search_index < 0:
            self.current_search_index = len(self.search_results) - 1
        
        self.search_next()
    
    def on_text_changed(self):
        """Handle text editor changes"""
        # Enable save button when text is modified
        if hasattr(self, 'current_event_data'):
            self.save_btn.setEnabled(True)
    
    def apply_translation(self):
        """Apply translation from translation helper"""
        translation = self.translation_edit.text().strip()
        if not translation:
            return
        
        # Get selected text in editor
        cursor = self.text_editor.textCursor()
        if cursor.hasSelection():
            cursor.insertText(translation)
            self.translation_edit.clear()
        else:
            QMessageBox.information(self, "Info", "Please select text in the editor to replace")
    
    def save_changes(self):
        """Save changes back to file"""
        if not self.current_file or not hasattr(self, 'current_event_data'):
            return
        
        try:
            # Parse edited text back to event structure
            edited_text = self.text_editor.toPlainText()
            self.update_event_from_text(edited_text)
            
            # Save entire file
            self.save_file()
            
            QMessageBox.information(self, "Success", "Changes saved successfully!")
            self.save_btn.setEnabled(False)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save changes: {str(e)}")
    
    def update_event_from_text(self, edited_text: str):
        """Update event data from edited text"""
        lines = edited_text.split('\n')
        event = self.current_event_data['event']
        event_list = event.get('list', [])
        
        # Parse TEXT_i_j: content format
        text_pattern = re.compile(r'TEXT_(\d+)_(\d+)(?:_(\d+))?: (.+)')
        
        for line in lines:
            match = text_pattern.match(line.strip())
            if match:
                cmd_idx = int(match.group(1))
                param_idx = int(match.group(2))
                sub_param_idx = match.group(3)
                new_text = match.group(4)
                
                if cmd_idx < len(event_list):
                    cmd = event_list[cmd_idx]
                    if isinstance(cmd, dict) and 'parameters' in cmd:
                        parameters = cmd['parameters']
                        
                        if sub_param_idx is not None:
                            # Nested parameter
                            sub_idx = int(sub_param_idx)
                            if (param_idx < len(parameters) and 
                                isinstance(parameters[param_idx], list) and 
                                sub_idx < len(parameters[param_idx])):
                                parameters[param_idx][sub_idx] = new_text
                        else:
                            # Direct parameter
                            if param_idx < len(parameters):
                                parameters[param_idx] = new_text
    
    def save_file(self):
        """Save the modified file"""
        # Load original file
        with open(self.current_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Update with modified events
        for chunk_id, chunk_data in self.events_chunks.items():
            events = chunk_data['events']
            start_index = chunk_data['start_index']
            
            for i, event in enumerate(events):
                original_index = start_index + i
                if original_index < len(data['data']) and data['data'][original_index] is not None:
                    data['data'][original_index] = event
        
        # Create backup
        backup_path = self.current_file + '.backup'
        os.rename(self.current_file, backup_path)
        
        # Save modified file
        with open(self.current_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    editor = OptimizedRPGEditor()
    editor.show()
    sys.exit(app.exec_())
