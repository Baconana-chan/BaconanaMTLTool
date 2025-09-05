"""
GUI Configuration Manager
Handles loading and saving GUI-specific settings like tab visibility
"""

import json
import os
from typing import Dict, Any, Optional


class GUIConfigManager:
    """Manages GUI-specific configuration in JSON format"""
    
    def __init__(self, config_file: str = "gui_config.json"):
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        self.load_default_config()
        
        # Load existing config if available
        if os.path.exists(config_file):
            self.load_config()
    
    def load_default_config(self):
        """Load default GUI configuration values"""
        self.config = {
            'visible_tabs': {
                'config': True,
                'translation': True,
                'lightnovel': True,
                'audio': False,
                'character': False,
                'novel': False,
                'local': False,
                'cloud': False,
                'providers': True,
                'advanced': False,
                'settings': True,
                'documentation': True,
                'about': True,
                'log': True
            },
            'window': {
                'width': 1200,
                'height': 800,
                'maximized': False,
                'position_x': 100,
                'position_y': 100
            },
            'preferences': {
                'auto_save_tab_settings': True,
                'remember_last_tab': True,
                'theme': 'default',
                'font_size': 9
            }
        }
    
    def load_config(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                
            # Merge with defaults (in case new settings were added)
            self.merge_config(loaded_config)
                    
        except Exception as e:
            print(f"Error loading GUI config: {e}")
            print("Using default GUI configuration")
    
    def merge_config(self, loaded_config: Dict[str, Any]):
        """Merge loaded config with defaults to ensure all keys exist"""
        for section, section_data in self.config.items():
            if section in loaded_config:
                if isinstance(section_data, dict):
                    # Merge section-level dictionaries
                    for key, default_value in section_data.items():
                        if key in loaded_config[section]:
                            self.config[section][key] = loaded_config[section][key]
                        # If key doesn't exist in loaded config, keep default
                else:
                    # Direct value replacement
                    self.config[section] = loaded_config[section]
            # If section doesn't exist in loaded config, keep defaults
    
    def save_config(self):
        """Save configuration to JSON file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error saving GUI config: {e}")
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return self.config.copy()
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get specific configuration section"""
        return self.config.get(section, {}).copy()
    
    def get_value(self, section: str, key: str, default: Any = None) -> Any:
        """Get specific configuration value"""
        return self.config.get(section, {}).get(key, default)
    
    def set_value(self, section: str, key: str, value: Any):
        """Set specific configuration value"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
    
    def set_section(self, section: str, data: Dict[str, Any]):
        """Set entire configuration section"""
        self.config[section] = data
    
    def get_visible_tabs(self) -> Dict[str, bool]:
        """Get tab visibility settings"""
        return self.get_section('visible_tabs')
    
    def set_visible_tabs(self, visible_tabs: Dict[str, bool]):
        """Set tab visibility settings"""
        self.set_section('visible_tabs', visible_tabs)
        
    def get_window_settings(self) -> Dict[str, Any]:
        """Get window settings"""
        return self.get_section('window')
    
    def set_window_settings(self, window_settings: Dict[str, Any]):
        """Set window settings"""
        self.set_section('window', window_settings)
        
    def get_preferences(self) -> Dict[str, Any]:
        """Get user preferences"""
        return self.get_section('preferences')
    
    def set_preferences(self, preferences: Dict[str, Any]):
        """Set user preferences"""
        self.set_section('preferences', preferences)
