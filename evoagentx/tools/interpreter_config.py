"""
Configuration management for OpenAI Code Interpreter integration
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class OpenAIConfig:
    api_key: Optional[str] = None
    model: str = "gpt-4-1106-preview"
    max_tokens: int = 4096
    timeout: int = 300
    max_cost_per_execution: float = 5.0
    enable_file_uploads: bool = True
    auto_cleanup: bool = True
    
    def __post_init__(self):
        if not self.api_key:
            self.api_key = os.getenv('OPENAI_API_KEY')
    
    def is_valid(self) -> bool:
        """Check if configuration is valid"""
        return bool(self.api_key)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'model': self.model,
            'max_tokens': self.max_tokens,
            'timeout': self.timeout,
            'max_cost_per_execution': self.max_cost_per_execution,
            'enable_file_uploads': self.enable_file_uploads,
            'auto_cleanup': self.auto_cleanup
        }


@dataclass 
class InterpreterConfig:
    openai: OpenAIConfig
    default_interpreter: str = "auto"
    enable_cost_tracking: bool = True
    enable_usage_analytics: bool = True
    security_level: str = "medium"
    
    @classmethod
    def from_env(cls) -> 'InterpreterConfig':
        """Create configuration from environment variables"""
        return cls(
            openai=OpenAIConfig(
                api_key=os.getenv('OPENAI_API_KEY'),
                model=os.getenv('OPENAI_MODEL', 'gpt-4-1106-preview'),
                max_tokens=int(os.getenv('OPENAI_MAX_TOKENS', '4096')),
                timeout=int(os.getenv('OPENAI_TIMEOUT', '300')),
                max_cost_per_execution=float(os.getenv('OPENAI_MAX_COST', '5.0'))
            ),
            default_interpreter=os.getenv('DEFAULT_INTERPRETER', 'auto'),
            security_level=os.getenv('SECURITY_LEVEL', 'medium')
        )
    
    def validate(self) -> bool:
        """Validate all configurations"""
        if not self.openai.is_valid():
            print("Warning: OpenAI API key not configured")
            return False
        
        if self.default_interpreter not in ['auto', 'python', 'docker', 'openai']:
            print(f"Warning: Invalid default interpreter: {self.default_interpreter}")
            return False
        
        return True


# Global configuration instance
_config: Optional[InterpreterConfig] = None

def get_config() -> InterpreterConfig:
    """Get global configuration instance"""
    global _config
    if _config is None:
        _config = InterpreterConfig.from_env()
        if not _config.validate():
            print("Configuration validation failed. Some features may not work.")
    return _config

def set_config(config: InterpreterConfig):
    """Set global configuration"""
    global _config
    _config = config

def reset_config():
    """Reset configuration to reload from environment"""
    global _config
    _config = None
