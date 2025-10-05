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
    "scaleai",
    "xai",
    "cohere",
    "huggingface",
    "databricks",
    "mistralai",
    "perplexity",
    "deepmind",
    "cerebras",
    "gitlab",
    "twitch",

]

# class ScraperSettings(BaseSettings):
#     headers: str = Field(default="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36")
#     time_out: int = Field(default=15)  
#     sleep_between_calls: float = Field(default=0.6)
#     OUTPUT_PATH: str = str("sample_jobs.jsonl")
#     # Scraper
#     ASHBY_ORGS: list[str] = Field(default_factory=lambda: ASHBY_COMPANIES)
#     GREENHOUSE_BOARDS: list[str] = Field(default_factory=lambda: GREENHOUSE_BOARDS_COMPANIES)
#     model_config = SettingsConfigDict(env_prefix="SCRAPE_", env_file=".env", env_file_encoding="utf-8")
#     database_url: str

# class DBSettings(BaseSettings):
    # HOST: str = Field(default="127.0.0.1")
    # PORT: int = Field(default=5436)
    # USER: str = Field(default="route_admin")
    # PASSWORD: str = Field(default="route_admin")
    # NAME: str = Field(default="jobsdb")
    # database_url: str
    # MAINTENANCE_DB: str = Field(default="postgres") # for CREATE DATABASE
    # model_config = SettingsConfigDict(env_prefix="DB_", env_file=".env", env_file_encoding="utf-8")
    # secret_key: str = "dev-secret-key-change-in-production"
    # algorithm: str = "HS256"

# class AppCoreSettings(BaseSettings):
    # ENV: str = Field(default="dev")
    # LOG_LEVEL: str = Field(default="INFO")
    # model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env", env_file_encoding="utf-8")
    # DEBUG: bool = Field(default=True)
    # database_url: str

    
# class ModelSettings(BaseSettings):
    # Embeddings
    # MODEL_NAME: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    # EMBED_DIM: int = Field(default=384)
    # BATCH_SIZE: int = Field(default=64)

    # # Search defaults
    # TOP_K: int = Field(default=20)
    # HYBRID_VEC_W: float = Field(default=0.7)
    # HYBRID_KW_W: float = Field(default=0.2)
    # HYBRID_REC_W: float = Field(default=0.1)
    # RECENCY_HALF_LIFE_DAYS: int = Field(default=7)
    # model_config = SettingsConfigDict(env_prefix="MODEL_", env_file=".env", env_file_encoding="utf-8")
    # database_url: str


# class AppSettings(BaseSettings):
#     core: AppCoreSettings = AppCoreSettings()
#     db: DBSettings = DBSettings()
#     model: ModelSettings = ModelSettings()
#     scrape: ScraperSettings = ScraperSettings()
#     model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
#     database_url: str


# # Use BaseModel for nested structures (no env loading)
# class AppCoreSettings(BaseModel):
#     name: str = "Job Board API"
#     debug: bool = False
#     environment: str = "development"


# class DBSettings(BaseModel):
#     url: str
#     echo: bool = False
#     pool_size: int = 5
#     maintenance_db: str
#     db_name: str
#     ashby_orgs: list[str] = Field(default_factory=lambda: ASHBY_COMPANIES)
#     greenhouse_boards: list[str] = Field(default_factory=lambda: GREENHOUSE_BOARDS_COMPANIES)
#     sleep_between_calls: float = Field(default=0.6)
    


# class ModelSettings(BaseModel):
#     model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
#     embed_dim: int = Field(default=384)
#     batch_size: int = Field(default=64)
#     top_k: int = Field(default=20)
#     hybrid_vec_w: float = Field(default=0.7)
#     hybrid_kw_w: float = Field(default=0.2)
#     hybrid_rec_w: float = Field(default=0.1)
#     recency_half_life_days: int = Field(default=7)


# class ScraperSettings(BaseModel):
#     interval: int = 3600
#     max_retries: int = 3


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