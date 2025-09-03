"""
Cloud AI Client - Support for Hugging Face, vLLM, and cloud platforms
"""

import requests
import json
import logging
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import asyncio
import aiohttp


@dataclass
class CloudConfig:
    """Configuration for cloud AI services"""
    provider: str
    endpoint_url: str
    api_key: Optional[str] = None
    model_name: str = ""
    timeout: int = 300  # 5 minutes default
    max_retries: int = 3


class CloudAIClient:
    """Client for various cloud AI services"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 300
        
    def create_huggingface_client(self, model_name: str, api_key: Optional[str] = None) -> CloudConfig:
        """Create Hugging Face Inference API client"""
        return CloudConfig(
            provider="huggingface",
            endpoint_url=f"https://api-inference.huggingface.co/models/{model_name}",
            api_key=api_key or os.getenv("HUGGINGFACE_API_TOKEN"),
            model_name=model_name
        )
    
    def create_vllm_client(self, endpoint_url: str, model_name: str) -> CloudConfig:
        """Create vLLM server client"""
        return CloudConfig(
            provider="vllm",
            endpoint_url=endpoint_url.rstrip('/') + '/v1/chat/completions',
            model_name=model_name
        )
    
    def create_colab_client(self, ngrok_url: str, model_name: str = "custom") -> CloudConfig:
        """Create Google Colab client via ngrok tunnel"""
        return CloudConfig(
            provider="colab",
            endpoint_url=ngrok_url.rstrip('/') + '/v1/chat/completions',
            model_name=model_name
        )
    
    def create_kaggle_client(self, endpoint_url: str, api_key: Optional[str] = None, 
                           model_name: str = "custom") -> CloudConfig:
        """Create Kaggle client"""
        return CloudConfig(
            provider="kaggle",
            endpoint_url=endpoint_url.rstrip('/') + '/v1/chat/completions',
            api_key=api_key,
            model_name=model_name
        )
    
    def translate_text(self, config: CloudConfig, text: str, prompt: str = "", 
                      vocabulary: str = "") -> str:
        """Translate text using cloud AI service"""
        try:
            if config.provider == "huggingface":
                return self._translate_huggingface(config, text, prompt, vocabulary)
            elif config.provider in ["vllm", "colab", "kaggle"]:
                return self._translate_openai_compatible(config, text, prompt, vocabulary)
            else:
                raise ValueError(f"Unsupported provider: {config.provider}")
                
        except Exception as e:
            logging.error(f"Translation failed with {config.provider}: {e}")
            raise
    
    def _translate_huggingface(self, config: CloudConfig, text: str, 
                             prompt: str, vocabulary: str) -> str:
        """Translate using Hugging Face Inference API"""
        headers = {}
        if config.api_key:
            headers["Authorization"] = f"Bearer {config.api_key}"
        
        # Create full prompt
        full_prompt = self._create_full_prompt(text, prompt, vocabulary)
        
        payload = {
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens": 2048,
                "temperature": 0.3,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        response = self.session.post(
            config.endpoint_url,
            headers=headers,
            json=payload,
            timeout=config.timeout
        )
        
        if response.status_code == 503:
            # Model is loading, wait and retry
            logging.info("Model is loading, waiting...")
            import time
            time.sleep(20)
            response = self.session.post(
                config.endpoint_url,
                headers=headers,
                json=payload,
                timeout=config.timeout
            )
        
        response.raise_for_status()
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0:
            return result[0].get("generated_text", "").strip()
        elif isinstance(result, dict):
            return result.get("generated_text", "").strip()
        else:
            raise ValueError(f"Unexpected response format: {result}")
    
    def _translate_openai_compatible(self, config: CloudConfig, text: str, 
                                   prompt: str, vocabulary: str) -> str:
        """Translate using OpenAI-compatible API (vLLM, Colab, Kaggle)"""
        headers = {
            "Content-Type": "application/json"
        }
        
        if config.api_key:
            headers["Authorization"] = f"Bearer {config.api_key}"
        
        # Create messages
        messages = []
        
        if prompt or vocabulary:
            system_message = self._create_system_prompt(prompt, vocabulary)
            messages.append({"role": "system", "content": system_message})
        
        messages.append({
            "role": "user", 
            "content": f"Translate the following Japanese text to English:\n\n{text}"
        })
        
        payload = {
            "model": config.model_name,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 2048,
            "stream": False
        }
        
        response = self.session.post(
            config.endpoint_url,
            headers=headers,
            json=payload,
            timeout=config.timeout
        )
        
        response.raise_for_status()
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"].strip()
        else:
            raise ValueError(f"Unexpected response format: {result}")
    
    def _create_full_prompt(self, text: str, prompt: str, vocabulary: str) -> str:
        """Create full prompt for single-shot models"""
        parts = []
        
        if prompt:
            parts.append(prompt)
        
        if vocabulary:
            parts.append(f"Vocabulary reference:\n{vocabulary}")
        
        parts.append(f"Japanese text to translate:\n{text}")
        parts.append("English translation:")
        
        return "\n\n".join(parts)
    
    def _create_system_prompt(self, prompt: str, vocabulary: str) -> str:
        """Create system prompt for chat models"""
        parts = []
        
        if prompt:
            parts.append(prompt)
        
        if vocabulary:
            parts.append(f"Use this vocabulary reference when appropriate:\n{vocabulary}")
        
        return "\n\n".join(parts) if parts else "You are a professional Japanese to English translator."
    
    def test_connection(self, config: CloudConfig) -> bool:
        """Test connection to cloud service"""
        try:
            if config.provider == "huggingface":
                return self._test_huggingface(config)
            elif config.provider in ["vllm", "colab", "kaggle"]:
                return self._test_openai_compatible(config)
            return False
        except Exception as e:
            logging.error(f"Connection test failed for {config.provider}: {e}")
            return False
    
    def _test_huggingface(self, config: CloudConfig) -> bool:
        """Test Hugging Face connection"""
        headers = {}
        if config.api_key:
            headers["Authorization"] = f"Bearer {config.api_key}"
        
        payload = {
            "inputs": "Hello",
            "parameters": {"max_new_tokens": 10}
        }
        
        response = self.session.post(
            config.endpoint_url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        return response.status_code in [200, 503]  # 503 means model is loading
    
    def _test_openai_compatible(self, config: CloudConfig) -> bool:
        """Test OpenAI-compatible API connection"""
        headers = {"Content-Type": "application/json"}
        if config.api_key:
            headers["Authorization"] = f"Bearer {config.api_key}"
        
        payload = {
            "model": config.model_name,
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 10
        }
        
        response = self.session.post(
            config.endpoint_url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        return response.status_code == 200
    
    def get_model_info(self, config: CloudConfig) -> Dict[str, Any]:
        """Get model information"""
        try:
            if config.provider == "huggingface":
                # Get model info from HF Hub
                info_url = f"https://huggingface.co/api/models/{config.model_name}"
                response = self.session.get(info_url, timeout=10)
                if response.status_code == 200:
                    return response.json()
            
            return {
                "provider": config.provider,
                "model": config.model_name,
                "endpoint": config.endpoint_url
            }
        except Exception as e:
            logging.error(f"Failed to get model info: {e}")
            return {}


class CloudSetupHelper:
    """Helper for setting up cloud AI services"""
    
    @staticmethod
    def generate_colab_setup_code(model_name: str = "Qwen/Qwen2-7B-Instruct") -> str:
        """Generate Google Colab setup code"""
        return f"""
# Google Colab Setup Code
# Run this in a Colab notebook to set up the translation server

# Install dependencies
!pip install transformers torch vllm fastapi uvicorn pyngrok

# Import libraries
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from fastapi import FastAPI
from pyngrok import ngrok
import uvicorn
import threading
from pydantic import BaseModel
from typing import List, Dict, Any

# Model setup
model_name = "{model_name}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto"
)

# FastAPI app
app = FastAPI()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    max_tokens: int = 2048
    temperature: float = 0.3

@app.post("/v1/chat/completions")
async def chat_completion(request: ChatRequest):
    try:
        # Format messages
        conversation = ""
        for msg in request.messages:
            conversation += f"{{msg.role}}: {{msg.content}}\\n"
        
        # Generate response
        inputs = tokenizer(conversation, return_tensors="pt").to(model.device)
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=request.max_tokens,
                temperature=request.temperature,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        response_text = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
        
        return {{
            "choices": [{{
                "message": {{
                    "role": "assistant",
                    "content": response_text
                }}
            }}]
        }}
    except Exception as e:
        return {{"error": str(e)}}

# Start ngrok tunnel
ngrok.set_auth_token("YOUR_NGROK_TOKEN")  # Replace with your ngrok token
public_url = ngrok.connect(8000)
print(f"Public URL: {{public_url}}")

# Start server in background
def run_server():
    uvicorn.run(app, host="0.0.0.0", port=8000)

server_thread = threading.Thread(target=run_server)
server_thread.daemon = True
server_thread.start()

print("Server is running! Use the public URL in BaconanaMTL Tool")
print("Keep this cell running to maintain the server")
"""
    
    @staticmethod
    def generate_kaggle_setup_code(model_name: str = "Qwen/Qwen2-7B-Instruct") -> str:
        """Generate Kaggle setup code"""
        return f"""
# Kaggle Setup Code
# Run this in a Kaggle notebook to set up the translation server

# Enable internet and GPU in Kaggle settings first!

# Install dependencies (may need to restart kernel after)
import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import transformers
except ImportError:
    install("transformers")
    
try:
    import fastapi
except ImportError:
    install("fastapi")
    install("uvicorn")

# The rest is similar to Colab setup
# Note: Kaggle doesn't support ngrok, so you'll need to use Kaggle's API
# or set up port forwarding differently
"""
    
    @staticmethod
    def generate_vllm_setup_code(model_name: str = "Qwen/Qwen2-7B-Instruct") -> str:
        """Generate vLLM setup code"""
        return f"""
# vLLM Setup Code
# Run this on a server with GPU to set up high-performance inference

# Install vLLM
pip install vllm

# Start vLLM server
python -m vllm.entrypoints.openai.api_server \\
    --model {model_name} \\
    --host 0.0.0.0 \\
    --port 8000 \\
    --served-model-name {model_name.split('/')[-1]}

# Server will be available at http://your-server-ip:8000
# Use this URL as the endpoint in BaconanaMTL Tool
"""
