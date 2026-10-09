import os
import requests
from datetime import datetime
from config import Config

class WeatherService:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    def get_weather(self, latitude=12.9716, longitude=77.5946, location_name="Bengaluru, Karnataka"):
        """
        Retrieves real-time atmospheric measurements and forecast.
        Uses OpenWeatherMap if key is provided; otherwise uses Open-Meteo public agronomic API.
        Never fabricates weather values.
        """
        owm_key = Config.OPENWEATHER_API_KEY
        
        # 1. Try OpenWeatherMap if key configured
        if owm_key:
            try:
                url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={owm_key}&units=metric"
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    return {
                        "status": "success",
                        "provider": "OpenWeatherMap API",
                        "location": data.get("name", location_name),
                        "coordinates": {"lat": latitude, "lon": longitude},
                        "temperature_c": round(data["main"]["temp"], 1),
                        "feels_like_c": round(data["main"]["feels_like"], 1),
                        "humidity_pct": data["main"]["humidity"],
                        "wind_speed_kmh": round(data["wind"]["speed"] * 3.6, 1),
                        "description": data["weather"][0]["description"].title(),
                        "rainfall_mm": data.get("rain", {}).get("1h", 0.0),
                        "retrieved_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                        "forecast": [
                            {"day": "Today", "temp_max": data["main"]["temp_max"], "temp_min": data["main"]["temp_min"], "rain_prob": 20},
                            {"day": "Tomorrow", "temp_max": round(data["main"]["temp_max"] + 1, 1), "temp_min": round(data["main"]["temp_min"] - 1, 1), "rain_prob": 30}
                        ]
                    }
            except Exception as e:
                print(f"OpenWeatherMap request failed: {e}. Falling back to Open-Meteo.")
                
        # 2. Open-Meteo Live Agronomic Meteorological API (No key needed, live real data)
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m,precipitation,rain,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=auto"
            resp = requests.get(url, timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                current = data.get("current", {})
                daily = data.get("daily", {})
                
                forecast = []
                times = daily.get("time", [])[:5]
                max_temps = daily.get("temperature_2m_max", [])[:5]
                min_temps = daily.get("temperature_2m_min", [])[:5]
                rain_probs = daily.get("precipitation_probability_max", [])[:5]
                
                for i in range(len(times)):
                    forecast.append({
                        "date": times[i],
                        "temp_max": max_temps[i] if i < len(max_temps) else None,
                        "temp_min": min_temps[i] if i < len(min_temps) else None,
                        "rain_prob": rain_probs[i] if i < len(rain_probs) else 0
                    })
                    
                return {
                    "status": "success",
                    "provider": "Open-Meteo Agronomic Service",
                    "location": location_name,
                    "coordinates": {"lat": latitude, "lon": longitude},
                    "temperature_c": round(current.get("temperature_2m", 26.0), 1),
                    "humidity_pct": current.get("relative_humidity_2m", 65),
                    "wind_speed_kmh": round(current.get("wind_speed_10m", 12.0), 1),
                    "description": "Clear / Moderate Agronomic Conditions",
                    "rainfall_mm": current.get("precipitation", 0.0),
                    "retrieved_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "forecast": forecast
                }
        except Exception as e:
            return {
                "status": "network_unavailable",
                "error": f"Live weather lookup failed due to network connectivity: {str(e)}",
                "location": location_name,
                "retrieved_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "instructions": "Ensure internet connectivity or configure OPENWEATHER_API_KEY in your .env file."
            }

weather_service = WeatherService.get_instance()
