import re
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, Field

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

ASHBY_COMPANIES = [
    "openai",
]

GREENHOUSE_BOARDS_COMPANIES = [
    "anthropic",
    # "scaleai",
    # "xai",
    # # "cohere",
    # # "huggingface",
    # "databricks",
    # # "mistralai",
    # # "perplexity",
    # "deepmind",
    # # "cerebras",
    # "gitlab",
    # "twitch",

]

# Only this loads from .env (with nested creation)
class Settings(BaseSettings):
    """Application settings - loads from .env"""
    
    # Direct fields
    database_url: str
    app_name: str = "Job Board API"
    app_debug: bool = True
    app_environment: str = "development"
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Model fields
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    model_embed_dim: int = 384
    model_batch_size: int = 64
    model_top_k: int = 20
    model_hybrid_vec_w: float = 0.7
    model_hybrid_kw_w: float = 0.2
    model_hybrid_rec_w: float = 0.1
    model_recency_half_life_days: int = 7
    
    # DB fields
    database_url: str
    db_name: str    
    db_echo: bool = False
    db_pool_size: int = 5
    ashby_orgs: list[str] = Field(default_factory=lambda: ASHBY_COMPANIES)
    greenhouse_boards: list[str] = Field(default_factory=lambda: GREENHOUSE_BOARDS_COMPANIES)
    sleep_between_calls: float = Field(default=0.6)
    
    # Scraper fields
    scrape_interval: int = 3600
    scrape_max_retries: int = 3
    headers: str = Field(default="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36")
    time_out: int = Field(default=15)

  
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


settings = Settings()