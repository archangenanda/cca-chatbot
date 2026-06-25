from fastapi import APIRouter
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from database import SessionLocal, QuestionNR, Ticket, Plainte
from tools import chercher_faq
import os

router = APIRouter()

# ── Initialisation du modèle ──────────────────────────────────
model = ChatOpenAI(
    model="openai/gpt-4o-mini",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0.7,
    max_tokens=1000,
)

tools = [chercher_faq]
model_with_tools = model.bind_tools(tools)

# ── Modèle de données ─────────────────────────────────────────
class MessageRequest(BaseModel):
    message: str

# ── Endpoint chatbot ──────────────────────────────────────────
@router.post("/")
def chat(request: MessageRequest):
    messages = [
        SystemMessage(content="""Tu es un assistant bancaire de CCA Bank.
        Détecte la langue du client et réponds OBLIGATOIREMENT dans cette même langue.
        Utilise l'outil chercher_faq pour répondre aux questions des clients.
        Si le client exprime une plainte ou réclamation, sois empathique et rassure-le."""),
        HumanMessage(content=request.message),
    ]

    # ── Détecte si c'est une plainte ──────────────────────
    if est_une_plainte(request.message):
        db = SessionLocal()
        db.add(Ticket(
            client="Client Web",
            message=request.message,
            statut="ouvert",
        ))
        db.add(Plainte(
            message=request.message,
            categorie="Général",
            statut="nouveau",
        ))
        db.commit()
        db.close()

    response = model_with_tools.invoke(messages)

    if response.tool_calls:
        tool_call   = response.tool_calls[0]
        tool_result = chercher_faq.invoke(tool_call["args"])

        if tool_result == "Je n'ai pas trouvé d'information sur ce sujet.":
            db = SessionLocal()
            db.add(QuestionNR(question=request.message))
            db.commit()
            db.close()

        mots_anglais = ["what","how","where","when","who","open","need","want","can","do","i"]
        langue = "English" if any(m in request.message.lower().split() for m in mots_anglais) else "français"

        messages.append(response)
        messages.append(ToolMessage(content=tool_result, tool_call_id=tool_call["id"]))
        messages.append(HumanMessage(content=f"Using the information above, answer the client in {langue}."))

        final_response = model_with_tools.invoke(messages)
        return {"reponse": final_response.content}

    return {"reponse": response.content}

# Mots qui indiquent une plainte
mots_plainte = [
    # Français
    "plainte", "réclamation", "reclamation", "problème", "probleme",
    "pas content", "mécontent", "mecontent", "insatisfait",
    "bug", "erreur", "bloqué", "bloque", "impossible",
    "ça ne marche pas", "ca ne marche pas", "ne fonctionne pas",
    "déçu", "decu", "scandaleux", "inacceptable", "remboursement",
    # Anglais
    "complaint", "issue", "unhappy", "problem", "not working",
    "disappointed", "unacceptable", "refund", "error", "blocked",
]

def est_une_plainte(message: str) -> bool:
    message_lower = message.lower()
    return any(mot in message_lower for mot in mots_plainte)