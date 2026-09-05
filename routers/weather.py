import os

from dotenv import load_dotenv
from fastapi import APIRouter

from models import WeatherResponse
from services.weather_service import WeatherService


# Read variables from the .env file
load_dotenv()


# Get the OpenWeather API key from .env
weather_api_key = os.getenv("WEATHER_API_KEY")


# Stop the application if the API key is missing
if not weather_api_key:
    raise RuntimeError("WEATHER_API_KEY is missing")


# Create the object of the class WeatherService
weather_service = WeatherService(weather_api_key)


router = APIRouter(
    prefix="/weather",
    tags=["weather"]
)

# This endpoint has one responsibility
# Get the HTTP-request and send it over to WeatherService
@router.get("/{city}", response_model=WeatherResponse)
async def get_weather(city: str):
    return await weather_service.get_weather(city)