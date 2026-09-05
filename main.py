from fastapi import FastAPI
from routers import weather


# FastAPI is a class.
# FastAPI() creates an instance of the FastAPI class.
app = FastAPI()


# This says to FastAPI to use all the endpoints registered in weather.router
app.include_router(weather.router)

