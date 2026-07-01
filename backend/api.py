import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from admin import router as admin_router
from chat import router as chat_router
from plaintes import router as plaintes_router

load_dotenv()

app = FastAPI(title="Chatbot CCA Bank API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://172.17.255.57:5173",
        "http://172.17.255.57:5174",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(chat_router,     prefix="/chat",     tags=["Chatbot"])
app.include_router(admin_router,    prefix="/admin",    tags=["Administration"])
app.include_router(plaintes_router, prefix="/plaintes", tags=["Plaintes"])

@app.get("/")
def home():
    return {"message": "Chatbot CCA Bank opérationnel !"}