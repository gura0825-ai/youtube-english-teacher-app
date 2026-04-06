import os

from dotenv import load_dotenv

load_dotenv()  # Load .env before importing routers that use env vars

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import process

app = FastAPI(title="YouTube English Teacher API", version="2.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(process.router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok"}
