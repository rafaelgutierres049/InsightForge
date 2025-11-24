from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import chat, upload
from dotenv import load_dotenv
import os
load_dotenv()

FRONTEND_URL = os.getenv("FRONTEND_URL")
APP_ENV = os.getenv("APP_ENV")

app = FastAPI(
    title="InsightForge Backend",
    description="Backend para o projeto InsightForge (RAG + Azure + Agentes)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/info")
async def info():
    return {
        "project": "InsightForge",
        "version": "1.0.0",
        "environment": APP_ENV
    }

app.include_router(upload.router, prefix="/upload", tags=["upload"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
