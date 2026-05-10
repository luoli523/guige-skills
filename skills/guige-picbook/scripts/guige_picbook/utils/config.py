"""Configuration management for guige-picbook."""

from enum import Enum
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


SETTINGS_ENV_FILES = (
    str(Path.home() / ".guige-skills" / ".env"),
    str(Path.home() / ".guige-skills" / "guige-picbook" / ".env"),
    ".guige-skills/.env",
    ".guige-skills/guige-picbook/.env",
)


class LLMProvider(str, Enum):
    """LLM提供商"""

    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GEMINI = "gemini"
    GROK = "grok"


class Language(str, Enum):
    """支持的语言"""

    CHINESE = "zh"
    ENGLISH = "en"
    JAPANESE = "ja"
    KOREAN = "ko"


class Settings(BaseSettings):
    """Application settings loaded from env vars and guige env files."""

    model_config = SettingsConfigDict(
        env_file=SETTINGS_ENV_FILES,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Anthropic (Claude)
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"

    # OpenAI (ChatGPT)
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_base_url: str = "https://api.openai.com/v1"

    # Google (Gemini)
    google_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    # xAI (Grok)
    grok_api_key: str = ""
    grok_model: str = "grok-2-latest"
    xai_base_url: str = "https://api.x.ai/v1"

    # LLM通用配置
    default_llm_provider: LLMProvider = LLMProvider.ANTHROPIC
    max_tokens: int = 4096

    # 搜索服务配置
    tavily_api_key: str = ""
    serp_api_key: str = ""

    # Telegram 配置
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # NotebookLM 配置
    notebooklm_notebook_name: str = "儿童绘本"

    # 输出配置
    output_dir: str = "./picbook"

    def get_active_api_key(self) -> str:
        """获取当前激活的LLM API密钥"""
        provider_keys = {
            LLMProvider.ANTHROPIC: self.anthropic_api_key,
            LLMProvider.OPENAI: self.openai_api_key,
            LLMProvider.GEMINI: self.google_api_key,
            LLMProvider.GROK: self.grok_api_key,
        }
        return provider_keys.get(self.default_llm_provider, "")

    def get_active_model(self) -> str:
        """获取当前激活的模型名称"""
        provider_models = {
            LLMProvider.ANTHROPIC: self.anthropic_model,
            LLMProvider.OPENAI: self.openai_model,
            LLMProvider.GEMINI: self.gemini_model,
            LLMProvider.GROK: self.grok_model,
        }
        return provider_models.get(self.default_llm_provider, "")


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()
