# llmServer/main.py

from fastapi import FastAPI
from app.api.v1.routes import main_router

app = FastAPI()

app.include_router(main_router.router, )