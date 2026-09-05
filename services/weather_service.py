import httpx
from fastapi import HTTPException


class WeatherService:
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def get_weather(self, city: str):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:

                geo_response = await client.get(
                    "https://api.openweathermap.org/geo/1.0/direct",
                    params={
                        "q": city,
                        "limit": 1,
                        "appid": self.api_key
                    }
                )

                if geo_response.status_code == 401:
                    raise HTTPException(
                        status_code=401,
                        detail="Invalid or inactive weather API key"
                    )

                geo_response.raise_for_status()

                geo_data = geo_response.json()

                if not geo_data:
                    raise HTTPException(
                        status_code=404,
                        detail="City not found"
                    )

                latitude = geo_data[0]["lat"]
                longitude = geo_data[0]["lon"]

                weather_response = await client.get(
                    "https://api.openweathermap.org/data/2.5/weather",
                    params={
                        "lat": latitude,
                        "lon": longitude,
                        "appid": self.api_key,
                        "units": "metric"
                    }
                )

                if weather_response.status_code == 401:
                    raise HTTPException(
                        status_code=401,
                        detail="Invalid or inactive weather API key"
                    )

                weather_response.raise_for_status()

                data = weather_response.json()

                return {
                    "city": data["name"],
                    "temperature": data["main"]["temp"],
                    "description": data["weather"][0]["description"],
                    "feels_like": data["main"]["feels_like"],
                    "humidity": data["main"]["humidity"]
                }

        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="Weather API request timed out"
            )

        except httpx.RequestError:
            raise HTTPException(
                status_code=503,
                detail="Weather API is unavailable"
            )

        except httpx.HTTPStatusError:
            raise HTTPException(
                status_code=502,
                detail="Weather API returned an error"
            )