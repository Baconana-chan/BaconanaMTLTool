"""
Provider Manager - Handles multiple AI providers with priority and fallback
"""

import json
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from core.models import ModelProvider, MODEL_DB
from core.api_client import APIClient
from core.cloud_client import CloudAIClient, CloudConfig


@dataclass
class ProviderConfig:
    """Configuration for a specific provider"""
    provider: ModelProvider
    name: str
    enabled: bool
    priority: int  # Lower number = higher priority
    config: Dict[str, Any]
    last_error: Optional[str] = None
    last_error_time: Optional[float] = None
    consecutive_failures: int = 0
    max_failures: int = 3


class ProviderStatus(Enum):
    """Provider status"""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"
    UNTESTED = "untested"


class ProviderManager:
    """Manages multiple AI providers with priority and fallback"""
    
    def __init__(self, config_file: str = "provider_config.json"):
        self.config_file = config_file
        self.providers: Dict[str, ProviderConfig] = {}
        self.status_cache: Dict[str, Tuple[ProviderStatus, float]] = {}
        self.cache_duration = 300  # 5 minutes
        self.load_config()
    
    def add_provider(self, name: str, provider: ModelProvider, config: Dict[str, Any], 
                    priority: int = 10, enabled: bool = True) -> None:
        """Add a new provider configuration"""
        self.providers[name] = ProviderConfig(
            provider=provider,
            name=name,
            enabled=enabled,
            priority=priority,
            config=config.copy(),
            consecutive_failures=0
        )
        self.save_config()
    
    def setup_providers(self, provider_configs: Dict[str, Dict[str, Any]]) -> None:
        """Setup multiple providers from configuration dict"""
        for name, config in provider_configs.items():
            provider_type = config.get('provider', 'openai')
            priority = config.get('priority', 10)
            enabled = config.get('enabled', True)
            
            # Convert string to ModelProvider enum
            if isinstance(provider_type, str):
                try:
                    provider = ModelProvider(provider_type.upper())
                except ValueError:
                    provider = ModelProvider.OPENAI  # fallback
            else:
                provider = provider_type
            
            self.add_provider(name, provider, config, priority, enabled)
    
    def remove_provider(self, name: str) -> bool:
        """Remove a provider"""
        if name in self.providers:
            del self.providers[name]
            if name in self.status_cache:
                del self.status_cache[name]
            self.save_config()
            return True
        return False
    
    def update_provider_priority(self, name: str, priority: int) -> bool:
        """Update provider priority"""
        if name in self.providers:
            self.providers[name].priority = priority
            self.save_config()
            return True
        return False
    
    def enable_provider(self, name: str, enabled: bool = True) -> bool:
        """Enable or disable a provider"""
        if name in self.providers:
            self.providers[name].enabled = enabled
            self.save_config()
            return True
        return False
    
    def get_sorted_providers(self) -> List[ProviderConfig]:
        """Get providers sorted by priority (enabled only)"""
        enabled_providers = [p for p in self.providers.values() if p.enabled]
        return sorted(enabled_providers, key=lambda x: x.priority)
    
    def get_providers(self) -> Dict[str, ProviderConfig]:
        """Get all providers"""
        return self.providers.copy()
    
    def record_failure(self, name: str, error_message: str) -> None:
        """Record a failure for a provider"""
        if name in self.providers:
            provider = self.providers[name]
            provider.consecutive_failures += 1
            provider.last_error = error_message
            provider.last_error_time = time.time()
            self.save_config()
    
    def reset_provider_failures(self, name: str) -> bool:
        """Reset failure count for a provider"""
        if name in self.providers:
            provider = self.providers[name]
            provider.consecutive_failures = 0
            provider.last_error = None
            provider.last_error_time = None
            self.save_config()
            return True
        return False
    
    def get_available_provider(self, test_connection: bool = False) -> Optional[ProviderConfig]:
        """Get the highest priority available provider"""
        sorted_providers = self.get_sorted_providers()
        
        for provider in sorted_providers:
            # Check if provider is in cooldown period
            if self._is_in_cooldown(provider):
                continue
            
            # Check cached status
            status = self._get_cached_status(provider.name)
            if status == ProviderStatus.AVAILABLE:
                return provider
            elif status in [ProviderStatus.RATE_LIMITED, ProviderStatus.ERROR]:
                continue
            
            # Test connection if needed
            if test_connection:
                if self._test_provider_connection(provider):
                    self._update_status_cache(provider.name, ProviderStatus.AVAILABLE)
                    return provider
                else:
                    self._update_status_cache(provider.name, ProviderStatus.ERROR)
                    continue
            else:
                # Assume available if not tested recently
                return provider
        
        return None
    
    def translate_with_fallback(self, text_batch: Dict[str, str], 
                              max_retries: int = 3) -> Tuple[Dict[str, str], str]:
        """
        Translate with automatic fallback to next provider on failure
        Returns: (translated_batch, used_provider_name)
        """
        sorted_providers = self.get_sorted_providers()
        last_error = None
        
        for provider in sorted_providers:
            if self._is_in_cooldown(provider):
                logging.info(f"Provider {provider.name} is in cooldown, skipping")
                continue
            
            try:
                logging.info(f"Attempting translation with provider: {provider.name}")
                
                # Create appropriate client
                client = self._create_client(provider)
                
                # Attempt translation
                result = client.translate_batch(text_batch)
                
                # Success - reset failure count
                provider.consecutive_failures = 0
                provider.last_error = None
                self._update_status_cache(provider.name, ProviderStatus.AVAILABLE)
                
                logging.info(f"Translation successful with provider: {provider.name}")
                return result, provider.name
                
            except Exception as e:
                error_msg = str(e).lower()
                provider.consecutive_failures += 1
                provider.last_error = str(e)
                provider.last_error_time = time.time()
                last_error = e
                
                logging.warning(f"Provider {provider.name} failed: {e}")
                
                # Check error type
                if "rate limit" in error_msg or "quota" in error_msg:
                    self._update_status_cache(provider.name, ProviderStatus.RATE_LIMITED)
                    logging.info(f"Rate limit detected for {provider.name}")
                else:
                    self._update_status_cache(provider.name, ProviderStatus.ERROR)
                
                # Continue to next provider
                continue
        
        # All providers failed
        error_msg = f"All providers failed. Last error: {last_error}"
        logging.error(error_msg)
        raise Exception(error_msg)
    
    def _create_client(self, provider: ProviderConfig) -> APIClient:
        """Create appropriate client for provider"""
        if provider.provider in [ModelProvider.HUGGINGFACE, ModelProvider.VLLM, 
                               ModelProvider.COLAB, ModelProvider.KAGGLE]:
            # Cloud client will be handled in APIClient
            pass
        
        # Create standard API client with provider config
        return APIClient(provider.config)
    
    def _test_provider_connection(self, provider: ProviderConfig) -> bool:
        """Test connection to a provider"""
        try:
            client = self._create_client(provider)
            success, _ = client.test_connection()
            return success
        except Exception as e:
            logging.warning(f"Connection test failed for {provider.name}: {e}")
            return False
    
    def _is_in_cooldown(self, provider: ProviderConfig) -> bool:
        """Check if provider is in cooldown period"""
        if provider.consecutive_failures < provider.max_failures:
            return False
        
        if not provider.last_error_time:
            return False
        
        # Exponential backoff: 2^failures minutes
        cooldown_duration = min(2 ** provider.consecutive_failures * 60, 3600)  # Max 1 hour
        return time.time() - provider.last_error_time < cooldown_duration
    
    def _get_cached_status(self, provider_name: str) -> ProviderStatus:
        """Get cached provider status"""
        if provider_name not in self.status_cache:
            return ProviderStatus.UNTESTED
        
        status, timestamp = self.status_cache[provider_name]
        if time.time() - timestamp > self.cache_duration:
            return ProviderStatus.UNTESTED
        
        return status
    
    def _update_status_cache(self, provider_name: str, status: ProviderStatus) -> None:
        """Update provider status cache"""
        self.status_cache[provider_name] = (status, time.time())
    
    def get_provider_status(self, provider_name: str) -> Dict[str, Any]:
        """Get detailed provider status"""
        if provider_name not in self.providers:
            return {"error": "Provider not found"}
        
        provider = self.providers[provider_name]
        status = self._get_cached_status(provider_name)
        
        return {
            "name": provider.name,
            "provider": provider.provider.value,
            "enabled": provider.enabled,
            "priority": provider.priority,
            "status": status.value,
            "consecutive_failures": provider.consecutive_failures,
            "last_error": provider.last_error,
            "in_cooldown": self._is_in_cooldown(provider),
            "cooldown_remaining": self._get_cooldown_remaining(provider)
        }
    
    def _get_cooldown_remaining(self, provider: ProviderConfig) -> Optional[int]:
        """Get remaining cooldown time in seconds"""
        if not self._is_in_cooldown(provider):
            return None
        
        cooldown_duration = min(2 ** provider.consecutive_failures * 60, 3600)
        elapsed = time.time() - provider.last_error_time
        return max(0, int(cooldown_duration - elapsed))
    
    def get_all_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all providers"""
        return {name: self.get_provider_status(name) for name in self.providers.keys()}
    
    def save_config(self) -> None:
        """Save provider configuration to file"""
        try:
            config_data = {
                "providers": {},
                "cache_duration": self.cache_duration
            }
            
            for name, provider in self.providers.items():
                config_data["providers"][name] = {
                    "provider": provider.provider.value,
                    "enabled": provider.enabled,
                    "priority": provider.priority,
                    "config": provider.config,
                    "last_error": provider.last_error,
                    "last_error_time": provider.last_error_time,
                    "consecutive_failures": provider.consecutive_failures,
                    "max_failures": provider.max_failures
                }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logging.error(f"Failed to save provider config: {e}")
    
    def load_config(self) -> None:
        """Load provider configuration from file"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            self.cache_duration = config_data.get("cache_duration", 300)
            
            for name, data in config_data.get("providers", {}).items():
                try:
                    provider_enum = ModelProvider(data["provider"])
                    self.providers[name] = ProviderConfig(
                        provider=provider_enum,
                        name=name,
                        enabled=data.get("enabled", True),
                        priority=data.get("priority", 10),
                        config=data.get("config", {}),
                        last_error=data.get("last_error"),
                        last_error_time=data.get("last_error_time"),
                        consecutive_failures=data.get("consecutive_failures", 0),
                        max_failures=data.get("max_failures", 3)
                    )
                except (ValueError, KeyError) as e:
                    logging.warning(f"Failed to load provider {name}: {e}")
                    
        except FileNotFoundError:
            # Create default config
            self._create_default_config()
        except Exception as e:
            logging.error(f"Failed to load provider config: {e}")
            self._create_default_config()
    
    def _create_default_config(self) -> None:
        """Create default provider configuration"""
        # Add OpenAI as default provider with highest priority
        self.add_provider(
            name="OpenAI",
            provider=ModelProvider.OPENAI,
            config={
                "key": "",
                "model": "gpt-4o",
                "api": "",
                "organization": ""
            },
            priority=1
        )
        
        # Add OpenRouter as second priority
        self.add_provider(
            name="OpenRouter", 
            provider=ModelProvider.OPENROUTER,
            config={
                "key": "",
                "model": "anthropic/claude-3.5-sonnet",
                "api": "https://openrouter.ai/api/v1"
            },
            priority=2
        )
        
        logging.info("Created default provider configuration")
    
    def reset_all_failures(self) -> None:
        """Reset failure counts for all providers"""
        for provider in self.providers.values():
            provider.consecutive_failures = 0
            provider.last_error = None
            provider.last_error_time = None
        self.status_cache.clear()
        self.save_config()
