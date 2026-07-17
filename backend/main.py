from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
from chat import router as chat_router
from plaintes import router as plaintes_router
import os

# ── Chargement des variables d'environnement ──────────────────
load_dotenv()

# ── Création de l'application FastAPI ─────────────────────────
app = FastAPI(title="CCA Bank Chatbot API")

# ── Configuration CORS ─────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://archange.3il32026.com",
        "http://localhost:5173",  # dev local (Vite)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Inclusion des routers ──────────────────────────────────────
# chat.py définit @router.post("/") -> combiné au prefix "/chat" ça donne POST /chat/
app.include_router(chat_router, prefix="/chat")
app.include_router(plaintes_router, prefix="/plaintes")


# ── Route racine (health check) ────────────────────────────────
@app.get("/")
async def root():
    return {"status": "ok", "service": "CCA Bank Chatbot API"}
