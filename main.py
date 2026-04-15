from fastapi import FastAPI
from api import whatsapp

app = FastAPI()

app.include_router(
    whatsapp.router,
)