from fastapi import FastAPI
from api import whatsapp

'''
Fastapi entry point
'''

app = FastAPI()

app.include_router(
    whatsapp.router,
)