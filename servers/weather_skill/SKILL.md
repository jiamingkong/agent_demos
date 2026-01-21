---
name: weather_skill
description: Get weather data from OpenWeatherMap API.
allowed-tools:
  - get_weather
---

# Weather Skill

This skill enables the agent to fetch current weather data for a city using the OpenWeatherMap API.

## Prerequisites

- OpenWeatherMap API key (sign up at https://openweathermap.org/api)
- Set environment variable `OPENWEATHER_API_KEY` or pass via config.

## Tools

### get_weather
Get current weather for a city.

- `city`: City name (e.g., "Beijing", "New York").
- `country_code`: Optional two‑letter country code (ISO 3166) to disambiguate cities.
- `units`: Temperature units: 'metric' (Celsius), 'imperial' (Fahrenheit), or 'standard' (Kelvin). Default 'metric'.

Returns temperature, humidity, description, and other weather details.

## Notes

- Free tier of OpenWeatherMap allows 60 calls per minute.
- City names may need country code for uniqueness.
- Requires internet connection.
