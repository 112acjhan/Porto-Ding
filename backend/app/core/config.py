import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(base_dir, ".env")

class Settings(BaseSettings):
    PROJECT_NAME: str = "SME-Ops-Orchestrator"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    model_config = SettingsConfigDict(
        env_file=env_path,      
        env_file_encoding="utf-8",
        extra="ignore"
    )

    ZAI_API_KEY: str = Field("", alias="ZAI_API_KEY")
    MODEL_NAME: str = "ilmu-glm-5.1"

    # --- PostgreSQL Database ---
    PostgreSQL_USER: str = "root"
    PostgreSQL_PASSWORD: str = "test_postgresql_password"
    PostgreSQL_HOST: str = "localhost"
    PostgreSQL_PORT: int = 5432
    PostgreSQL_DB: str = "porto_ding_registry"

    # --- Google Ecosystem ---
    GOOGLE_SHEETS_JSON_PATH: str = "semiotic-vial-479900-f1-fd82833f6af5.json"
    OPERATIONAL_LEDGER_NAME: str = "Operational Ledger"

    # --- Messaging Gateways ---
    WHATSAPP_VERIFY_TOKEN: str = ""
    WHATSAPP_ACCESS_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    TELEGRAM_BOT_TOKEN: str = "test_telegram_bot_token"

    # --- Security Settings ---
    PII_MASK_CHAR: str = "X"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    SECRET_KEY: str = "test_secret_key"  # For JWT signing

# Initialize the settings object
settings = Settings()
