from fastapi import FastAPI
from messaging import messaging_routes
from fastapi.middleware.cors import CORSMiddleware

'''
Fastapi entry point
'''

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # your dashboard URL
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    messaging_routes.router,
)