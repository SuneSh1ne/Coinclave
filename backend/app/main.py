from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.routers import auth, coins, users, exchange, notifications, public

# Create uploads directory if not exists
os.makedirs("uploads", exist_ok=True)

app = FastAPI(title="Coinclave API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем статику для отдачи изображений
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Routers
app.include_router(auth.router)
app.include_router(coins.router)
app.include_router(users.router)
app.include_router(exchange.router)
app.include_router(notifications.router)
app.include_router(public.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Coinclave API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}