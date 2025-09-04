"""
Llama.cpp Client - Interface for local LLM models via llama.cpp
"""

import os
import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import requests
import time
import threading

try:
    from llama_cpp import Llama
    LLAMACPP_AVAILABLE = True
except ImportError:
    LLAMACPP_AVAILABLE = False


class LlamaCppClient:
    """Client for llama.cpp models"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        self.models_dir = Path("models/llamacpp")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Currently loaded model
        self.current_model = None
        self.current_model_path = None
        
        # Popular GGUF models with download links
        self.available_models = {
            "llama-3.2-1b-instruct": {
                "name": "Llama 3.2 1B Instruct",
                "size": "1.3GB",
                "url": "https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf",
                "description": "Small, fast model good for basic tasks"
            },
            "llama-3.2-3b-instruct": {
                "name": "Llama 3.2 3B Instruct", 
                "size": "2.0GB",
                "url": "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf",
                "description": "Balanced model for general use"
            },
            "llama-3.1-8b-instruct": {
                "name": "Llama 3.1 8B Instruct",
                "size": "4.9GB", 
                "url": "https://huggingface.co/bartowski/Meta-Llama-3.1-8B-Instruct-GGUF/resolve/main/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
                "description": "High quality model for complex tasks"
            },
            "qwen2.5-7b-instruct": {
                "name": "Qwen2.5 7B Instruct",
                "size": "4.4GB",
                "url": "https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF/resolve/main/Qwen2.5-7B-Instruct-Q4_K_M.gguf", 
                "description": "Multilingual model with good reasoning"
            },
            "mistral-7b-instruct": {
                "name": "Mistral 7B Instruct v0.3",
                "size": "4.1GB",
                "url": "https://huggingface.co/bartowski/Mistral-7B-Instruct-v0.3-GGUF/resolve/main/Mistral-7B-Instruct-v0.3-Q4_K_M.gguf",
                "description": "Fast and efficient instruction-following model"
            },
            "gemma-2-9b-instruct": {
                "name": "Gemma 2 9B Instruct",
                "size": "5.4GB", 
                "url": "https://huggingface.co/bartowski/gemma-2-9b-it-GGUF/resolve/main/gemma-2-9b-it-Q4_K_M.gguf",
                "description": "Google's high-performance model"
            }
        }

    def is_available(self) -> bool:
        """Check if llama.cpp is available"""
        return LLAMACPP_AVAILABLE

    def get_installed_models(self) -> List[str]:
        """Get list of installed GGUF models"""
        installed = []
        for model_file in self.models_dir.glob("*.gguf"):
            model_name = model_file.stem
            installed.append(model_name)
        return installed

    def is_model_installed(self, model_key: str) -> bool:
        """Check if a specific model is installed"""
        if model_key in self.available_models:
            model_file = f"{model_key}.gguf"
        else:
            model_file = f"{model_key}.gguf"
        
        model_path = self.models_dir / model_file
        return model_path.exists()

    def download_model(self, model_key: str, progress_callback=None) -> bool:
        """Download a model"""
        if model_key not in self.available_models:
            self.logger.error(f"Unknown model: {model_key}")
            return False
        
        model_info = self.available_models[model_key]
        model_file = f"{model_key}.gguf"
        model_path = self.models_dir / model_file
        
        if model_path.exists():
            self.logger.info(f"Model {model_key} already exists")
            return True
        
        try:
            if progress_callback:
                progress_callback(0, f"Starting download of {model_info['name']} ({model_info['size']})")
            
            self.logger.info(f"Downloading {model_info['name']} from {model_info['url']}")
            
            response = requests.get(model_info['url'], stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(model_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            mb_downloaded = downloaded / (1024 * 1024)
                            mb_total = total_size / (1024 * 1024)
                            progress_callback(progress, f"Downloaded {mb_downloaded:.1f}MB / {mb_total:.1f}MB")
            
            if progress_callback:
                progress_callback(100, f"Download completed: {model_info['name']}")
            
            self.logger.info(f"Successfully downloaded {model_info['name']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error downloading model {model_key}: {e}")
            if model_path.exists():
                model_path.unlink()  # Remove partial download
            return False

    def load_model(self, model_key: str, **kwargs) -> bool:
        """Load a model for inference"""
        if not LLAMACPP_AVAILABLE:
            raise ImportError("llama-cpp-python not available. Install with: pip install llama-cpp-python")
        
        if model_key in self.available_models:
            model_file = f"{model_key}.gguf"
        else:
            model_file = f"{model_key}.gguf"
        
        model_path = self.models_dir / model_file
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model {model_key} not found. Please download it first.")
        
        # If model is already loaded, don't reload
        if self.current_model and self.current_model_path == str(model_path):
            return True
        
        try:
            # Unload current model
            if self.current_model:
                del self.current_model
                self.current_model = None
            
            # Load new model
            self.logger.info(f"Loading model from {model_path}")
            
            # Default parameters
            model_params = {
                'model_path': str(model_path),
                'n_ctx': kwargs.get('n_ctx', 4096),  # Context length
                'n_threads': kwargs.get('n_threads', -1),  # -1 = auto
                'n_gpu_layers': kwargs.get('n_gpu_layers', 0),  # GPU layers (0 = CPU only)
                'verbose': False
            }
            
            self.current_model = Llama(**model_params)
            self.current_model_path = str(model_path)
            
            self.logger.info(f"Successfully loaded model {model_key}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading model {model_key}: {e}")
            self.current_model = None
            self.current_model_path = None
            return False

    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using the loaded model"""
        if not self.current_model:
            raise RuntimeError("No model loaded. Load a model first with load_model()")
        
        try:
            # Generation parameters
            generation_params = {
                'max_tokens': kwargs.get('max_tokens', 2048),
                'temperature': kwargs.get('temperature', 0.7),
                'top_p': kwargs.get('top_p', 0.9),
                'top_k': kwargs.get('top_k', 40),
                'repeat_penalty': kwargs.get('repeat_penalty', 1.1),
                'stop': kwargs.get('stop', [])
            }
            
            response = self.current_model(prompt, **generation_params)
            
            if isinstance(response, dict) and 'choices' in response:
                return response['choices'][0]['text']
            else:
                return str(response)
                
        except Exception as e:
            self.logger.error(f"Error generating text: {e}")
            raise

    def translate_text(self, text: str, target_language: str, source_language: str = "auto", **kwargs) -> str:
        """Translate text using the loaded model"""
        if not self.current_model:
            raise RuntimeError("No model loaded. Load a model first with load_model()")
        
        # Create translation prompt
        if source_language == "auto":
            prompt = f"""Translate the following text to {target_language}. Only return the translation, no explanations:

Text to translate: {text}

Translation:"""
        else:
            prompt = f"""Translate the following text from {source_language} to {target_language}. Only return the translation, no explanations:

Text to translate: {text}

Translation:"""
        
        try:
            # Use lower temperature for more consistent translations
            translation_params = {
                'max_tokens': kwargs.get('max_tokens', 1024),
                'temperature': kwargs.get('temperature', 0.3),
                'top_p': kwargs.get('top_p', 0.9),
                'stop': kwargs.get('stop', ['\n\n', 'Text to translate:', 'Translation:'])
            }
            
            response = self.current_model(prompt, **translation_params)
            
            if isinstance(response, dict) and 'choices' in response:
                result = response['choices'][0]['text'].strip()
            else:
                result = str(response).strip()
            
            # Clean up the response
            if result.startswith("Translation:"):
                result = result[12:].strip()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error translating text: {e}")
            raise

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the currently loaded model"""
        if not self.current_model:
            return {"status": "no_model_loaded"}
        
        return {
            "status": "loaded",
            "model_path": self.current_model_path,
            "model_name": Path(self.current_model_path).stem if self.current_model_path else None
        }

    def unload_model(self):
        """Unload the current model to free memory"""
        if self.current_model:
            del self.current_model
            self.current_model = None
            self.current_model_path = None
            self.logger.info("Model unloaded")
