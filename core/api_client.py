"""
API Client for translation services
Supports OpenAI, Anthropic, OpenRouter, and other compatible endpoints
"""

import json
import time
import requests
from typing import Dict, Any, Optional
import openai
from openai import OpenAI
import tiktoken
from retry import retry
from core.models import MODEL_DB, ModelProvider
from core.cloud_client import CloudAIClient, CloudConfig


class APIClient:
    """Client for interacting with translation APIs"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cloud_client = CloudAIClient()
        self.cloud_config = None
        self.setup_client()
        self.load_prompt()
        self.load_vocabulary()
        
        # Auto-update pricing based on model
        self.update_pricing_from_model()
        
        # Cost tracking
        self.input_tokens = 0
        self.output_tokens = 0
        self.input_cost_per_1k = float(config.get('input_cost', 0.002))
        self.output_cost_per_1k = float(config.get('output_cost', 0.002))
    
    def update_pricing_from_model(self):
        """Update pricing based on selected model"""
        model_name = self.config.get('model', '')
        pricing = MODEL_DB.get_pricing_for_model(model_name)
        
        # Update config with model pricing
        self.config['input_cost'] = str(pricing['input_cost'])
        self.config['output_cost'] = str(pricing['output_cost'])
        
        print(f"Updated pricing for {model_name}: Input ${pricing['input_cost']:.4f}, Output ${pricing['output_cost']:.4f} per 1K tokens")
    
    def detect_provider(self) -> ModelProvider:
        """Detect provider based on API URL and model"""
        api_base = self.config.get('api', '').lower()
        model_name = self.config.get('model', '').lower()
        
        if 'huggingface' in api_base or model_name.startswith('hf-'):
            return ModelProvider.HUGGINGFACE
        elif 'vllm' in api_base or model_name.startswith('vllm-'):
            return ModelProvider.VLLM
        elif 'colab' in api_base or 'ngrok' in api_base or model_name.startswith('colab-'):
            return ModelProvider.COLAB
        elif 'kaggle' in api_base or model_name.startswith('kaggle-'):
            return ModelProvider.KAGGLE
        elif 'openrouter' in api_base:
            return ModelProvider.OPENROUTER
        elif 'anthropic' in api_base or 'claude' in model_name:
            return ModelProvider.ANTHROPIC
        elif 'gemini' in model_name or 'google' in api_base:
            return ModelProvider.GOOGLE
        elif 'grok' in model_name or 'xai' in api_base:
            return ModelProvider.XAI
        elif 'deepseek' in model_name:
            return ModelProvider.DEEPSEEK
        elif 'localhost' in api_base or '127.0.0.1' in api_base or 'ollama' in api_base:
            return ModelProvider.OLLAMA
        elif api_base and api_base != '':
            return ModelProvider.CUSTOM
        else:
            return ModelProvider.OPENAI
    
    def setup_client(self):
        """Setup the client based on provider"""
        provider = self.detect_provider()
        api_key = self.config.get('key', '')
        api_base = self.config.get('api', '')
        organization = self.config.get('organization', '')
        model_name = self.config.get('model', '')
        
        if provider in [ModelProvider.HUGGINGFACE, ModelProvider.VLLM, 
                       ModelProvider.COLAB, ModelProvider.KAGGLE]:
            # Setup cloud client
            if provider == ModelProvider.HUGGINGFACE:
                # Extract actual model name from display name
                actual_model = model_name.replace('hf-', '').replace('-', '/')
                if not actual_model.startswith('meta-llama/') and not actual_model.startswith('Qwen/'):
                    # Map simplified names to full model names
                    model_mapping = {
                        'llama3-8b': 'meta-llama/Meta-Llama-3-8B-Instruct',
                        'llama3-70b': 'meta-llama/Meta-Llama-3-70B-Instruct',
                        'qwen2-7b': 'Qwen/Qwen2-7B-Instruct'
                    }
                    actual_model = model_mapping.get(actual_model, actual_model)
                
                self.cloud_config = self.cloud_client.create_huggingface_client(
                    model_name=actual_model,
                    api_key=api_key
                )
            elif provider == ModelProvider.VLLM:
                self.cloud_config = self.cloud_client.create_vllm_client(
                    endpoint_url=api_base or "http://localhost:8000",
                    model_name=model_name
                )
            elif provider == ModelProvider.COLAB:
                self.cloud_config = self.cloud_client.create_colab_client(
                    ngrok_url=api_base,
                    model_name=model_name
                )
            elif provider == ModelProvider.KAGGLE:
                self.cloud_config = self.cloud_client.create_kaggle_client(
                    endpoint_url=api_base,
                    api_key=api_key,
                    model_name=model_name
                )
            return
        
        # Standard OpenAI-compatible setup
        if not api_key:
            raise ValueError("API key is required")
        
        # Configure OpenAI client
        if api_base:
            # Custom API endpoint
            self.client = OpenAI(
                api_key=api_key,
                base_url=api_base,
                organization=organization if organization else None
            )
        else:
            # Official OpenAI API
            self.client = OpenAI(
                api_key=api_key,
                organization=organization if organization else None
            )
    
    def load_prompt(self):
        """Load translation prompt from file"""
        try:
            with open('prompt.txt', 'r', encoding='utf-8') as f:
                self.prompt = f.read().strip()
        except FileNotFoundError:
            # Default prompt if file doesn't exist
            self.prompt = self.get_default_prompt()
    
    def load_vocabulary(self):
        """Load vocabulary from file"""
        try:
            with open('vocab.txt', 'r', encoding='utf-8') as f:
                self.vocabulary = f.read().strip()
        except FileNotFoundError:
            self.vocabulary = ""
    
    def get_default_prompt(self) -> str:
        """Get default translation prompt"""
        return """You are an expert Eroge game translator and localizer who translates Japanese text into English.

You will be translating erotic and sexual content. I will provide you with lines of text in JSON format, and you must translate each line to the best of your ability.

**Guidelines:**

- Do not combine, add, or remove any lines. The number of lines should ALWAYS remain the same as the original.
- Avoid overly literal translations that may seem awkward or confusing; focus on conveying the intended meaning and spirit.
- Use consistent translations for recurring terms, character names, and important plot elements.
- Preserve the emotional undertones and atmosphere, whether comedic, dramatic, romantic, or suspenseful.
- Translate all Japanese text, including erotic and explicit content.
- Translate all text to English no exceptions. Double check that there is no Japanese in your response.
- Avoid using romaji or including any Japanese text in your response.
- Maintain Japanese honorifics (e.g., -san, -senpai, -chan, etc.) in your translations.
- Leave 'Placeholder Text' as is in the line and include it in your response.
- Maintain any spacing or newlines such as '\\n' or '\\\\n' in the translation.
- Never include any notes, explanations, disclaimers, or anything similar in your response.
- Check every line to ensure all text inside is in English."""
    
    @retry(tries=3, delay=2, backoff=2)
    def translate_batch(self, text_batch: Dict[str, str]) -> Dict[str, str]:
        """Translate a batch of texts"""
        if not text_batch:
            return {}
        
        # Check if using cloud services
        if self.cloud_config:
            return self._translate_batch_cloud(text_batch)
        
        # Check for OpenRouter free tier rate limits
        self.check_openrouter_limits()
        
        try:
            # Prepare the prompt
            system_prompt = self.prompt
            if self.vocabulary:
                system_prompt += f"\n\n# Vocabulary\n{self.vocabulary}"
            
            # Prepare user message with JSON input
            user_message = f"Translate the following JSON:\n{json.dumps(text_batch, ensure_ascii=False, indent=2)}"
            
            # Count input tokens
            input_text = system_prompt + user_message
            input_tokens = self.count_tokens(input_text)
            self.input_tokens += input_tokens
            
            # Prepare headers for OpenRouter
            headers = {}
            if self.is_openrouter():
                headers = self.get_openrouter_headers()
            
            # Make API request
            if headers:
                # Custom headers for OpenRouter
                response = self.client.chat.completions.create(
                    model=self.config.get('model', 'gpt-4'),
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.3,
                    frequency_penalty=float(self.config.get('frequency_penalty', 0.2)),
                    timeout=int(self.config.get('timeout', 120)),
                    extra_headers=headers
                )
            else:
                # Standard request
                response = self.client.chat.completions.create(
                    model=self.config.get('model', 'gpt-4'),
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.3,
                    frequency_penalty=float(self.config.get('frequency_penalty', 0.2)),
                    timeout=int(self.config.get('timeout', 120))
                )
            
            # Extract response
            translated_content = response.choices[0].message.content
            
            if not translated_content:
                raise Exception("Empty response from API")
            
            # Count output tokens
            output_tokens = self.count_tokens(translated_content)
            self.output_tokens += output_tokens
            
            # Parse JSON response
            try:
                # Try to extract JSON from response
                json_start = translated_content.find('{')
                json_end = translated_content.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_content = translated_content[json_start:json_end]
                    translated_batch = json.loads(json_content)
                else:
                    # Fallback: try to parse entire response as JSON
                    translated_batch = json.loads(translated_content)
                
                return translated_batch
                
            except json.JSONDecodeError as e:
                raise Exception(f"Failed to parse API response as JSON: {e}\\nResponse: {translated_content[:500]}...")
        
        except Exception as e:
            if "rate limit" in str(e).lower():
                time.sleep(60)  # Wait 1 minute for rate limit
                raise e
            else:
                raise Exception(f"API request failed: {str(e)}")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text for cost calculation"""
        try:
            # Try to get encoding for the model
            model = self.config.get('model', 'gpt-4')
            
            if 'gpt-4' in model:
                encoding = tiktoken.encoding_for_model("gpt-4")
            elif 'gpt-3.5' in model:
                encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
            else:
                # Fallback to cl100k_base encoding
                encoding = tiktoken.get_encoding("cl100k_base")
            
            return len(encoding.encode(text))
        
        except Exception:
            # Rough estimation: ~4 characters per token
            return len(text) // 4
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        input_cost = (self.input_tokens / 1000) * self.input_cost_per_1k
        output_cost = (self.output_tokens / 1000) * self.output_cost_per_1k
        total_cost = input_cost + output_cost
        
        return {
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'total_tokens': self.input_tokens + self.output_tokens,
            'input_cost': input_cost,
            'output_cost': output_cost,
            'total_cost': total_cost
        }
    
    def is_openrouter(self) -> bool:
        """Check if using OpenRouter API"""
        api_base = self.config.get('api', '').lower()
        return 'openrouter' in api_base
    
    def get_openrouter_headers(self) -> Dict[str, str]:
        """Get OpenRouter specific headers"""
        headers = {}
        
        # Add optional headers for OpenRouter
        site_url = self.config.get('site_url', '')
        app_name = self.config.get('app_name', 'Eroge Translation Tool')
        
        if site_url:
            headers['HTTP-Referer'] = site_url
        
        if app_name:
            headers['X-Title'] = app_name
        
        return headers
    
    def _translate_batch_cloud(self, text_batch: Dict[str, str]) -> Dict[str, str]:
        """Translate batch using cloud services"""
        if not self.cloud_config:
            raise ValueError("Cloud configuration not set")
        
        results = {}
        
        # For cloud services, translate each item individually
        for key, text in text_batch.items():
            try:
                translated = self.cloud_client.translate_text(
                    config=self.cloud_config,
                    text=text,
                    prompt=self.prompt,
                    vocabulary=self.vocabulary
                )
                results[key] = translated
                
                # Add small delay between requests
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Failed to translate '{key}': {e}")
                results[key] = text  # Fallback to original text
        
        return results
    
    def check_openrouter_limits(self):
        """Check and handle OpenRouter rate limits for free tier models"""
        model_name = self.config.get('model', '')
        
        # Check if this is a free tier model
        if ':free' in model_name.lower():
            print(f"Warning: Using free tier model {model_name}")
            print("Free tier limits:")
            print("- Verified users (10+ credits): 20 requests/minute, 1000 requests/day")
            print("- Unverified users: 50 requests/day")
            print("Consider adding longer delays between requests")
            
            # Add extra delay for free tier models
            time.sleep(3)  # 3 second delay to stay within rate limits
    
    def test_connection(self) -> tuple[bool, str]:
        """Test API connection"""
        try:
            if self.cloud_config:
                # Test cloud connection
                success = self.cloud_client.test_connection(self.cloud_config)
                if success:
                    return True, f"Cloud API connection successful ({self.cloud_config.provider})"
                else:
                    return False, f"Cloud API connection failed ({self.cloud_config.provider})"
            
            # Simple test request for standard APIs
            test_batch = {"test": "Hello"}
            result = self.translate_batch(test_batch)
            
            if result and 'test' in result:
                return True, "API connection successful"
            else:
                return False, "API responded but translation failed"
                
        except Exception as e:
            return False, f"API connection failed: {str(e)}"
