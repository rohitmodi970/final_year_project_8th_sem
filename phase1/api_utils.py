import logging

import requests


def calculate_aqi_from_pm25(pm25: float) -> int:
    if pm25 <= 12.0:
        aqi = (50 / 12.0) * pm25
    elif pm25 <= 35.4:
        aqi = 50 + ((100 - 50) / (35.4 - 12.1)) * (pm25 - 12.1)
    elif pm25 <= 55.4:
        aqi = 100 + ((150 - 100) / (55.4 - 35.5)) * (pm25 - 35.5)
    elif pm25 <= 150.4:
        aqi = 150 + ((200 - 150) / (150.4 - 55.5)) * (pm25 - 55.5)
    else:
        aqi = 200 + ((300 - 200) / (250.4 - 150.5)) * min(pm25 - 150.5, 99.9)
    return int(aqi)


def fetch_weather(lat: float, lon: float, api_key: str, city_name: str) -> dict:
    weather_url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&appid={api_key}"
    )
    fallback = {
        "location": city_name,
        "wind_speed_mps": 3.0,
        "wind_dir_deg": 180,
        "temperature_k": 305.15,
        "humidity_pct": 70,
        "description": "fallback",
        "source": "fallback_defaults",
    }

    try:
        response = requests.get(weather_url, timeout=20)
        response.raise_for_status()
        data = response.json()
        wind = data.get("wind", {})
        main = data.get("main", {})
        weather = data.get("weather", [{}])[0]

        return {
            "location": city_name,
            "wind_speed_mps": float(wind.get("speed", fallback["wind_speed_mps"])),
            "wind_dir_deg": int(wind.get("deg", fallback["wind_dir_deg"])),
            "temperature_k": float(main.get("temp", fallback["temperature_k"])),
            "humidity_pct": int(main.get("humidity", fallback["humidity_pct"])),
            "description": weather.get("description", fallback["description"]),
            "source": "live_openweathermap",
        }
    except Exception as exc:
        logging.warning("Weather API failed for %s: %s", city_name, exc)
        return fallback


def fetch_aqi(lat: float, lon: float, api_key: str, city_name: str) -> dict:
    aqi_url = (
        "https://api.openweathermap.org/data/2.5/air_pollution"
        f"?lat={lat}&lon={lon}&appid={api_key}"
    )
    fallback = {
        "location": city_name,
        "pm2_5_ugm3": float("nan"),
        "pm10_ugm3": float("nan"),
        "no2_ugm3": float("nan"),
        "o3_ugm3": float("nan"),
        "so2_ugm3": float("nan"),
        "co_ugm3": float("nan"),
        "openweather_aqi_1to5": -1,
        "us_epa_aqi": 100,
        "source": "fallback_defaults",
    }

    try:
        response = requests.get(aqi_url, timeout=20)
        response.raise_for_status()
        data = response.json()
        components = data["list"][0]["components"]
        pm25 = float(components["pm2_5"])
        pm10 = float(components["pm10"])
        no2 = float(components["no2"])
        o3 = float(components["o3"])
        so2 = float(components["so2"])
        co = float(components["co"])
        openweather_aqi = int(data["list"][0]["main"]["aqi"])

        return {
            "location": city_name,
            "pm2_5_ugm3": pm25,
            "pm10_ugm3": pm10,
            "no2_ugm3": no2,
            "o3_ugm3": o3,
            "so2_ugm3": so2,
            "co_ugm3": co,
            "openweather_aqi_1to5": openweather_aqi,
            "us_epa_aqi": calculate_aqi_from_pm25(pm25),
            "source": "live_openweathermap_air_pollution",
        }
    except Exception as exc:
        logging.warning("AQI API failed for %s: %s", city_name, exc)
        return fallback
