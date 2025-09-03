"""
Configuration Manager
Handles loading and saving application configuration
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_file: str = ".env"):
        self.config_file = config_file
        self.config: Dict[str, str] = {}
        self.load_default_config()
        
        # Load existing config if available
        if os.path.exists(config_file):
            self.load_config(config_file)
    
    def load_default_config(self):
        """Load default configuration values"""
        self.config = {
            'api': '',
            'key': '',
            'organization': '',
            'model': 'gpt-4',
            'language': 'English',
            'timeout': '120',
            'fileThreads': '1',
            'threads': '1',
            'width': '60',
            'listWidth': '100',
            'noteWidth': '75',
            'input_cost': '0.002',
            'output_cost': '0.002',
            'batchsize': '10',
            'frequency_penalty': '0.2'
        }
    
    def load_config(self, config_file: Optional[str] = None):
        """Load configuration from file"""
        if config_file is None:
            config_file = self.config_file
            
        try:
            load_dotenv(config_file)
            
            # Update config with loaded values
            for key in self.config.keys():
                value = os.getenv(key)
                if value is not None:
                    self.config[key] = value
                    
        except Exception as e:
            print(f"Error loading config: {e}")
    
    def save_config(self, config_dict: Optional[Dict[str, Any]] = None):
        """Save configuration to file"""
        if config_dict:
            self.config.update(config_dict)
        
        try:
            # Create .env file content
            with open(self.config_file, 'w', encoding='utf-8') as f:
                f.write("#API link, leave blank to use OpenAI API\n")
                f.write(f'api="{self.config.get("api", "")}"\n\n')
                
                f.write("#API key\n")
                f.write(f'key="{self.config.get("key", "")}"\n\n')
                
                f.write("#Organization key, make something up for self hosted or other API\n")
                f.write(f'organization="{self.config.get("organization", "")}"\n\n')
                
                f.write("#LLM model name\n")
                f.write(f'model="{self.config.get("model", "gpt-4")}"\n\n')
                
                f.write("#The language to translate TO\n")
                f.write(f'language="{self.config.get("language", "English")}"\n\n')
                
                f.write("#The timeout before disconnect error, 30 to 120 recommended\n")
                f.write(f'timeout="{self.config.get("timeout", "120")}"\n\n')
                
                f.write("#The number of files to translate at the same time\n")
                f.write(f'fileThreads="{self.config.get("fileThreads", "1")}"\n\n')
                
                f.write("#The number of threads per file\n")
                f.write(f'threads="{self.config.get("threads", "1")}"\n\n')
                
                f.write("#The wordwrap of dialogue text\n")
                f.write(f'width="{self.config.get("width", "60")}"\n\n')
                
                f.write("#The wordwrap of items and help text\n")
                f.write(f'listWidth="{self.config.get("listWidth", "100")}"\n\n')
                
                f.write("#The wordwrap of notes text\n")
                f.write(f'noteWidth="{self.config.get("noteWidth", "75")}"\n\n')
                
                f.write("# Custom input API cost\n")
                f.write(f'input_cost={self.config.get("input_cost", "0.002")}\n\n')
                
                f.write("# Custom output API cost\n")
                f.write(f'output_cost={self.config.get("output_cost", "0.002")}\n\n')
                
                f.write("# Batch size\n")
                f.write(f'batchsize="{self.config.get("batchsize", "10")}"\n\n')
                
                f.write("# Frequency penalty\n")
                f.write(f'frequency_penalty={self.config.get("frequency_penalty", "0.2")}\n')
                
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return self.config.copy()
    
    def get_value(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get specific configuration value"""
        return self.config.get(key, default)
    
    def set_value(self, key: str, value: Any):
        """Set specific configuration value"""
        self.config[key] = str(value)
    
    def validate_config(self) -> tuple[bool, str]:
        """Validate configuration"""
        if not self.config.get('key'):
            return False, "API key is required"
        
        if not self.config.get('model'):
            return False, "Model is required"
        
        try:
            timeout = int(self.config.get('timeout', 120))
            if timeout < 30 or timeout > 300:
                return False, "Timeout must be between 30 and 300 seconds"
        except ValueError:
            return False, "Timeout must be a valid number"
        
        try:
            threads = int(self.config.get('threads', 1))
            if threads < 1 or threads > 20:
                return False, "Threads must be between 1 and 20"
        except ValueError:
            return False, "Threads must be a valid number"
        
        return True, "Configuration is valid"
