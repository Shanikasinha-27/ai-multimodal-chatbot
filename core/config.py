import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
load_dotenv(BASE_DIR / ".env", override=True)


class Settings:
    PROJECT_NAME: str = "Multimodal Emotional Support Chatbot"
    VERSION: str = "1.0.0"
    
    # Gemini Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
    
    # Database Configuration
    DB_TYPE: str = os.getenv("DB_TYPE", "mysql")
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "emotional_chatbot_db")
    
    # Fallback SQLite DB path
    SQLITE_DB_PATH: Path = BASE_DIR / "chatbot.db"
    
    # Backend API Configuration
    API_HOST: str = os.getenv("API_HOST", "127.0.0.1")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
    
    # Storage directories for uploaded & generated media
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    AUDIO_DIR: Path = BASE_DIR / "uploads" / "audio"
    IMAGE_DIR: Path = BASE_DIR / "uploads" / "images"
    
    # Guardrails
    ENABLE_STRICT_GUARDRAILS: bool = os.getenv("ENABLE_STRICT_GUARDRAILS", "true").lower() == "true"
    CRISIS_HELPLINE_PRIMARY: str = os.getenv(
        "CRISIS_HELPLINE_PRIMARY", 
        "988 (Suicide & Crisis Lifeline - Call/Text 24/7, Free & Confidential)"
    )
    CRISIS_HELPLINE_TEXT: str = os.getenv(
        "CRISIS_HELPLINE_TEXT", 
        "Text HOME to 741741 (Crisis Text Line - Free, 24/7 Support)"
    )

settings = Settings()

# Ensure media upload directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.AUDIO_DIR.mkdir(parents=True, exist_ok=True)
settings.IMAGE_DIR.mkdir(parents=True, exist_ok=True)
