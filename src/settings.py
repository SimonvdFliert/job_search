import re
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

AI_KEYWORDS = [
    r"\bAI\b",
    r"\bML\b",
    r"machine\s+learning",
    r"artificial\s+intelligence",
    r"deep\s+learning",
    r"LLM",
    r"NLP",
    r"data\s+scientist",
    r"(ML|AI)\s+engineer",
    r"(research|applied)\s+(scientist|engineer)",
]

AI_RE = re.compile("|".join(AI_KEYWORDS), flags=re.I)

ASHBY_ORGS = [
    "openai",
]

GREENHOUSE_BOARDS = [
    "anthropic",
    "scaleai",
    "xai",
]

class ScraperSettings(BaseSettings):
    headers: str = Field(default="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36")
    time_out: int = Field(default=15)  
    sleep_between_calls: float = Field(default=0.6)
    OUTPUT_PATH: str = str("sample_jobs.jsonl")
    # Scraper
    ASHBY_ORGS: list[str] = Field(default_factory=lambda: ["openai"])
    GREENHOUSE_BOARDS: list[str] = Field(default_factory=lambda: ["anthropic", "scaleai", "xai"])
    model_config = SettingsConfigDict(env_prefix="SCRAPE_", env_file=".env", env_file_encoding="utf-8")

class DBSettings(BaseSettings):
    HOST: str = Field(default="127.0.0.1")
    PORT: int = Field(default=5436)
    USER: str = Field(default="route_admin")
    PASSWORD: str = Field(default="route_admin")
    NAME: str = Field(default="jobsdb")
    MAINTENANCE_DB: str = Field(default="postgres") # for CREATE DATABASE
    model_config = SettingsConfigDict(env_prefix="DB_", env_file=".env", env_file_encoding="utf-8")

class AppCoreSettings(BaseSettings):
    ENV: str = Field(default="dev")
    LOG_LEVEL: str = Field(default="INFO")
    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env", env_file_encoding="utf-8")
    DEBUG: bool = Field(default=True)
    
class ModelSettings(BaseSettings):
    # Embeddings
    MODEL_NAME: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    EMBED_DIM: int = Field(default=384)
    BATCH_SIZE: int = Field(default=64)

    # Search defaults
    TOP_K: int = Field(default=20)
    HYBRID_VEC_W: float = Field(default=0.7)
    HYBRID_KW_W: float = Field(default=0.2)
    HYBRID_REC_W: float = Field(default=0.1)
    RECENCY_HALF_LIFE_DAYS: int = Field(default=7)
    model_config = SettingsConfigDict(env_prefix="MODEL_", env_file=".env", env_file_encoding="utf-8")

class AppSettings(BaseSettings):
    core: AppCoreSettings = AppCoreSettings()
    db: DBSettings = DBSettings()
    model: ModelSettings = ModelSettings()
    scrape: ScraperSettings = ScraperSettings()
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = AppSettings()