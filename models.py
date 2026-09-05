from pydantic import BaseModel


# Defines the structure of the response from our weather endpoint.
class WeatherResponse(BaseModel):
    city: str
    temperature: float
    description: str
    feels_like: float
    humidity: int
