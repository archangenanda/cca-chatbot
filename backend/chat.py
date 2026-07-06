from fastapi import APIRouter
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from database import SessionLocal, QuestionNR, Ticket, Plainte, Client
from tools import chercher_faq
from datetime import datetime, date
import os

router = APIRouter()

model = ChatOpenAI(
    model="openai/gpt-4o-mini",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0.7,
    max_tokens=3000,
)

tools = [chercher_faq]
model_with_tools = model.bind_tools(tools)

class MessageHistorique(BaseModel):
    role: str
    content: str

class ClientInfo(BaseModel):
    nom: str
    prenom: str
    telephone: str

class MessageRequest(BaseModel):
    message: str
    historique: list[MessageHistorique] = []
    client: ClientInfo | None = None

@router.post("/")
def chat(request: MessageRequest):

    client_id = None
    nom_client = "Client Web"
    prenom_client = ""
    telephone_client = ""

    if request.client:
        db = SessionLocal()
        nouveau_client = Client(
            nom=request.client.nom,
            prenom=request.client.prenom,
            telephone=request.client.telephone,
            date_connexion=date.today(),
            heure_connexion=datetime.now().time(),
        )
        db.add(nouveau_client)
        db.commit()
        db.refresh(nouveau_client)
        client_id = nouveau_client.id
        nom_client = request.client.nom
        prenom_client = request.client.prenom
        telephone_client = request.client.telephone
        db.close()

    # ── Construction des messages avec historique ──────────────
    messages = [
        SystemMessage(
            content=f"""Tu es un assistant bancaire de CCA Bank.
        Détecte la langue du client et réponds OBLIGATOIREMENT dans cette même langue.
        Utilise l'outil chercher_faq pour répondre aux questions des clients.
        Le client s'appelle {prenom_client} {nom_client}. Utilise son prénom pour personnaliser tes réponses.

        IMPORTANT - Guide conversationnel :
        - Si le client veut ouvrir un compte, demande-lui D'ABORD quel type de compte il souhaite ouvrir (Compte courant, Compte épargne, Compte entreprise, etc.) avant de donner les documents.
        - Si le client veut un crédit, demande-lui D'ABORD le type de structure (SARL, SA, GIC, Association, etc.) avant de donner les documents.
        - Ne donne les documents requis QU'APRÈS avoir identifié le type de compte ou de crédit.
        - Pose UNE question à la fois pour guider le client.

        Si le client exprime une plainte ou réclamation, sois empathique et rassure-le.
        Tu te souviens du contexte de la conversation et tu peux y faire référence."""
        ),
    ]

    # Ajouter l'historique
    for msg in request.historique:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            messages.append(AIMessage(content=msg.content))

    # Ajouter le message actuel
    messages.append(HumanMessage(content=request.message))

    # ── Détection de plainte ───────────────────────────────────
    if est_une_plainte(request.message):
        db = SessionLocal()
        db.add(Ticket(
            client_id=client_id,
            client=f"{prenom_client} {nom_client}".strip(),
            message=request.message,
            statut="ouvert",
        ))
        db.add(Plainte(
            client_id=client_id,
            nom_client=nom_client,
            prenom_client=prenom_client,
            telephone_client=telephone_client,
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

# ── Mots qui indiquent une plainte ────────────────────────────
mots_plainte = [
    "plainte", "réclamation", "reclamation", "problème", "probleme",
    "pas content", "mécontent", "mecontent", "insatisfait",
    "bug", "erreur", "bloqué", "bloque", "impossible",
    "ça ne marche pas", "ca ne marche pas", "ne fonctionne pas",
    "déçu", "decu", "scandaleux", "inacceptable", "remboursement",
    "complaint", "issue", "unhappy", "problem", "not working",
    "disappointed", "unacceptable", "refund", "error", "blocked",
]

def est_une_plainte(message: str) -> bool:
    message_lower = message.lower()
    return any(mot in message_lower for mot in mots_plainte)