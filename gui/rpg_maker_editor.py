"""
RPG Maker File Editor with Tag Detection and Auto-Update
Allows manual translation with real-time file updates
"""

import json
import os
import re
from typing import Dict, List, Any, Optional, Tuple
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                           QLabel, QPushButton, QFileDialog, QGroupBox,
                           QCheckBox, QScrollArea, QSplitter, QMessageBox,
                           QProgressBar, QComboBox, QSpinBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QTextCharFormat, QTextCursor, QColor

from core.rpg_maker_processor import RPGMakerProcessor

class RPGMakerFileEditor(QWidget):
    """Interactive editor for RPG Maker files with tag detection"""
    
    file_updated = pyqtSignal(str)  # Signal when file is updated
    
    def __init__(self):
        super().__init__()
        self.processor = RPGMakerProcessor()
        self.current_file = None
        self.current_data = None
        self.detected_segments = []  # List of (start_pos, end_pos, original_text, event_code)
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save_changes)
        self.auto_save_enabled = True
        self.auto_save_delay = 2000  # 2 seconds
        
        # Japanese text detection pattern
        self.japanese_pattern = re.compile(r'[ひらがなカタカナ漢字ー々〆〤]+')
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # File selection section
        file_section = QGroupBox("📄 File Selection")
        file_layout = QHBoxLayout(file_section)
        
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("font-weight: bold;")
        file_layout.addWidget(self.file_label)
        
        self.browse_btn = QPushButton("📂 Browse File")
        self.browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.browse_btn)
        
        self.reload_btn = QPushButton("🔄 Reload")
        self.reload_btn.clicked.connect(self.reload_file)
        self.reload_btn.setEnabled(False)
        file_layout.addWidget(self.reload_btn)
        
        layout.addWidget(file_section)
        
        # Event codes configuration
        codes_section = QGroupBox("🎮 Event Codes to Detect")
        codes_layout = QVBoxLayout(codes_section)
        
        # Preset buttons
        preset_layout = QHBoxLayout()
        
        self.recommended_btn = QPushButton("Recommended Only")
        self.recommended_btn.clicked.connect(lambda: self.apply_preset('recommended'))
        preset_layout.addWidget(self.recommended_btn)
        
        self.dialogue_btn = QPushButton("Dialogue Only")
        self.dialogue_btn.clicked.connect(lambda: self.apply_preset('dialogue'))
        preset_layout.addWidget(self.dialogue_btn)
        
        self.all_codes_btn = QPushButton("All Codes")
        self.all_codes_btn.clicked.connect(lambda: self.apply_preset('all'))
        preset_layout.addWidget(self.all_codes_btn)
        
        codes_layout.addLayout(preset_layout)
        
        # Code checkboxes in scroll area
        codes_scroll = QScrollArea()
        codes_widget = QWidget()
        self.codes_layout = QVBoxLayout(codes_widget)
        
        self.code_checkboxes = {}
        self.setup_code_checkboxes()
        
        codes_scroll.setWidget(codes_widget)
        codes_scroll.setMaximumHeight(150)
        codes_layout.addWidget(codes_scroll)
        
        layout.addWidget(codes_section)
        
        # Auto-save settings
        autosave_section = QGroupBox("💾 Auto-Save Settings")
        autosave_layout = QHBoxLayout(autosave_section)
        
        self.autosave_checkbox = QCheckBox("Enable Auto-Save")
        self.autosave_checkbox.setChecked(True)
        self.autosave_checkbox.toggled.connect(self.toggle_autosave)
        autosave_layout.addWidget(self.autosave_checkbox)
        
        autosave_layout.addWidget(QLabel("Delay (seconds):"))
        self.delay_spinbox = QSpinBox()
        self.delay_spinbox.setRange(1, 30)
        self.delay_spinbox.setValue(2)
        self.delay_spinbox.valueChanged.connect(self.update_autosave_delay)
        autosave_layout.addWidget(self.delay_spinbox)
        
        self.save_btn = QPushButton("💾 Save Now")
        self.save_btn.clicked.connect(self.save_changes)
        self.save_btn.setEnabled(False)
        autosave_layout.addWidget(self.save_btn)
        
        layout.addWidget(autosave_section)
        
        # Main editor area
        editor_splitter = QSplitter(Qt.Horizontal)
        
        # Left side: Original text viewer
        left_section = QGroupBox("📖 Detected Text Segments")
        left_layout = QVBoxLayout(left_section)
        
        self.segments_info = QLabel("Load a file to see detected segments")
        left_layout.addWidget(self.segments_info)
        
        self.segments_list = QTextEdit()
        self.segments_list.setReadOnly(True)
        self.segments_list.setMaximumWidth(300)
        left_layout.addWidget(self.segments_list)
        
        editor_splitter.addWidget(left_section)
        
        # Right side: Interactive editor
        right_section = QGroupBox("✏️ Interactive Editor")
        right_layout = QVBoxLayout(right_section)
        
        # Editor controls
        editor_controls = QHBoxLayout()
        
        self.highlight_btn = QPushButton("🔍 Highlight Detected Text")
        self.highlight_btn.clicked.connect(self.highlight_detected_text)
        self.highlight_btn.setEnabled(False)
        editor_controls.addWidget(self.highlight_btn)
        
        self.clear_highlight_btn = QPushButton("🧹 Clear Highlights")
        self.clear_highlight_btn.clicked.connect(self.clear_highlights)
        self.clear_highlight_btn.setEnabled(False)
        editor_controls.addWidget(self.clear_highlight_btn)
        
        right_layout.addLayout(editor_controls)
        
        # Main text editor
        self.text_editor = QTextEdit()
        self.text_editor.setFont(QFont("Consolas", 10))
        self.text_editor.textChanged.connect(self.on_text_changed)
        right_layout.addWidget(self.text_editor)
        
        # Status bar
        self.status_label = QLabel("Ready")
        right_layout.addWidget(self.status_label)
        
        editor_splitter.addWidget(right_section)
        
        layout.addWidget(editor_splitter)
        
    def setup_code_checkboxes(self):
        """Setup checkboxes for event codes"""
        try:
            categories = self.processor.get_code_categories()
            
            for category_name, codes in categories.items():
                # Category header
                category_label = QLabel(f"📂 {category_name.replace('_', ' ').title()}")
                category_label.setStyleSheet("font-weight: bold; color: #333; margin-top: 5px;")
                self.codes_layout.addWidget(category_label)
                
                # Codes in category
                for code_info in codes:
                    checkbox = QCheckBox(f"{code_info.code}: {code_info.name}")
                    checkbox.setChecked(code_info.recommended)
                    checkbox.toggled.connect(self.update_detection)
                    self.code_checkboxes[code_info.code] = checkbox
                    self.codes_layout.addWidget(checkbox)
                    
        except Exception as e:
            print(f"Error setting up code checkboxes: {e}")
    
    def apply_preset(self, preset_name):
        """Apply preset code selection"""
        if preset_name == 'recommended':
            enabled_codes = {401, 405, 102}
        elif preset_name == 'dialogue':
            enabled_codes = {401, 405}
        elif preset_name == 'all':
            enabled_codes = set(self.processor.available_codes.keys())
        else:
            return
        
        # Update checkboxes
        for code, checkbox in self.code_checkboxes.items():
            checkbox.setChecked(code in enabled_codes)
        
        self.update_detection()
    
    def browse_file(self):
        """Browse for RPG Maker JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select RPG Maker JSON File",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            self.load_file(file_path)
    
    def load_file(self, file_path):
        """Load and parse RPG Maker file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.current_data = json.load(f)
            
            self.current_file = file_path
            self.file_label.setText(f"📄 {os.path.basename(file_path)}")
            
            # Display raw JSON in editor
            formatted_json = json.dumps(self.current_data, ensure_ascii=False, indent=2)
            self.text_editor.setPlainText(formatted_json)
            
            # Enable controls
            self.reload_btn.setEnabled(True)
            self.save_btn.setEnabled(True)
            self.highlight_btn.setEnabled(True)
            self.clear_highlight_btn.setEnabled(True)
            
            # Detect text segments
            self.update_detection()
            
            self.status_label.setText(f"Loaded: {os.path.basename(file_path)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file:\n{e}")
    
    def reload_file(self):
        """Reload current file"""
        if self.current_file:
            self.load_file(self.current_file)
    
    def update_detection(self):
        """Update text detection based on selected codes"""
        if not self.current_data:
            return
        
        # Get enabled codes
        enabled_codes = set()
        for code, checkbox in self.code_checkboxes.items():
            if checkbox.isChecked():
                enabled_codes.add(code)
        
        self.processor.set_enabled_codes(enabled_codes)
        
        # Extract text segments with positions
        self.detect_text_segments()
        self.update_segments_display()
    
    def detect_text_segments(self):
        """Detect text segments in the current JSON"""
        self.detected_segments = []
        
        if not self.current_data:
            return
        
        # Get current text content
        text_content = self.text_editor.toPlainText()
        
        # Extract texts with their event codes
        texts_with_codes = []
        self._extract_texts_with_codes(self.current_data, texts_with_codes)
        
        # Find positions of detected texts in the editor
        for text, event_code in texts_with_codes:
            if not text or not self.japanese_pattern.search(text):
                continue
            
            # Find all occurrences of this text
            start_pos = 0
            while True:
                pos = text_content.find(f'"{text}"', start_pos)
                if pos == -1:
                    break
                
                # Add segment (excluding quotes)
                segment_start = pos + 1
                segment_end = pos + len(text) + 1
                self.detected_segments.append((segment_start, segment_end, text, event_code))
                start_pos = pos + 1
    
    def _extract_texts_with_codes(self, obj, texts_with_codes, current_code=None):
        """Recursively extract texts with their event codes"""
        if isinstance(obj, dict):
            # Check for event lists
            if 'list' in obj and isinstance(obj['list'], list):
                for event in obj['list']:
                    if isinstance(event, dict):
                        code = event.get('code', 0)
                        if code in self.processor.enabled_codes:
                            parameters = event.get('parameters', [])
                            for param in parameters:
                                if isinstance(param, str) and self.japanese_pattern.search(param):
                                    texts_with_codes.append((param, code))
                                elif isinstance(param, list):
                                    for sub_param in param:
                                        if isinstance(sub_param, str) and self.japanese_pattern.search(sub_param):
                                            texts_with_codes.append((sub_param, code))
            
            # Check other fields
            for key, value in obj.items():
                self._extract_texts_with_codes(value, texts_with_codes, current_code)
                
        elif isinstance(obj, list):
            for item in obj:
                self._extract_texts_with_codes(item, texts_with_codes, current_code)
    
    def update_segments_display(self):
        """Update the segments list display"""
        if not self.detected_segments:
            self.segments_info.setText("No text segments detected")
            self.segments_list.setPlainText("No Japanese text found with selected event codes.")
            return
        
        self.segments_info.setText(f"Found {len(self.detected_segments)} text segments")
        
        # Group segments by event code
        code_groups = {}
        for _, _, text, code in self.detected_segments:
            if code not in code_groups:
                code_groups[code] = []
            if text not in [t for t, _ in code_groups[code]]:  # Avoid duplicates
                code_groups[code].append((text, code))
        
        # Create display text
        display_text = ""
        for code in sorted(code_groups.keys()):
            code_info = self.processor.available_codes.get(code)
            code_name = code_info.name if code_info else "Unknown"
            display_text += f"=== Code {code}: {code_name} ===\n"
            
            for i, (text, _) in enumerate(code_groups[code], 1):
                display_text += f"{i}. {text}\n"
            display_text += "\n"
        
        self.segments_list.setPlainText(display_text)
    
    def highlight_detected_text(self):
        """Highlight detected text segments in the editor"""
        if not self.detected_segments:
            return
        
        cursor = self.text_editor.textCursor()
        
        # Create highlight format
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor(255, 255, 0, 100))  # Light yellow
        
        # Apply highlights
        for start_pos, end_pos, text, code in self.detected_segments:
            cursor.setPosition(start_pos)
            cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
            cursor.mergeCharFormat(highlight_format)
    
    def clear_highlights(self):
        """Clear all highlights from the editor"""
        cursor = self.text_editor.textCursor()
        cursor.select(QTextCursor.Document)
        
        # Create normal format
        normal_format = QTextCharFormat()
        cursor.mergeCharFormat(normal_format)
        
        # Reset cursor
        cursor.clearSelection()
        self.text_editor.setTextCursor(cursor)
    
    def on_text_changed(self):
        """Handle text changes in the editor"""
        if self.auto_save_enabled and self.current_file:
            # Restart the auto-save timer
            self.auto_save_timer.stop()
            self.auto_save_timer.start(self.auto_save_delay)
            self.status_label.setText("Modified - Auto-save pending...")
    
    def toggle_autosave(self, enabled):
        """Toggle auto-save functionality"""
        self.auto_save_enabled = enabled
        if not enabled:
            self.auto_save_timer.stop()
    
    def update_autosave_delay(self, delay):
        """Update auto-save delay"""
        self.auto_save_delay = delay * 1000  # Convert to milliseconds
    
    def auto_save_changes(self):
        """Auto-save changes to file"""
        self.auto_save_timer.stop()
        self.save_changes(auto=True)
    
    def save_changes(self, auto=False):
        """Save changes to the file"""
        if not self.current_file:
            return
        
        try:
            # Parse the modified JSON
            modified_text = self.text_editor.toPlainText()
            modified_data = json.loads(modified_text)
            
            # Create backup
            backup_path = f"{self.current_file}.backup"
            if not os.path.exists(backup_path):
                with open(backup_path, 'w', encoding='utf-8') as f:
                    json.dump(self.current_data, f, ensure_ascii=False, indent=2)
            
            # Save modified data
            with open(self.current_file, 'w', encoding='utf-8') as f:
                json.dump(modified_data, f, ensure_ascii=False, indent=2)
            
            self.current_data = modified_data
            
            # Update detection after save
            self.update_detection()
            
            save_type = "Auto-saved" if auto else "Saved"
            self.status_label.setText(f"{save_type}: {os.path.basename(self.current_file)}")
            
            # Emit signal
            self.file_updated.emit(self.current_file)
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON format:\n{e}"
            if auto:
                self.status_label.setText("Auto-save failed - JSON error")
            else:
                QMessageBox.critical(self, "JSON Error", error_msg)
        except Exception as e:
            error_msg = f"Failed to save file:\n{e}"
            if auto:
                self.status_label.setText("Auto-save failed")
            else:
                QMessageBox.critical(self, "Save Error", error_msg)
