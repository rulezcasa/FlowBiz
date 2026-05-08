from fastapi import FastAPI
from messaging import routes

'''
Fastapi entry point
'''

app = FastAPI()

app.include_router(
    routes.router,
)