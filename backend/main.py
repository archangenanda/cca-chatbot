from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from tools import chercher_faq
import os

# ── Chargement des variables d'environnement ──────────────────
load_dotenv()

# ── Initialisation du modèle via OpenRouter ───────────────────
model = ChatOpenAI(
    model="openai/gpt-4o-mini",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0.7,
    max_tokens=1000,
)

# ── Connecte les outils au modèle ─────────────────────────────
tools = [chercher_faq]
model_with_tools = model.bind_tools(tools)

# ── Test ──────────────────────────────────────────────────────
response = model_with_tools.invoke([
    SystemMessage(content="Tu es un assistant bancaire de CCA Bank. Réponds toujours en français. Utilise toujours l'outil chercher_faq pour répondre aux questions."),
    HumanMessage(content="Quels documents pour ouvrir un compte courant ?"),
])

print(response.content)