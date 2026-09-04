from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx 
import os 
from dotenv import load_dotenv 

# Reads the variables in .env file and make them accessible
load_dotenv()

# Get the value from the varibale TEST_API_KEY
# (The real API key is stored in .env)
# This hides the API key from the public
weather_api_key = os.getenv("WEATHER_API_KEY")

if not weather_api_key:
    raise RuntimeError("WEATHER_API_KEY is missing")


# FastAPI is a class
# FastAPI() creates an instance (object) of the FastAPI class
# app is a variable that refers to that instance

app = FastAPI()

posts = [
    {"id": 1, "title": "First post"},
    {"id": 2, "title": "Second post"}
]


class Post(BaseModel):
    title: str

class WeatherResponse(BaseModel):
    city: str
    temperature: float
    description: str
    feels_like: str
    humidity: int


# @app.get("/") is a decorator. It tells FastAPI that the function below
# should be called when it receives a GET request to "/".

@app.get('/')
def root():
    return {"message": "Hello World!"}



# GET endpoint that returns all posts
@app.get("/posts")
def get_posts():
    return {"posts": posts}


# GET endpoint that returns one specific post
@app.get("/posts/{post_id}")
def get_post(post_id: int):
    for post in posts:
        if post["id"] == post_id:
            return post
    
    raise HTTPException(status_code=404, detail="Post not found")


@app.post("/posts", status_code=201)
def create_post(post: Post):
    if posts:
        new_id = max( p ["id"] for p in posts) + 1
    else:
        new_id = 1
    
    new_post = {
        "id": new_id,
        "title": post.title
    }

    posts.append(new_post)

    return new_post


@app.delete("/posts/{post_id}")
def delete_post(post_id: int):
    for post in posts:
        if post["id"] == post_id:
            posts.remove(post)
            return {"message": "Post deleted"}
        
    raise HTTPException(status_code=404, detail="Post not found")


# UPDATE 
@app.put("/posts/{post_id}")
def update_post(post_id: int, updated_post: Post):
    for post in posts:
        if post["id"] == post_id:
            post["title"] = updated_post.title
            return post

    raise HTTPException(status_code=404, detail="Post not found")


# Externt API-anrop med httpx
@app.get("/external-posts")

# async def gör funktionen asynkron
async def get_external_posts():

    # httpx.AsyncClient() är klienten som skcikar HTTP-requests
    async with httpx.AsyncClient() as client:

        # await client.get() väntar på svaret utan att blockera serven (synkron kod)
        response = await client.get(
            "https://jsonplaceholder.typicode.com/posts"
        )
    
    return response.json()


@app.get("/external-posts/{post_id}")
async def get_external_post(post_id: int):
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"https://jsonplaceholder.typicode.com/posts/{post_id}"
            )

        if response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail="External post not found"
            )

        response.raise_for_status()

        return response.json()

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="External API timed out"
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="External API is unavailable"
        )

    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=502,
            detail="External API returned an error"
        )
    



@app.get("/weather/{city}", response_model=WeatherResponse)
async def get_weather(city: str):
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:

            # STEP 1:
            # Send the city name to OpenWeather Geocoding API.
            # This converts, for example, "Lund" into latitude and longitude.
            geo_response = await client.get(
                "https://api.openweathermap.org/geo/1.0/direct",
                params={
                    "q": city,
                    "limit": 1,
                    "appid": weather_api_key
                }
            )

            # Check if the request to OpenWeather failed.
            geo_response.raise_for_status()

            # Convert the JSON response to Python data.
            geo_data = geo_response.json()

            # If the list is empty, OpenWeather could not find the city.
            if not geo_data:
                raise HTTPException(
                    status_code=404,
                    detail="City not found"
                )

            # Get latitude and longitude from the first result.
            latitude = geo_data[0]["lat"]
            longitude = geo_data[0]["lon"]


            # STEP 2:
            # Use latitude and longitude to request the actual weather data.
            weather_response = await client.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={
                    "lat": latitude,
                    "lon": longitude,
                    "appid": weather_api_key,
                    "units": "metric"
                }
            )

            # Handle invalid/inactive API key.
            if weather_response.status_code == 401:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or inactive weather API key"
                )

            # Check for other HTTP errors.
            weather_response.raise_for_status()

            # Convert the weather response from JSON to Python data.
            data = weather_response.json()

            # Return only the weather information that our API needs.
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