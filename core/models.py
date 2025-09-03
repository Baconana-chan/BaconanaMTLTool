"""
Model Database - Information about AI models and their pricing
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class ModelProvider(Enum):
    """Model providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    XAI = "xai"
    DEEPSEEK = "deepseek"
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    VLLM = "vllm"
    COLAB = "colab"
    KAGGLE = "kaggle"
    CUSTOM = "custom"


class ContentPolicy(Enum):
    """Content moderation policy for models"""
    SFW = "sfw"  # Safe for work - strict content filtering
    NSFW = "nsfw"  # Not safe for work - relaxed content filtering
    DEVELOPER_RESPONSIBILITY = "dev_responsibility"  # No filtering, developer responsibility


@dataclass
class ModelPricing:
    """Model pricing information"""
    input_cost: float  # Cost per 1M tokens
    output_cost: float  # Cost per 1M tokens
    cache_hit_cost: Optional[float] = None  # For models with caching
    cache_write_cost: Optional[float] = None  # For cache writes
    cache_refresh_cost: Optional[float] = None  # For cache refreshes
    high_context_input: Optional[float] = None  # For high context pricing
    high_context_output: Optional[float] = None
    high_context_threshold: Optional[int] = None  # Context threshold


@dataclass
class ModelInfo:
    """Complete model information"""
    name: str
    display_name: str
    provider: ModelProvider
    pricing: ModelPricing
    context_length: int
    description: str
    api_name: str  # Name used in API calls
    supports_cache: bool = False
    supports_system_prompt: bool = True
    recommended_for_translation: bool = True
    content_policy: ContentPolicy = ContentPolicy.SFW
    eroge_support: bool = False  # Explicitly supports erotic content


class ModelDatabase:
    """Database of AI models and their information"""
    
    def __init__(self):
        self.models = self._initialize_models()
    
    def _initialize_models(self) -> Dict[str, ModelInfo]:
        """Initialize the model database"""
        models = {}
        
        # OpenAI Models - Partial filtering
        models["gpt-4"] = ModelInfo(
            name="gpt-4",
            display_name="GPT-4 (0613)",
            provider=ModelProvider.OPENAI,
            pricing=ModelPricing(input_cost=30.0, output_cost=60.0),
            context_length=8192,
            description="OpenAI's flagship model for complex tasks",
            api_name="gpt-4-0613",
            content_policy=ContentPolicy.SFW,
            eroge_support=False
        )
        
        models["gpt-3.5-turbo"] = ModelInfo(
            name="gpt-3.5-turbo",
            display_name="GPT-3.5 Turbo (0125)",
            provider=ModelProvider.OPENAI,
            pricing=ModelPricing(input_cost=0.5, output_cost=1.5),
            context_length=16384,
            description="Fast and efficient for most tasks",
            api_name="gpt-3.5-turbo-0125",
            content_policy=ContentPolicy.SFW,
            eroge_support=False
        )
        
        models["gpt-4-turbo"] = ModelInfo(
            name="gpt-4-turbo",
            display_name="GPT-4 Turbo (2024-04-09)",
            provider=ModelProvider.OPENAI,
            pricing=ModelPricing(input_cost=10.0, output_cost=30.0),
            context_length=128000,
            description="Latest GPT-4 with extended context",
            api_name="gpt-4-turbo-2024-04-09",
            content_policy=ContentPolicy.SFW,
            eroge_support=False
        )
        
        models["gpt-4o"] = ModelInfo(
            name="gpt-4o",
            display_name="GPT-4o (2024-11-20)",
            provider=ModelProvider.OPENAI,
            pricing=ModelPricing(
                input_cost=2.5, 
                output_cost=10.0,
                cache_hit_cost=1.25
            ),
            context_length=128000,
            description="Multimodal flagship model",
            api_name="gpt-4o-2024-11-20",
            supports_cache=True,
            content_policy=ContentPolicy.SFW,
            eroge_support=False
        )
        
        models["o1"] = ModelInfo(
            name="o1",
            display_name="o1 (2024-12-17)",
            provider=ModelProvider.OPENAI,
            pricing=ModelPricing(input_cost=15.0, output_cost=60.0),
            context_length=200000,
            description="Advanced reasoning model",
            api_name="o1-2024-12-17",
            content_policy=ContentPolicy.SFW,
            eroge_support=False
        )
        
        models["o3-mini"] = ModelInfo(
            name="o3-mini",
            display_name="o3-mini (2025-01-31)",
            provider=ModelProvider.OPENAI,
            pricing=ModelPricing(input_cost=1.1, output_cost=4.4),
            context_length=128000,
            description="Compact reasoning model",
            api_name="o3-mini-2025-01-31",
            content_policy=ContentPolicy.SFW,
            eroge_support=False
        )
        
        models["gpt-4.1"] = ModelInfo(
            name="gpt-4.1",
            display_name="GPT-4.1 (2025-04-14)",
            provider=ModelProvider.OPENAI,
            pricing=ModelPricing(input_cost=2.0, output_cost=8.0),
            context_length=200000,
            description="Enhanced GPT-4 with improved capabilities",
            api_name="gpt-4.1-2025-04-14",
            content_policy=ContentPolicy.SFW,
            eroge_support=False
        )
        
        models["gpt-4.1-mini"] = ModelInfo(
            name="gpt-4.1-mini",
            display_name="GPT-4.1 Mini (2025-04-14)",
            provider=ModelProvider.OPENAI,
            pricing=ModelPricing(input_cost=0.4, output_cost=1.6),
            context_length=128000,
            description="Efficient version of GPT-4.1",
            api_name="gpt-4.1-mini-2025-04-14",
            content_policy=ContentPolicy.SFW,
            eroge_support=False
        )
        
        models["o4-mini"] = ModelInfo(
            name="o4-mini",
            display_name="o4-mini (2025-04-16)",
            provider=ModelProvider.OPENAI,
            pricing=ModelPricing(input_cost=1.1, output_cost=4.4),
            context_length=200000,
            description="Next-gen compact reasoning model",
            api_name="o4-mini-2025-04-16",
            content_policy=ContentPolicy.SFW,
            eroge_support=False
        )
        
        models["o3"] = ModelInfo(
            name="o3",
            display_name="o3 (2025-04-16)",
            provider=ModelProvider.OPENAI,
            pricing=ModelPricing(input_cost=2.0, output_cost=8.0),
            context_length=200000,
            description="Advanced reasoning model",
            api_name="o3-2025-04-16",
            content_policy=ContentPolicy.SFW,
            eroge_support=False
        )
        
        models["gpt-5-mini"] = ModelInfo(
            name="gpt-5-mini",
            display_name="GPT-5 Mini (2025-08-07)",
            provider=ModelProvider.OPENAI,
            pricing=ModelPricing(input_cost=0.25, output_cost=2.0),
            context_length=256000,
            description="Efficient next-generation model",
            api_name="gpt-5-mini-2025-08-07"
        )
        
        models["gpt-5"] = ModelInfo(
            name="gpt-5",
            display_name="GPT-5 (2025-08-07)",
            provider=ModelProvider.OPENAI,
            pricing=ModelPricing(input_cost=1.25, output_cost=10.0),
            context_length=512000,
            description="Next-generation flagship model",
            api_name="gpt-5-2025-08-07"
        )
        
        # Anthropic Models - Strict filtering
        models["claude-haiku-3"] = ModelInfo(
            name="claude-haiku-3",
            display_name="Claude 3 Haiku",
            provider=ModelProvider.ANTHROPIC,
            pricing=ModelPricing(
                input_cost=0.25,
                output_cost=1.25,
                cache_hit_cost=0.03,
                cache_write_cost=0.30
            ),
            context_length=200000,
            description="Fast and efficient model for simple tasks",
            api_name="claude-3-haiku-20240307",
            supports_cache=True,
            content_policy=ContentPolicy.SFW,
            eroge_support=False
        )
        
        models["claude-haiku-3.5"] = ModelInfo(
            name="claude-haiku-3.5",
            display_name="Claude 3.5 Haiku",
            provider=ModelProvider.ANTHROPIC,
            pricing=ModelPricing(
                input_cost=0.8,
                output_cost=4.0,
                cache_hit_cost=0.08,
                cache_write_cost=1.0
            ),
            context_length=200000,
            description="Improved Haiku with better capabilities",
            api_name="claude-3-5-haiku-20241022",
            supports_cache=True,
            content_policy=ContentPolicy.SFW,
            eroge_support=False
        )
        
        models["claude-sonnet-3.7"] = ModelInfo(
            name="claude-sonnet-3.7",
            display_name="Claude 3.7 Sonnet",
            provider=ModelProvider.ANTHROPIC,
            pricing=ModelPricing(
                input_cost=3.0,
                output_cost=15.0,
                cache_hit_cost=0.30,
                cache_write_cost=3.75
            ),
            context_length=200000,
            description="Balanced performance and capability",
            api_name="claude-3-7-sonnet",
            supports_cache=True,
            content_policy=ContentPolicy.SFW,
            eroge_support=False
        )
        
        models["claude-sonnet-4"] = ModelInfo(
            name="claude-sonnet-4",
            display_name="Claude 4 Sonnet",
            provider=ModelProvider.ANTHROPIC,
            pricing=ModelPricing(
                input_cost=3.0,
                output_cost=15.0,
                cache_hit_cost=0.30,
                cache_write_cost=3.75
            ),
            context_length=200000,
            description="Next-gen balanced model",
            api_name="claude-4-sonnet",
            supports_cache=True,
            content_policy=ContentPolicy.SFW,
            eroge_support=False
        )
        
        models["claude-opus-4"] = ModelInfo(
            name="claude-opus-4",
            display_name="Claude 4 Opus",
            provider=ModelProvider.ANTHROPIC,
            pricing=ModelPricing(
                input_cost=15.0,
                output_cost=75.0,
                cache_hit_cost=1.50,
                cache_write_cost=18.75
            ),
            context_length=200000,
            description="Most capable Anthropic model",
            api_name="claude-4-opus",
            supports_cache=True,
            content_policy=ContentPolicy.SFW,
            eroge_support=False
        )
        
        models["claude-opus-4.1"] = ModelInfo(
            name="claude-opus-4.1",
            display_name="Claude 4.1 Opus",
            provider=ModelProvider.ANTHROPIC,
            pricing=ModelPricing(
                input_cost=15.0,
                output_cost=75.0,
                cache_hit_cost=1.50,
                cache_write_cost=18.75
            ),
            context_length=200000,
            description="Enhanced Claude Opus",
            api_name="claude-4-1-opus",
            supports_cache=True,
            content_policy=ContentPolicy.SFW,
            eroge_support=False
        )
        
        # Google Models - Strict filtering
        models["gemini-2.5-flash"] = ModelInfo(
            name="gemini-2.5-flash",
            display_name="Gemini 2.5 Flash",
            provider=ModelProvider.GOOGLE,
            pricing=ModelPricing(input_cost=0.30, output_cost=2.5),
            context_length=1000000,
            description="Fast multimodal model",
            api_name="gemini-2.5-flash",
            content_policy=ContentPolicy.SFW,
            eroge_support=False
        )
        
        models["gemini-2.5-pro"] = ModelInfo(
            name="gemini-2.5-pro",
            display_name="Gemini 2.5 Pro",
            provider=ModelProvider.GOOGLE,
            pricing=ModelPricing(
                input_cost=1.25,
                output_cost=10.0,
                high_context_input=2.5,
                high_context_output=15.0,
                high_context_threshold=200000
            ),
            context_length=2000000,
            description="Advanced multimodal model",
            api_name="gemini-2.5-pro",
            content_policy=ContentPolicy.SFW,
            eroge_support=False
        )
        
        # xAI Models - Minimal filtering
        models["grok-3-mini"] = ModelInfo(
            name="grok-3-mini",
            display_name="Grok 3 Mini",
            provider=ModelProvider.XAI,
            pricing=ModelPricing(input_cost=0.30, output_cost=0.50),
            context_length=128000,
            description="Compact model from xAI",
            api_name="grok-3-mini",
            content_policy=ContentPolicy.NSFW,
            eroge_support=True
        )
        
        models["grok-3"] = ModelInfo(
            name="grok-3",
            display_name="Grok 3",
            provider=ModelProvider.XAI,
            pricing=ModelPricing(input_cost=3.0, output_cost=15.0),
            context_length=128000,
            description="Advanced model from xAI",
            api_name="grok-3",
            content_policy=ContentPolicy.NSFW,
            eroge_support=True
        )
        
        models["grok-4"] = ModelInfo(
            name="grok-4",
            display_name="Grok 4",
            provider=ModelProvider.XAI,
            pricing=ModelPricing(input_cost=3.0, output_cost=15.0),
            context_length=200000,
            description="Latest model from xAI",
            api_name="grok-4",
            content_policy=ContentPolicy.NSFW,
            eroge_support=True
        )
        
        # DeepSeek Models - No filtering
        models["deepseek-v3.1"] = ModelInfo(
            name="deepseek-v3.1",
            display_name="DeepSeek V3.1",
            provider=ModelProvider.DEEPSEEK,
            pricing=ModelPricing(
                input_cost=0.56,
                output_cost=1.68,
                cache_hit_cost=0.07
            ),
            context_length=128000,
            description="Advanced reasoning model from DeepSeek",
            api_name="deepseek-v3.1",
            supports_cache=True,
            content_policy=ContentPolicy.NSFW,
            eroge_support=True
        )
        
        # OpenRouter Models - Developer responsibility
        models["openrouter-auto"] = ModelInfo(
            name="openrouter-auto",
            display_name="OpenRouter Auto",
            provider=ModelProvider.OPENROUTER,
            pricing=ModelPricing(input_cost=0.0, output_cost=0.0),  # Variable pricing
            context_length=200000,
            description="Auto-select best model (Developer responsibility for content policy)",
            api_name="openrouter/auto",
            content_policy=ContentPolicy.DEVELOPER_RESPONSIBILITY,
            eroge_support=True
        )
        
        # Ollama Models - Local models
        models["ollama-local"] = ModelInfo(
            name="ollama-local",
            display_name="Ollama (Local)",
            provider=ModelProvider.OLLAMA,
            pricing=ModelPricing(input_cost=0.0, output_cost=0.0),  # Free local
            context_length=128000,
            description="Local self-hosted models (Developer responsibility)",
            api_name="ollama",
            content_policy=ContentPolicy.DEVELOPER_RESPONSIBILITY,
            eroge_support=True
        )
        
        # Hugging Face Models - Transformers
        models["hf-llama3-8b"] = ModelInfo(
            name="hf-llama3-8b",
            display_name="Llama 3 8B (Hugging Face)",
            provider=ModelProvider.HUGGINGFACE,
            pricing=ModelPricing(input_cost=0.0, output_cost=0.0),  # Free with own compute
            context_length=8192,
            description="Meta's Llama 3 8B via Hugging Face Transformers",
            api_name="meta-llama/Meta-Llama-3-8B-Instruct",
            content_policy=ContentPolicy.DEVELOPER_RESPONSIBILITY,
            eroge_support=True
        )
        
        models["hf-llama3-70b"] = ModelInfo(
            name="hf-llama3-70b",
            display_name="Llama 3 70B (Hugging Face)",
            provider=ModelProvider.HUGGINGFACE,
            pricing=ModelPricing(input_cost=0.0, output_cost=0.0),  # Free with own compute
            context_length=8192,
            description="Meta's Llama 3 70B via Hugging Face Transformers",
            api_name="meta-llama/Meta-Llama-3-70B-Instruct",
            content_policy=ContentPolicy.DEVELOPER_RESPONSIBILITY,
            eroge_support=True
        )
        
        models["hf-qwen2-7b"] = ModelInfo(
            name="hf-qwen2-7b",
            display_name="Qwen2 7B (Hugging Face)",
            provider=ModelProvider.HUGGINGFACE,
            pricing=ModelPricing(input_cost=0.0, output_cost=0.0),  # Free with own compute
            context_length=32768,
            description="Alibaba's Qwen2 7B via Hugging Face Transformers",
            api_name="Qwen/Qwen2-7B-Instruct",
            content_policy=ContentPolicy.DEVELOPER_RESPONSIBILITY,
            eroge_support=True
        )
        
        # vLLM Models - High performance inference
        models["vllm-llama3-8b"] = ModelInfo(
            name="vllm-llama3-8b",
            display_name="Llama 3 8B (vLLM)",
            provider=ModelProvider.VLLM,
            pricing=ModelPricing(input_cost=0.0, output_cost=0.0),  # Free with own compute
            context_length=8192,
            description="High-performance Llama 3 8B inference via vLLM",
            api_name="meta-llama/Meta-Llama-3-8B-Instruct",
            content_policy=ContentPolicy.DEVELOPER_RESPONSIBILITY,
            eroge_support=True
        )
        
        models["vllm-qwen2-7b"] = ModelInfo(
            name="vllm-qwen2-7b",
            display_name="Qwen2 7B (vLLM)",
            provider=ModelProvider.VLLM,
            pricing=ModelPricing(input_cost=0.0, output_cost=0.0),  # Free with own compute
            context_length=32768,
            description="High-performance Qwen2 7B inference via vLLM",
            api_name="Qwen/Qwen2-7B-Instruct",
            content_policy=ContentPolicy.DEVELOPER_RESPONSIBILITY,
            eroge_support=True
        )
        
        # Google Colab Models - Cloud hosting
        models["colab-hosted"] = ModelInfo(
            name="colab-hosted",
            display_name="Google Colab Hosted Model",
            provider=ModelProvider.COLAB,
            pricing=ModelPricing(input_cost=0.0, output_cost=0.0),  # Free with Colab compute
            context_length=32768,
            description="Model hosted on Google Colab with remote API access",
            api_name="colab-custom",
            content_policy=ContentPolicy.DEVELOPER_RESPONSIBILITY,
            eroge_support=True
        )
        
        # Kaggle Models - Cloud hosting
        models["kaggle-hosted"] = ModelInfo(
            name="kaggle-hosted",
            display_name="Kaggle Hosted Model",
            provider=ModelProvider.KAGGLE,
            pricing=ModelPricing(input_cost=0.0, output_cost=0.0),  # Free with Kaggle compute
            context_length=32768,
            description="Model hosted on Kaggle with remote API access",
            api_name="kaggle-custom",
            content_policy=ContentPolicy.DEVELOPER_RESPONSIBILITY,
            eroge_support=True
        )
        
        return models
    
    def get_model(self, name: str) -> Optional[ModelInfo]:
        """Get model information by name"""
        return self.models.get(name)
    
    def get_models_by_provider(self, provider: ModelProvider) -> List[ModelInfo]:
        """Get all models from a specific provider"""
        return [model for model in self.models.values() if model.provider == provider]
    
    def get_recommended_models(self) -> List[ModelInfo]:
        """Get models recommended for translation"""
        return [model for model in self.models.values() if model.recommended_for_translation]
    
    def get_eroge_compatible_models(self) -> List[ModelInfo]:
        """Get models that support erotic content translation"""
        return [model for model in self.models.values() if model.eroge_support]
    
    def get_models_by_content_policy(self, policy: ContentPolicy) -> List[ModelInfo]:
        """Get models by content policy"""
        return [model for model in self.models.values() if model.content_policy == policy]
    
    def get_sfw_models(self) -> List[ModelInfo]:
        """Get safe-for-work models only"""
        return self.get_models_by_content_policy(ContentPolicy.SFW)
    
    def get_nsfw_models(self) -> List[ModelInfo]:
        """Get models that handle NSFW content"""
        return [model for model in self.models.values() 
                if model.content_policy in [ContentPolicy.NSFW, ContentPolicy.DEVELOPER_RESPONSIBILITY]]
    
    def get_model_content_warning(self, model_name: str) -> str:
        """Get content policy warning for a model"""
        model = self.get_model(model_name)
        if not model:
            return "Unknown model"
        
        if model.content_policy == ContentPolicy.SFW:
            return "⚠️ This model has strict content filtering and may not work well with erotic content"
        elif model.content_policy == ContentPolicy.NSFW:
            return "✅ This model handles mature content with minimal filtering"
        elif model.content_policy == ContentPolicy.DEVELOPER_RESPONSIBILITY:
            return "🔓 No content filtering - developer responsibility for appropriate use"
        return ""
    
    def get_all_models(self) -> List[ModelInfo]:
        """Get all available models"""
        return list(self.models.values())
    
    def get_model_names(self) -> List[str]:
        """Get all model names"""
        return list(self.models.keys())
    
    def get_pricing_for_model(self, name: str, context_size: int = 0) -> Dict[str, float]:
        """Get pricing information for a model"""
        model = self.get_model(name)
        if not model:
            return {"input_cost": 0.002, "output_cost": 0.002}  # Default pricing
        
        pricing = model.pricing
        
        # Check if we need high context pricing
        if (pricing.high_context_threshold and 
            context_size > pricing.high_context_threshold and
            pricing.high_context_input and pricing.high_context_output):
            input_cost = pricing.high_context_input / 1000  # Convert to per 1K tokens
            output_cost = pricing.high_context_output / 1000
        else:
            input_cost = pricing.input_cost / 1000  # Convert to per 1K tokens
            output_cost = pricing.output_cost / 1000
        
        result = {
            "input_cost": input_cost,
            "output_cost": output_cost
        }
        
        if pricing.cache_hit_cost:
            result["cache_hit_cost"] = pricing.cache_hit_cost / 1000
        
        return result
    
    def add_custom_model(self, model_info: ModelInfo):
        """Add a custom model to the database"""
        self.models[model_info.name] = model_info
    
    def update_model_pricing(self, name: str, pricing: ModelPricing):
        """Update pricing for an existing model"""
        if name in self.models:
            self.models[name].pricing = pricing
    
    def get_model_pricing(self, name: str) -> Dict[str, float]:
        """Get pricing information for a model"""
        model = self.get_model(name)
        if not model:
            # Return default fallback pricing
            return {
                "input_cost": 0.002,
                "output_cost": 0.002
            }
        
        pricing = {
            "input_cost": model.pricing.input_cost / 1000,  # Convert to per-1K tokens
            "output_cost": model.pricing.output_cost / 1000
        }
        
        if model.pricing.cache_hit_cost:
            pricing["cache_hit_cost"] = model.pricing.cache_hit_cost / 1000
        if model.pricing.cache_write_cost:
            pricing["cache_write_cost"] = model.pricing.cache_write_cost / 1000
            
        return pricing
    
    def get_model_info(self, name: str) -> Dict[str, Any]:
        """Get model info in legacy format for compatibility"""
        model = self.get_model(name)
        if not model:
            # Return default fallback
            return {
                "provider": "unknown",
                "display_name": name,
                "pricing": {"input": 0.002, "output": 0.002},
                "context_window": 4096
            }
        
        # Convert to legacy format
        pricing_dict = {"input": model.pricing.input_cost, "output": model.pricing.output_cost}
        if model.pricing.cache_hit_cost:
            pricing_dict["cache_hit"] = model.pricing.cache_hit_cost
        if model.pricing.cache_write_cost:
            pricing_dict["cache_write"] = model.pricing.cache_write_cost
            
        return {
            "provider": model.provider.value,
            "display_name": model.display_name,
            "pricing": pricing_dict,
            "context_window": model.context_length,
            "supports_caching": model.supports_cache
        }


# Create ModelManager alias for compatibility
class ModelManager:
    """Compatibility wrapper for ModelDatabase"""
    
    def __init__(self):
        self.db = MODEL_DB
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get model info in legacy format"""
        return self.db.get_model_info(model_name)
    
    def get_models_by_provider(self, provider: str) -> Dict[str, Dict[str, Any]]:
        """Get models by provider"""
        models = {}
        for name, model in self.db.models.items():
            if model.provider.value == provider:
                models[name] = self.get_model_info(name)
        return models
    
    def get_recommended_models(self) -> Dict[str, Dict[str, Any]]:
        """Get recommended models"""
        models = {}
        for name, model in self.db.models.items():
            if model.recommended_for_translation:
                models[name] = self.get_model_info(name)
        return models


# Global model database instance
MODEL_DB = ModelDatabase()
