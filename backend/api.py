from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from tools import chercher_faq
import os

# ── Chargement des variables d'environnement ──────────────────
load_dotenv()

# ── Initialisation de FastAPI ─────────────────────────────────
app = FastAPI()

# ── CORS ──────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# ── Endpoint test ─────────────────────────────────────────────
@app.get("/")
def home():
    return {"message": "Chatbot CCA Bank opérationnel !"}

# ── Endpoint principal ────────────────────────────────────────
@app.post("/chat")
def chat(request: MessageRequest):
    messages = [
        SystemMessage(content="""Tu es un assistant bancaire de CCA Bank.
        Détecte la langue du client et réponds OBLIGATOIREMENT dans cette même langue.
        Utilise l'outil chercher_faq pour répondre aux questions des clients."""),
        HumanMessage(content=request.message),
    ]
    
    response = model_with_tools.invoke(messages)
    
    if response.tool_calls:
        tool_call = response.tool_calls[0]
        tool_result = chercher_faq.invoke(tool_call["args"])
        
        # Détecte la langue du message
        mots_anglais = ["what", "how", "where", "when", "who", "open", "need", "want", "can", "do", "i"]
        langue = "English" if any(mot in request.message.lower().split() for mot in mots_anglais) else "français"
        
        messages.append(response)
        messages.append(ToolMessage(
            content=tool_result,
            tool_call_id=tool_call["id"]
        ))
        
        # Instruction explicite de traduction
        messages.append(HumanMessage(
            content=f"Using the information above, answer the client in {langue}."
        ))
        
        final_response = model_with_tools.invoke(messages)
        return {"reponse": final_response.content}
    
    return {"reponse": response.content}