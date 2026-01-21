import os

import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather_skill", log_level="ERROR")

API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"


@mcp.tool()
def get_weather(city: str, country_code: str = "", units: str = "metric") -> str:
    """
    Get current weather for a city.

    Args:
        city: City name (e.g., "Beijing", "New York").
        country_code: Optional two‑letter country code (ISO 3166) to disambiguate cities.
        units: Temperature units: 'metric' (Celsius), 'imperial' (Fahrenheit), or 'standard' (Kelvin). Default 'metric'.

    Returns:
        Temperature, humidity, description, and other weather details.
    """
    if not API_KEY:
        return "Error: OPENWEATHER_API_KEY environment variable not set. Please set it to your OpenWeatherMap API key."

    # Build query
    query = city
    if country_code:
        query += f",{country_code}"
    params = {
        "q": query,
        "appid": API_KEY,
        "units": units,
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Extract relevant fields
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        description = data["weather"][0]["description"]
        wind_speed = data["wind"]["speed"]
        city_name = data["name"]
        country = data["sys"].get("country", "")

        unit_label = {"metric": "°C", "imperial": "°F", "standard": "K"}.get(units, "")

        result = (
            f"Weather in {city_name}, {country}:\n"
            f"  Temperature: {temp}{unit_label}\n"
            f"  Humidity: {humidity}%\n"
            f"  Conditions: {description.capitalize()}\n"
            f"  Wind speed: {wind_speed} m/s"
        )
        return result
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"
    except (KeyError, IndexError) as e:
        return f"Unexpected response format: {e}"


if __name__ == "__main__":
    mcp.run()
