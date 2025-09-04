"""
Main Window for Eroge Translation Tool
User-friendly interface for configuring and running translations
"""

import os
import json
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QLabel, QLineEdit, QPushButton, 
                             QTextEdit, QTextBrowser, QFileDialog, QProgressBar, QSpinBox,
                             QComboBox, QCheckBox, QGroupBox, QGridLayout,
                             QMessageBox, QScrollArea, QFrame, QDoubleSpinBox,
                             QInputDialog, QDialog, QApplication, QDesktopWidget, QListWidget)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QPixmap

import os
import time
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
        self.setWindowTitle("BaconanaMTL Tool v1.2")

        # Get screen geometry
        screen = QApplication.desktop().screenGeometry()
        
        # Start maximized but respect screen size
        self.showMaximized()
        
        # Set reasonable fallback size (80% of screen size)
        fallback_width = int(screen.width() * 0.8)
        fallback_height = int(screen.height() * 0.8)
        fallback_x = int((screen.width() - fallback_width) / 2)
        fallback_y = int((screen.height() - fallback_height) / 2)
        
        self.setGeometry(fallback_x, fallback_y, fallback_width, fallback_height)
        
        # Set minimum size based on screen size
        min_width = min(800, int(screen.width() * 0.4))
        min_height = min(600, int(screen.height() * 0.4))
        self.setMinimumSize(min_width, min_height)
        
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
        self.setup_lightnovel_tab(tab_widget)
        self.setup_audio_tab(tab_widget)
        self.setup_character_tab(tab_widget)
        self.setup_novel_writing_tab(tab_widget)
        self.setup_cloud_tab(tab_widget)
        self.setup_providers_tab(tab_widget)
        self.setup_advanced_tab(tab_widget)
        self.setup_documentation_tab(tab_widget)
        self.setup_about_tab(tab_widget)
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
        
        tab_widget.addTab(trans_widget, "🌐 Game Translation")
        
    def setup_lightnovel_tab(self, tab_widget):
        """Setup light novel translation tab with scroll area"""
        ln_widget = QWidget()
        main_layout = QVBoxLayout(ln_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create scrollable content widget
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
        # Header
        header_label = QLabel("📚 Light Novel Translation")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setStyleSheet("color: #8E24AA; margin: 10px 0px;")
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel("Translate light novels in various formats (TXT, DOCX, PDF, EPUB) with specialized prompts and terminology.")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; margin-bottom: 15px;")
        layout.addWidget(desc_label)
        
        # Input file section
        input_group = QGroupBox("📁 Input File")
        input_layout = QVBoxLayout(input_group)
        
        # File selection
        file_layout = QHBoxLayout()
        self.ln_input_file_edit = QLineEdit()
        self.ln_input_file_edit.setPlaceholderText("Select light novel file (TXT, DOCX, PDF, EPUB)")
        self.ln_browse_file_btn = QPushButton("📁 Browse File")
        self.ln_browse_file_btn.clicked.connect(self.browse_lightnovel_file)
        file_layout.addWidget(self.ln_input_file_edit)
        file_layout.addWidget(self.ln_browse_file_btn)
        input_layout.addLayout(file_layout)
        
        # File info label
        self.ln_file_info_label = QLabel("No file selected")
        self.ln_file_info_label.setStyleSheet("color: #666; font-style: italic; margin: 5px 0px;")
        input_layout.addWidget(self.ln_file_info_label)
        
        layout.addWidget(input_group)
        
        # Output settings section
        output_group = QGroupBox("💾 Output Settings")
        output_layout = QVBoxLayout(output_group)
        
        # Output directory
        dir_layout = QHBoxLayout()
        self.ln_output_dir_edit = QLineEdit()
        self.ln_output_dir_edit.setPlaceholderText("Select output directory")
        self.ln_browse_output_btn = QPushButton("📂 Browse Directory")
        self.ln_browse_output_btn.clicked.connect(self.browse_lightnovel_output)
        dir_layout.addWidget(self.ln_output_dir_edit)
        dir_layout.addWidget(self.ln_browse_output_btn)
        output_layout.addLayout(dir_layout)
        
        # Output format selection
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Output Format:"))
        self.ln_output_format_combo = QComboBox()
        self.ln_output_format_combo.addItems(["Same as input", "TXT", "DOCX", "PDF", "EPUB"])
        self.ln_output_format_combo.setCurrentText("Same as input")
        format_layout.addWidget(self.ln_output_format_combo)
        format_layout.addStretch()
        output_layout.addLayout(format_layout)
        
        layout.addWidget(output_group)
        
        # Translation settings section
        settings_group = QGroupBox("⚙️ Translation Settings")
        settings_layout = QVBoxLayout(settings_group)
        
        # Use specialized prompt checkbox
        self.ln_use_specialized_prompt = QCheckBox("Use specialized light novel prompt")
        self.ln_use_specialized_prompt.setChecked(True)
        self.ln_use_specialized_prompt.setToolTip("Use prompts optimized for light novel translation")
        settings_layout.addWidget(self.ln_use_specialized_prompt)
        
        # Use specialized vocabulary checkbox
        self.ln_use_specialized_vocab = QCheckBox("Use specialized light novel vocabulary")
        self.ln_use_specialized_vocab.setChecked(True)
        self.ln_use_specialized_vocab.setToolTip("Use vocabulary terms common in light novels")
        settings_layout.addWidget(self.ln_use_specialized_vocab)
        
        # Eroge content checkbox
        self.ln_eroge_mode = QCheckBox("🔞 Enable eroge/mature content mode")
        self.ln_eroge_mode.setChecked(False)
        self.ln_eroge_mode.setToolTip("Enable specialized handling for erotic/mature content with appropriate prompts and vocabulary")
        self.ln_eroge_mode.setStyleSheet("QCheckBox { color: #FF6B6B; font-weight: bold; }")
        settings_layout.addWidget(self.ln_eroge_mode)
        
        # Auto-detect eroge content
        self.ln_auto_detect_eroge = QCheckBox("🔍 Auto-detect mature content")
        self.ln_auto_detect_eroge.setChecked(True)
        self.ln_auto_detect_eroge.setToolTip("Automatically detect erotic content and enable appropriate mode")
        settings_layout.addWidget(self.ln_auto_detect_eroge)
        
        # Text chunking settings
        chunking_group = QGroupBox("📄 Text Processing")
        chunking_layout = QVBoxLayout(chunking_group)
        
        # Enable text chunking
        self.ln_enable_chunking = QCheckBox("Enable smart text chunking (recommended for API safety)")
        self.ln_enable_chunking.setChecked(True)
        self.ln_enable_chunking.setToolTip("Split large texts into smaller chunks to avoid API moderation issues")
        chunking_layout.addWidget(self.ln_enable_chunking)
        
        # Chunk size setting
        chunk_layout = QHBoxLayout()
        chunk_layout.addWidget(QLabel("Max tokens per chunk:"))
        self.ln_chunk_size = QSpinBox()
        self.ln_chunk_size.setRange(500, 3000)
        self.ln_chunk_size.setValue(1500)
        self.ln_chunk_size.setToolTip("Maximum tokens per translation request (1500-2000 recommended)")
        chunk_layout.addWidget(self.ln_chunk_size)
        chunk_layout.addStretch()
        chunking_layout.addLayout(chunk_layout)
        
        # Overlap setting
        overlap_layout = QHBoxLayout()
        overlap_layout.addWidget(QLabel("Context overlap tokens:"))
        self.ln_overlap_tokens = QSpinBox()
        self.ln_overlap_tokens.setRange(50, 500)
        self.ln_overlap_tokens.setValue(100)
        self.ln_overlap_tokens.setToolTip("Tokens to overlap between chunks for context continuity")
        overlap_layout.addWidget(self.ln_overlap_tokens)
        overlap_layout.addStretch()
        chunking_layout.addLayout(overlap_layout)
        
        settings_layout.addWidget(chunking_group)
        
        # Chapter processing options
        chapter_layout = QHBoxLayout()
        chapter_layout.addWidget(QLabel("Chapter Processing:"))
        self.ln_chapter_mode_combo = QComboBox()
        self.ln_chapter_mode_combo.addItems(["Auto-detect chapters", "Process as single text", "Split by length"])
        self.ln_chapter_mode_combo.setCurrentText("Auto-detect chapters")
        chapter_layout.addWidget(self.ln_chapter_mode_combo)
        chapter_layout.addStretch()
        settings_layout.addLayout(chapter_layout)
        
        # Max chapter length for splitting
        length_layout = QHBoxLayout()
        length_layout.addWidget(QLabel("Max section length (characters):"))
        self.ln_max_section_length = QSpinBox()
        self.ln_max_section_length.setRange(1000, 20000)
        self.ln_max_section_length.setValue(5000)
        self.ln_max_section_length.setToolTip("Maximum length for auto-split sections")
        length_layout.addWidget(self.ln_max_section_length)
        length_layout.addStretch()
        settings_layout.addLayout(length_layout)
        
        layout.addWidget(settings_group)
        
        # Model recommendations section
        recommendations_group = QGroupBox("🤖 Model Recommendations")
        recommendations_layout = QVBoxLayout(recommendations_group)
        
        self.ln_model_warning_label = QLabel("")
        self.ln_model_warning_label.setWordWrap(True)
        self.ln_model_warning_label.setStyleSheet("color: #FF6B6B; font-weight: bold; padding: 5px; border: 1px solid #FF6B6B; border-radius: 3px; background-color: #FFF5F5;")
        self.ln_model_warning_label.setVisible(False)
        recommendations_layout.addWidget(self.ln_model_warning_label)
        
        self.ln_model_recommendation_label = QLabel("💡 For best results with mature content, consider using OpenRouter models or self-hosted solutions (Ollama)")
        self.ln_model_recommendation_label.setWordWrap(True)
        self.ln_model_recommendation_label.setStyleSheet("color: #4CAF50; padding: 5px; border: 1px solid #4CAF50; border-radius: 3px; background-color: #F5FFF5;")
        recommendations_layout.addWidget(self.ln_model_recommendation_label)
        
        layout.addWidget(recommendations_group)
        
        # Progress section
        progress_group = QGroupBox("📊 Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.ln_progress_bar = QProgressBar()
        self.ln_progress_bar.setVisible(False)
        progress_layout.addWidget(self.ln_progress_bar)
        
        self.ln_status_label = QLabel("Ready to translate light novel")
        self.ln_status_label.setStyleSheet("color: #666; font-style: italic;")
        progress_layout.addWidget(self.ln_status_label)
        
        layout.addWidget(progress_group)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        self.ln_estimate_btn = QPushButton("💰 Estimate Cost")
        self.ln_estimate_btn.clicked.connect(self.estimate_lightnovel_cost)
        self.ln_estimate_btn.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold; padding: 8px;")
        control_layout.addWidget(self.ln_estimate_btn)
        
        self.ln_translate_btn = QPushButton("🚀 Start Translation")
        self.ln_translate_btn.clicked.connect(self.start_lightnovel_translation)
        self.ln_translate_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        control_layout.addWidget(self.ln_translate_btn)
        
        self.ln_pause_btn = QPushButton("⏸️ Pause")
        self.ln_pause_btn.clicked.connect(self.pause_lightnovel_translation)
        self.ln_pause_btn.setEnabled(False)
        control_layout.addWidget(self.ln_pause_btn)
        
        self.ln_stop_btn = QPushButton("⏹️ Stop")
        self.ln_stop_btn.clicked.connect(self.stop_lightnovel_translation)
        self.ln_stop_btn.setEnabled(False)
        control_layout.addWidget(self.ln_stop_btn)
        
        layout.addLayout(control_layout)
        
        # Add stretch to push content to top
        layout.addStretch()
        
        # Set content widget to scroll area
        scroll_area.setWidget(content_widget)
        
        # Add scroll area to main layout
        main_layout.addWidget(scroll_area)
        
        # Connect signals for eroge mode updates
        self.ln_eroge_mode.toggled.connect(self.update_model_recommendations)
        self.model_combo.currentTextChanged.connect(self.update_model_recommendations)
        
        tab_widget.addTab(ln_widget, "📚 Light Novel")
    
    def setup_audio_tab(self, tab_widget):
        """Setup audio transcription and subtitles tab"""
        audio_widget = QWidget()
        layout = QVBoxLayout(audio_widget)
        
        # Scroll area
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Audio File Selection Group
        file_group = QGroupBox("🎵 Audio File Selection")
        file_layout = QGridLayout(file_group)
        
        file_layout.addWidget(QLabel("Audio File:"), 0, 0)
        self.audio_file_edit = QLineEdit()
        self.audio_file_edit.setPlaceholderText("Select audio or video file...")
        file_layout.addWidget(self.audio_file_edit, 0, 1)
        
        self.audio_browse_btn = QPushButton("Browse")
        self.audio_browse_btn.clicked.connect(self.browse_audio_file)
        file_layout.addWidget(self.audio_browse_btn, 0, 2)
        
        # Audio info display
        self.audio_info_label = QLabel("No file selected")
        self.audio_info_label.setStyleSheet("color: gray; font-style: italic;")
        file_layout.addWidget(self.audio_info_label, 1, 0, 1, 3)
        
        scroll_layout.addWidget(file_group)
        
        # Transcription Provider Group
        provider_group = QGroupBox("🤖 Transcription Provider")
        provider_layout = QGridLayout(provider_group)
        
        provider_layout.addWidget(QLabel("Provider:"), 0, 0)
        self.audio_provider_combo = QComboBox()
        self.audio_provider_combo.addItems([
            "OpenAI Whisper ($0.006/min)",
            "Groq Whisper V3 Large ($0.111/hr)",
            "Groq Whisper Large V3 Turbo ($0.04/hr)",
            "AssemblyAI Universal-2 ($0.12/hr)",
            "Nova-1 ($0.0043/min)",
            "Nova-2 ($0.0043/min)",
            "Nova-3 Multilingual ($0.0052/min)",
            "Nova-3 Monolingual ($0.0043/min)",
            "Speechmatics ($0.30/hr)",
            "Gladia ($0.612/hr)",
            "Azure AI Speech Batch ($0.18/hr)",
            "Azure AI Speech Realtime ($1.0/hr)",
            "---Local Models---",
            "Faster-Whisper Tiny (Free)",
            "Faster-Whisper Base (Free)",
            "Faster-Whisper Small (Free)",
            "Faster-Whisper Medium (Free)",
            "Faster-Whisper Large-V1 (Free)",
            "Faster-Whisper Large-V2 (Free)"
        ])
        self.audio_provider_combo.currentTextChanged.connect(self.update_transcription_cost)
        provider_layout.addWidget(self.audio_provider_combo, 0, 1)
        
        # Cost estimation
        self.cost_label = QLabel("Estimated cost: $0.00")
        self.cost_label.setStyleSheet("font-weight: bold; color: green;")
        provider_layout.addWidget(self.cost_label, 1, 0, 1, 2)
        
        scroll_layout.addWidget(provider_group)
        
        # Local Model Management Group
        local_model_group = QGroupBox("💾 Local Model Management")
        local_layout = QVBoxLayout(local_model_group)
        
        # Installed models list
        installed_label = QLabel("Installed Models:")
        local_layout.addWidget(installed_label)
        
        self.installed_models_list = QTextEdit()
        self.installed_models_list.setMaximumHeight(80)
        self.installed_models_list.setReadOnly(True)
        local_layout.addWidget(self.installed_models_list)
        
        # Model download section
        download_layout = QHBoxLayout()
        
        download_layout.addWidget(QLabel("Download Model:"))
        self.model_download_combo = QComboBox()
        self.model_download_combo.addItems([
            "tiny (39 MB)",
            "base (74 MB)", 
            "small (244 MB)",
            "medium (769 MB)",
            "large-v1 (1550 MB)",
            "large-v2 (1550 MB)"
        ])
        download_layout.addWidget(self.model_download_combo)
        
        self.download_model_btn = QPushButton("Download")
        self.download_model_btn.clicked.connect(self.download_model)
        download_layout.addWidget(self.download_model_btn)
        
        self.delete_model_btn = QPushButton("Delete")
        self.delete_model_btn.clicked.connect(self.delete_model)
        download_layout.addWidget(self.delete_model_btn)
        
        local_layout.addLayout(download_layout)
        
        # Download progress
        self.model_progress = QProgressBar()
        self.model_progress.setVisible(False)
        local_layout.addWidget(self.model_progress)
        
        self.model_status_label = QLabel("")
        local_layout.addWidget(self.model_status_label)
        
        scroll_layout.addWidget(local_model_group)
        
        # Transcription Options Group
        options_group = QGroupBox("⚙️ Transcription Options")
        options_layout = QGridLayout(options_group)
        
        options_layout.addWidget(QLabel("Language:"), 0, 0)
        self.audio_language_combo = QComboBox()
        self.audio_language_combo.addItems([
            "Auto-detect",
            "English", "Japanese", "Chinese", "Korean", "Spanish", 
            "French", "German", "Russian", "Italian", "Portuguese"
        ])
        options_layout.addWidget(self.audio_language_combo, 0, 1)
        
        self.audio_translate_check = QCheckBox("Translate to target language after transcription")
        options_layout.addWidget(self.audio_translate_check, 1, 0, 1, 2)
        
        scroll_layout.addWidget(options_group)
        
        # Local Model Settings Group (only visible when using faster-whisper)
        self.local_settings_group = QGroupBox("🔧 Local Model Settings")
        local_settings_layout = QGridLayout(self.local_settings_group)
        
        # Compute Type
        local_settings_layout.addWidget(QLabel("Compute Type:"), 0, 0)
        self.compute_type_combo = QComboBox()
        self.compute_type_combo.addItems(["auto", "float32", "float16", "int8"])
        self.compute_type_combo.setCurrentText("auto")
        self.compute_type_combo.setToolTip("Choose compute precision. float32 is most compatible but slower.")
        local_settings_layout.addWidget(self.compute_type_combo, 0, 1)
        
        # Device
        local_settings_layout.addWidget(QLabel("Device:"), 0, 2)
        self.device_combo = QComboBox()
        self.device_combo.addItems(["cpu", "cuda", "auto"])
        self.device_combo.setCurrentText("cpu")
        self.device_combo.setToolTip("Processing device. CUDA requires compatible GPU.")
        local_settings_layout.addWidget(self.device_combo, 0, 3)
        
        # Beam Size
        local_settings_layout.addWidget(QLabel("Beam Size:"), 1, 0)
        self.beam_size_spin = QSpinBox()
        self.beam_size_spin.setRange(1, 10)
        self.beam_size_spin.setValue(5)
        self.beam_size_spin.setToolTip("Higher values improve accuracy but are slower.")
        local_settings_layout.addWidget(self.beam_size_spin, 1, 1)
        
        # Temperature
        local_settings_layout.addWidget(QLabel("Temperature:"), 1, 2)
        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setRange(0.0, 1.0)
        self.temperature_spin.setValue(0.0)
        self.temperature_spin.setSingleStep(0.1)
        self.temperature_spin.setToolTip("Sampling temperature. 0 = deterministic, higher = more random.")
        local_settings_layout.addWidget(self.temperature_spin, 1, 3)
        
        # Additional options
        self.vad_filter_check = QCheckBox("Voice Activity Detection (VAD)")
        self.vad_filter_check.setChecked(True)
        self.vad_filter_check.setToolTip("Filter out non-speech segments.")
        local_settings_layout.addWidget(self.vad_filter_check, 2, 0, 1, 2)
        
        self.word_timestamps_check = QCheckBox("Word-level timestamps")
        self.word_timestamps_check.setChecked(False)
        self.word_timestamps_check.setToolTip("Generate timestamps for individual words.")
        local_settings_layout.addWidget(self.word_timestamps_check, 2, 2, 1, 2)
        
        scroll_layout.addWidget(self.local_settings_group)
        self.local_settings_group.setVisible(False)  # Hidden by default
        
        # Subtitle Output Group
        subtitle_group = QGroupBox("📝 Subtitle Output")
        subtitle_layout = QGridLayout(subtitle_group)
        
        subtitle_layout.addWidget(QLabel("Output Format:"), 0, 0)
        self.subtitle_format_combo = QComboBox()
        self.subtitle_format_combo.addItems(["SRT", "VTT", "ASS"])
        self.subtitle_format_combo.currentTextChanged.connect(self.on_subtitle_format_changed)
        subtitle_layout.addWidget(self.subtitle_format_combo, 0, 1)
        
        # ASS Settings (hidden by default)
        self.ass_settings_group = QGroupBox("🎨 ASS Subtitle Settings")
        ass_settings_layout = QGridLayout(self.ass_settings_group)
        
        ass_settings_layout.addWidget(QLabel("Auto-detect video resolution:"), 0, 0)
        self.auto_resolution_check = QCheckBox()
        self.auto_resolution_check.setChecked(True)
        self.auto_resolution_check.setToolTip("Automatically detect video resolution and adjust font size")
        ass_settings_layout.addWidget(self.auto_resolution_check, 0, 1)
        
        ass_settings_layout.addWidget(QLabel("Manual font size:"), 1, 0)
        self.manual_font_spin = QSpinBox()
        self.manual_font_spin.setRange(8, 72)
        self.manual_font_spin.setValue(28)
        self.manual_font_spin.setEnabled(False)
        self.manual_font_spin.setToolTip("Manual font size (used when auto-detection is disabled)")
        ass_settings_layout.addWidget(self.manual_font_spin, 1, 1)
        
        self.auto_resolution_check.toggled.connect(lambda checked: self.manual_font_spin.setEnabled(not checked))
        
        subtitle_layout.addWidget(self.ass_settings_group, 0, 2, 2, 1)
        self.ass_settings_group.setVisible(False)  # Hidden by default
        
        subtitle_layout.addWidget(QLabel("Output Directory:"), 1, 0)
        self.subtitle_output_edit = QLineEdit()
        self.subtitle_output_edit.setPlaceholderText("Select output directory...")
        subtitle_layout.addWidget(self.subtitle_output_edit, 1, 1)
        
        self.subtitle_browse_btn = QPushButton("Browse")
        self.subtitle_browse_btn.clicked.connect(self.browse_subtitle_output)
        subtitle_layout.addWidget(self.subtitle_browse_btn, 1, 2)
        
        self.save_raw_check = QCheckBox("Save raw transcription text file")
        subtitle_layout.addWidget(self.save_raw_check, 2, 0, 1, 3)
        
        scroll_layout.addWidget(subtitle_group)
        
    def on_subtitle_format_changed(self):
        """Show/hide ASS settings based on selected format"""
        is_ass = self.subtitle_format_combo.currentText() == "ASS"
        self.ass_settings_group.setVisible(is_ass)
        
        # Action Buttons
        action_layout = QHBoxLayout()
        
        self.transcribe_btn = QPushButton("🎯 Start Transcription")
        self.transcribe_btn.clicked.connect(self.start_transcription)
        self.transcribe_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 10px; font-weight: bold; }")
        action_layout.addWidget(self.transcribe_btn)
        
        self.stop_transcription_btn = QPushButton("⏹️ Stop")
        self.stop_transcription_btn.clicked.connect(self.stop_transcription)
        self.stop_transcription_btn.setEnabled(False)
        action_layout.addWidget(self.stop_transcription_btn)
        
        scroll_layout.addLayout(action_layout)
        
        # Progress and Status
        progress_group = QGroupBox("📊 Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.transcription_progress = QProgressBar()
        progress_layout.addWidget(self.transcription_progress)
        
        self.transcription_status = QLabel("Ready to transcribe")
        progress_layout.addWidget(self.transcription_status)
        
        # Time estimation label
        self.transcription_time_label = QLabel("")
        self.transcription_time_label.setStyleSheet("color: #666; font-style: italic;")
        progress_layout.addWidget(self.transcription_time_label)
        
        scroll_layout.addWidget(progress_group)
        
        # Preview Group
        preview_group = QGroupBox("👁️ Transcription Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.transcription_preview = QTextEdit()
        self.transcription_preview.setPlaceholderText("Transcription results will appear here...")
        self.transcription_preview.setMaximumHeight(200)
        preview_layout.addWidget(self.transcription_preview)
        
        scroll_layout.addWidget(preview_group)
        
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # Initialize audio processor
        self.audio_processor = None
        self.update_installed_models()
        
        tab_widget.addTab(audio_widget, "🎵 Audio & Subtitles")
    
    def setup_character_tab(self, tab_widget):
        """Setup character generator tab"""
        char_widget = QWidget()
        layout = QVBoxLayout(char_widget)
        
        # Header
        header_label = QLabel("👥 Character Generator")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setStyleSheet("color: #9C27B0; margin: 10px 0px;")
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel("Create detailed characters for your stories with AI assistance. Choose style and customize attributes.")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; margin-bottom: 15px;")
        layout.addWidget(desc_label)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Character Style Group
        style_group = QGroupBox("🎨 Character Style")
        style_layout = QGridLayout(style_group)
        
        style_layout.addWidget(QLabel("Style:"), 0, 0)
        self.char_style_combo = QComboBox()
        self.char_style_combo.addItems(["Japanese", "Korean", "Chinese", "Fantasy", "Western"])
        self.char_style_combo.currentTextChanged.connect(self.update_style_preview)
        style_layout.addWidget(self.char_style_combo, 0, 1)
        
        # Style preview
        self.style_preview_label = QLabel()
        self.style_preview_label.setWordWrap(True)
        self.style_preview_label.setStyleSheet("background: #f5f5f5; padding: 10px; border-radius: 5px; margin: 10px 0px;")
        style_layout.addWidget(self.style_preview_label, 1, 0, 1, 2)
        
        scroll_layout.addWidget(style_group)
        
        # Character Requirements Group
        req_group = QGroupBox("📋 Character Requirements")
        req_layout = QGridLayout(req_group)
        
        # Basic fields
        req_layout.addWidget(QLabel("Age Range:"), 0, 0)
        self.char_age_edit = QLineEdit()
        self.char_age_edit.setPlaceholderText("e.g., 16-18, young adult, elderly")
        req_layout.addWidget(self.char_age_edit, 0, 1)
        
        req_layout.addWidget(QLabel("Gender:"), 0, 2)
        self.char_gender_combo = QComboBox()
        self.char_gender_combo.addItems(["Any", "Female", "Male", "Non-binary"])
        req_layout.addWidget(self.char_gender_combo, 0, 3)
        
        req_layout.addWidget(QLabel("Occupation:"), 1, 0)
        self.char_occupation_edit = QLineEdit()
        self.char_occupation_edit.setPlaceholderText("e.g., student, warrior, merchant")
        req_layout.addWidget(self.char_occupation_edit, 1, 1)
        
        req_layout.addWidget(QLabel("Personality Traits:"), 1, 2)
        self.char_personality_edit = QLineEdit()
        self.char_personality_edit.setPlaceholderText("e.g., cheerful, mysterious, brave")
        req_layout.addWidget(self.char_personality_edit, 1, 3)
        
        # Custom fields
        custom_label = QLabel("Custom Requirements:")
        custom_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        req_layout.addWidget(custom_label, 2, 0, 1, 4)
        
        self.char_custom_edit = QTextEdit()
        self.char_custom_edit.setPlaceholderText("Describe any specific requirements for this character...")
        self.char_custom_edit.setMaximumHeight(80)
        req_layout.addWidget(self.char_custom_edit, 3, 0, 1, 4)
        
        scroll_layout.addWidget(req_group)
        
        # Generated Character Display
        char_display_group = QGroupBox("🎭 Generated Character")
        char_display_layout = QVBoxLayout(char_display_group)
        
        # Character name and basic info
        char_info_layout = QHBoxLayout()
        
        char_info_layout.addWidget(QLabel("Name:"))
        self.char_name_display = QLineEdit()
        self.char_name_display.setReadOnly(True)
        char_info_layout.addWidget(self.char_name_display)
        
        self.generate_char_btn = QPushButton("🎲 Generate Character")
        self.generate_char_btn.clicked.connect(self.generate_character)
        self.generate_char_btn.setStyleSheet("QPushButton { background-color: #9C27B0; color: white; padding: 10px; font-weight: bold; }")
        char_info_layout.addWidget(self.generate_char_btn)
        
        char_display_layout.addLayout(char_info_layout)
        
        # Character details tabs
        self.char_details_tabs = QTabWidget()
        
        # Personality tab
        personality_widget = QWidget()
        personality_layout = QVBoxLayout(personality_widget)
        self.char_personality_display = QTextEdit()
        self.char_personality_display.setReadOnly(True)
        personality_layout.addWidget(self.char_personality_display)
        self.char_details_tabs.addTab(personality_widget, "Personality")
        
        # Appearance tab
        appearance_widget = QWidget()
        appearance_layout = QVBoxLayout(appearance_widget)
        self.char_appearance_display = QTextEdit()
        self.char_appearance_display.setReadOnly(True)
        appearance_layout.addWidget(self.char_appearance_display)
        self.char_details_tabs.addTab(appearance_widget, "Appearance")
        
        # Background tab
        background_widget = QWidget()
        background_layout = QVBoxLayout(background_widget)
        self.char_background_display = QTextEdit()
        self.char_background_display.setReadOnly(True)
        background_layout.addWidget(self.char_background_display)
        self.char_details_tabs.addTab(background_widget, "Background")
        
        # Custom fields tab
        custom_widget = QWidget()
        custom_layout = QVBoxLayout(custom_widget)
        self.char_custom_display = QTextEdit()
        self.char_custom_display.setReadOnly(True)
        custom_layout.addWidget(self.char_custom_display)
        self.char_details_tabs.addTab(custom_widget, "Other Details")
        
        char_display_layout.addWidget(self.char_details_tabs)
        
        scroll_layout.addWidget(char_display_group)
        
        # Character Management Group
        char_mgmt_group = QGroupBox("💾 Character Management")
        char_mgmt_layout = QVBoxLayout(char_mgmt_group)
        
        # Save/Load buttons
        mgmt_buttons_layout = QHBoxLayout()
        
        self.save_char_btn = QPushButton("💾 Save Character")
        self.save_char_btn.clicked.connect(self.save_character)
        self.save_char_btn.setEnabled(False)
        mgmt_buttons_layout.addWidget(self.save_char_btn)
        
        self.load_char_btn = QPushButton("📂 Load Character")
        self.load_char_btn.clicked.connect(self.load_character)
        mgmt_buttons_layout.addWidget(self.load_char_btn)
        
        self.new_char_btn = QPushButton("🆕 New Character")
        self.new_char_btn.clicked.connect(self.new_character)
        mgmt_buttons_layout.addWidget(self.new_char_btn)
        
        char_mgmt_layout.addLayout(mgmt_buttons_layout)
        
        # Saved characters list
        self.saved_chars_list = QListWidget()
        self.saved_chars_list.setMaximumHeight(120)
        self.saved_chars_list.itemDoubleClicked.connect(self.load_selected_character)
        char_mgmt_layout.addWidget(QLabel("Saved Characters:"))
        char_mgmt_layout.addWidget(self.saved_chars_list)
        
        scroll_layout.addWidget(char_mgmt_group)
        
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # Initialize character system
        self.novel_db = None
        self.novel_assistant = None
        self.current_character = None
        self.update_style_preview()
        self.refresh_saved_characters()
        
        tab_widget.addTab(char_widget, "👥 Character Generator")
    
    def setup_novel_writing_tab(self, tab_widget):
        """Setup novel writing tab"""
        novel_widget = QWidget()
        layout = QVBoxLayout(novel_widget)
        
        # Header
        header_label = QLabel("📝 Novel Writing Assistant")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setStyleSheet("color: #FF5722; margin: 10px 0px;")
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel("Write novels, stories, and scripts with AI assistance. Maintain context and character consistency.")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; margin-bottom: 15px;")
        layout.addWidget(desc_label)
        
        # Create main horizontal layout
        main_layout = QHBoxLayout()
        
        # Left side - Project and context
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_widget.setMaximumWidth(350)
        
        # Project Management
        project_group = QGroupBox("📚 Project")
        project_layout = QVBoxLayout(project_group)
        
        # Project selection
        project_select_layout = QHBoxLayout()
        self.novel_project_combo = QComboBox()
        self.novel_project_combo.currentTextChanged.connect(self.load_novel_project)
        project_select_layout.addWidget(self.novel_project_combo)
        
        self.new_project_btn = QPushButton("➕")
        self.new_project_btn.setMaximumWidth(30)
        self.new_project_btn.clicked.connect(self.create_new_project)
        project_select_layout.addWidget(self.new_project_btn)
        
        project_layout.addLayout(project_select_layout)
        
        # Project info
        self.project_info_label = QLabel("No project selected")
        self.project_info_label.setWordWrap(True)
        self.project_info_label.setStyleSheet("background: #f5f5f5; padding: 8px; border-radius: 4px;")
        project_layout.addWidget(self.project_info_label)
        
        left_layout.addWidget(project_group)
        
        # Context Management
        context_group = QGroupBox("📝 Writing Context")
        context_layout = QVBoxLayout(context_group)
        
        context_layout.addWidget(QLabel("Current Context:"))
        self.novel_context_edit = QTextEdit()
        self.novel_context_edit.setPlaceholderText("Describe the current situation, location, mood...")
        self.novel_context_edit.setMaximumHeight(100)
        context_layout.addWidget(self.novel_context_edit)
        
        context_layout.addWidget(QLabel("Key Points to Remember:"))
        self.key_points_edit = QTextEdit()
        self.key_points_edit.setPlaceholderText("• Important plot points\n• Character developments\n• Secrets revealed")
        self.key_points_edit.setMaximumHeight(80)
        context_layout.addWidget(self.key_points_edit)
        
        left_layout.addWidget(context_group)
        
        # Active Characters
        chars_group = QGroupBox("👥 Active Characters")
        chars_layout = QVBoxLayout(chars_group)
        
        self.active_chars_list = QListWidget()
        self.active_chars_list.setMaximumHeight(100)
        self.active_chars_list.setSelectionMode(QListWidget.MultiSelection)
        chars_layout.addWidget(self.active_chars_list)
        
        chars_buttons_layout = QHBoxLayout()
        self.add_char_btn = QPushButton("Add Character")
        self.add_char_btn.clicked.connect(self.add_active_character)
        chars_buttons_layout.addWidget(self.add_char_btn)
        
        self.remove_char_btn = QPushButton("Remove")
        self.remove_char_btn.clicked.connect(self.remove_active_character)
        chars_buttons_layout.addWidget(self.remove_char_btn)
        
        chars_layout.addLayout(chars_buttons_layout)
        
        left_layout.addWidget(chars_group)
        
        # Writing Tools
        tools_group = QGroupBox("🛠️ Writing Tools")
        tools_layout = QVBoxLayout(tools_group)
        
        tools_layout.addWidget(QLabel("Writing Mode:"))
        self.writing_mode_combo = QComboBox()
        self.writing_mode_combo.addItems([
            "Continue Story",
            "Write Scene", 
            "Write Dialogue",
            "Describe Character",
            "Build World",
            "Free Writing"
        ])
        tools_layout.addWidget(self.writing_mode_combo)
        
        self.writing_goal_edit = QLineEdit()
        self.writing_goal_edit.setPlaceholderText("What do you want to accomplish?")
        tools_layout.addWidget(QLabel("Goal:"))
        tools_layout.addWidget(self.writing_goal_edit)
        
        self.generate_text_btn = QPushButton("✨ Generate with AI")
        self.generate_text_btn.clicked.connect(self.generate_writing)
        self.generate_text_btn.setStyleSheet("QPushButton { background-color: #FF5722; color: white; padding: 8px; font-weight: bold; }")
        tools_layout.addWidget(self.generate_text_btn)
        
        left_layout.addWidget(tools_group)
        
        left_layout.addStretch()
        main_layout.addWidget(left_widget)
        
        # Right side - Writing area
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Writing area header
        writing_header_layout = QHBoxLayout()
        
        self.word_count_label = QLabel("Words: 0")
        self.word_count_label.setStyleSheet("font-weight: bold; color: #FF5722;")
        writing_header_layout.addWidget(self.word_count_label)
        
        writing_header_layout.addStretch()
        
        self.save_writing_btn = QPushButton("💾 Save")
        self.save_writing_btn.clicked.connect(self.save_writing)
        writing_header_layout.addWidget(self.save_writing_btn)
        
        self.export_writing_btn = QPushButton("📤 Export")
        self.export_writing_btn.clicked.connect(self.export_writing)
        writing_header_layout.addWidget(self.export_writing_btn)
        
        right_layout.addLayout(writing_header_layout)
        
        # Main writing area
        self.novel_text_edit = QTextEdit()
        self.novel_text_edit.setPlaceholderText("Start writing your story here...")
        self.novel_text_edit.textChanged.connect(self.update_word_count)
        self.novel_text_edit.setStyleSheet("""
            QTextEdit {
                font-family: 'Times New Roman', serif;
                font-size: 12pt;
                line-height: 1.6;
                padding: 20px;
                background-color: #ffffff;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        """)
        right_layout.addWidget(self.novel_text_edit)
        
        main_layout.addWidget(right_widget, 2)  # Give more space to writing area
        
        layout.addLayout(main_layout)
        
        # Initialize novel system
        self.current_project = None
        self.current_session = None
        self.refresh_projects()
        
        tab_widget.addTab(novel_widget, "📝 Novel Writing")
        
        # Setup Local Models tab
        self.setup_local_models_tab(tab_widget)
    
    def setup_local_models_tab(self, tab_widget):
        """Setup local models management tab"""
        local_widget = QWidget()
        layout = QVBoxLayout(local_widget)
        
        # Header
        header_label = QLabel("🖥️ Local Models (Llama.cpp)")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setStyleSheet("color: #4CAF50; margin: 10px 0px;")
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel("Manage local LLM models for offline translation. Models run on your device without internet connection.")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; margin-bottom: 15px;")
        layout.addWidget(desc_label)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Model Management Group
        model_group = QGroupBox("📦 Model Management")
        model_layout = QVBoxLayout(model_group)
        
        # Available Models List
        available_label = QLabel("Available Models:")
        available_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        model_layout.addWidget(available_label)
        
        self.available_models_list = QListWidget()
        self.available_models_list.setMaximumHeight(200)
        model_layout.addWidget(self.available_models_list)
        
        # Model actions
        model_actions_layout = QHBoxLayout()
        
        self.download_model_btn = QPushButton("📥 Download Selected Model")
        self.download_model_btn.clicked.connect(self.download_selected_model)
        self.download_model_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 8px; font-weight: bold; }")
        model_actions_layout.addWidget(self.download_model_btn)
        
        self.refresh_models_btn = QPushButton("🔄 Refresh List")
        self.refresh_models_btn.clicked.connect(self.refresh_local_models)
        model_actions_layout.addWidget(self.refresh_models_btn)
        
        model_layout.addLayout(model_actions_layout)
        
        # Installed Models
        installed_label = QLabel("Installed Models:")
        installed_label.setStyleSheet("font-weight: bold; margin-top: 15px;")
        model_layout.addWidget(installed_label)
        
        self.installed_models_list = QListWidget()
        self.installed_models_list.setMaximumHeight(150)
        model_layout.addWidget(self.installed_models_list)
        
        # Model info display
        self.model_info_label = QLabel("Select a model to see details")
        self.model_info_label.setStyleSheet("background: #f5f5f5; padding: 10px; border-radius: 5px; margin: 10px 0px;")
        self.model_info_label.setWordWrap(True)
        model_layout.addWidget(self.model_info_label)
        
        scroll_layout.addWidget(model_group)
        
        # Model Configuration Group
        config_group = QGroupBox("⚙️ Model Configuration")
        config_layout = QGridLayout(config_group)
        
        # Context Length
        config_layout.addWidget(QLabel("Context Length:"), 0, 0)
        self.local_ctx_spin = QSpinBox()
        self.local_ctx_spin.setRange(512, 32768)
        self.local_ctx_spin.setValue(4096)
        self.local_ctx_spin.setSuffix(" tokens")
        config_layout.addWidget(self.local_ctx_spin, 0, 1)
        
        # GPU Layers
        config_layout.addWidget(QLabel("GPU Layers:"), 0, 2)
        self.gpu_layers_spin = QSpinBox()
        self.gpu_layers_spin.setRange(0, 100)
        self.gpu_layers_spin.setValue(0)
        self.gpu_layers_spin.setToolTip("Number of layers to run on GPU (0 = CPU only)")
        config_layout.addWidget(self.gpu_layers_spin, 0, 3)
        
        # Threads
        config_layout.addWidget(QLabel("CPU Threads:"), 1, 0)
        self.threads_spin = QSpinBox()
        self.threads_spin.setRange(-1, 64)
        self.threads_spin.setValue(-1)
        self.threads_spin.setSpecialValueText("Auto")
        self.threads_spin.setToolTip("-1 for automatic detection")
        config_layout.addWidget(self.threads_spin, 1, 1)
        
        # Temperature
        config_layout.addWidget(QLabel("Temperature:"), 1, 2)
        self.local_temp_spin = QDoubleSpinBox()
        self.local_temp_spin.setRange(0.0, 2.0)
        self.local_temp_spin.setValue(0.7)
        self.local_temp_spin.setSingleStep(0.1)
        self.local_temp_spin.setToolTip("Randomness in generation (0.0 = deterministic)")
        config_layout.addWidget(self.local_temp_spin, 1, 3)
        
        scroll_layout.addWidget(config_group)
        
        # Model Testing Group
        test_group = QGroupBox("🧪 Model Testing")
        test_layout = QVBoxLayout(test_group)
        
        # Model selection for testing
        test_selection_layout = QHBoxLayout()
        test_selection_layout.addWidget(QLabel("Test Model:"))
        self.test_model_combo = QComboBox()
        test_selection_layout.addWidget(self.test_model_combo)
        
        self.load_model_btn = QPushButton("🔄 Load Model")
        self.load_model_btn.clicked.connect(self.load_selected_model)
        test_selection_layout.addWidget(self.load_model_btn)
        
        self.unload_model_btn = QPushButton("⏹️ Unload Model")
        self.unload_model_btn.clicked.connect(self.unload_current_model)
        self.unload_model_btn.setEnabled(False)
        test_selection_layout.addWidget(self.unload_model_btn)
        
        test_layout.addLayout(test_selection_layout)
        
        # Test input
        test_layout.addWidget(QLabel("Test Translation:"))
        self.test_input = QTextEdit()
        self.test_input.setPlaceholderText("Enter text to translate...")
        self.test_input.setMaximumHeight(80)
        test_layout.addWidget(self.test_input)
        
        # Test controls
        test_controls_layout = QHBoxLayout()
        
        test_controls_layout.addWidget(QLabel("Target Language:"))
        self.test_target_combo = QComboBox()
        self.test_target_combo.addItems(["English", "Japanese", "Chinese", "Korean", "Spanish", "French", "German", "Russian"])
        test_controls_layout.addWidget(self.test_target_combo)
        
        self.test_translate_btn = QPushButton("🔄 Test Translation")
        self.test_translate_btn.clicked.connect(self.test_translation)
        self.test_translate_btn.setEnabled(False)
        test_controls_layout.addWidget(self.test_translate_btn)
        
        test_layout.addLayout(test_controls_layout)
        
        # Test output
        self.test_output = QTextEdit()
        self.test_output.setPlaceholderText("Translation result will appear here...")
        self.test_output.setMaximumHeight(80)
        self.test_output.setReadOnly(True)
        test_layout.addWidget(self.test_output)
        
        scroll_layout.addWidget(test_group)
        
        # Status and Progress
        status_group = QGroupBox("📊 Status")
        status_layout = QVBoxLayout(status_group)
        
        self.local_status_label = QLabel("Ready")
        self.local_status_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
        status_layout.addWidget(self.local_status_label)
        
        self.local_progress_bar = QProgressBar()
        self.local_progress_bar.setVisible(False)
        status_layout.addWidget(self.local_progress_bar)
        
        scroll_layout.addWidget(status_group)
        
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # Initialize local models
        self.llamacpp_client = None
        self.refresh_local_models()
        
        tab_widget.addTab(local_widget, "🖥️ Local Models")
    
    def setup_cloud_tab(self, tab_widget):
        """Setup cloud AI services tab"""
        cloud_widget = QWidget()
        layout = QVBoxLayout(cloud_widget)
        
        # Header
        header_label = QLabel("☁️ Cloud AI Services")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setStyleSheet("color: #2196F3; margin: 10px 0px;")
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel("Configure Hugging Face, vLLM, Google Colab, and Kaggle integrations for free/low-cost AI translation.")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; margin-bottom: 15px;")
        layout.addWidget(desc_label)
        
        # Hugging Face section
        hf_group = QGroupBox("🤗 Hugging Face")
        hf_layout = QVBoxLayout(hf_group)
        
        # HF API token
        hf_token_layout = QHBoxLayout()
        hf_token_layout.addWidget(QLabel("API Token:"))
        self.hf_token_edit = QLineEdit()
        self.hf_token_edit.setPlaceholderText("Optional - for unlimited access")
        self.hf_token_edit.setEchoMode(QLineEdit.Password)
        hf_token_layout.addWidget(self.hf_token_edit)
        hf_layout.addLayout(hf_token_layout)
        
        # HF model selection
        hf_model_layout = QVBoxLayout()
        hf_model_layout.addWidget(QLabel("Model (enter any HuggingFace model name):"))
        
        # Editable combobox for model selection
        self.hf_model_combo = QComboBox()
        self.hf_model_combo.setEditable(True)
        self.hf_model_combo.setInsertPolicy(QComboBox.InsertAtTop)
        self.hf_model_combo.addItems([
            "meta-llama/Meta-Llama-3.1-8B-Instruct",
            "meta-llama/Meta-Llama-3.1-70B-Instruct",
            "meta-llama/Meta-Llama-3-8B-Instruct",
            "meta-llama/Meta-Llama-3-70B-Instruct", 
            "Qwen/Qwen2.5-7B-Instruct",
            "Qwen/Qwen2.5-14B-Instruct",
            "Qwen/Qwen2.5-32B-Instruct",
            "Qwen/Qwen2-7B-Instruct",
            "microsoft/DialoGPT-large",
            "HuggingFaceH4/zephyr-7b-beta",
            "mistralai/Mistral-7B-Instruct-v0.2",
            "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "google/flan-t5-large",
            "bigscience/bloom-7b1",
            "stabilityai/stablelm-tuned-alpha-7b",
            "anthropic/claude-instant-1",
            "EleutherAI/gpt-j-6b",
            "EleutherAI/gpt-neox-20b"
        ])
        self.hf_model_combo.setCurrentText("Qwen/Qwen2.5-7B-Instruct")
        hf_model_layout.addWidget(self.hf_model_combo)
        
        # Add help text
        help_label = QLabel("💡 You can enter any model from HuggingFace Hub (e.g., microsoft/DialoGPT-medium, facebook/blenderbot-400M-distill)")
        help_label.setStyleSheet("color: #666; font-size: 11px; font-style: italic;")
        help_label.setWordWrap(True)
        hf_model_layout.addWidget(help_label)
        
        hf_layout.addLayout(hf_model_layout)
        
        # HF test button
        hf_buttons_layout = QHBoxLayout()
        
        self.hf_test_btn = QPushButton("🧪 Test Connection")
        self.hf_test_btn.clicked.connect(self.test_huggingface_connection)
        hf_buttons_layout.addWidget(self.hf_test_btn)
        
        self.hf_browse_btn = QPushButton("🔍 Browse Popular Models")
        self.hf_browse_btn.clicked.connect(self.show_popular_hf_models)
        hf_buttons_layout.addWidget(self.hf_browse_btn)
        
        hf_layout.addLayout(hf_buttons_layout)
        
        layout.addWidget(hf_group)
        
        # vLLM section
        vllm_group = QGroupBox("⚡ vLLM Server")
        vllm_layout = QVBoxLayout(vllm_group)
        
        # vLLM endpoint
        vllm_endpoint_layout = QHBoxLayout()
        vllm_endpoint_layout.addWidget(QLabel("Endpoint URL:"))
        self.vllm_endpoint_edit = QLineEdit()
        self.vllm_endpoint_edit.setPlaceholderText("http://your-server:8000")
        vllm_endpoint_layout.addWidget(self.vllm_endpoint_edit)
        vllm_layout.addLayout(vllm_endpoint_layout)
        
        # vLLM model name
        vllm_model_layout = QHBoxLayout()
        vllm_model_layout.addWidget(QLabel("Model Name:"))
        self.vllm_model_edit = QLineEdit()
        self.vllm_model_edit.setPlaceholderText("model-name")
        vllm_model_layout.addWidget(self.vllm_model_edit)
        vllm_layout.addLayout(vllm_model_layout)
        
        # vLLM test button
        self.vllm_test_btn = QPushButton("🧪 Test Connection")
        self.vllm_test_btn.clicked.connect(self.test_vllm_connection)
        vllm_layout.addWidget(self.vllm_test_btn)
        
        # vLLM setup guide button
        self.vllm_setup_btn = QPushButton("📋 Show Setup Code")
        self.vllm_setup_btn.clicked.connect(self.show_vllm_setup)
        vllm_layout.addWidget(self.vllm_setup_btn)
        
        layout.addWidget(vllm_group)
        
        # Google Colab section
        colab_group = QGroupBox("🔬 Google Colab")
        colab_layout = QVBoxLayout(colab_group)
        
        # Colab ngrok URL
        colab_url_layout = QHBoxLayout()
        colab_url_layout.addWidget(QLabel("Ngrok URL:"))
        self.colab_url_edit = QLineEdit()
        self.colab_url_edit.setPlaceholderText("https://xxxx-xx-xx-xx-xx.ngrok.io")
        colab_url_layout.addWidget(self.colab_url_edit)
        colab_layout.addLayout(colab_url_layout)
        
        # Colab test button
        self.colab_test_btn = QPushButton("🧪 Test Connection")
        self.colab_test_btn.clicked.connect(self.test_colab_connection)
        colab_layout.addWidget(self.colab_test_btn)
        
        # Colab setup guide button
        self.colab_setup_btn = QPushButton("📋 Show Setup Code")
        self.colab_setup_btn.clicked.connect(self.show_colab_setup)
        colab_layout.addWidget(self.colab_setup_btn)
        
        layout.addWidget(colab_group)
        
        # Kaggle section
        kaggle_group = QGroupBox("📊 Kaggle")
        kaggle_layout = QVBoxLayout(kaggle_group)
        
        # Kaggle endpoint
        kaggle_endpoint_layout = QHBoxLayout()
        kaggle_endpoint_layout.addWidget(QLabel("Endpoint URL:"))
        self.kaggle_endpoint_edit = QLineEdit()
        self.kaggle_endpoint_edit.setPlaceholderText("https://kaggle-notebook-url")
        kaggle_endpoint_layout.addWidget(self.kaggle_endpoint_edit)
        kaggle_layout.addLayout(kaggle_endpoint_layout)
        
        # Kaggle API key
        kaggle_key_layout = QHBoxLayout()
        kaggle_key_layout.addWidget(QLabel("API Key:"))
        self.kaggle_key_edit = QLineEdit()
        self.kaggle_key_edit.setPlaceholderText("Optional")
        self.kaggle_key_edit.setEchoMode(QLineEdit.Password)
        kaggle_key_layout.addWidget(self.kaggle_key_edit)
        kaggle_layout.addLayout(kaggle_key_layout)
        
        # Kaggle test button
        self.kaggle_test_btn = QPushButton("🧪 Test Connection")
        self.kaggle_test_btn.clicked.connect(self.test_kaggle_connection)
        kaggle_layout.addWidget(self.kaggle_test_btn)
        
        # Kaggle setup guide button
        self.kaggle_setup_btn = QPushButton("📋 Show Setup Code")
        self.kaggle_setup_btn.clicked.connect(self.show_kaggle_setup)
        kaggle_layout.addWidget(self.kaggle_setup_btn)
        
        layout.addWidget(kaggle_group)
        
        # Status section
        status_group = QGroupBox("📊 Status")
        status_layout = QVBoxLayout(status_group)
        
        self.cloud_status_label = QLabel("No cloud services configured")
        self.cloud_status_label.setStyleSheet("color: #666; font-style: italic;")
        status_layout.addWidget(self.cloud_status_label)
        
        layout.addWidget(status_group)
        
        layout.addStretch()
        tab_widget.addTab(cloud_widget, "☁️ Cloud AI")
    
    def setup_providers_tab(self, tab_widget):
        """Setup providers management tab"""
        providers_widget = QWidget()
        layout = QVBoxLayout(providers_widget)
        
        # Header
        header_label = QLabel("🔄 Provider Management")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setStyleSheet("color: #9C27B0; margin: 10px 0px;")
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel("Manage multiple AI providers with priority and automatic fallback. Higher priority providers will be tried first.")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; margin-bottom: 15px;")
        layout.addWidget(desc_label)
        
        # Controls section
        controls_group = QGroupBox("🎛️ Controls")
        controls_layout = QHBoxLayout(controls_group)
        
        self.add_provider_btn = QPushButton("➕ Add Provider")
        self.add_provider_btn.clicked.connect(self.add_provider_dialog)
        controls_layout.addWidget(self.add_provider_btn)
        
        self.test_all_providers_btn = QPushButton("🧪 Test All")
        self.test_all_providers_btn.clicked.connect(self.test_all_providers)
        controls_layout.addWidget(self.test_all_providers_btn)
        
        self.reset_failures_btn = QPushButton("🔄 Reset Failures")
        self.reset_failures_btn.clicked.connect(self.reset_all_provider_failures)
        controls_layout.addWidget(self.reset_failures_btn)
        
        self.refresh_status_btn = QPushButton("🔄 Refresh Status")
        self.refresh_status_btn.clicked.connect(self.refresh_provider_status)
        controls_layout.addWidget(self.refresh_status_btn)
        
        controls_layout.addStretch()
        layout.addWidget(controls_group)
        
        # Providers list section
        providers_group = QGroupBox("📋 Providers (Priority Order)")
        providers_layout = QVBoxLayout(providers_group)
        
        # Create scroll area for providers
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.providers_list_widget = QWidget()
        self.providers_list_layout = QVBoxLayout(self.providers_list_widget)
        
        scroll_area.setWidget(self.providers_list_widget)
        providers_layout.addWidget(scroll_area)
        
        layout.addWidget(providers_group)
        
        # Status section
        status_group = QGroupBox("📊 System Status")
        status_layout = QVBoxLayout(status_group)
        
        self.provider_status_label = QLabel("Loading provider status...")
        self.provider_status_label.setStyleSheet("color: #666; font-style: italic;")
        status_layout.addWidget(self.provider_status_label)
        
        layout.addWidget(status_group)
        
        # Initialize provider manager
        try:
            from core.provider_manager import ProviderManager
            self.provider_manager = ProviderManager()
            self.refresh_provider_status()
        except Exception as e:
            self.provider_status_label.setText(f"Error loading provider manager: {e}")
        
        tab_widget.addTab(providers_widget, "🔄 Providers")

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
        
        # Light Novel specific settings
        lightnovel_group = QGroupBox("📖 Light Novel Settings")
        lightnovel_layout = QGridLayout(lightnovel_group)
        
        # Output format selection
        lightnovel_layout.addWidget(QLabel("Output Format:"), 0, 0)
        self.lightnovel_output_format = QComboBox()
        self.lightnovel_output_format.addItems(["txt", "docx", "pdf", "epub"])
        self.lightnovel_output_format.setCurrentText("txt")
        lightnovel_layout.addWidget(self.lightnovel_output_format, 0, 1)
        
        # Light Novel specific prompt button
        self.ln_prompt_btn = QPushButton("📝 Use Light Novel Prompt")
        self.ln_prompt_btn.clicked.connect(self.use_lightnovel_prompt)
        lightnovel_layout.addWidget(self.ln_prompt_btn, 1, 0)
        
        # Light Novel vocabulary button
        self.ln_vocab_btn = QPushButton("📚 Load Light Novel Vocabulary")
        self.ln_vocab_btn.clicked.connect(self.use_lightnovel_vocabulary)
        lightnovel_layout.addWidget(self.ln_vocab_btn, 1, 1)
        
        layout.addWidget(lightnovel_group)
        
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
        
    def setup_documentation_tab(self, tab_widget):
        """Setup documentation tab"""
        doc_widget = QWidget()
        layout = QVBoxLayout(doc_widget)
        
        # Create scroll area for documentation
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Documentation content
        doc_content = self.get_documentation_content()
        
        # Create text browser for rich text display
        from PyQt5.QtWidgets import QTextBrowser
        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)
        text_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 10px;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 11pt;
            }
        """)
        text_browser.setHtml(doc_content)
        
        scroll_layout.addWidget(text_browser)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        # Button to open README file
        readme_btn = QPushButton("📄 Open README.md")
        readme_btn.clicked.connect(self.open_readme_file)
        button_layout.addWidget(readme_btn)
        
        # Button to open GitHub repository
        github_btn = QPushButton("🌐 GitHub Repository")
        github_btn.clicked.connect(self.open_github_repo)
        button_layout.addWidget(github_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        tab_widget.addTab(doc_widget, "📖 Documentation")
        
    def setup_about_tab(self, tab_widget):
        """Setup about tab"""
        about_widget = QWidget()
        layout = QVBoxLayout(about_widget)
        
        # Create scrollable area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # About content
        about_browser = QTextBrowser()
        about_browser.setOpenExternalLinks(True)
        about_browser.setHtml(self.get_about_content())
        about_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                font-family: 'Segoe UI', Arial, sans-serif;
                line-height: 1.5;
            }
            .app-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                margin-bottom: 20px;
            }
            .section {
                background-color: white;
                border: 1px solid #e1e5e9;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 15px;
            }
            .section h3 {
                color: #2c3e50;
                margin-top: 0;
                margin-bottom: 10px;
                font-size: 18px;
                font-weight: 600;
            }
            .section p, .section li {
                color: #495057;
                margin-bottom: 8px;
            }
            .version {
                background-color: #e7f3ff;
                border-left: 4px solid #0066cc;
                padding: 10px;
                margin: 10px 0;
            }
            .warning {
                background-color: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 10px;
                margin: 10px 0;
            }
            .support {
                background-color: #d1ecf1;
                border-left: 4px solid #17a2b8;
                padding: 10px;
                margin: 10px 0;
            }
            .thanks {
                background-color: #d4edda;
                border-left: 4px solid #28a745;
                padding: 10px;
                margin: 10px 0;
            }
            a {
                color: #0066cc;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        """)
        
        content_layout.addWidget(about_browser)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        github_btn = QPushButton("🐛 Report Issues")
        github_btn.clicked.connect(lambda: self.open_url("https://github.com/Baconana-chan/BaconanaMTLTool/issues"))
        github_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        
        kofi_btn = QPushButton("☕ Support Development")
        kofi_btn.clicked.connect(lambda: self.open_url("https://ko-fi.com/baconana_chan"))
        kofi_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff5722;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e64a19;
            }
        """)
        
        original_btn = QPushButton("🌟 Original Tool")
        original_btn.clicked.connect(lambda: self.open_url("https://gitgud.io/DazedAnon/DazedMTLTool"))
        original_btn.setStyleSheet("""
            QPushButton {
                background-color: #6f42c1;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a359a;
            }
        """)
        
        button_layout.addWidget(github_btn)
        button_layout.addWidget(kofi_btn)
        button_layout.addWidget(original_btn)
        button_layout.addStretch()
        
        content_layout.addLayout(button_layout)
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        tab_widget.addTab(about_widget, "ℹ️ About")
        
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
        from core.lightnovel_processor import LightNovelProcessor
        
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
        lightnovel_processor = LightNovelProcessor()
        
        # Check for light novel files first (they could be mistaken for other formats)
        if self.detect_lightnovel_project(directory, lightnovel_processor):
            self.project_type_label.setText("✅ Light Novel project detected")
            self.project_type_label.setStyleSheet("color: #8E24AA; font-weight: bold;")
        elif renpy_processor.detect_renpy_project(directory):
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
    
    def detect_lightnovel_project(self, directory, lightnovel_processor):
        """Detect if directory contains light novel files"""
        import glob
        
        light_novel_extensions = ['.txt', '.docx', '.pdf', '.epub']
        
        for ext in light_novel_extensions:
            pattern = os.path.join(directory, f"*{ext}")
            files = glob.glob(pattern)
            if files:
                # Check if any file can be processed
                for file_path in files:
                    if lightnovel_processor.can_process(file_path):
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
        
        # Load cloud configuration as well
        self.load_cloud_config()
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
        
        # Load cloud configuration
        self.load_cloud_config()
    
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
            'ollama_model': self.ollama_model_edit.text(),
            # Light Novel specific
            'lightnovel_output_format': self.lightnovel_output_format.currentText(),
            'custom_prompt': self.prompt_edit.toPlainText(),
            'target_language': self.language_combo.currentText()
        }
    
    def get_provider_configs(self):
        """Get provider configurations from the providers tab"""
        provider_configs = {}
        
        # Get configurations from provider widgets
        for provider_widget in self.provider_widgets.values():
            if provider_widget.enabled_check.isChecked():
                provider_name = provider_widget.provider_name
                config = {
                    'provider': provider_widget.provider_type.value,
                    'enabled': True,
                    'priority': provider_widget.priority_spin.value(),
                    'api_key': provider_widget.api_key_edit.text(),
                    'api_url': provider_widget.api_url_edit.text(),
                    'model': provider_widget.model_edit.text(),
                    'timeout': 30,
                    'max_retries': 3
                }
                
                # Add provider-specific configs
                if hasattr(provider_widget, 'org_edit'):
                    config['organization'] = provider_widget.org_edit.text()
                
                provider_configs[provider_name] = config
        
        return provider_configs
    
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
    
    def use_lightnovel_prompt(self):
        """Load light novel specific prompt"""
        try:
            # Check if eroge mode is enabled
            is_eroge = self.ln_eroge_mode.isChecked() if hasattr(self, 'ln_eroge_mode') else False
            
            if is_eroge:
                # Load eroge prompt
                prompt_file = "lightnovel_eroge_prompt.txt"
                try:
                    with open(prompt_file, 'r', encoding='utf-8') as f:
                        prompt_text = f.read()
                    self.prompt_edit.setPlainText(prompt_text)
                    self.log_message("Eroge light novel prompt loaded")
                    QMessageBox.information(self, "Success", "Eroge light novel specific prompt loaded!")
                except FileNotFoundError:
                    # Fallback to inline prompt
                    from core.lightnovel_processor import LightNovelProcessor
                    processor = LightNovelProcessor()
                    prompt_text = processor.create_specialized_prompt("", True)
                    self.prompt_edit.setPlainText(prompt_text)
                    self.log_message("Eroge light novel prompt loaded (fallback)")
                    QMessageBox.information(self, "Success", "Eroge light novel prompt loaded!")
            else:
                # Load standard light novel prompt
                prompt_file = "lightnovel_prompt.txt"
                try:
                    with open(prompt_file, 'r', encoding='utf-8') as f:
                        prompt_text = f.read()
                    self.prompt_edit.setPlainText(prompt_text)
                    self.log_message("Light novel prompt loaded")
                    QMessageBox.information(self, "Success", "Light novel specific prompt loaded!")
                except FileNotFoundError:
                    # Fallback to inline prompt
                    from core.lightnovel_processor import LightNovelProcessor
                    processor = LightNovelProcessor()
                    prompt_text = processor.create_specialized_prompt("", False)
                    self.prompt_edit.setPlainText(prompt_text)
                    self.log_message("Light novel prompt loaded (fallback)")
                    QMessageBox.information(self, "Success", "Light novel prompt loaded!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load prompt: {str(e)}")
    
    def use_lightnovel_vocabulary(self):
        """Load light novel specific vocabulary"""
        try:
            # Check if eroge mode is enabled
            is_eroge = self.ln_eroge_mode.isChecked() if hasattr(self, 'ln_eroge_mode') else False
            
            vocab_text = ""
            
            # Load standard light novel vocabulary
            vocab_file = "lightnovel_vocab.txt"
            try:
                with open(vocab_file, 'r', encoding='utf-8') as f:
                    vocab_text = f.read()
            except FileNotFoundError:
                # Fallback to inline vocab
                from core.lightnovel_processor import LightNovelProcessor
                processor = LightNovelProcessor()
                vocab_text = processor.create_specialized_vocabulary(False)
            
            # Add eroge vocabulary if enabled
            if is_eroge:
                eroge_vocab_file = "lightnovel_eroge_vocab.txt"
                try:
                    with open(eroge_vocab_file, 'r', encoding='utf-8') as f:
                        eroge_vocab = f.read()
                    vocab_text += "\n\n" + eroge_vocab
                except FileNotFoundError:
                    # Fallback to inline eroge vocab
                    from core.lightnovel_processor import LightNovelProcessor
                    processor = LightNovelProcessor()
                    eroge_vocab = processor.create_specialized_vocabulary(True)
                    vocab_text += "\n\n" + eroge_vocab
            
            self.vocab_edit.setPlainText(vocab_text)
            
            mode_text = "eroge light novel" if is_eroge else "light novel"
            self.log_message(f"{mode_text.title()} vocabulary loaded")
            QMessageBox.information(self, "Success", f"{mode_text.title()} specific vocabulary loaded!")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load vocabulary: {str(e)}")
    
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
        
        # Setup providers from provider manager
        provider_configs = self.get_provider_configs()
        if provider_configs:
            self.translation_manager.setup_providers(provider_configs)
            self.log_message(f"Configured {len(provider_configs)} providers with automatic fallback")
        
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
    
    # Light Novel Methods
    def browse_lightnovel_file(self):
        """Browse for light novel file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Light Novel File",
            "",
            "Light Novel Files (*.txt *.docx *.pdf *.epub);;Text Files (*.txt);;Word Documents (*.docx);;PDF Files (*.pdf);;EPUB Files (*.epub);;All Files (*)"
        )
        if file_path:
            self.ln_input_file_edit.setText(file_path)
            self.analyze_lightnovel_file(file_path)
    
    def browse_lightnovel_output(self):
        """Browse for light novel output directory"""
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.ln_output_dir_edit.setText(directory)
    
    def analyze_lightnovel_file(self, file_path):
        """Analyze selected light novel file"""
        try:
            from core.lightnovel_processor import LightNovelProcessor
            from core.models import ModelDatabase
            
            processor = LightNovelProcessor()
            model_db = ModelDatabase()
            
            if not processor.can_process(file_path):
                self.ln_file_info_label.setText("⚠️ Unsupported file format or missing dependencies")
                self.ln_file_info_label.setStyleSheet("color: #f44336; font-weight: bold;")
                return
            
            # Extract basic info
            extracted_data = processor.extract_text(file_path)
            
            if "error" in extracted_data:
                self.ln_file_info_label.setText(f"❌ Error: {extracted_data['error']}")
                self.ln_file_info_label.setStyleSheet("color: #f44336; font-weight: bold;")
                return
            
            # Detect eroge content
            translatable_content = processor.get_translatable_content(extracted_data)
            sample_text = " ".join(translatable_content[:5])  # Sample first 5 sections
            is_eroge = processor.detect_eroge_content(sample_text)
            
            # Auto-update eroge mode if detection is enabled
            if self.ln_auto_detect_eroge.isChecked() and is_eroge:
                self.ln_eroge_mode.setChecked(True)
                self.ln_status_label.setText("🔍 Mature content detected - Eroge mode enabled")
                self.ln_status_label.setStyleSheet("color: #FF6B6B; font-weight: bold;")
            
            # Show model warnings based on current selection and eroge mode
            self.update_model_recommendations()
            
            # Get file info
            import os
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)
            
            metadata = extracted_data.get('metadata', {})
            chapters = extracted_data.get('chapters', [])
            
            info_text = f"✅ File analyzed successfully\n"
            info_text += f"📁 Size: {file_size_mb:.2f} MB\n"
            info_text += f"📄 Format: {metadata.get('format', 'unknown').upper()}\n"
            info_text += f"📚 Chapters: {len(chapters)}\n"
            info_text += f"🌏 Translatable sections: {len(translatable_content)}\n"
            
            if is_eroge:
                info_text += f"🔞 Mature content detected\n"
            
            if metadata.get('title'):
                info_text += f"📖 Title: {metadata['title']}\n"
            if metadata.get('author'):
                info_text += f"✍️ Author: {metadata['author']}\n"
            
            self.ln_file_info_label.setText(info_text)
            self.ln_file_info_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            
            # Auto-set output directory if not set
            if not self.ln_output_dir_edit.text():
                input_dir = os.path.dirname(file_path)
                output_dir = os.path.join(input_dir, "translated")
                self.ln_output_dir_edit.setText(output_dir)
            
        except Exception as e:
            self.ln_file_info_label.setText(f"❌ Analysis error: {str(e)}")
            self.ln_file_info_label.setStyleSheet("color: #f44336; font-weight: bold;")
    
    def update_model_recommendations(self):
        """Update model recommendations based on eroge mode and current model selection"""
        try:
            from core.models import ModelDatabase, ContentPolicy
            
            model_db = ModelDatabase()
            current_model = self.model_combo.currentText()
            is_eroge_mode = self.ln_eroge_mode.isChecked()
            
            if is_eroge_mode:
                # Check if current model supports eroge content
                model_info = model_db.get_model(current_model)
                if model_info:
                    warning = model_db.get_model_content_warning(current_model)
                    if model_info.content_policy == ContentPolicy.SFW:
                        self.ln_model_warning_label.setText(f"⚠️ {warning}")
                        self.ln_model_warning_label.setVisible(True)
                    else:
                        self.ln_model_warning_label.setVisible(False)
                
                # Show recommendations for NSFW models
                nsfw_models = model_db.get_nsfw_models()
                if nsfw_models:
                    recommended_names = [model.display_name for model in nsfw_models[:3]]
                    self.ln_model_recommendation_label.setText(
                        f"💡 Recommended models for mature content: {', '.join(recommended_names)} or use OpenRouter/Ollama"
                    )
                else:
                    self.ln_model_recommendation_label.setText(
                        "💡 For mature content, consider using OpenRouter models or self-hosted solutions (Ollama)"
                    )
            else:
                self.ln_model_warning_label.setVisible(False)
                self.ln_model_recommendation_label.setText(
                    "💡 All models work well for standard light novel content"
                )
                
        except Exception as e:
            logging.error(f"Error updating model recommendations: {e}")
    
    def estimate_lightnovel_cost(self):
        """Estimate cost for light novel translation"""
        input_file = self.ln_input_file_edit.text().strip()
        
        if not input_file:
            QMessageBox.warning(self, "Warning", "Please select a light novel file first.")
            return
        
        if not os.path.exists(input_file):
            QMessageBox.warning(self, "Warning", "Selected file does not exist.")
            return
        
        try:
            # Get current config for estimation
            config = self.get_current_config()
            
            # Add light novel specific settings
            config['lightnovel_output_format'] = self.ln_output_format_combo.currentText().lower()
            config['lightnovel_use_specialized_prompt'] = self.ln_use_specialized_prompt.isChecked()
            config['lightnovel_use_specialized_vocab'] = self.ln_use_specialized_vocab.isChecked()
            config['lightnovel_max_section_length'] = self.ln_max_section_length.value()
            
            from utils.project_estimator import ProjectEstimator
            estimator = ProjectEstimator()
            
            self.ln_status_label.setText("Estimating translation cost...")
            
            # Estimate for single file
            estimate = estimator.estimate_lightnovel_cost(input_file, config)
            
            self.ln_status_label.setText("Cost estimation completed")
            self.show_lightnovel_estimation_results(estimate)
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to estimate cost: {str(e)}")
            self.ln_status_label.setText("Cost estimation failed")
    
    def show_lightnovel_estimation_results(self, estimate):
        """Show light novel cost estimation results"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Light Novel Translation Cost Estimation")
        dialog.setModal(True)
        dialog.resize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Create summary text
        summary_text = f"""
📚 LIGHT NOVEL TRANSLATION ESTIMATE

📁 File: {estimate.get('file_name', 'Unknown')}
📄 Format: {estimate.get('format', 'Unknown').upper()}
📊 Size: {estimate.get('file_size_mb', 0):.2f} MB

📖 Content Analysis:
• Chapters: {estimate.get('chapters', 0)}
• Translatable sections: {estimate.get('translatable_sections', 0)}
• Total characters: {estimate.get('total_characters', 0):,}
• Japanese characters: {estimate.get('japanese_characters', 0):,}

💰 Cost Estimation:
• Input tokens: {estimate.get('input_tokens', 0):,}
• Expected output tokens: {estimate.get('output_tokens', 0):,}
• Estimated cost: ${estimate.get('total_cost', 0):.4f}

⏱️ Time Estimate:
• Estimated processing time: {estimate.get('estimated_minutes', 0):.1f} minutes
• API calls required: {estimate.get('api_calls', 0):,}

🎯 Translation Settings:
• Model: {estimate.get('model', 'Unknown')}
• Specialized prompt: {'Yes' if estimate.get('use_specialized_prompt', False) else 'No'}
• Specialized vocabulary: {'Yes' if estimate.get('use_specialized_vocab', False) else 'No'}
• Output format: {estimate.get('output_format', 'Same as input')}
"""
        
        text_area = QTextEdit()
        text_area.setPlainText(summary_text)
        text_area.setReadOnly(True)
        layout.addWidget(text_area)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Save Report")
        save_btn.clicked.connect(lambda: self.save_lightnovel_estimation_report(estimate))
        button_layout.addWidget(save_btn)
        
        close_btn = QPushButton("❌ Close")
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec_()
    
    def save_lightnovel_estimation_report(self, estimate):
        """Save light novel estimation report"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, 
                "Save Estimation Report",
                f"lightnovel_estimation_{estimate.get('file_name', 'report')}.txt",
                "Text Files (*.txt);;All Files (*)"
            )
            
            if filename:
                report_content = f"""Light Novel Translation Cost Estimation Report
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

FILE INFORMATION:
File: {estimate.get('file_name', 'Unknown')}
Format: {estimate.get('format', 'Unknown').upper()}
Size: {estimate.get('file_size_mb', 0):.2f} MB

CONTENT ANALYSIS:
Chapters: {estimate.get('chapters', 0)}
Translatable sections: {estimate.get('translatable_sections', 0)}
Total characters: {estimate.get('total_characters', 0):,}
Japanese characters: {estimate.get('japanese_characters', 0):,}

COST ESTIMATION:
Model: {estimate.get('model', 'Unknown')}
Input tokens: {estimate.get('input_tokens', 0):,}
Expected output tokens: {estimate.get('output_tokens', 0):,}
Input cost: ${estimate.get('input_cost', 0):.6f}
Output cost: ${estimate.get('output_cost', 0):.6f}
Total estimated cost: ${estimate.get('total_cost', 0):.4f}

TIME ESTIMATION:
Estimated processing time: {estimate.get('estimated_minutes', 0):.1f} minutes
API calls required: {estimate.get('api_calls', 0):,}

SETTINGS:
Specialized prompt: {'Yes' if estimate.get('use_specialized_prompt', False) else 'No'}
Specialized vocabulary: {'Yes' if estimate.get('use_specialized_vocab', False) else 'No'}
Output format: {estimate.get('output_format', 'Same as input')}
Max section length: {estimate.get('max_section_length', 5000)} characters
"""
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                
                QMessageBox.information(self, "Success", f"Report saved to {filename}")
                self.log_message(f"Light novel estimation report saved: {filename}")
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save report: {str(e)}")
    
    def start_lightnovel_translation(self):
        """Start light novel translation"""
        input_file = self.ln_input_file_edit.text().strip()
        output_dir = self.ln_output_dir_edit.text().strip()
        
        if not input_file:
            QMessageBox.warning(self, "Warning", "Please select a light novel file.")
            return
        
        if not os.path.exists(input_file):
            QMessageBox.warning(self, "Warning", "Selected file does not exist.")
            return
        
        if not output_dir:
            QMessageBox.warning(self, "Warning", "Please select an output directory.")
            return
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Get configuration
        config = self.get_current_config()
        
        # Add light novel specific settings
        output_format = self.ln_output_format_combo.currentText().lower()
        if output_format == "same as input":
            output_format = os.path.splitext(input_file)[1][1:]  # Remove dot
        
        config['lightnovel_output_format'] = output_format
        config['lightnovel_use_specialized_prompt'] = self.ln_use_specialized_prompt.isChecked()
        config['lightnovel_use_specialized_vocab'] = self.ln_use_specialized_vocab.isChecked()
        config['lightnovel_max_section_length'] = self.ln_max_section_length.value()
        config['lightnovel_chapter_mode'] = self.ln_chapter_mode_combo.currentText()
        config['lightnovel_eroge_mode'] = self.ln_eroge_mode.isChecked()
        config['lightnovel_enable_chunking'] = self.ln_enable_chunking.isChecked()
        config['lightnovel_chunk_size'] = self.ln_chunk_size.value()
        config['lightnovel_overlap_tokens'] = self.ln_overlap_tokens.value()
        
        # Warn about model compatibility if eroge mode is enabled
        if self.ln_eroge_mode.isChecked():
            from core.models import ModelDatabase, ContentPolicy
            model_db = ModelDatabase()
            current_model = self.model_combo.currentText()
            model_info = model_db.get_model(current_model)
            
            if model_info and model_info.content_policy == ContentPolicy.SFW:
                reply = QMessageBox.question(
                    self, 
                    "Model Compatibility Warning",
                    f"The selected model ({model_info.display_name}) has strict content filtering and may not work well with erotic content.\n\n"
                    "Recommended alternatives:\n"
                    "• OpenRouter models (developer responsibility)\n"
                    "• Ollama (local models)\n"
                    "• xAI Grok models\n"
                    "• DeepSeek models\n\n"
                    "Do you want to continue with the current model?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
        
        # Create translation manager for single file (use file's parent directory as input)
        input_dir = os.path.dirname(input_file)
        self.lightnovel_translation_manager = TranslationManager(config, input_dir, output_dir)
        
        # Setup providers for light novel translation
        provider_configs = self.get_provider_configs()
        if provider_configs:
            self.lightnovel_translation_manager.setup_providers(provider_configs)
            self.log_message(f"Light novel translation: Configured {len(provider_configs)} providers with automatic fallback")
        
        # Connect signals
        self.lightnovel_translation_manager.progress_updated.connect(self.update_lightnovel_progress)
        self.lightnovel_translation_manager.log_message.connect(self.log_message)
        self.lightnovel_translation_manager.translation_complete.connect(self.on_lightnovel_translation_complete)
        self.lightnovel_translation_manager.error_occurred.connect(self.on_lightnovel_error)
        
        # Update UI
        self.ln_translate_btn.setEnabled(False)
        self.ln_pause_btn.setEnabled(True)
        self.ln_stop_btn.setEnabled(True)
        self.ln_progress_bar.setVisible(True)
        self.ln_status_label.setText("Starting light novel translation...")
        
        # Start translation
        self.lightnovel_translation_manager.start()
        self.log_message("Light novel translation started...")
    
    def pause_lightnovel_translation(self):
        """Pause light novel translation"""
        if hasattr(self, 'lightnovel_translation_manager') and self.lightnovel_translation_manager:
            self.lightnovel_translation_manager.pause()
            self.ln_status_label.setText("Translation paused")
            self.log_message("Light novel translation paused")
    
    def stop_lightnovel_translation(self):
        """Stop light novel translation"""
        if hasattr(self, 'lightnovel_translation_manager') and self.lightnovel_translation_manager:
            self.lightnovel_translation_manager.stop()
            self.ln_translate_btn.setEnabled(True)
            self.ln_pause_btn.setEnabled(False)
            self.ln_stop_btn.setEnabled(False)
            self.ln_progress_bar.setVisible(False)
            self.ln_status_label.setText("Translation stopped by user")
            self.log_message("Light novel translation stopped by user")
    
    def update_lightnovel_progress(self, current, total, filename):
        """Update light novel translation progress"""
        if total > 0:
            progress = int((current / total) * 100)
            self.ln_progress_bar.setValue(progress)
            self.ln_status_label.setText(f"Processing: {filename} ({current}/{total})")
    
    def on_lightnovel_translation_complete(self, original, translated):
        """Handle light novel translation completion"""
        self.ln_translate_btn.setEnabled(True)
        self.ln_pause_btn.setEnabled(False)
        self.ln_stop_btn.setEnabled(False)
        self.ln_progress_bar.setVisible(False)
        self.ln_status_label.setText("Light novel translation completed!")
        self.log_message("Light novel translation completed!")
        
        QMessageBox.information(self, "Success", "Light novel translation completed successfully!")
    
    def on_lightnovel_error(self, error_message):
        """Handle light novel translation error"""
        self.ln_translate_btn.setEnabled(True)
        self.ln_pause_btn.setEnabled(False)
        self.ln_stop_btn.setEnabled(False)
        self.ln_progress_bar.setVisible(False)
        self.ln_status_label.setText("Translation failed")
        self.log_message(f"Light novel translation error: {error_message}")
        
        QMessageBox.warning(self, "Translation Error", f"Translation failed: {error_message}")
    
    # Cloud AI Service Methods
    def test_huggingface_connection(self):
        """Test Hugging Face connection"""
        try:
            from core.cloud_client import CloudAIClient
            
            token = self.hf_token_edit.text().strip()
            model = self.hf_model_combo.currentText().strip()
            
            if not model:
                QMessageBox.warning(self, "Error", "Please enter a model name")
                return
            
            # Add model to combo box if it's new
            if self.hf_model_combo.findText(model) == -1:
                self.hf_model_combo.insertItem(0, model)
                self.hf_model_combo.setCurrentText(model)
            
            client = CloudAIClient()
            config = client.create_huggingface_client(model, token or None)
            
            # Show loading message
            self.cloud_status_label.setText(f"🔄 Testing connection to {model}...")
            QApplication.processEvents()  # Update UI
            
            if client.test_connection(config):
                QMessageBox.information(self, "Success", f"Hugging Face connection successful!\nModel: {model}")
                self.cloud_status_label.setText(f"✅ Hugging Face: {model}")
                self.log_message(f"Hugging Face connection test successful: {model}")
                
                # Save the working model to config
                self.save_cloud_config()
            else:
                QMessageBox.warning(self, "Failed", f"Hugging Face connection failed!\nModel: {model}\n\nPossible issues:\n- Model name is incorrect\n- Model is private and requires API token\n- Model is currently loading (try again in a minute)")
                self.cloud_status_label.setText(f"❌ Hugging Face: Connection failed")
                self.log_message(f"Hugging Face connection test failed: {model}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Test failed: {str(e)}\n\nTips:\n- Check model name spelling\n- Verify API token if using private models\n- Some models may take time to load")
            self.cloud_status_label.setText(f"❌ Hugging Face: Error")
            self.log_message(f"Hugging Face test error: {str(e)}")
    
    def show_popular_hf_models(self):
        """Show dialog with popular HuggingFace models"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Popular HuggingFace Models")
        dialog.resize(900, 600)
        
        layout = QVBoxLayout(dialog)
        
        # Header
        header_label = QLabel("🤗 Popular HuggingFace Models for Translation")
        header_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_label.setStyleSheet("color: #FF6B35; margin: 10px 0px;")
        layout.addWidget(header_label)
        
        # Create tab widget for different categories
        tab_widget = QTabWidget()
        
        # General Purpose models
        general_models = [
            ("meta-llama/Meta-Llama-3.1-8B-Instruct", "Llama 3.1 8B", "Meta's latest instruction-tuned model (8B params)"),
            ("meta-llama/Meta-Llama-3.1-70B-Instruct", "Llama 3.1 70B", "Larger Llama 3.1 model (70B params) - high quality"),
            ("meta-llama/Meta-Llama-3-8B-Instruct", "Llama 3 8B", "Previous generation Llama model (8B params)"),
            ("microsoft/DialoGPT-large", "DialoGPT Large", "Microsoft's conversational model"),
            ("HuggingFaceH4/zephyr-7b-beta", "Zephyr 7B", "Helpful assistant model based on Mistral"),
            ("mistralai/Mistral-7B-Instruct-v0.2", "Mistral 7B", "Mistral AI's instruction model"),
            ("mistralai/Mixtral-8x7B-Instruct-v0.1", "Mixtral 8x7B", "Mixture of experts model (56B total params)")
        ]
        
        # Chinese/Japanese focused models
        asian_models = [
            ("Qwen/Qwen2.5-7B-Instruct", "Qwen 2.5 7B", "Alibaba's latest model, excellent for Chinese/Japanese"),
            ("Qwen/Qwen2.5-14B-Instruct", "Qwen 2.5 14B", "Larger Qwen model with better quality"),
            ("Qwen/Qwen2.5-32B-Instruct", "Qwen 2.5 32B", "Largest Qwen model (requires more resources)"),
            ("Qwen/Qwen2-7B-Instruct", "Qwen 2 7B", "Previous generation Qwen model"),
            ("microsoft/DialoGPT-medium", "DialoGPT Medium", "Medium-sized conversational model"),
            ("rinna/japanese-gpt-neox-3.6b-instruction-sft", "Japanese GPT NeoX", "Japanese-focused model"),
            ("line-corporation/japanese-large-lm-3.6b-instruction-sft", "LINE Japanese LM", "LINE's Japanese language model")
        ]
        
        # Lightweight models
        light_models = [
            ("microsoft/DialoGPT-small", "DialoGPT Small", "Lightweight conversational model"),
            ("google/flan-t5-large", "FLAN-T5 Large", "Google's instruction-tuned T5"),
            ("google/flan-t5-base", "FLAN-T5 Base", "Smaller FLAN-T5 model"),
            ("stabilityai/stablelm-tuned-alpha-7b", "StableLM 7B", "Stability AI's language model"),
            ("EleutherAI/gpt-j-6b", "GPT-J 6B", "EleutherAI's 6B parameter model"),
            ("facebook/blenderbot-400M-distill", "BlenderBot 400M", "Facebook's lightweight chatbot")
        ]
        
        # Experimental/Research models  
        experimental_models = [
            ("bigscience/bloom-7b1", "BLOOM 7B", "Multilingual model from BigScience"),
            ("EleutherAI/gpt-neox-20b", "GPT-NeoX 20B", "Large EleutherAI model (20B params)"),
            ("anthropic/claude-instant-1", "Claude Instant", "Anthropic's model (if available)"),
            ("togethercomputer/RedPajama-INCITE-7B-Instruct", "RedPajama 7B", "Open-source instruction model"),
            ("WizardLM/WizardLM-7B-V1.0", "WizardLM 7B", "Instruction-following model"),
            ("teknium/OpenHermes-2.5-Mistral-7B", "OpenHermes 2.5", "Fine-tuned Mistral model")
        ]
        
        # Create tabs
        for tab_name, models in [
            ("🌟 General Purpose", general_models),
            ("🈵 Chinese/Japanese", asian_models), 
            ("⚡ Lightweight", light_models),
            ("🔬 Experimental", experimental_models)
        ]:
            tab_widget.addTab(self._create_model_list_widget(models), tab_name)
        
        layout.addWidget(tab_widget)
        
        # Instructions
        instructions = QLabel("""
💡 <b>How to use:</b>
• Click on any model to copy its name to the clipboard
• Paste the model name in the HuggingFace model field
• Some models may require an API token for private access
• Larger models provide better quality but may be slower
• Chinese/Japanese models work best for Asian language translation
        """)
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; font-size: 11px; margin: 10px;")
        layout.addWidget(instructions)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        close_btn = QPushButton("❌ Close")
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        dialog.exec_()
    
    def _create_model_list_widget(self, models):
        """Create a widget with list of models"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        for model_id, name, description in models:
            model_frame = QFrame()
            model_frame.setFrameStyle(QFrame.Box)
            model_frame.setStyleSheet("QFrame { border: 1px solid #ddd; border-radius: 5px; margin: 2px; }")
            
            model_layout = QVBoxLayout(model_frame)
            
            # Model name and button
            name_layout = QHBoxLayout()
            name_label = QLabel(f"<b>{name}</b>")
            name_label.setStyleSheet("font-size: 12px; color: #333;")
            name_layout.addWidget(name_label)
            
            name_layout.addStretch()
            
            use_btn = QPushButton("📋 Use This Model")
            use_btn.clicked.connect(lambda checked, model=model_id: self._select_hf_model(model))
            name_layout.addWidget(use_btn)
            
            model_layout.addLayout(name_layout)
            
            # Model ID
            id_label = QLabel(f"<code>{model_id}</code>")
            id_label.setStyleSheet("font-size: 10px; color: #666; font-family: 'Consolas', monospace;")
            model_layout.addWidget(id_label)
            
            # Description
            desc_label = QLabel(description)
            desc_label.setStyleSheet("font-size: 11px; color: #888;")
            desc_label.setWordWrap(True)
            model_layout.addWidget(desc_label)
            
            layout.addWidget(model_frame)
        
        layout.addStretch()
        return widget
    
    def _select_hf_model(self, model_id):
        """Select HuggingFace model and close dialog"""
        # Set the model in the combo box
        if self.hf_model_combo.findText(model_id) == -1:
            self.hf_model_combo.insertItem(0, model_id)
        self.hf_model_combo.setCurrentText(model_id)
        
        # Close any open dialogs
        for child in self.findChildren(QDialog):
            if child.isVisible() and "Popular HuggingFace Models" in child.windowTitle():
                child.accept()
                break
        
        QMessageBox.information(self, "Model Selected", f"Selected model: {model_id}\n\nYou can now test the connection or start translation.")
        self.log_message(f"Selected HuggingFace model: {model_id}")
    
    def test_vllm_connection(self):
        """Test vLLM connection"""
        try:
            from core.cloud_client import CloudAIClient
            
            endpoint = self.vllm_endpoint_edit.text().strip()
            model = self.vllm_model_edit.text().strip()
            
            if not endpoint or not model:
                QMessageBox.warning(self, "Error", "Please enter both endpoint URL and model name")
                return
            
            client = CloudAIClient()
            config = client.create_vllm_client(endpoint, model)
            
            if client.test_connection(config):
                QMessageBox.information(self, "Success", "vLLM connection successful!")
                self.cloud_status_label.setText(f"✅ vLLM: {endpoint}")
                self.log_message(f"vLLM connection test successful: {endpoint}")
            else:
                QMessageBox.warning(self, "Failed", "vLLM connection failed!")
                self.log_message(f"vLLM connection test failed: {endpoint}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Test failed: {str(e)}")
            self.log_message(f"vLLM test error: {str(e)}")
    
    def test_colab_connection(self):
        """Test Google Colab connection"""
        try:
            from core.cloud_client import CloudAIClient
            
            url = self.colab_url_edit.text().strip()
            
            if not url:
                QMessageBox.warning(self, "Error", "Please enter ngrok URL")
                return
            
            client = CloudAIClient()
            config = client.create_colab_client(url)
            
            if client.test_connection(config):
                QMessageBox.information(self, "Success", "Google Colab connection successful!")
                self.cloud_status_label.setText(f"✅ Colab: {url}")
                self.log_message(f"Colab connection test successful: {url}")
            else:
                QMessageBox.warning(self, "Failed", "Google Colab connection failed!")
                self.log_message(f"Colab connection test failed: {url}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Test failed: {str(e)}")
            self.log_message(f"Colab test error: {str(e)}")
    
    def test_kaggle_connection(self):
        """Test Kaggle connection"""
        try:
            from core.cloud_client import CloudAIClient
            
            endpoint = self.kaggle_endpoint_edit.text().strip()
            api_key = self.kaggle_key_edit.text().strip()
            
            if not endpoint:
                QMessageBox.warning(self, "Error", "Please enter endpoint URL")
                return
            
            client = CloudAIClient()
            config = client.create_kaggle_client(endpoint, api_key or None)
            
            if client.test_connection(config):
                QMessageBox.information(self, "Success", "Kaggle connection successful!")
                self.cloud_status_label.setText(f"✅ Kaggle: {endpoint}")
                self.log_message(f"Kaggle connection test successful: {endpoint}")
            else:
                QMessageBox.warning(self, "Failed", "Kaggle connection failed!")
                self.log_message(f"Kaggle connection test failed: {endpoint}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Test failed: {str(e)}")
            self.log_message(f"Kaggle test error: {str(e)}")
    
    def show_vllm_setup(self):
        """Show vLLM setup code"""
        from core.cloud_client import CloudSetupHelper
        
        model_name = self.vllm_model_edit.text().strip() or "Qwen/Qwen2-7B-Instruct"
        setup_code = CloudSetupHelper.generate_vllm_setup_code(model_name)
        
        dialog = QDialog(self)
        dialog.setWindowTitle("vLLM Setup Code")
        dialog.resize(800, 600)
        
        layout = QVBoxLayout(dialog)
        
        text_area = QTextEdit()
        text_area.setPlainText(setup_code)
        text_area.setReadOnly(True)
        text_area.setFont(QFont("Consolas", 10))
        layout.addWidget(text_area)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        copy_btn = QPushButton("📋 Copy to Clipboard")
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(setup_code))
        button_layout.addWidget(copy_btn)
        
        close_btn = QPushButton("❌ Close")
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        dialog.exec_()
    
    def show_colab_setup(self):
        """Show Google Colab setup code"""
        from core.cloud_client import CloudSetupHelper
        
        setup_code = CloudSetupHelper.generate_colab_setup_code()
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Google Colab Setup Code")
        dialog.resize(800, 600)
        
        layout = QVBoxLayout(dialog)
        
        text_area = QTextEdit()
        text_area.setPlainText(setup_code)
        text_area.setReadOnly(True)
        text_area.setFont(QFont("Consolas", 10))
        layout.addWidget(text_area)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        copy_btn = QPushButton("📋 Copy to Clipboard")
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(setup_code))
        button_layout.addWidget(copy_btn)
        
        close_btn = QPushButton("❌ Close")
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        dialog.exec_()
    
    def show_kaggle_setup(self):
        """Show Kaggle setup code"""
        from core.cloud_client import CloudSetupHelper
        
        setup_code = CloudSetupHelper.generate_kaggle_setup_code()
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Kaggle Setup Code")
        dialog.resize(800, 600)
        
        layout = QVBoxLayout(dialog)
        
        text_area = QTextEdit()
        text_area.setPlainText(setup_code)
        text_area.setReadOnly(True)
        text_area.setFont(QFont("Consolas", 10))
        layout.addWidget(text_area)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        copy_btn = QPushButton("📋 Copy to Clipboard")
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(setup_code))
        button_layout.addWidget(copy_btn)
        
        close_btn = QPushButton("❌ Close")
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        dialog.exec_()
    
    def save_cloud_config(self):
        """Save cloud configuration to config"""
        cloud_config = {
            'huggingface': {
                'token': self.hf_token_edit.text().strip(),
                'model': self.hf_model_combo.currentText()
            },
            'vllm': {
                'endpoint': self.vllm_endpoint_edit.text().strip(),
                'model': self.vllm_model_edit.text().strip()
            },
            'colab': {
                'url': self.colab_url_edit.text().strip()
            },
            'kaggle': {
                'endpoint': self.kaggle_endpoint_edit.text().strip(),
                'api_key': self.kaggle_key_edit.text().strip()
            }
        }
        
        # Save to config file or settings
        try:
            import json
            with open('cloud_config.json', 'w', encoding='utf-8') as f:
                json.dump(cloud_config, f, indent=2)
            self.log_message("Cloud configuration saved")
        except Exception as e:
            self.log_message(f"Failed to save cloud config: {e}")
    
    def load_cloud_config(self):
        """Load cloud configuration from config"""
        try:
            import json
            with open('cloud_config.json', 'r', encoding='utf-8') as f:
                cloud_config = json.load(f)
            
            # Load Hugging Face config
            hf_config = cloud_config.get('huggingface', {})
            self.hf_token_edit.setText(hf_config.get('token', ''))
            model_text = hf_config.get('model', '')
            if model_text:
                # Check if model exists in combo box
                index = self.hf_model_combo.findText(model_text)
                if index >= 0:
                    self.hf_model_combo.setCurrentIndex(index)
                else:
                    # Add custom model to the top of the list
                    self.hf_model_combo.insertItem(0, model_text)
                    self.hf_model_combo.setCurrentIndex(0)
            
            # Load vLLM config
            vllm_config = cloud_config.get('vllm', {})
            self.vllm_endpoint_edit.setText(vllm_config.get('endpoint', ''))
            self.vllm_model_edit.setText(vllm_config.get('model', ''))
            
            # Load Colab config
            colab_config = cloud_config.get('colab', {})
            self.colab_url_edit.setText(colab_config.get('url', ''))
            
            # Load Kaggle config
            kaggle_config = cloud_config.get('kaggle', {})
            self.kaggle_endpoint_edit.setText(kaggle_config.get('endpoint', ''))
            self.kaggle_key_edit.setText(kaggle_config.get('api_key', ''))
            
            self.log_message("Cloud configuration loaded")
        except FileNotFoundError:
            pass  # No config file yet
        except Exception as e:
            self.log_message(f"Failed to load cloud config: {e}")
    
    # Provider Management Methods
    def refresh_provider_status(self):
        """Refresh provider status display"""
        if not hasattr(self, 'provider_manager'):
            return
        
        # Clear existing widgets
        for i in reversed(range(self.providers_list_layout.count())):
            child = self.providers_list_layout.takeAt(i)
            if child.widget():
                child.widget().deleteLater()
        
        # Get all providers sorted by priority
        all_status = self.provider_manager.get_all_provider_status()
        sorted_providers = sorted(all_status.items(), key=lambda x: x[1]['priority'])
        
        # Display each provider
        for name, status in sorted_providers:
            provider_widget = self.create_provider_widget(name, status)
            self.providers_list_layout.addWidget(provider_widget)
        
        # Update system status
        available_provider = self.provider_manager.get_available_provider()
        if available_provider:
            self.provider_status_label.setText(f"✅ Ready - Primary: {available_provider.name}")
        else:
            self.provider_status_label.setText("❌ No providers available")
    
    def create_provider_widget(self, name: str, status: dict) -> QWidget:
        """Create widget for a single provider"""
        widget = QFrame()
        widget.setFrameStyle(QFrame.StyledPanel)
        widget.setStyleSheet("QFrame { border: 1px solid #ccc; border-radius: 5px; margin: 2px; padding: 5px; }")
        
        layout = QVBoxLayout(widget)
        
        # Header with name and status
        header_layout = QHBoxLayout()
        
        # Status indicator
        if status['enabled']:
            if status['status'] == 'available':
                status_icon = "✅"
                status_color = "#4CAF50"
            elif status['status'] == 'rate_limited':
                status_icon = "⏳"
                status_color = "#FF9800"
            elif status['status'] == 'error':
                status_icon = "❌"
                status_color = "#F44336"
            else:
                status_icon = "❓"
                status_color = "#9E9E9E"
        else:
            status_icon = "⏸️"
            status_color = "#9E9E9E"
        
        name_label = QLabel(f"{status_icon} {name}")
        name_label.setFont(QFont("Arial", 12, QFont.Bold))
        name_label.setStyleSheet(f"color: {status_color};")
        header_layout.addWidget(name_label)
        
        # Priority
        priority_label = QLabel(f"Priority: {status['priority']}")
        priority_label.setStyleSheet("color: #666;")
        header_layout.addWidget(priority_label)
        
        header_layout.addStretch()
        
        # Controls
        controls_layout = QHBoxLayout()
        
        # Priority buttons
        priority_up_btn = QPushButton("⬆️")
        priority_up_btn.setMaximumWidth(30)
        priority_up_btn.clicked.connect(lambda: self.change_provider_priority(name, -1))
        controls_layout.addWidget(priority_up_btn)
        
        priority_down_btn = QPushButton("⬇️")
        priority_down_btn.setMaximumWidth(30)
        priority_down_btn.clicked.connect(lambda: self.change_provider_priority(name, 1))
        controls_layout.addWidget(priority_down_btn)
        
        # Enable/disable button
        toggle_btn = QPushButton("⏸️" if status['enabled'] else "▶️")
        toggle_btn.setMaximumWidth(30)
        toggle_btn.clicked.connect(lambda: self.toggle_provider(name))
        controls_layout.addWidget(toggle_btn)
        
        # Test button
        test_btn = QPushButton("🧪")
        test_btn.setMaximumWidth(30)
        test_btn.clicked.connect(lambda: self.test_single_provider(name))
        controls_layout.addWidget(test_btn)
        
        # Remove button
        remove_btn = QPushButton("🗑️")
        remove_btn.setMaximumWidth(30)
        remove_btn.clicked.connect(lambda: self.remove_provider(name))
        controls_layout.addWidget(remove_btn)
        
        header_layout.addLayout(controls_layout)
        layout.addLayout(header_layout)
        
        # Details
        details_text = f"Provider: {status['provider']} | Failures: {status['consecutive_failures']}"
        if status['in_cooldown']:
            details_text += f" | Cooldown: {status['cooldown_remaining']}s"
        if status['last_error']:
            details_text += f" | Error: {status['last_error'][:50]}..."
        
        details_label = QLabel(details_text)
        details_label.setStyleSheet("color: #666; font-size: 10px;")
        details_label.setWordWrap(True)
        layout.addWidget(details_label)
        
        return widget
    
    def add_provider_dialog(self):
        """Show dialog to add new provider"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Provider")
        dialog.resize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        # Provider name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        name_edit = QLineEdit()
        name_layout.addWidget(name_edit)
        layout.addLayout(name_layout)
        
        # Provider type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        type_combo = QComboBox()
        type_combo.addItems([
            "OpenAI", "OpenRouter", "Anthropic", "Google", "xAI", "DeepSeek",
            "Hugging Face", "vLLM", "Google Colab", "Kaggle", "Ollama", "Custom"
        ])
        type_layout.addWidget(type_combo)
        layout.addLayout(type_layout)
        
        # API Key
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("API Key:"))
        key_edit = QLineEdit()
        key_edit.setEchoMode(QLineEdit.Password)
        key_layout.addWidget(key_edit)
        layout.addLayout(key_layout)
        
        # API URL
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("API URL:"))
        url_edit = QLineEdit()
        url_layout.addWidget(url_edit)
        layout.addLayout(url_layout)
        
        # Model
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model:"))
        model_edit = QLineEdit()
        model_layout.addWidget(model_edit)
        layout.addLayout(model_layout)
        
        # Priority
        priority_layout = QHBoxLayout()
        priority_layout.addWidget(QLabel("Priority:"))
        priority_spin = QSpinBox()
        priority_spin.setRange(1, 100)
        priority_spin.setValue(10)
        priority_layout.addWidget(priority_spin)
        layout.addLayout(priority_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("➕ Add")
        add_btn.clicked.connect(lambda: self.add_provider_from_dialog(
            dialog, name_edit.text(), type_combo.currentText(),
            key_edit.text(), url_edit.text(), model_edit.text(), priority_spin.value()
        ))
        button_layout.addWidget(add_btn)
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        dialog.exec_()
    
    def add_provider_from_dialog(self, dialog, name, provider_type, api_key, api_url, model, priority):
        """Add provider from dialog input"""
        try:
            if not name.strip():
                QMessageBox.warning(self, "Error", "Provider name is required")
                return
            
            # Map provider type to enum
            provider_mapping = {
                "OpenAI": "openai",
                "OpenRouter": "openrouter", 
                "Anthropic": "anthropic",
                "Google": "google",
                "xAI": "xai",
                "DeepSeek": "deepseek",
                "Hugging Face": "huggingface",
                "vLLM": "vllm",
                "Google Colab": "colab",
                "Kaggle": "kaggle",
                "Ollama": "ollama",
                "Custom": "custom"
            }
            
            from core.models import ModelProvider
            provider_enum = ModelProvider(provider_mapping[provider_type])
            
            # Create config
            config = {
                "key": api_key,
                "api": api_url,
                "model": model
            }
            
            # Add provider
            self.provider_manager.add_provider(
                name=name.strip(),
                provider=provider_enum,
                config=config,
                priority=priority
            )
            
            dialog.accept()
            self.refresh_provider_status()
            self.log_message(f"Added provider: {name}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add provider: {e}")
    
    def change_provider_priority(self, name: str, delta: int):
        """Change provider priority"""
        if hasattr(self, 'provider_manager'):
            status = self.provider_manager.get_provider_status(name)
            new_priority = max(1, status['priority'] + delta)
            self.provider_manager.update_provider_priority(name, new_priority)
            self.refresh_provider_status()
            self.log_message(f"Updated {name} priority to {new_priority}")
    
    def toggle_provider(self, name: str):
        """Toggle provider enabled/disabled"""
        if hasattr(self, 'provider_manager'):
            status = self.provider_manager.get_provider_status(name)
            new_enabled = not status['enabled']
            self.provider_manager.enable_provider(name, new_enabled)
            self.refresh_provider_status()
            action = "enabled" if new_enabled else "disabled"
            self.log_message(f"Provider {name} {action}")
    
    def test_single_provider(self, name: str):
        """Test single provider connection"""
        if hasattr(self, 'provider_manager'):
            try:
                provider = self.provider_manager.providers[name]
                success = self.provider_manager._test_provider_connection(provider)
                if success:
                    QMessageBox.information(self, "Success", f"Provider {name} connection successful!")
                    self.log_message(f"Provider {name} test successful")
                else:
                    QMessageBox.warning(self, "Failed", f"Provider {name} connection failed!")
                    self.log_message(f"Provider {name} test failed")
                self.refresh_provider_status()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Test failed: {e}")
                self.log_message(f"Provider {name} test error: {e}")
    
    def remove_provider(self, name: str):
        """Remove provider after confirmation"""
        reply = QMessageBox.question(
            self, "Confirm Remove", 
            f"Are you sure you want to remove provider '{name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if hasattr(self, 'provider_manager'):
                self.provider_manager.remove_provider(name)
                self.refresh_provider_status()
                self.log_message(f"Removed provider: {name}")
    
    def test_all_providers(self):
        """Test all providers"""
        if hasattr(self, 'provider_manager'):
            self.log_message("Testing all providers...")
            for name in self.provider_manager.providers.keys():
                self.test_single_provider(name)
    
    def reset_all_provider_failures(self):
        """Reset failure counts for all providers"""
        if hasattr(self, 'provider_manager'):
            self.provider_manager.reset_all_failures()
            self.refresh_provider_status()
            self.log_message("Reset all provider failure counts")
    
    def get_documentation_content(self):
        """Get HTML content for documentation tab"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { 
                    font-family: 'Segoe UI', Arial, sans-serif; 
                    margin: 20px; 
                    line-height: 1.6; 
                    background-color: #ffffff;
                    color: #333333;
                }
                h1 { 
                    color: #2c3e50; 
                    border-bottom: 3px solid #3498db; 
                    padding-bottom: 10px; 
                }
                h2 { 
                    color: #34495e; 
                    border-bottom: 2px solid #95a5a6; 
                    padding-bottom: 8px; 
                    margin-top: 30px; 
                }
                h3 { 
                    color: #2c3e50; 
                    margin-top: 25px; 
                    font-weight: bold;
                }
                .feature { 
                    background: #f8f9fa; 
                    padding: 15px; 
                    margin: 10px 0; 
                    border-radius: 8px; 
                    border-left: 4px solid #17a2b8;
                }
                .highlight { 
                    background: #ffc107; 
                    color: #212529; 
                    padding: 3px 8px; 
                    border-radius: 4px; 
                    font-weight: bold;
                }
                .new { 
                    background: #dc3545; 
                    color: white; 
                    padding: 3px 8px; 
                    border-radius: 4px; 
                    font-size: 0.8em; 
                    font-weight: bold;
                }
                ul { padding-left: 25px; }
                li { margin: 5px 0; color: #333333; }
                .tab-info { 
                    background: #e3f2fd; 
                    color: #1a1a1a; 
                    padding: 15px; 
                    border-radius: 8px; 
                    margin: 10px 0; 
                    border-left: 4px solid #2196f3;
                }
                .tab-info h3 {
                    color: #1565c0;
                    margin-top: 0;
                    font-weight: bold;
                }
                .warning { 
                    background: #fff3cd; 
                    color: #856404; 
                    padding: 15px; 
                    border-radius: 8px; 
                    margin: 10px 0; 
                    border-left: 4px solid #ffc107;
                }
                .code { 
                    background: #f8f9fa; 
                    color: #495057; 
                    padding: 15px; 
                    border-radius: 8px; 
                    font-family: 'Consolas', 'Monaco', monospace; 
                    border-left: 4px solid #6f42c1;
                }
            </style>
        </head>
        <body>
            <h1>🚀 BaconanaMTL Tool - Documentation</h1>
            
            <div class="feature">
                <h2>📋 Quick Start Guide</h2>
                <ol>
                    <li><strong>Configure Providers:</strong> Set up your AI providers in the "🔄 Providers" tab</li>
                    <li><strong>Select Project:</strong> Choose your game folder in "🌐 Game Translation" or "📚 Light Novel" tabs</li>
                    <li><strong>Start Translation:</strong> Click translate and monitor progress with automatic provider fallback</li>
                </ol>
            </div>

            <h2>🎯 Application Tabs Overview</h2>
            
            <div class="tab-info">
                <h3>⚙️ Configuration</h3>
                <p>Basic API settings for backward compatibility. For multiple providers, use the <strong>Providers</strong> tab instead.</p>
                <ul>
                    <li>Single API provider setup</li>
                    <li>Model selection and pricing</li>
                    <li>Connection testing</li>
                </ul>
            </div>

            <div class="tab-info">
                <h3>🌐 Game Translation</h3>
                <p>Main translation interface for games with automatic engine detection.</p>
                <ul>
                    <li><strong>Supported Engines:</strong> RPG Maker, Ren'Py, Unity, Wolf RPG Editor, KiriKiri, NScripter, Live Maker, TyranoBuilder, SRPG Studio, Lune, Regex</li>
                    <li>Automatic project type detection</li>
                    <li>Real-time progress monitoring</li>
                    <li>Batch processing with smart threading</li>
                </ul>
            </div>

            <div class="tab-info">
                <h3>📚 Light Novel</h3>
                <p>Specialized interface for visual novels and light novels with advanced content handling.</p>
                <ul>
                    <li><strong>Content Detection:</strong> Automatic eroge/adult content classification</li>
                    <li><strong>Model Filtering:</strong> SFW/NSFW model compatibility checking</li>
                    <li><strong>Smart Chunking:</strong> Sentence-aware text segmentation</li>
                    <li><strong>Multiple Formats:</strong> Text, EPUB, JSON output options</li>
                    <li><strong>Cost Estimation:</strong> Detailed analysis before translation</li>
                </ul>
            </div>

            <div class="tab-info">
                <h3>🎵 Audio & Subtitles <span class="new">NEW!</span></h3>
                <p>Transcribe audio/video and generate subtitles with multiple providers.</p>
                <ul>
                    <li><strong>Cloud Providers:</strong> OpenAI Whisper, Groq, AssemblyAI, Nova, Azure</li>
                    <li><strong>Local Processing:</strong> Faster-Whisper for offline transcription</li>
                    <li><strong>Multiple Formats:</strong> SRT, VTT, ASS subtitle generation</li>
                    <li><strong>Auto-sizing:</strong> Adaptive font sizes based on video resolution</li>
                    <li><strong>Translation Integration:</strong> Direct translation after transcription</li>
                </ul>
            </div>

            <div class="tab-info">
                <h3>🖥️ Local Models <span class="new">NEW!</span></h3>
                <p>Run AI models locally using llama.cpp for complete offline translation.</p>
                <ul>
                    <li><strong>Model Management:</strong> Download and manage Llama, Qwen, Mistral, Gemma models</li>
                    <li><strong>Zero Cost:</strong> No API fees, unlimited local inference</li>
                    <li><strong>Privacy:</strong> Complete data privacy, no cloud connections</li>
                    <li><strong>GPU Acceleration:</strong> Optional CUDA support for faster inference</li>
                    <li><strong>Configurable:</strong> Adjust context length, temperature, threads</li>
                    <li><strong>Test Interface:</strong> Built-in translation testing</li>
                </ul>
            </div>

            <div class="tab-info">
                <h3>👥 Character Generator <span class="new">NEW!</span></h3>
                <p>Create and manage detailed character profiles for your stories with AI assistance.</p>
                <ul>
                    <li><strong>Multi-Style Generation:</strong> Japanese, Korean, Chinese, Fantasy character styles</li>
                    <li><strong>Comprehensive Profiles:</strong> Appearance, personality, background, relationships</li>
                    <li><strong>Custom Fields:</strong> Add unlimited custom attributes for characters</li>
                    <li><strong>AI-Powered Creation:</strong> Intelligent character generation with cultural context</li>
                    <li><strong>Character Database:</strong> Save, edit, and manage character collections</li>
                    <li><strong>Export/Import:</strong> JSON-based character data for portability</li>
                    <li><strong>Visual Descriptions:</strong> Detailed physical appearance generation</li>
                </ul>
            </div>

            <div class="tab-info">
                <h3>📝 Novel Writing <span class="new">NEW!</span></h3>
                <p>AI-assisted novel writing with context awareness and character integration.</p>
                <ul>
                    <li><strong>Context Memory:</strong> AI remembers plot points, character development, and story beats</li>
                    <li><strong>Character Integration:</strong> Direct access to character database for consistency</li>
                    <li><strong>Adaptive Prompts:</strong> Genre-specific writing prompts (Romance, Fantasy, Sci-Fi, etc.)</li>
                    <li><strong>Chapter Management:</strong> Organize stories into chapters with individual summaries</li>
                    <li><strong>Multiple Formats:</strong> Export to TXT, DOCX, EPUB, Markdown</li>
                    <li><strong>Writing Styles:</strong> Choose between narrative styles and perspectives</li>
                    <li><strong>Scene Planning:</strong> Outline and develop individual scenes</li>
                    <li><strong>Revision Tools:</strong> AI-powered editing and improvement suggestions</li>
                </ul>
            </div>

            <div class="tab-info">
                <h3>☁️ Cloud AI</h3>
                <p>Access cloud platforms and advanced AI models.</p>
                <ul>
                    <li><strong>HuggingFace:</strong> 1000+ transformer models with manual selection</li>
                    <li><strong>vLLM:</strong> High-performance inference with custom deployments</li>
                    <li><strong>Google Colab:</strong> Free GPU-accelerated translation</li>
                    <li><strong>Kaggle:</strong> Notebook-based processing</li>
                    <li><strong>Setup Code Generation:</strong> Automatic configuration for cloud platforms</li>
                </ul>
            </div>

            <div class="tab-info">
                <h3>🔄 Providers</h3>
                <p>Advanced provider management with automatic failover.</p>
                <ul>
                    <li><strong>Multiple Providers:</strong> Configure OpenAI, Anthropic, Gemini, xAI, DeepSeek, etc.</li>
                    <li><strong>Priority System:</strong> Set provider preference order</li>
                    <li><strong>Automatic Fallback:</strong> Seamless switching when providers fail</li>
                    <li><strong>Real-time Monitoring:</strong> Provider status and health tracking</li>
                    <li><strong>Failure Management:</strong> Automatic retry and cooldown handling</li>
                </ul>
            </div>

            <div class="tab-info">
                <h3>🔧 Advanced</h3>
                <p>Fine-tune translation behavior and customize prompts.</p>
                <ul>
                    <li>Custom translation prompts</li>
                    <li>Term dictionaries for consistency</li>
                    <li>File inclusion/exclusion patterns</li>
                    <li>Threading and performance settings</li>
                </ul>
            </div>

            <div class="tab-info">
                <h3>📋 Log</h3>
                <p>Real-time monitoring and debugging information.</p>
                <ul>
                    <li>Translation progress and status</li>
                    <li>Provider switching notifications</li>
                    <li>Error messages and warnings</li>
                    <li>Performance metrics</li>
                </ul>
            </div>

            <h2>✨ Key Features</h2>

            <div class="feature">
                <h3>🔄 Provider Management System</h3>
                <p>Industry-grade provider management with automatic failover ensures <span class="highlight">99.9% uptime</span> for your translations.</p>
                <ul>
                    <li><strong>Priority-based routing:</strong> Configure which providers to use first</li>
                    <li><strong>Automatic failover:</strong> Seamless switching when providers fail</li>
                    <li><strong>Rate limit handling:</strong> Intelligent backoff and retry mechanisms</li>
                    <li><strong>Cost optimization:</strong> Route to cheaper providers when possible</li>
                </ul>
            </div>

            <div class="feature">
                <h3>🤖 AI Provider Support</h3>
                <p>Support for <span class="highlight">7+ major AI providers</span> plus cloud platforms:</p>
                <ul>
                    <li><strong>OpenAI:</strong> GPT-3.5, GPT-4, GPT-4-turbo, GPT-4o</li>
                    <li><strong>Anthropic:</strong> Claude-3-haiku, Claude-3-sonnet, Claude-3.5-sonnet</li>
                    <li><strong>Google:</strong> Gemini-1.5-pro, Gemini-1.5-flash</li>
                    <li><strong>xAI:</strong> Grok-beta (great for adult content)</li>
                    <li><strong>DeepSeek:</strong> DeepSeek-chat, DeepSeek-coder</li>
                    <li><strong>OpenRouter:</strong> 200+ models via unified API</li>
                    <li><strong>Ollama:</strong> Local models (Llama, Mistral, etc.)</li>
                </ul>
            </div>

            <div class="feature">
                <h3>📚 Light Novel Processing</h3>
                <p>Advanced content-aware processing for visual novels and light novels:</p>
                <ul>
                    <li><strong>Eroge Detection:</strong> Automatic adult content classification</li>
                    <li><strong>Model Compatibility:</strong> SFW/NSFW model filtering</li>
                    <li><strong>Smart Chunking:</strong> Sentence-boundary aware text segmentation</li>
                    <li><strong>Multiple Outputs:</strong> Text, EPUB, JSON formats</li>
                </ul>
            </div>

            <div class="feature">
                <h3>🎨 Creative Writing Suite <span class="new">NEW!</span></h3>
                <p>Complete toolkit for creative writing with AI assistance:</p>
                <ul>
                    <li><strong>Character Generator:</strong> Create detailed characters with cultural authenticity</li>
                    <li><strong>Novel Writing Assistant:</strong> Context-aware story development</li>
                    <li><strong>Multi-Cultural Styles:</strong> Japanese, Korean, Chinese, Fantasy character archetypes</li>
                    <li><strong>Smart Context Memory:</strong> AI tracks characters, plot, and story elements</li>
                    <li><strong>Multiple Genres:</strong> Romance, Fantasy, Sci-Fi, Mystery, and more</li>
                </ul>
            </div>

            <div class="feature">
                <h3>🎵 Multimedia Processing <span class="new">NEW!</span></h3>
                <p>Professional audio and video processing capabilities:</p>
                <ul>
                    <li><strong>Audio Transcription:</strong> Multiple cloud and local providers</li>
                    <li><strong>Subtitle Generation:</strong> SRT, VTT, ASS formats with auto-sizing</li>
                    <li><strong>Translation Integration:</strong> Direct translation after transcription</li>
                    <li><strong>Local Processing:</strong> Faster-Whisper for offline transcription</li>
                </ul>
            </div>

            <h2>🎮 Supported Game Engines</h2>
            
            <div class="feature">
                <ul>
                    <li><strong>RPG Maker MV/MZ:</strong> JSON game data with structure preservation</li>
                    <li><strong>Ren'Py:</strong> Visual novel scripts with markup handling</li>
                    <li><strong>Unity:</strong> Localization files (JSON, CSV, XML)</li>
                    <li><strong>Wolf RPG Editor:</strong> Scripts and archives with binary extraction</li>
                    <li><strong>KiriKiri:</strong> Engine scripts and archives</li>
                    <li><strong>NScripter:</strong> Game scripts with pattern matching</li>
                    <li><strong>Live Maker:</strong> Binary files with encoding detection</li>
                    <li><strong>TyranoBuilder:</strong> TyranoScript with tag preservation</li>
                    <li><strong>SRPG Studio:</strong> Tactical RPG data</li>
                    <li><strong>Lune:</strong> Binary formats with text extraction</li>
                    <li><strong>Regex:</strong> Custom pattern-based processing</li>
                </ul>
            </div>

            <div class="warning">
                <h3>⚠️ Important Notes</h3>
                <ul>
                    <li><strong>API Keys Required:</strong> You need valid API keys from your chosen providers</li>
                    <li><strong>Backup Your Files:</strong> Always backup original files before translation</li>
                    <li><strong>Content Policies:</strong> Some providers have strict content filtering</li>
                    <li><strong>Rate Limits:</strong> Free tiers have usage limits - consider paid plans for large projects</li>
                </ul>
            </div>

            <h2>💡 Tips for Best Results</h2>
            
            <div class="feature">
                <ul>
                    <li><strong>Use Multiple Providers:</strong> Configure 2-3 providers for best reliability</li>
                    <li><strong>Set Priorities:</strong> Put your preferred (fastest/cheapest) provider first</li>
                    <li><strong>Adult Content:</strong> Use xAI Grok, OpenRouter, or Ollama for eroge/adult content</li>
                    <li><strong>Quality vs Cost:</strong> GPT-4 for best quality, GPT-3.5 for cost efficiency</li>
                    <li><strong>Large Projects:</strong> Use Light Novel tab for books, Game Translation for games</li>
                    <li><strong>Custom Prompts:</strong> Adapt prompts for specific content types or styles</li>
                </ul>
            </div>

            <h2>📝 Creative Writing & Character Generation</h2>

            <div class="feature">
                <h3>🎭 Character Generator Usage</h3>
                <ul>
                    <li><strong>Cultural Styles:</strong> Choose from Japanese, Korean, Chinese, or Fantasy character types</li>
                    <li><strong>Custom Fields:</strong> Add any attributes you need (skills, relationships, items, etc.)</li>
                    <li><strong>Export/Import:</strong> Save character libraries as JSON files for backup or sharing</li>
                    <li><strong>Integration:</strong> Characters automatically appear in the Novel Writing tab</li>
                </ul>
            </div>

            <div class="feature">
                <h3>✍️ Novel Writing Assistant</h3>
                <ul>
                    <li><strong>Context Memory:</strong> AI tracks story elements across chapters for consistency</li>
                    <li><strong>Genre Prompts:</strong> Specialized prompts for Romance, Fantasy, Sci-Fi, Mystery, and more</li>
                    <li><strong>Chapter Organization:</strong> Automatic chapter management with summaries</li>
                    <li><strong>Character Integration:</strong> Reference any character from your database instantly</li>
                    <li><strong>Multiple Export Formats:</strong> Save as TXT, DOCX, EPUB, or Markdown</li>
                </ul>
            </div>

            <div class="warning">
                <h3>⚠️ Important Notes for Creative Features</h3>
                <ul>
                    <li><strong>AI Provider Required:</strong> Character generation and writing assistance require configured AI providers</li>
                    <li><strong>Context Limits:</strong> Very long stories may exceed model context windows - use chapter summaries</li>
                    <li><strong>Data Storage:</strong> Characters and stories are saved locally in the application folder</li>
                    <li><strong>Quality Depends on Model:</strong> Better models (GPT-4, Claude-3.5) produce higher quality content</li>
                    <li><strong>Creative License:</strong> AI-generated content should be reviewed and edited for best results</li>
                </ul>
            </div>

            <div class="code">
                <strong>Getting Started:</strong><br>
                1. Go to "🔄 Providers" tab<br>
                2. Click "➕ Add Provider" and configure OpenAI or another provider<br>
                3. Test the connection<br>
                4. Go to appropriate translation tab<br>
                5. Select your project and click translate!
            </div>

            <p style="text-align: center; margin-top: 30px; color: #7f8c8d;">
                <strong>Need help?</strong> Check the GitHub repository or contact support.
            </p>
        </body>
        </html>
        """
    
    def open_readme_file(self):
        """Open README.md file"""
        import os
        import subprocess
        readme_path = os.path.join(os.getcwd(), "README.md")
        
        try:
            if os.path.exists(readme_path):
                if os.name == 'nt':  # Windows
                    os.startfile(readme_path)
                else:  # macOS and Linux
                    subprocess.call(['open' if os.uname().sysname == 'Darwin' else 'xdg-open', readme_path])
                self.log_message("Opened README.md file")
            else:
                QMessageBox.warning(self, "File Not Found", "README.md file not found in the current directory.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open README.md: {e}")
    
    def open_github_repo(self):
        """Open GitHub repository in browser"""
        import webbrowser
        try:
            webbrowser.open("https://github.com/Baconana-chan/BaconanaMTLTool")
            self.log_message("Opened GitHub repository")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open GitHub repository: {e}")
    
    def open_url(self, url):
        """Open URL in default browser"""
        import webbrowser
        try:
            webbrowser.open(url)
            self.log_message(f"Opened URL: {url}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open URL: {e}")
    
    def get_about_content(self):
        """Get HTML content for the About tab"""
        # Read requirements.txt to get dependencies
        dependencies = []
        try:
            with open("requirements.txt", "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        # Extract package name (before == or >=)
                        pkg_name = line.split("==")[0].split(">=")[0].strip()
                        dependencies.append(pkg_name)
        except FileNotFoundError:
            dependencies = ["PyQt5", "requests", "tiktoken", "transformers", "torch"]
        
        deps_list = ", ".join(dependencies) if dependencies else "PyQt5, requests, tiktoken, transformers, torch"
        
        return f"""
        <div class="app-header">
            <h1>🚀 BaconanaMTL Tool</h1>
            <h2>Advanced AI Translation Tool</h2>
        </div>
        
        <div class="version">
            <h3>📋 Version Information</h3>
            <p><strong>Version:</strong> 1.2</p>
            <p><strong>Release Date:</strong> September 2025</p>
        </div>
        
        <div class="section">
            <h3>📝 Description</h3>
            <p>BaconanaMTL Tool is a comprehensive AI-powered translation application designed for various types of content including:</p>
            <ul>
                <li><strong>🎮 Games:</strong> RPG Maker, Ren'Py, Unity, Wolf RPG Editor, KiriKiri, NScripter, LiveMaker, TyranoBuilder, SRPG Studio, Lune</li>
                <li><strong>📚 Light Novels:</strong> EPUB, TXT, PDF formats with smart content detection</li>
                <li><strong>🔧 Custom Content:</strong> Regex-based processing for specialized formats</li>
            </ul>
            <p>The tool supports multiple AI providers with automatic fallback, smart cost estimation, and content-aware processing.</p>
        </div>
        
        <div class="section">
            <h3>🌟 Key Features</h3>
            <ul>
                <li><strong>Multi-Provider Support:</strong> OpenAI, Anthropic, OpenRouter, Ollama, HuggingFace, vLLM, Google Colab, Kaggle</li>
                <li><strong>Priority System:</strong> Automatic provider fallback with configurable priorities</li>
                <li><strong>Smart Processing:</strong> Content-aware chunking and context preservation</li>
                <li><strong>Cost Estimation:</strong> Real-time token counting and cost calculation</li>
                <li><strong>Cloud Integration:</strong> Support for cloud-based AI services</li>
                <li><strong>SFW/NSFW Detection:</strong> Automatic content policy matching</li>
            </ul>
        </div>
        
        <div class="warning">
            <h3>⚠️ Important Notice</h3>
            <p><strong>Beta Software:</strong> This application is in active development. Not all functionality has been thoroughly tested.</p>
            <p><strong>Bug Reports:</strong> If you encounter issues not related to API errors, please report them on our GitHub Issues page.</p>
            <p><strong>Use at Your Own Risk:</strong> Always backup your original files before translation.</p>
        </div>
        
        <div class="support">
            <h3>💝 Support Development</h3>
            <p>If you find this tool useful, consider supporting its development:</p>
            <ul>
                <li><strong>Ko-fi:</strong> <a href="https://ko-fi.com/baconana_chan">https://ko-fi.com/baconana_chan</a></li>
                <li><strong>GitHub:</strong> Star the repository and report issues</li>
                <li><strong>Community:</strong> Share feedback and suggestions</li>
            </ul>
        </div>
        
        <div class="section">
            <h3>🐛 Bug Reports & Issues</h3>
            <p>For technical issues (excluding API-related problems), please visit:</p>
            <p><strong>GitHub Issues:</strong> <a href="https://github.com/Baconana-chan/BaconanaMTLTool/issues">https://github.com/Baconana-chan/BaconanaMTLTool/issues</a></p>
            <p>When reporting bugs, please include:</p>
            <ul>
                <li>Operating system and version</li>
                <li>Steps to reproduce the issue</li>
                <li>Error messages (if any)</li>
                <li>Input file format and size</li>
            </ul>
        </div>
        
        <div class="thanks">
            <h3>🙏 Acknowledgments</h3>
            <p><strong>Original Inspiration:</strong> <a href="https://gitgud.io/DazedAnon/DazedMTLTool">DazedMTLTool by DazedAnon</a></p>
            <p><strong>Dependencies:</strong> This tool is built upon excellent open-source libraries including {deps_list}</p>
            <p><strong>Community:</strong> Thanks to all users providing feedback and bug reports</p>
        </div>
        
        <div class="section">
            <h3>📜 License & Legal</h3>
            <p><strong>License:</strong> MIT License (see repository for details)</p>
            <p><strong>AI Services:</strong> Users are responsible for compliance with AI provider terms of service</p>
            <p><strong>Content:</strong> Users are responsible for the content they choose to translate</p>
        </div>
        """
    
    # Audio Tab Methods
    def browse_audio_file(self):
        """Browse for audio/video file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Audio/Video File",
            "", "Audio/Video Files (*.mp3 *.wav *.flac *.m4a *.mp4 *.avi *.mkv *.mov);;All Files (*)")
        if file_path:
            self.audio_file_edit.setText(file_path)
            self.update_audio_info(file_path)
            self.update_transcription_cost()

    def update_audio_info(self, file_path):
        """Update audio file information display"""
        try:
            if not self.audio_processor:
                from core.audio_processor import AudioProcessor
                self.audio_processor = AudioProcessor(self.config_manager)
            
            duration = self.audio_processor.get_audio_duration(file_path)
            if duration > 0:
                minutes = int(duration // 60)
                seconds = int(duration % 60)
                size_mb = os.path.getsize(file_path) / (1024 * 1024)
                self.audio_info_label.setText(f"Duration: {minutes}:{seconds:02d} | Size: {size_mb:.1f} MB")
                self.audio_info_label.setStyleSheet("color: green; font-weight: bold;")
            else:
                self.audio_info_label.setText("Could not read audio file information")
                self.audio_info_label.setStyleSheet("color: orange;")
        except Exception as e:
            self.audio_info_label.setText(f"Error: {str(e)}")
            self.audio_info_label.setStyleSheet("color: red;")

    def update_transcription_cost(self):
        """Update cost estimation for transcription"""
        if not self.audio_file_edit.text():
            self.cost_label.setText("Estimated cost: $0.00")
            return
        
        try:
            if not self.audio_processor:
                from core.audio_processor import AudioProcessor
                self.audio_processor = AudioProcessor(self.config_manager)
            
            duration = self.audio_processor.get_audio_duration(self.audio_file_edit.text())
            if duration == 0:
                self.cost_label.setText("Estimated cost: Unable to calculate")
                return
            
            provider_text = self.audio_provider_combo.currentText()
            
            # Show/hide local model settings based on provider
            is_faster_whisper = "Faster-Whisper" in provider_text
            self.local_settings_group.setVisible(is_faster_whisper)
            
            provider_map = {
                "OpenAI Whisper": "openai-whisper",
                "Groq Whisper V3 Large": "groq-whisper-v3-large",
                "Groq Whisper Large V3 Turbo": "groq-whisper-large-v3-turbo",
                "AssemblyAI Universal-2": "assemblyai-universal-2",
                "Nova-1": "nova-1",
                "Nova-2": "nova-2",
                "Nova-3 Multilingual": "nova-3-multilingual",
                "Nova-3 Monolingual": "nova-3-monolingual",
                "Speechmatics": "speechmatics",
                "Gladia": "gladia",
                "Azure AI Speech Batch": "azure-ai-speech-batch",
                "Azure AI Speech Realtime": "azure-ai-speech-realtime"
            }
            
            provider_key = None
            for name, key in provider_map.items():
                if name in provider_text:
                    provider_key = key
                    break
            
            if provider_key:
                cost_info = self.audio_processor.estimate_cost(duration, provider_key)
                self.cost_label.setText(f"Estimated cost: ${cost_info['cost']:.4f} ({cost_info['price_per_unit']:.4f}/${cost_info['unit']})")
                if cost_info['cost'] == 0:
                    self.cost_label.setStyleSheet("font-weight: bold; color: green;")
                else:
                    self.cost_label.setStyleSheet("font-weight: bold; color: orange;")
            else:
                self.cost_label.setText("Estimated cost: $0.00 (Local)")
                self.cost_label.setStyleSheet("font-weight: bold; color: green;")
                
        except Exception as e:
            self.cost_label.setText(f"Cost estimation error: {str(e)}")
            self.cost_label.setStyleSheet("color: red;")

    def update_installed_models(self):
        """Update the list of installed local models"""
        try:
            if not self.audio_processor:
                from core.audio_processor import AudioProcessor
                self.audio_processor = AudioProcessor(self.config_manager)
            
            installed = self.audio_processor.get_installed_models()
            if installed:
                self.installed_models_list.setText("\n".join([f"✓ {model}" for model in installed]))
            else:
                self.installed_models_list.setText("No local models installed")
        except Exception as e:
            self.installed_models_list.setText(f"Error checking models: {str(e)}")

    def download_model(self):
        """Download selected model"""
        model_text = self.model_download_combo.currentText()
        model_name = model_text.split()[0]  # Extract model name before size info
        
        try:
            if not self.audio_processor:
                from core.audio_processor import AudioProcessor
                self.audio_processor = AudioProcessor(self.config_manager)
            
            if self.audio_processor.is_model_installed(model_name):
                QMessageBox.information(self, "Model Already Installed", 
                                      f"Model '{model_name}' is already installed.")
                return
            
            self.download_model_btn.setEnabled(False)
            self.model_progress.setVisible(True)
            self.model_progress.setValue(0)
            self.model_status_label.setText(f"Downloading {model_name}...")
            
            def progress_callback(current, total, status):
                progress = int((current / total) * 100)
                self.model_progress.setValue(progress)
                self.model_status_label.setText(status)
                QApplication.processEvents()
            
            success = self.audio_processor.download_model(model_name, progress_callback)
            
            if success:
                self.model_status_label.setText(f"✓ Model {model_name} downloaded successfully!")
                self.update_installed_models()
                QMessageBox.information(self, "Download Complete", 
                                      f"Model '{model_name}' has been downloaded successfully.")
            else:
                self.model_status_label.setText(f"✗ Failed to download {model_name}")
                QMessageBox.warning(self, "Download Failed", 
                                  f"Failed to download model '{model_name}'. Check the log for details.")
            
        except Exception as e:
            self.model_status_label.setText(f"✗ Error: {str(e)}")
            QMessageBox.critical(self, "Download Error", f"Error downloading model: {str(e)}")
        finally:
            self.download_model_btn.setEnabled(True)
            self.model_progress.setVisible(False)

    def delete_model(self):
        """Delete selected model"""
        model_text = self.model_download_combo.currentText()
        model_name = model_text.split()[0]
        
        try:
            if not self.audio_processor:
                from core.audio_processor import AudioProcessor
                self.audio_processor = AudioProcessor(self.config_manager)
            
            if not self.audio_processor.is_model_installed(model_name):
                QMessageBox.information(self, "Model Not Installed", 
                                      f"Model '{model_name}' is not installed.")
                return
            
            reply = QMessageBox.question(self, "Delete Model", 
                                       f"Are you sure you want to delete model '{model_name}'?",
                                       QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                success = self.audio_processor.delete_model(model_name)
                if success:
                    self.model_status_label.setText(f"✓ Model {model_name} deleted successfully!")
                    self.update_installed_models()
                    QMessageBox.information(self, "Delete Complete", 
                                          f"Model '{model_name}' has been deleted.")
                else:
                    QMessageBox.warning(self, "Delete Failed", 
                                      f"Failed to delete model '{model_name}'.")
        except Exception as e:
            QMessageBox.critical(self, "Delete Error", f"Error deleting model: {str(e)}")

    def browse_subtitle_output(self):
        """Browse for subtitle output directory"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", "")
        if directory:
            self.subtitle_output_edit.setText(directory)

    def start_transcription(self):
        """Start the transcription process"""
        if not self.audio_file_edit.text():
            QMessageBox.warning(self, "No Audio File", "Please select an audio file first.")
            return
        
        if not self.subtitle_output_edit.text():
            QMessageBox.warning(self, "No Output Directory", "Please select an output directory.")
            return
        
        try:
            self.transcribe_btn.setEnabled(False)
            self.stop_transcription_btn.setEnabled(True)
            self.transcription_progress.setValue(0)
            self.transcription_status.setText("Starting transcription...")
            
            # Start transcription in a separate thread
            from PyQt5.QtCore import QThread, pyqtSignal
            
            class TranscriptionThread(QThread):
                progress_updated = pyqtSignal(int, str)
                transcription_complete = pyqtSignal(object, str)
                error_occurred = pyqtSignal(str)
                
                def __init__(self, processor, audio_file, provider, options):
                    super().__init__()
                    self.processor = processor
                    self.audio_file = audio_file
                    self.provider = provider
                    self.options = options
                
                def run(self):
                    try:
                        self.progress_updated.emit(25, "Initializing...")
                        
                        # Create progress callback for local models
                        def progress_callback(percent, message):
                            self.progress_updated.emit(percent, message)
                        
                        # Add progress callback to options if using faster-whisper
                        if "Faster-Whisper" in self.provider:
                            self.options['progress_callback'] = progress_callback
                        
                        # Determine provider
                        provider_text = self.provider
                        if "OpenAI" in provider_text:
                            provider_key = "openai-whisper"
                        elif "Faster-Whisper" in provider_text:
                            # Extract model name from text like "Faster-Whisper Tiny (Free)"
                            if "Tiny" in provider_text:
                                model_name = "tiny"
                            elif "Base" in provider_text:
                                model_name = "base"
                            elif "Small" in provider_text:
                                model_name = "small"
                            elif "Medium" in provider_text:
                                model_name = "medium"
                            elif "Large-V1" in provider_text:
                                model_name = "large-v1"
                            elif "Large-V2" in provider_text:
                                model_name = "large-v2"
                            else:
                                model_name = "base"  # default fallback
                            
                            provider_key = f"faster-whisper-{model_name}"
                        else:
                            raise ValueError(f"Unsupported provider: {provider_text}")
                        
                        if "Faster-Whisper" not in provider_text:
                            self.progress_updated.emit(50, "Transcribing audio...")
                        
                        # Perform transcription
                        result = self.processor.transcribe_audio(self.audio_file, provider_key, **self.options)
                        
                        self.progress_updated.emit(90, "Transcription complete")
                        self.transcription_complete.emit(result, provider_key)
                        
                    except Exception as e:
                        self.error_occurred.emit(str(e))
            
            if not self.audio_processor:
                from core.audio_processor import AudioProcessor
                self.audio_processor = AudioProcessor(self.config_manager)
            
            # Prepare transcription options
            options = {}
            if self.audio_language_combo.currentText() != "Auto-detect":
                options['language'] = self.audio_language_combo.currentText().lower()
            
            # Add local model settings if using faster-whisper
            provider_text = self.audio_provider_combo.currentText()
            if "Faster-Whisper" in provider_text:
                options['compute_type'] = self.compute_type_combo.currentText()
                options['device'] = self.device_combo.currentText()
                options['beam_size'] = self.beam_size_spin.value()
                options['temperature'] = self.temperature_spin.value()
                options['vad_filter'] = self.vad_filter_check.isChecked()
                options['word_timestamps'] = self.word_timestamps_check.isChecked()
            
            # Start transcription thread
            self.transcription_thread = TranscriptionThread(
                self.audio_processor,
                self.audio_file_edit.text(),
                self.audio_provider_combo.currentText(),
                options
            )
            
            self.transcription_thread.progress_updated.connect(self.update_transcription_progress)
            self.transcription_thread.transcription_complete.connect(self.on_transcription_complete)
            self.transcription_thread.error_occurred.connect(self.on_transcription_error)
            self.transcription_thread.start()
            
        except Exception as e:
            self.on_transcription_error(str(e))

    def update_transcription_progress(self, value, status):
        """Update transcription progress"""
        self.transcription_progress.setValue(value)
        self.transcription_status.setText(status)
        
        # Update time estimation if status contains timing info
        if "elapsed" in status or "remaining" in status:
            self.transcription_time_label.setText(status)
        elif value == 100:
            self.transcription_time_label.setText("Transcription completed!")

    def on_transcription_complete(self, result, provider):
        """Handle completed transcription"""
        try:
            # Display preview
            self.transcription_preview.setText(result.text)
            
            # Save files
            output_dir = self.subtitle_output_edit.text()
            base_name = os.path.splitext(os.path.basename(self.audio_file_edit.text()))[0]
            
            # Save raw text if requested
            if self.save_raw_check.isChecked():
                raw_path = os.path.join(output_dir, f"{base_name}_raw.txt")
                with open(raw_path, 'w', encoding='utf-8') as f:
                    f.write(result.text)
                self.log_message(f"Raw transcription saved to: {raw_path}")
            
            # Translate if requested
            final_result = result
            if self.audio_translate_check.isChecked():
                self.transcription_status.setText("Translating...")
                self.transcription_progress.setValue(95)
                QApplication.processEvents()
                
                # Get target language from main config
                config = self.config_manager.get_config()
                target_lang = config.get('target_language', 'english')
                final_result = self.audio_processor.translate_subtitles(result, target_lang)
            
            # Save subtitles
            subtitle_format = self.subtitle_format_combo.currentText().lower()
            subtitle_path = os.path.join(output_dir, f"{base_name}.{subtitle_format}")
            
            # Pass source file path for resolution detection in ASS format
            source_file = self.audio_file_edit.text()
            
            # Get ASS settings if ASS format is selected
            if subtitle_format == "ass":
                auto_resolution = self.auto_resolution_check.isChecked()
                manual_font_size = self.manual_font_spin.value()
                success = self.audio_processor.save_subtitles(final_result, subtitle_path, subtitle_format, 
                                                            source_file, auto_resolution, manual_font_size)
            else:
                success = self.audio_processor.save_subtitles(final_result, subtitle_path, subtitle_format, source_file)
            
            if success:
                self.transcription_status.setText("✓ Transcription completed successfully!")
                self.transcription_progress.setValue(100)
                self.log_message(f"Subtitles saved to: {subtitle_path}")
                QMessageBox.information(self, "Transcription Complete", 
                                      f"Transcription completed successfully!\nOutput saved to: {subtitle_path}")
            else:
                self.transcription_status.setText("✗ Error saving subtitles")
                QMessageBox.warning(self, "Save Error", "Error saving subtitle files.")
                
        except Exception as e:
            self.on_transcription_error(str(e))
        finally:
            self.transcribe_btn.setEnabled(True)
            self.stop_transcription_btn.setEnabled(False)

    def on_transcription_error(self, error_msg):
        """Handle transcription error"""
        self.transcription_status.setText(f"✗ Error: {error_msg}")
        self.transcription_progress.setValue(0)
        self.transcribe_btn.setEnabled(True)
        self.stop_transcription_btn.setEnabled(False)
        self.log_message(f"Transcription error: {error_msg}")
        QMessageBox.critical(self, "Transcription Error", f"Error during transcription:\n{error_msg}")

    def stop_transcription(self):
        """Stop the transcription process"""
        if hasattr(self, 'transcription_thread') and self.transcription_thread.isRunning():
            self.transcription_thread.terminate()
            self.transcription_thread.wait()
        
        self.transcription_status.setText("Transcription stopped")
        self.transcription_progress.setValue(0)
        self.transcribe_btn.setEnabled(True)
        self.stop_transcription_btn.setEnabled(False)

    # ==================== LOCAL MODELS METHODS ====================
    
    def refresh_local_models(self):
        """Refresh the list of available and installed models"""
        try:
            if not self.llamacpp_client:
                from core.llamacpp_client import LlamaCppClient
                self.llamacpp_client = LlamaCppClient(self.config_manager)
            
            # Clear lists
            self.available_models_list.clear()
            self.installed_models_list.clear()
            self.test_model_combo.clear()
            
            # Populate available models
            for model_key, model_info in self.llamacpp_client.available_models.items():
                display_text = f"{model_info['name']} ({model_info['size']}) - {model_info['description']}"
                self.available_models_list.addItem(display_text)
                self.available_models_list.item(self.available_models_list.count() - 1).setData(Qt.UserRole, model_key)
            
            # Populate installed models
            installed = self.llamacpp_client.get_installed_models()
            for model_name in installed:
                self.installed_models_list.addItem(model_name)
                self.test_model_combo.addItem(model_name)
            
            self.local_status_label.setText(f"Ready - {len(installed)} models installed")
            
            # Connect selection handlers
            self.available_models_list.itemClicked.connect(self.on_available_model_selected)
            self.installed_models_list.itemClicked.connect(self.on_installed_model_selected)
            
        except Exception as e:
            self.local_status_label.setText(f"Error: {e}")
            self.log_message(f"Error refreshing local models: {e}")

    def on_available_model_selected(self, item):
        """Handle selection of available model"""
        model_key = item.data(Qt.UserRole)
        if model_key and model_key in self.llamacpp_client.available_models:
            model_info = self.llamacpp_client.available_models[model_key]
            info_text = f"""
Model: {model_info['name']}
Size: {model_info['size']}
Description: {model_info['description']}
Status: {'Installed' if self.llamacpp_client.is_model_installed(model_key) else 'Available for download'}
"""
            self.model_info_label.setText(info_text.strip())

    def on_installed_model_selected(self, item):
        """Handle selection of installed model"""
        model_name = item.text()
        info_text = f"""
Model: {model_name}
Status: Installed and ready to use
Location: models/llamacpp/{model_name}.gguf
"""
        self.model_info_label.setText(info_text.strip())

    def download_selected_model(self):
        """Download the selected model"""
        current_item = self.available_models_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a model to download.")
            return
        
        model_key = current_item.data(Qt.UserRole)
        if not model_key:
            return
        
        # Check if already installed
        if self.llamacpp_client.is_model_installed(model_key):
            QMessageBox.information(self, "Already Installed", f"Model {model_key} is already installed.")
            return
        
        try:
            self.download_model_btn.setEnabled(False)
            self.local_progress_bar.setVisible(True)
            self.local_progress_bar.setValue(0)
            
            # Start download in thread
            from PyQt5.QtCore import QThread, pyqtSignal
            
            class DownloadThread(QThread):
                progress_updated = pyqtSignal(int, str)
                download_complete = pyqtSignal(bool, str)
                
                def __init__(self, client, model_key):
                    super().__init__()
                    self.client = client
                    self.model_key = model_key
                
                def run(self):
                    def progress_callback(percent, message):
                        self.progress_updated.emit(percent, message)
                    
                    try:
                        success = self.client.download_model(self.model_key, progress_callback)
                        self.download_complete.emit(success, "Download completed successfully" if success else "Download failed")
                    except Exception as e:
                        self.download_complete.emit(False, str(e))
            
            self.download_thread = DownloadThread(self.llamacpp_client, model_key)
            self.download_thread.progress_updated.connect(self.update_download_progress)
            self.download_thread.download_complete.connect(self.on_download_complete)
            self.download_thread.start()
            
        except Exception as e:
            self.on_download_complete(False, str(e))

    def update_download_progress(self, percent, message):
        """Update download progress"""
        self.local_progress_bar.setValue(percent)
        self.local_status_label.setText(message)

    def on_download_complete(self, success, message):
        """Handle download completion"""
        self.local_progress_bar.setVisible(False)
        self.download_model_btn.setEnabled(True)
        
        if success:
            self.local_status_label.setText("Download completed successfully")
            self.refresh_local_models()
            QMessageBox.information(self, "Download Complete", "Model downloaded successfully!")
        else:
            self.local_status_label.setText(f"Download failed: {message}")
            QMessageBox.critical(self, "Download Failed", f"Failed to download model:\n{message}")

    def load_selected_model(self):
        """Load the selected model for testing"""
        model_name = self.test_model_combo.currentText()
        if not model_name:
            QMessageBox.warning(self, "No Model", "Please select a model to load.")
            return
        
        try:
            self.load_model_btn.setEnabled(False)
            self.local_status_label.setText("Loading model...")
            
            # Load model with current settings
            success = self.llamacpp_client.load_model(
                model_name,
                n_ctx=self.local_ctx_spin.value(),
                n_threads=self.threads_spin.value(),
                n_gpu_layers=self.gpu_layers_spin.value()
            )
            
            if success:
                self.local_status_label.setText(f"Model loaded: {model_name}")
                self.test_translate_btn.setEnabled(True)
                self.unload_model_btn.setEnabled(True)
                self.load_model_btn.setText("🔄 Reload Model")
            else:
                self.local_status_label.setText("Failed to load model")
                QMessageBox.critical(self, "Load Failed", "Failed to load the model.")
            
        except Exception as e:
            self.local_status_label.setText(f"Error: {e}")
            QMessageBox.critical(self, "Load Error", f"Error loading model:\n{e}")
        finally:
            self.load_model_btn.setEnabled(True)

    def unload_current_model(self):
        """Unload the current model"""
        try:
            self.llamacpp_client.unload_model()
            self.local_status_label.setText("Model unloaded")
            self.test_translate_btn.setEnabled(False)
            self.unload_model_btn.setEnabled(False)
            self.load_model_btn.setText("🔄 Load Model")
        except Exception as e:
            QMessageBox.critical(self, "Unload Error", f"Error unloading model:\n{e}")

    def test_translation(self):
        """Test translation with the loaded model"""
        if not self.test_input.toPlainText().strip():
            QMessageBox.warning(self, "No Input", "Please enter text to translate.")
            return
        
        try:
            self.test_translate_btn.setEnabled(False)
            self.local_status_label.setText("Translating...")
            
            text = self.test_input.toPlainText().strip()
            target_lang = self.test_target_combo.currentText()
            
            # Perform translation
            result = self.llamacpp_client.translate_text(
                text, 
                target_lang,
                temperature=self.local_temp_spin.value()
            )
            
            self.test_output.setPlainText(result)
            self.local_status_label.setText("Translation completed")
            
        except Exception as e:
            self.local_status_label.setText(f"Translation error: {e}")
            QMessageBox.critical(self, "Translation Error", f"Error during translation:\n{e}")
        finally:
            self.test_translate_btn.setEnabled(True)
    
    # Character Tab Methods
    def update_style_preview(self):
        """Update character style preview"""
        style = self.char_style_combo.currentText()
        previews = {
            "Japanese": "Japanese style characters with names like Akira, Sakura, Yuki. Traditional Japanese aesthetics, anime/manga inspired features.",
            "Korean": "Korean style characters with names like Min-jun, So-young, Hae-won. Modern K-drama aesthetics, fashionable appearance.",
            "Chinese": "Chinese style characters with names like Wei Lin, Mei Ling, Chen. Traditional and modern Chinese cultural elements.",
            "Fantasy": "Fantasy characters with mystical names like Lyraleth, Thorven, Zephyr. Magic-inspired features, mythical aesthetics.",
            "Western": "Western style characters with names like Emily, Alexander, Sarah. Contemporary or historical Western appearance."
        }
        self.style_preview_label.setText(previews.get(style, ""))
    
    def generate_character(self):
        """Generate a new character using AI"""
        try:
            if not self.novel_assistant:
                from core.novel_assistant import NovelAssistant
                from core.api_client import APIClient
                api_client = APIClient(self.config.get("provider_config", {}))
                self.novel_assistant = NovelAssistant(api_client)
            
            # Gather requirements
            style = self.char_style_combo.currentText()
            age = self.char_age_edit.text()
            gender = self.char_gender_combo.currentText()
            occupation = self.char_occupation_edit.text()
            personality = self.char_personality_edit.text()
            custom = self.char_custom_edit.toPlainText()
            
            requirements = {
                "style": style,
                "age": age if age else "any",
                "gender": gender if gender != "Any" else "any",
                "occupation": occupation if occupation else "any",
                "personality": personality if personality else "varied",
                "custom": custom if custom else "none"
            }
            
            self.generate_char_btn.setText("🔄 Generating...")
            self.generate_char_btn.setEnabled(False)
            
            # Generate character
            character = self.novel_assistant.generate_character(requirements)
            
            if character:
                self.current_character = character
                self.display_character(character)
                self.save_char_btn.setEnabled(True)
                self.log_message(f"Generated character: {character.name}")
            else:
                self.log_message("Failed to generate character", "error")
            
        except Exception as e:
            self.log_message(f"Error generating character: {str(e)}", "error")
        finally:
            self.generate_char_btn.setText("🎲 Generate Character")
            self.generate_char_btn.setEnabled(True)
    
    def display_character(self, character):
        """Display character details"""
        self.char_name_display.setText(character.name)
        self.char_personality_display.setText(character.personality)
        self.char_appearance_display.setText(character.appearance)
        self.char_background_display.setText(character.background)
        
        # Display custom fields
        custom_text = ""
        for field, value in character.custom_fields.items():
            custom_text += f"{field}: {value}\n\n"
        self.char_custom_display.setText(custom_text.strip())
    
    def save_character(self):
        """Save current character"""
        if not self.current_character:
            return
        
        try:
            if not self.novel_db:
                from core.novel_models import NovelDatabase
                self.novel_db = NovelDatabase()
            
            self.novel_db.save_character(self.current_character)
            self.log_message(f"Character '{self.current_character.name}' saved")
            self.refresh_saved_characters()
            
        except Exception as e:
            self.log_message(f"Error saving character: {str(e)}", "error")
    
    def load_character(self):
        """Load selected character"""
        current_item = self.saved_chars_list.currentItem()
        if not current_item:
            return
        
        char_id = current_item.data(0x0100)  # Qt.UserRole
        self.load_character_by_id(char_id)
    
    def load_selected_character(self, item):
        """Load character when double-clicked"""
        char_id = item.data(0x0100)  # Qt.UserRole
        self.load_character_by_id(char_id)
    
    def load_character_by_id(self, char_id):
        """Load character by ID"""
        try:
            if not self.novel_db:
                from core.novel_models import NovelDatabase
                self.novel_db = NovelDatabase()
            
            character = self.novel_db.get_character(char_id)
            if character:
                self.current_character = character
                self.display_character(character)
                self.save_char_btn.setEnabled(True)
                self.log_message(f"Loaded character: {character.name}")
            
        except Exception as e:
            self.log_message(f"Error loading character: {str(e)}", "error")
    
    def new_character(self):
        """Start creating a new character"""
        self.current_character = None
        self.char_name_display.clear()
        self.char_personality_display.clear()
        self.char_appearance_display.clear()
        self.char_background_display.clear()
        self.char_custom_display.clear()
        self.save_char_btn.setEnabled(False)
        
        # Clear input fields
        self.char_age_edit.clear()
        self.char_gender_combo.setCurrentIndex(0)
        self.char_occupation_edit.clear()
        self.char_personality_edit.clear()
        self.char_custom_edit.clear()
    
    def refresh_saved_characters(self):
        """Refresh the list of saved characters"""
        self.saved_chars_list.clear()
        
        try:
            if not self.novel_db:
                from core.novel_models import NovelDatabase
                self.novel_db = NovelDatabase()
            
            characters = self.novel_db.get_all_characters()
            for character in characters:
                item = QListWidgetItem(f"{character.name} ({character.style})")
                item.setData(0x0100, character.id)  # Qt.UserRole
                self.saved_chars_list.addItem(item)
                
        except Exception as e:
            self.log_message(f"Error loading characters: {str(e)}", "error")
    
    # Novel Writing Tab Methods
    def create_new_project(self):
        """Create a new novel project"""
        from PyQt5.QtWidgets import QInputDialog
        
        title, ok = QInputDialog.getText(self, "New Project", "Project Title:")
        if not ok or not title.strip():
            return
        
        description, ok = QInputDialog.getMultiLineText(self, "New Project", "Project Description:")
        if not ok:
            description = ""
        
        try:
            if not self.novel_db:
                from core.novel_models import NovelDatabase
                self.novel_db = NovelDatabase()
            
            from core.novel_models import Project
            project = Project(
                title=title.strip(),
                description=description.strip(),
                genre="",
                style="",
                target_length=""
            )
            
            self.novel_db.save_project(project)
            self.log_message(f"Created project: {title}")
            self.refresh_projects()
            
            # Select the new project
            index = self.novel_project_combo.findText(title)
            if index >= 0:
                self.novel_project_combo.setCurrentIndex(index)
                
        except Exception as e:
            self.log_message(f"Error creating project: {str(e)}", "error")
    
    def load_novel_project(self, project_title):
        """Load selected project"""
        if not project_title or project_title == "Select Project...":
            self.current_project = None
            self.project_info_label.setText("No project selected")
            self.active_chars_list.clear()
            return
        
        try:
            if not self.novel_db:
                from core.novel_models import NovelDatabase
                self.novel_db = NovelDatabase()
            
            projects = self.novel_db.get_all_projects()
            project = next((p for p in projects if p.title == project_title), None)
            
            if project:
                self.current_project = project
                info_text = f"Title: {project.title}\n"
                if project.description:
                    info_text += f"Description: {project.description}\n"
                if project.genre:
                    info_text += f"Genre: {project.genre}\n"
                self.project_info_label.setText(info_text.strip())
                
                self.load_project_characters()
                self.log_message(f"Loaded project: {project_title}")
            
        except Exception as e:
            self.log_message(f"Error loading project: {str(e)}", "error")
    
    def load_project_characters(self):
        """Load characters for current project"""
        self.active_chars_list.clear()
        
        if not self.current_project:
            return
        
        try:
            if not self.novel_db:
                from core.novel_models import NovelDatabase
                self.novel_db = NovelDatabase()
            
            characters = self.novel_db.get_all_characters()
            for character in characters:
                item = QListWidgetItem(character.name)
                item.setData(0x0100, character.id)  # Qt.UserRole
                self.active_chars_list.addItem(item)
                
        except Exception as e:
            self.log_message(f"Error loading characters: {str(e)}", "error")
    
    def add_active_character(self):
        """Add character to active list"""
        # This would open a dialog to select from saved characters
        self.load_project_characters()
    
    def remove_active_character(self):
        """Remove character from active list"""
        current_item = self.active_chars_list.currentItem()
        if current_item:
            self.active_chars_list.takeItem(self.active_chars_list.row(current_item))
    
    def generate_writing(self):
        """Generate text using AI assistance"""
        try:
            if not self.novel_assistant:
                from core.novel_assistant import NovelAssistant
                from core.api_client import APIClient
                api_client = APIClient(self.config.get("provider_config", {}))
                self.novel_assistant = NovelAssistant(api_client)
            
            mode = self.writing_mode_combo.currentText()
            goal = self.writing_goal_edit.text()
            context = self.novel_context_edit.toPlainText()
            key_points = self.key_points_edit.toPlainText()
            current_text = self.novel_text_edit.toPlainText()
            
            # Get active characters
            active_chars = []
            for i in range(self.active_chars_list.count()):
                item = self.active_chars_list.item(i)
                char_id = item.data(0x0100)
                character = self.novel_db.get_character(char_id) if self.novel_db else None
                if character:
                    active_chars.append(character)
            
            self.generate_text_btn.setText("🔄 Generating...")
            self.generate_text_btn.setEnabled(False)
            
            # Generate based on mode
            generated_text = ""
            if mode == "Continue Story":
                generated_text = self.novel_assistant.continue_story(
                    current_text, context, active_chars, goal
                )
            elif mode == "Write Scene":
                generated_text = self.novel_assistant.write_scene(
                    goal, context, active_chars, key_points
                )
            elif mode == "Write Dialogue":
                generated_text = self.novel_assistant.write_dialogue(
                    active_chars, context, goal
                )
            elif mode == "Free Writing":
                generated_text = self.novel_assistant.continue_story(
                    current_text, f"{context}\n\nGoal: {goal}", active_chars
                )
            
            if generated_text:
                # Add generated text to writing area
                cursor = self.novel_text_edit.textCursor()
                cursor.movePosition(cursor.End)
                cursor.insertText("\n\n" + generated_text)
                self.novel_text_edit.setTextCursor(cursor)
                
                self.log_message(f"Generated {len(generated_text)} characters using {mode}")
            else:
                self.log_message("Failed to generate text", "error")
            
        except Exception as e:
            self.log_message(f"Error generating text: {str(e)}", "error")
        finally:
            self.generate_text_btn.setText("✨ Generate with AI")
            self.generate_text_btn.setEnabled(True)
    
    def update_word_count(self):
        """Update word count display"""
        text = self.novel_text_edit.toPlainText()
        word_count = len(text.split()) if text.strip() else 0
        self.word_count_label.setText(f"Words: {word_count}")
    
    def save_writing(self):
        """Save current writing session"""
        if not self.current_project:
            self.log_message("Please select a project first", "error")
            return
        
        try:
            if not self.novel_db:
                from core.novel_models import NovelDatabase
                self.novel_db = NovelDatabase()
            
            from core.novel_models import WritingSession
            import datetime
            
            session = WritingSession(
                project_id=self.current_project.id,
                content=self.novel_text_edit.toPlainText(),
                timestamp=datetime.datetime.now(),
                word_count=len(self.novel_text_edit.toPlainText().split())
            )
            
            self.novel_db.save_writing_session(session)
            self.log_message("Writing session saved")
            
        except Exception as e:
            self.log_message(f"Error saving writing: {str(e)}", "error")
    
    def export_writing(self):
        """Export writing to file"""
        from PyQt5.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Writing", f"{self.current_project.title if self.current_project else 'novel'}.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.novel_text_edit.toPlainText())
                self.log_message(f"Writing exported to {filename}")
            except Exception as e:
                self.log_message(f"Error exporting: {str(e)}", "error")
    
    def refresh_projects(self):
        """Refresh the list of projects"""
        self.novel_project_combo.clear()
        self.novel_project_combo.addItem("Select Project...")
        
        try:
            if not self.novel_db:
                from core.novel_models import NovelDatabase
                self.novel_db = NovelDatabase()
            
            projects = self.novel_db.get_all_projects()
            for project in projects:
                self.novel_project_combo.addItem(project.title)
                
        except Exception as e:
            self.log_message(f"Error loading projects: {str(e)}", "error")
