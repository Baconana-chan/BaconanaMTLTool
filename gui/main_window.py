"""
Main Window for Eroge Translation Tool
User-friendly interface for configuring and running translations
"""

import os
import json
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QLabel, QLineEdit, QPushButton, 
                             QTextEdit, QFileDialog, QProgressBar, QSpinBox,
                             QComboBox, QCheckBox, QGroupBox, QGridLayout,
                             QMessageBox, QScrollArea, QFrame, QDoubleSpinBox,
                             QInputDialog)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QPixmap

from core.translator import TranslationManager
from core.config import ConfigManager
from localization.language_manager import LanguageManager
from utils.project_estimator import ProjectEstimator


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.language_manager = LanguageManager()
        self.translation_manager = None
        self.setup_ui()
        self.load_config()
        
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("Eroge Translation Tool v1.0")
        self.setGeometry(100, 100, 900, 700)
        self.setMinimumSize(800, 600)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # Create tabs
        self.setup_config_tab(tab_widget)
        self.setup_translation_tab(tab_widget)
        self.setup_advanced_tab(tab_widget)
        self.setup_log_tab(tab_widget)
        
        # Status bar
        self.statusBar().showMessage("Ready to translate!")
        
    def setup_config_tab(self, tab_widget):
        """Setup configuration tab"""
        config_widget = QWidget()
        layout = QVBoxLayout(config_widget)
        
        # Scroll area for config
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # API Configuration Group
        api_group = QGroupBox("🔑 API Configuration")
        api_layout = QGridLayout(api_group)
        
        # API URL
        api_layout.addWidget(QLabel("API URL:"), 0, 0)
        self.api_url_edit = QLineEdit()
        self.api_url_edit.setPlaceholderText("Leave blank for OpenAI API")
        api_layout.addWidget(self.api_url_edit, 0, 1)
        
        # API Key
        api_layout.addWidget(QLabel("API Key:"), 1, 0)
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.api_key_edit.setPlaceholderText("Enter your API key")
        api_layout.addWidget(self.api_key_edit, 1, 1)
        
        # Show/Hide API Key
        self.show_key_checkbox = QCheckBox("Show API Key")
        self.show_key_checkbox.toggled.connect(self.toggle_api_key_visibility)
        api_layout.addWidget(self.show_key_checkbox, 1, 2)
        
        # Organization
        api_layout.addWidget(QLabel("Organization:"), 2, 0)
        self.organization_edit = QLineEdit()
        self.organization_edit.setPlaceholderText("Organization ID (optional)")
        api_layout.addWidget(self.organization_edit, 2, 1)
        
        # Model
        api_layout.addWidget(QLabel("Model:"), 3, 0)
        self.model_combo = QComboBox()
        
        # Load models from database
        from core.models import MODEL_DB, ModelProvider
        self.model_db = MODEL_DB
        
        # Add models grouped by provider
        self.model_combo.addItem("--- OpenAI Models ---")
        openai_models = self.model_db.get_models_by_provider(ModelProvider.OPENAI)
        for model in openai_models:
            self.model_combo.addItem(f"{model.display_name}", model.name)
        
        self.model_combo.addItem("--- Anthropic Models ---")
        anthropic_models = self.model_db.get_models_by_provider(ModelProvider.ANTHROPIC)
        for model in anthropic_models:
            self.model_combo.addItem(f"{model.display_name}", model.name)
        
        self.model_combo.addItem("--- Google Models ---")
        google_models = self.model_db.get_models_by_provider(ModelProvider.GOOGLE)
        for model in google_models:
            self.model_combo.addItem(f"{model.display_name}", model.name)
        
        self.model_combo.addItem("--- xAI Models ---")
        xai_models = self.model_db.get_models_by_provider(ModelProvider.XAI)
        for model in xai_models:
            self.model_combo.addItem(f"{model.display_name}", model.name)
        
        self.model_combo.addItem("--- DeepSeek Models ---")
        deepseek_models = self.model_db.get_models_by_provider(ModelProvider.DEEPSEEK)
        for model in deepseek_models:
            self.model_combo.addItem(f"{model.display_name}", model.name)
        
        self.model_combo.addItem("--- Custom Model ---")
        self.model_combo.addItem("Custom Model", "custom")
        
        self.model_combo.setEditable(True)
        self.model_combo.currentTextChanged.connect(self.on_model_changed)
        api_layout.addWidget(self.model_combo, 3, 1)
        
        scroll_layout.addWidget(api_group)
        
        # Translation Settings Group
        translation_group = QGroupBox("🌐 Translation Settings")
        trans_layout = QGridLayout(translation_group)
        
        # Target Language
        trans_layout.addWidget(QLabel("Target Language:"), 0, 0)
        self.language_combo = QComboBox()
        
        # Add supported languages from language manager
        supported_languages = self.language_manager.get_supported_languages()
        self.language_combo.addItems(supported_languages)
        self.language_combo.setEditable(False)  # Only predefined languages
        
        # Connect to update prompt/vocab when language changes
        self.language_combo.currentTextChanged.connect(self.on_language_changed)
        
        trans_layout.addWidget(self.language_combo, 0, 1)
        
        # Timeout
        trans_layout.addWidget(QLabel("Timeout (seconds):"), 1, 0)
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(30, 300)
        self.timeout_spin.setValue(120)
        trans_layout.addWidget(self.timeout_spin, 1, 1)
        
        # Threads
        trans_layout.addWidget(QLabel("File Threads:"), 2, 0)
        self.file_threads_spin = QSpinBox()
        self.file_threads_spin.setRange(1, 10)
        self.file_threads_spin.setValue(1)
        trans_layout.addWidget(self.file_threads_spin, 2, 1)
        
        trans_layout.addWidget(QLabel("Threads per File:"), 3, 0)
        self.threads_spin = QSpinBox()
        self.threads_spin.setRange(1, 20)
        self.threads_spin.setValue(1)
        trans_layout.addWidget(self.threads_spin, 3, 1)
        
        # Batch Size
        trans_layout.addWidget(QLabel("Batch Size:"), 4, 0)
        self.batch_size_spin = QSpinBox()
        self.batch_size_spin.setRange(1, 50)
        self.batch_size_spin.setValue(10)
        trans_layout.addWidget(self.batch_size_spin, 4, 1)
        
        scroll_layout.addWidget(translation_group)
        
        # Text Formatting Group
        format_group = QGroupBox("📝 Text Formatting")
        format_layout = QGridLayout(format_group)
        
        # Width settings
        format_layout.addWidget(QLabel("Dialogue Width:"), 0, 0)
        self.width_spin = QSpinBox()
        self.width_spin.setRange(40, 200)
        self.width_spin.setValue(60)
        format_layout.addWidget(self.width_spin, 0, 1)
        
        format_layout.addWidget(QLabel("List Width:"), 1, 0)
        self.list_width_spin = QSpinBox()
        self.list_width_spin.setRange(50, 300)
        self.list_width_spin.setValue(100)
        format_layout.addWidget(self.list_width_spin, 1, 1)
        
        format_layout.addWidget(QLabel("Note Width:"), 2, 0)
        self.note_width_spin = QSpinBox()
        self.note_width_spin.setRange(40, 200)
        self.note_width_spin.setValue(75)
        format_layout.addWidget(self.note_width_spin, 2, 1)
        
        scroll_layout.addWidget(format_group)
        
        # Cost Settings Group
        cost_group = QGroupBox("💰 API Cost Settings")
        cost_layout = QGridLayout(cost_group)
        
        cost_layout.addWidget(QLabel("Input Cost (per 1K tokens):"), 0, 0)
        self.input_cost_spin = QDoubleSpinBox()
        self.input_cost_spin.setRange(0.0001, 1.0)
        self.input_cost_spin.setDecimals(4)
        self.input_cost_spin.setValue(0.002)
        cost_layout.addWidget(self.input_cost_spin, 0, 1)
        
        cost_layout.addWidget(QLabel("Output Cost (per 1K tokens):"), 1, 0)
        self.output_cost_spin = QDoubleSpinBox()
        self.output_cost_spin.setRange(0.0001, 1.0)
        self.output_cost_spin.setDecimals(4)
        self.output_cost_spin.setValue(0.002)
        cost_layout.addWidget(self.output_cost_spin, 1, 1)
        
        cost_layout.addWidget(QLabel("Frequency Penalty:"), 2, 0)
        self.frequency_penalty_spin = QDoubleSpinBox()
        self.frequency_penalty_spin.setRange(0.0, 2.0)
        self.frequency_penalty_spin.setDecimals(1)
        self.frequency_penalty_spin.setValue(0.2)
        cost_layout.addWidget(self.frequency_penalty_spin, 2, 1)
        
        scroll_layout.addWidget(cost_group)
        
        # OpenRouter Configuration Group
        openrouter_group = QGroupBox("🌐 OpenRouter Configuration")
        openrouter_layout = QGridLayout(openrouter_group)
        
        openrouter_layout.addWidget(QLabel("OpenRouter API URL:"), 0, 0)
        self.openrouter_url_edit = QLineEdit()
        self.openrouter_url_edit.setText("https://openrouter.ai/api/v1")
        self.openrouter_url_edit.setPlaceholderText("https://openrouter.ai/api/v1")
        openrouter_layout.addWidget(self.openrouter_url_edit, 0, 1)
        
        openrouter_layout.addWidget(QLabel("Site URL (optional):"), 1, 0)
        self.site_url_edit = QLineEdit()
        self.site_url_edit.setPlaceholderText("https://your-site.com")
        openrouter_layout.addWidget(self.site_url_edit, 1, 1)
        
        openrouter_layout.addWidget(QLabel("App Name (optional):"), 2, 0)
        self.app_name_edit = QLineEdit()
        self.app_name_edit.setPlaceholderText("Eroge Translation Tool")
        openrouter_layout.addWidget(self.app_name_edit, 2, 1)
        
        scroll_layout.addWidget(openrouter_group)
        
        # Ollama Configuration Group
        ollama_group = QGroupBox("🦙 Ollama Configuration")
        ollama_layout = QGridLayout(ollama_group)
        
        ollama_layout.addWidget(QLabel("Ollama API URL:"), 0, 0)
        self.ollama_url_edit = QLineEdit()
        self.ollama_url_edit.setText("http://localhost:11434/v1")
        self.ollama_url_edit.setPlaceholderText("http://localhost:11434/v1")
        ollama_layout.addWidget(self.ollama_url_edit, 0, 1)
        
        ollama_layout.addWidget(QLabel("Model Name:"), 1, 0)
        self.ollama_model_edit = QLineEdit()
        self.ollama_model_edit.setPlaceholderText("llama3:8b")
        ollama_layout.addWidget(self.ollama_model_edit, 1, 1)
        
        scroll_layout.addWidget(ollama_group)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.test_api_btn = QPushButton("🔍 Test API Connection")
        self.test_api_btn.clicked.connect(self.test_api_connection)
        button_layout.addWidget(self.test_api_btn)
        
        self.save_config_btn = QPushButton("💾 Save Configuration")
        self.save_config_btn.clicked.connect(self.save_config)
        button_layout.addWidget(self.save_config_btn)
        
        self.load_config_btn = QPushButton("📂 Load Configuration")
        self.load_config_btn.clicked.connect(self.load_config_dialog)
        button_layout.addWidget(self.load_config_btn)
        
        scroll_layout.addLayout(button_layout)
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        tab_widget.addTab(config_widget, "⚙️ Configuration")
        
    def setup_translation_tab(self, tab_widget):
        """Setup translation tab"""
        trans_widget = QWidget()
        layout = QVBoxLayout(trans_widget)
        
        # File selection group
        file_group = QGroupBox("📁 File Selection")
        file_layout = QVBoxLayout(file_group)
        
        # Input directory
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Game Directory:"))
        self.input_dir_edit = QLineEdit()
        self.input_dir_edit.setPlaceholderText("Select game root folder (RPG Maker: www/data or data | Ren'Py: game folder)")
        input_layout.addWidget(self.input_dir_edit)
        
        self.browse_input_btn = QPushButton("📂 Browse")
        self.browse_input_btn.clicked.connect(self.browse_input_directory)
        input_layout.addWidget(self.browse_input_btn)
        file_layout.addLayout(input_layout)
        
        # Add project type detection info
        self.project_type_label = QLabel("Project type will be auto-detected")
        self.project_type_label.setStyleSheet("color: #666; font-style: italic;")
        file_layout.addWidget(self.project_type_label)
        info_label = QLabel("💡 Tip: For RPG Maker games, select the root folder. Text files are usually in:\n"
                           "   • RPG Maker MV: game_folder/www/data/\n"
                           "   • RPG Maker MZ: game_folder/data/")
        info_label.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
        info_label.setWordWrap(True)
        file_layout.addWidget(info_label)
        
        # Output directory
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output Directory:"))
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setPlaceholderText("Leave empty to auto-create 'translated' folder in input directory")
        output_layout.addWidget(self.output_dir_edit)
        
        self.browse_output_btn = QPushButton("📂 Browse")
        self.browse_output_btn.clicked.connect(self.browse_output_directory)
        output_layout.addWidget(self.browse_output_btn)
        file_layout.addLayout(output_layout)
        
        # Project estimation section
        estimate_layout = QHBoxLayout()
        self.estimate_btn = QPushButton("📊 Estimate Project Cost")
        self.estimate_btn.clicked.connect(self.estimate_project)
        self.estimate_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        estimate_layout.addWidget(self.estimate_btn)
        estimate_layout.addStretch()
        file_layout.addLayout(estimate_layout)
        
        layout.addWidget(file_group)
        
        # Translation options
        options_group = QGroupBox("🎯 Translation Options")
        options_layout = QVBoxLayout(options_group)
        
        self.backup_checkbox = QCheckBox("Create backup of original files")
        self.backup_checkbox.setChecked(True)
        options_layout.addWidget(self.backup_checkbox)
        
        self.overwrite_checkbox = QCheckBox("Overwrite existing translations")
        options_layout.addWidget(self.overwrite_checkbox)
        
        self.preview_checkbox = QCheckBox("Preview translations before applying")
        options_layout.addWidget(self.preview_checkbox)
        
        layout.addWidget(options_group)
        
        # Progress section
        progress_group = QGroupBox("📊 Translation Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_label = QLabel("Ready to start translation")
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        
        self.file_progress_label = QLabel("")
        progress_layout.addWidget(self.file_progress_label)
        
        layout.addWidget(progress_group)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        # Estimate button
        self.estimate_btn = QPushButton("📊 Estimate Project")
        self.estimate_btn.clicked.connect(self.estimate_project)
        self.estimate_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        control_layout.addWidget(self.estimate_btn)
        
        self.start_btn = QPushButton("🚀 Start Translation")
        self.start_btn.clicked.connect(self.start_translation)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        control_layout.addWidget(self.start_btn)
        
        self.pause_btn = QPushButton("⏸️ Pause")
        self.pause_btn.clicked.connect(self.pause_translation)
        self.pause_btn.setEnabled(False)
        control_layout.addWidget(self.pause_btn)
        
        self.stop_btn = QPushButton("⏹️ Stop")
        self.stop_btn.clicked.connect(self.stop_translation)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)
        
        layout.addLayout(control_layout)
        
        tab_widget.addTab(trans_widget, "🌐 Translation")
        
    def setup_advanced_tab(self, tab_widget):
        """Setup advanced settings tab"""
        advanced_widget = QWidget()
        layout = QVBoxLayout(advanced_widget)
        
        # Custom prompt section
        prompt_group = QGroupBox("📝 Custom Translation Prompt")
        prompt_layout = QVBoxLayout(prompt_group)
        
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setMaximumHeight(200)
        prompt_layout.addWidget(self.prompt_edit)
        
        prompt_buttons = QHBoxLayout()
        self.load_prompt_btn = QPushButton("📂 Load Prompt")
        self.load_prompt_btn.clicked.connect(self.load_prompt)
        prompt_buttons.addWidget(self.load_prompt_btn)
        
        self.save_prompt_btn = QPushButton("💾 Save Prompt")
        self.save_prompt_btn.clicked.connect(self.save_prompt)
        prompt_buttons.addWidget(self.save_prompt_btn)
        
        self.reset_prompt_btn = QPushButton("🔄 Reset to Default")
        self.reset_prompt_btn.clicked.connect(self.reset_prompt)
        prompt_buttons.addWidget(self.reset_prompt_btn)
        
        prompt_layout.addLayout(prompt_buttons)
        layout.addWidget(prompt_group)
        
        # Vocabulary section
        vocab_group = QGroupBox("📚 Custom Vocabulary")
        vocab_layout = QVBoxLayout(vocab_group)
        
        self.vocab_edit = QTextEdit()
        self.vocab_edit.setMaximumHeight(200)
        vocab_layout.addWidget(self.vocab_edit)
        
        vocab_buttons = QHBoxLayout()
        self.load_vocab_btn = QPushButton("📂 Load Vocabulary")
        self.load_vocab_btn.clicked.connect(self.load_vocabulary)
        vocab_buttons.addWidget(self.load_vocab_btn)
        
        self.save_vocab_btn = QPushButton("💾 Save Vocabulary")
        self.save_vocab_btn.clicked.connect(self.save_vocabulary)
        vocab_buttons.addWidget(self.save_vocab_btn)
        
        vocab_layout.addLayout(vocab_buttons)
        layout.addWidget(vocab_group)
        
        # File filters
        filter_group = QGroupBox("🗂️ File Filters")
        filter_layout = QVBoxLayout(filter_group)
        
        self.include_patterns_edit = QLineEdit()
        self.include_patterns_edit.setPlaceholderText("Include patterns (e.g., *.json, Map*.json)")
        filter_layout.addWidget(QLabel("Include Patterns:"))
        filter_layout.addWidget(self.include_patterns_edit)
        
        self.exclude_patterns_edit = QLineEdit()
        self.exclude_patterns_edit.setPlaceholderText("Exclude patterns (e.g., System.json, CommonEvents.json)")
        filter_layout.addWidget(QLabel("Exclude Patterns:"))
        filter_layout.addWidget(self.exclude_patterns_edit)
        
        layout.addWidget(filter_group)
        
        tab_widget.addTab(advanced_widget, "🔧 Advanced")
        
    def setup_log_tab(self, tab_widget):
        """Setup log tab"""
        log_widget = QWidget()
        layout = QVBoxLayout(log_widget)
        
        # Log controls
        log_controls = QHBoxLayout()
        
        self.clear_log_btn = QPushButton("🗑️ Clear Log")
        self.clear_log_btn.clicked.connect(self.clear_log)
        log_controls.addWidget(self.clear_log_btn)
        
        self.save_log_btn = QPushButton("💾 Save Log")
        self.save_log_btn.clicked.connect(self.save_log)
        log_controls.addWidget(self.save_log_btn)
        
        log_controls.addStretch()
        
        self.auto_scroll_checkbox = QCheckBox("Auto-scroll")
        self.auto_scroll_checkbox.setChecked(True)
        log_controls.addWidget(self.auto_scroll_checkbox)
        
        layout.addLayout(log_controls)
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Consolas", 9))
        layout.addWidget(self.log_display)
        
        tab_widget.addTab(log_widget, "📋 Log")
    
    def on_model_changed(self):
        """Handle model selection change"""
        current_data = self.model_combo.currentData()
        if current_data and current_data != "custom":
            # Update pricing automatically
            pricing = self.model_db.get_pricing_for_model(current_data)
            
            self.input_cost_spin.setValue(pricing['input_cost'])
            self.output_cost_spin.setValue(pricing['output_cost'])
            
            # Show info about the model
            model_info = self.model_db.get_model(current_data)
            if model_info:
                self.log_message(f"Selected {model_info.display_name}")
                self.log_message(f"Provider: {model_info.provider.value}")
                self.log_message(f"Context length: {model_info.context_length:,} tokens")
                self.log_message(f"Pricing updated: ${pricing['input_cost']:.4f} input, ${pricing['output_cost']:.4f} output per 1K tokens")
    
    def toggle_api_key_visibility(self, show):
        """Toggle API key visibility"""
        if show:
            self.api_key_edit.setEchoMode(QLineEdit.Normal)
        else:
            self.api_key_edit.setEchoMode(QLineEdit.Password)
    
    def browse_input_directory(self):
        """Browse for input directory"""
        directory = QFileDialog.getExistingDirectory(self, "Select Game Directory")
        if directory:
            self.input_dir_edit.setText(directory)
            self.detect_project_type(directory)
    
    def detect_project_type(self, directory):
        """Detect and display project type"""
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
        
        renpy_processor = RenpyProcessor()
        unity_processor = UnityProcessor()
        wolf_processor = WolfProcessor()
        kirikiri_processor = KiriKiriProcessor()
        nscripter_processor = NScripterProcessor()
        livemaker_processor = LiveMakerProcessor()
        tyranobuilder_processor = TyranoBuilderProcessor()
        srpg_studio_processor = SRPGStudioProcessor()
        lune_processor = LuneProcessor()
        regex_processor = RegexProcessor()
        
        if renpy_processor.detect_renpy_project(directory):
            self.project_type_label.setText("✅ Ren'Py project detected")
            self.project_type_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        elif unity_processor.detect_unity_project(directory):
            self.project_type_label.setText("✅ Unity project detected")
            self.project_type_label.setStyleSheet("color: #9C27B0; font-weight: bold;")
        elif wolf_processor.detect_wolf_project(directory):
            self.project_type_label.setText("✅ Wolf RPG Editor project detected")
            self.project_type_label.setStyleSheet("color: #FF5722; font-weight: bold;")
        elif kirikiri_processor.detect_kirikiri_project(directory):
            self.project_type_label.setText("✅ KiriKiri project detected")
            self.project_type_label.setStyleSheet("color: #3F51B5; font-weight: bold;")
        elif nscripter_processor.detect_nscripter_project(directory):
            self.project_type_label.setText("✅ NScripter project detected")
            self.project_type_label.setStyleSheet("color: #009688; font-weight: bold;")
        elif len(livemaker_processor.find_livemaker_files(directory)) > 0:
            self.project_type_label.setText("✅ Live Maker project detected")
            self.project_type_label.setStyleSheet("color: #E91E63; font-weight: bold;")
        elif len(tyranobuilder_processor.find_tyranobuilder_files(directory)) > 0:
            self.project_type_label.setText("✅ TyranoBuilder project detected")
            self.project_type_label.setStyleSheet("color: #9C27B0; font-weight: bold;")
        elif len(srpg_studio_processor.find_srpg_studio_files(directory)) > 0:
            self.project_type_label.setText("✅ SRPG Studio project detected")
            self.project_type_label.setStyleSheet("color: #607D8B; font-weight: bold;")
        elif len(lune_processor.find_lune_files(directory)) > 0:
            self.project_type_label.setText("✅ Lune project detected")
            self.project_type_label.setStyleSheet("color: #FF9800; font-weight: bold;")
        elif len(regex_processor.find_regex_files(directory)) > 0:
            self.project_type_label.setText("✅ Regex project detected")
            self.project_type_label.setStyleSheet("color: #CDDC39; font-weight: bold;")
        elif self.detect_rpg_maker_project(directory):
            self.project_type_label.setText("✅ RPG Maker project detected")
            self.project_type_label.setStyleSheet("color: #2196F3; font-weight: bold;")
        else:
            self.project_type_label.setText("⚠️ No supported project detected")
            self.project_type_label.setStyleSheet("color: #FF9800; font-weight: bold;")
    
    def detect_rpg_maker_project(self, directory):
        """Detect if directory contains RPG Maker project"""
        # Check for common paths
        possible_paths = [
            os.path.join(directory, 'www', 'data'),
            os.path.join(directory, 'data'),
            os.path.join(directory, 'www', 'js', 'plugins')
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                # Look for RPG Maker JSON files
                for file in os.listdir(path):
                    if file.endswith('.json') and any(
                        pattern in file for pattern in ['Map', 'CommonEvents', 'System']
                    ):
                        return True
        return False
    
    def browse_output_directory(self):
        """Browse for output directory"""
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.output_dir_edit.setText(directory)
    
    def test_api_connection(self):
        """Test API connection"""
        self.log_message("Testing API connection...")
        # TODO: Implement API test
        QMessageBox.information(self, "API Test", "API connection test would be implemented here")
    
    def save_config(self):
        """Save current configuration"""
        config = self.get_current_config()
        self.config_manager.save_config(config)
        self.log_message("Configuration saved successfully")
        QMessageBox.information(self, "Success", "Configuration saved successfully!")
    
    def load_config_dialog(self):
        """Load configuration from file"""
        filename, _ = QFileDialog.getOpenFileName(self, "Load Configuration", "", "ENV files (*.env)")
        if filename:
            self.config_manager.load_config(filename)
            self.load_config()
            self.log_message(f"Configuration loaded from {filename}")
    
    def load_config(self):
        """Load configuration into UI"""
        config = self.config_manager.get_config()
        
        self.api_url_edit.setText(config.get('api', ''))
        self.api_key_edit.setText(config.get('key', ''))
        self.organization_edit.setText(config.get('organization', ''))
        self.model_combo.setCurrentText(config.get('model', 'gpt-4'))
        self.language_combo.setCurrentText(config.get('language', 'English'))
        self.timeout_spin.setValue(int(config.get('timeout', 120)))
        self.file_threads_spin.setValue(int(config.get('fileThreads', 1)))
        self.threads_spin.setValue(int(config.get('threads', 1)))
        self.width_spin.setValue(int(config.get('width', 60)))
        self.list_width_spin.setValue(int(config.get('listWidth', 100)))
        self.note_width_spin.setValue(int(config.get('noteWidth', 75)))
        self.input_cost_spin.setValue(float(config.get('input_cost', 0.002)))
        self.output_cost_spin.setValue(float(config.get('output_cost', 0.002)))
        self.batch_size_spin.setValue(int(config.get('batchsize', 10)))
        self.frequency_penalty_spin.setValue(float(config.get('frequency_penalty', 0.2)))
    
    def get_current_config(self):
        """Get current configuration from UI"""
        # Get model value - use currentData if available, otherwise currentText
        model_data = self.model_combo.currentData()
        model_value = model_data if model_data and model_data != "custom" else self.model_combo.currentText()
        
        return {
            'api': self.api_url_edit.text(),
            'key': self.api_key_edit.text(),
            'organization': self.organization_edit.text(),
            'model': model_value,
            'language': self.language_combo.currentText(),
            'timeout': str(self.timeout_spin.value()),
            'fileThreads': str(self.file_threads_spin.value()),
            'threads': str(self.threads_spin.value()),
            'width': str(self.width_spin.value()),
            'listWidth': str(self.list_width_spin.value()),
            'noteWidth': str(self.note_width_spin.value()),
            'input_cost': str(self.input_cost_spin.value()),
            'output_cost': str(self.output_cost_spin.value()),
            'batchsize': str(self.batch_size_spin.value()),
            'frequency_penalty': str(self.frequency_penalty_spin.value()),
            # OpenRouter specific
            'openrouter_url': self.openrouter_url_edit.text(),
            'site_url': self.site_url_edit.text(),
            'app_name': self.app_name_edit.text(),
            # Ollama specific
            'ollama_url': self.ollama_url_edit.text(),
            'ollama_model': self.ollama_model_edit.text()
        }
    
    def load_prompt(self):
        """Load custom prompt from file"""
        try:
            with open('prompt.txt', 'r', encoding='utf-8') as f:
                self.prompt_edit.setPlainText(f.read())
            self.log_message("Prompt loaded from prompt.txt")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load prompt: {e}")
    
    def save_prompt(self):
        """Save current prompt to file"""
        try:
            with open('prompt.txt', 'w', encoding='utf-8') as f:
                f.write(self.prompt_edit.toPlainText())
            self.log_message("Prompt saved to prompt.txt")
            QMessageBox.information(self, "Success", "Prompt saved successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save prompt: {e}")
    
    def reset_prompt(self):
        """Reset prompt to default"""
        self.load_prompt()
    
    def load_vocabulary(self):
        """Load vocabulary from file"""
        try:
            with open('vocab.txt', 'r', encoding='utf-8') as f:
                self.vocab_edit.setPlainText(f.read())
            self.log_message("Vocabulary loaded from vocab.txt")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load vocabulary: {e}")
    
    def save_vocabulary(self):
        """Save current vocabulary to file"""
        try:
            with open('vocab.txt', 'w', encoding='utf-8') as f:
                f.write(self.vocab_edit.toPlainText())
            self.log_message("Vocabulary saved to vocab.txt")
            QMessageBox.information(self, "Success", "Vocabulary saved successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save vocabulary: {e}")
    
    def start_translation(self):
        """Start translation process"""
        if not self.validate_inputs():
            return
        
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        
        config = self.get_current_config()
        input_dir = self.input_dir_edit.text()
        output_dir = self.output_dir_edit.text()
        
        self.translation_manager = TranslationManager(config, input_dir, output_dir)
        self.translation_manager.progress_updated.connect(self.update_progress)
        self.translation_manager.log_message.connect(self.log_message)
        self.translation_manager.finished.connect(self.translation_finished)
        
        self.translation_manager.start()
        self.log_message("Translation started...")
    
    def pause_translation(self):
        """Pause translation process"""
        if self.translation_manager:
            self.translation_manager.pause()
            self.log_message("Translation paused")
    
    def stop_translation(self):
        """Stop translation process"""
        if self.translation_manager:
            self.translation_manager.stop()
            self.translation_finished()
            self.log_message("Translation stopped by user")
    
    def translation_finished(self):
        """Handle translation completion"""
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setValue(100)
        self.log_message("Translation completed!")
    
    def validate_inputs(self):
        """Validate user inputs"""
        if not self.api_key_edit.text().strip():
            QMessageBox.warning(self, "Error", "Please enter your API key")
            return False
        
        if not self.input_dir_edit.text().strip():
            QMessageBox.warning(self, "Error", "Please select an input directory")
            return False
        
        # Auto-create output directory if not specified
        if not self.output_dir_edit.text().strip():
            input_dir = self.input_dir_edit.text().strip()
            auto_output_dir = os.path.join(input_dir, "translated")
            self.output_dir_edit.setText(auto_output_dir)
            self.log_message(f"Auto-created output directory: {auto_output_dir}")
        
        if not os.path.exists(self.input_dir_edit.text()):
            QMessageBox.warning(self, "Error", "Input directory does not exist")
            return False
        
        return True
    
    def update_progress(self, current, total, filename=""):
        """Update progress indicators"""
        if total > 0:
            progress = int((current / total) * 100)
            self.progress_bar.setValue(progress)
            self.progress_label.setText(f"Progress: {current}/{total} files")
            if filename:
                self.file_progress_label.setText(f"Current file: {filename}")
    
    def log_message(self, message):
        """Add message to log"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        self.log_display.append(formatted_message)
        
        if self.auto_scroll_checkbox.isChecked():
            cursor = self.log_display.textCursor()
            cursor.movePosition(cursor.End)
            self.log_display.setTextCursor(cursor)
    
    def clear_log(self):
        """Clear log display"""
        self.log_display.clear()
    
    def save_log(self):
        """Save log to file"""
        filename, _ = QFileDialog.getSaveFileName(self, "Save Log", "translation_log.txt", "Text files (*.txt)")
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_display.toPlainText())
                QMessageBox.information(self, "Success", "Log saved successfully!")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save log: {e}")
    
    def on_language_changed(self, language_display_name: str):
        """Handle language selection change"""
        if language_display_name == "Other (Custom)":
            # Show dialog for custom language input
            custom_language, ok = QInputDialog.getText(
                self, 
                "Custom Language", 
                "Enter the target language name:",
                text="English"
            )
            if ok and custom_language.strip():
                # Update config with custom language
                self.config_manager.set_value('language', custom_language.strip())
                self.log_message(f"Custom language set to: {custom_language.strip()}")
            else:
                # Revert to previous selection
                self.language_combo.blockSignals(True)
                self.language_combo.setCurrentText("English (en)")
                self.language_combo.blockSignals(False)
                return
        else:
            # Update prompts and vocabulary for selected language
            lang_info = self.language_manager.get_language_info(language_display_name)
            if lang_info:
                self.log_message(f"Language changed to: {lang_info['native_name']} ({lang_info['code']})")
                
                # Auto-load localized prompt and vocabulary
                localized_prompt = self.language_manager.get_prompt_for_language(language_display_name)
                localized_vocab = self.language_manager.get_vocab_for_language(language_display_name)
                
                # Update the text fields if they exist
                if hasattr(self, 'prompt_edit'):
                    self.prompt_edit.setPlainText(localized_prompt)
                if hasattr(self, 'vocab_edit'):
                    self.vocab_edit.setPlainText(localized_vocab)
                
                self.log_message(f"Updated prompt and vocabulary for {lang_info['native_name']}")
                
                # Update config
                self.config_manager.set_value('language', lang_info['name'])
    
    def show_estimation_results(self, estimate):
        """Show project estimation results"""
        total_files = estimate.get('total_files', 0)
        translatable_files = estimate.get('translatable_files', 0)
        total_japanese_strings = estimate.get('total_japanese_strings', 0)
        estimated_tokens = estimate.get('estimated_tokens', 0)
        estimated_cost = estimate.get('estimated_cost', 0.0)
        
        # Format the results
        result_text = f"""Project Estimation Results:
        
📁 Files:
  • Total files found: {total_files}
  • Files needing translation: {translatable_files}
  
📝 Content:
  • Japanese text entries: {total_japanese_strings:,}
  • Estimated tokens: {estimated_tokens:,}
  
💰 Cost Estimation:
  • Estimated cost: ${estimated_cost:.2f}
  • Model: {self.model_combo.currentText()}
  
⏱️ Time Estimation:
  • Estimated time: {self.estimate_translation_time(estimated_tokens)} minutes
  
Note: These are rough estimates. Actual costs and time may vary."""
        
        # Show in a message box
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Project Estimation")
        msg_box.setText("Project estimation completed!")
        msg_box.setDetailedText(result_text)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.exec_()
        
        # Also log the summary
        self.log_message(f"Project estimated: {translatable_files} files, {total_japanese_strings:,} strings, ~${estimated_cost:.2f}")
    
    def estimate_translation_time(self, estimated_tokens: int) -> int:
        """Estimate translation time in minutes"""
        # Rough estimate: 1000 tokens per minute for GPT-4, 2000 for GPT-3.5
        model = self.model_combo.currentText().lower()
        
        if 'gpt-4' in model or 'claude' in model:
            tokens_per_minute = 1000
        elif 'gpt-3.5' in model or 'gemini' in model:
            tokens_per_minute = 2000
        else:
            tokens_per_minute = 1500  # Default estimate
        
        # Add overhead for batching and rate limits
        overhead_factor = 1.5
        
        estimated_minutes = (estimated_tokens / tokens_per_minute) * overhead_factor
        return max(1, int(estimated_minutes))
    
    def estimate_project(self):
        """Estimate project translation costs and requirements"""
        input_dir = self.input_dir_edit.text().strip()
        
        if not input_dir:
            QMessageBox.warning(self, "Error", "Please select a game directory first")
            return
        
        if not os.path.exists(input_dir):
            QMessageBox.warning(self, "Error", "Selected directory does not exist")
            return
        
        # Get current model
        current_model = self.model_combo.currentText()
        if not current_model:
            QMessageBox.warning(self, "Error", "Please select a model first")
            return
        
        try:
            # Show progress dialog
            from PyQt5.QtWidgets import QProgressDialog
            progress = QProgressDialog("Analyzing project files...", "Cancel", 0, 0, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.setAutoClose(True)
            progress.setAutoReset(True)
            progress.show()
            
            # Create estimator and run estimation
            estimator = ProjectEstimator()
            estimate = estimator.estimate_project(input_dir, current_model)
            
            progress.close()
            
            # Show results in a dialog
            self.show_estimation_results(estimate)
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to estimate project: {str(e)}")
            self.log_message(f"Estimation error: {str(e)}")
    
    def show_estimation_results(self, estimate):
        """Show estimation results in a dialog"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Project Cost Estimation")
        dialog.setModal(True)
        dialog.resize(700, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Summary section
        summary = estimate['summary']
        
        summary_text = f"""
🔍 PROJECT ANALYSIS SUMMARY
{'=' * 50}

📊 FILES:
  • Total files found: {summary['total_files_found']}
  • Files needing translation: {summary['translatable_files']}
  • Japanese text entries: {summary['total_japanese_strings']:,}

🤖 MODEL: {summary['model_name']}

🔢 ESTIMATED TOKENS:
  • Input tokens: {summary['estimated_input_tokens']:,}
  • Output tokens: {summary['estimated_output_tokens']:,}
  • Total tokens: {summary['estimated_input_tokens'] + summary['estimated_output_tokens']:,}

💰 ESTIMATED COST:
  • Input cost: ${summary['estimated_cost']['input_cost']:.4f}
  • Output cost: ${summary['estimated_cost']['output_cost']:.4f}
  • Total estimated cost: ${summary['estimated_cost']['total_cost']:.4f}

⚠️  Note: These are estimates. Actual costs may vary based on:
   • Actual token usage (depends on text complexity)
   • API pricing changes
   • Translation quality requirements
   • Caching and optimization features
"""
        
        # Add file details
        if estimate['file_details']:
            summary_text += f"\n\n📁 FILE BREAKDOWN (Top 10):\n"
            for i, file_detail in enumerate(estimate['file_details'][:10]):
                rel_path = file_detail['relative_path']
                strings = file_detail['japanese_strings']
                tokens = file_detail['estimated_input_tokens'] + file_detail['estimated_output_tokens']
                summary_text += f"  {i+1:2d}. {rel_path}: {strings} strings (~{tokens:,} tokens)\n"
            
            if len(estimate['file_details']) > 10:
                remaining = len(estimate['file_details']) - 10
                summary_text += f"     ... and {remaining} more files\n"
        
        # Text display
        text_display = QTextEdit()
        text_display.setPlainText(summary_text)
        text_display.setReadOnly(True)
        text_display.setFont(QFont("Consolas", 10))
        layout.addWidget(text_display)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Save Report")
        save_btn.clicked.connect(lambda: self.save_estimation_report(estimate))
        button_layout.addWidget(save_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec_()
    
    def save_estimation_report(self, estimate):
        """Save estimation report to file"""
        estimator = ProjectEstimator()
        report = estimator.generate_estimate_report(estimate)
        
        filename, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Estimation Report", 
            f"estimation_report_{estimate['summary']['model_name'].replace('/', '_')}.txt",
            "Text files (*.txt)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(report)
                
                QMessageBox.information(self, "Success", f"Report saved to {filename}")
                self.log_message(f"Estimation report saved: {filename}")
                
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save report: {str(e)}")
