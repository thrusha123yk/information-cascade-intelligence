import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from backend directory or project root
base_dir = Path(__file__).resolve().parent.parent
env_path = base_dir / ".env"
if not env_path.exists():
    env_path = base_dir.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()
SUPABASE_TABLE = os.getenv("SUPABASE_TABLE", "articles").strip()

# Local SQLite Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{base_dir / 'cascade_intelligence.db'}")

# GDELT configuration
GDELT_TIMESPAN = os.getenv("GDELT_TIMESPAN", "24h")
MAX_GDELT_RECORDS = int(os.getenv("MAX_GDELT_RECORDS", "75"))

# RSS Feeds configuration
RSS_FEEDS = [
    ("BBC World", "https://feeds.bbci.co.uk/news/world/rss.xml"),
    ("The Guardian World", "https://www.theguardian.com/world/rss"),
    ("UN News", "https://news.un.org/feed/subscribe/en/news/all/rss.xml"),
    ("WHO News", "https://www.who.int/rss-feeds/news-english.xml")
]

# Weather Context configuration (Open-Meteo)
WEATHER_ENABLED = os.getenv("WEATHER_ENABLED", "true").lower() in ("true", "1", "yes")
WEATHER_LAT = float(os.getenv("WEATHER_LAT", "12.9141"))
WEATHER_LON = float(os.getenv("WEATHER_LON", "74.8560"))
WEATHER_LOCATION = os.getenv("WEATHER_LOCATION", "Mangaluru")

# NASA EONET / Open Science API configuration
NASA_API_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")
NASA_EONET_ENABLED = os.getenv("NASA_EONET_ENABLED", "true").lower() in ("true", "1", "yes")

# CORS Origins
CORS_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000").split(",") if origin.strip()]

# AI Agent Configuration (Google Gemini)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()
GEMINI_MODEL_ID = os.getenv("GEMINI_MODEL_ID", "gemini-3.5-flash-lite").strip()
