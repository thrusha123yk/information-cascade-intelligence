import httpx
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any
from ..config import WEATHER_ENABLED, WEATHER_LAT, WEATHER_LON, WEATHER_LOCATION

logger = logging.getLogger(__name__)

# Weather code interpretations (WMO code)
WMO_INTERPRETATIONS = {
    0: "Clear sky",
    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    95: "Thunderstorm: Slight or moderate", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
}

async def fetch_weather_context() -> List[Dict[str, Any]]:
    """
    Collects environmental & atmospheric conditions from Open-Meteo API.
    Provides verified baseline context for weather and climate information cascades.
    """
    if not WEATHER_ENABLED:
        return []
        
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": WEATHER_LAT,
        "longitude": WEATHER_LON,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,surface_pressure",
        "timezone": "UTC"
    }
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            
        current = data.get("current", {})
        code = current.get("weather_code", 0)
        condition_desc = WMO_INTERPRETATIONS.get(code, f"Weather Code {code}")
        
        now = datetime.now(timezone.utc).isoformat()
        temp = current.get("temperature_2m", 0)
        humidity = current.get("relative_humidity_2m", 0)
        precip = current.get("precipitation", 0)
        wind = current.get("wind_speed_10m", 0)
        
        title = f"Environmental Context: {WEATHER_LOCATION} Weather Observation ({temp}°C, {condition_desc})"
        description = (
            f"Open-Meteo verified atmospheric reading at Lat {WEATHER_LAT}, Lon {WEATHER_LON} ({WEATHER_LOCATION}): "
            f"Condition: {condition_desc}, Temperature: {temp}°C, Humidity: {humidity}%, "
            f"Precipitation: {precip}mm, Wind Speed: {wind} km/h."
        )
        url_ref = f"https://open-meteo.com/en/docs?latitude={WEATHER_LAT}&longitude={WEATHER_LON}"
        
        record = {
            "title": title,
            "url": url_ref,
            "source": "Open-Meteo Environmental Network",
            "source_type": "weather_api",
            "published_at": current.get("time") or now,
            "collected_at": now,
            "description": description,
            "origin": "Open-Meteo",
            "author": "Open-Meteo API",
            "location": WEATHER_LOCATION,
            "metadata": {
                "temperature_2m": temp,
                "humidity": humidity,
                "condition": condition_desc,
                "precipitation": precip,
                "wind_speed": wind
            }
        }
        return [record]
    except Exception as exc:
        logger.warning("Open-Meteo collector encountered error: %s", exc)
        return []

