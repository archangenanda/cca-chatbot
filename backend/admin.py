from fastapi import APIRouter, Query
from pydantic import BaseModel
from datetime import datetime, timedelta
from database import SessionLocal, Admin, FAQ, Ticket, QuestionNR
from auth import verifier_mot_de_passe, creer_token

router = APIRouter()

# ── Modèle de données Ticket ──────────────────────────────────
class TicketRequest(BaseModel):
    client  : str
    message : str
    statut  : str = "ouvert"

# ── Créer un ticket manuellement ──────────────────────────────
@router.post("/tickets")
def create_ticket(request: TicketRequest):
    db = SessionLocal()
    ticket = Ticket(
        client=request.client,
        message=request.message,
        statut=request.statut,
    )
    db.add(ticket)
    db.commit()
    db.close()
    return {"message": "Ticket créé avec succès !"}

# ── Modifier un ticket ────────────────────────────────────────
@router.put("/tickets/{ticket_id}")
def update_ticket(ticket_id: int, request: TicketRequest):
    db = SessionLocal()
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        db.close()
        return {"erreur": "Ticket introuvable"}
    ticket.client  = request.client
    ticket.message = request.message
    ticket.statut  = request.statut
    db.commit()
    db.close()
    return {"message": "Ticket modifié avec succès !"}

# ── Supprimer un ticket ───────────────────────────────────────
@router.delete("/tickets/{ticket_id}")
def delete_ticket(ticket_id: int):
    db = SessionLocal()
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        db.close()
        return {"erreur": "Ticket introuvable"}
    db.delete(ticket)
    db.commit()
    db.close()
    return {"message": "Ticket supprimé avec succès !"}

# ── Modèles de données ────────────────────────────────────────
class LoginRequest(BaseModel):
    username: str
    password: str

class FAQRequest(BaseModel):
    categorie: str
    question: str
    reponse: str

# ── Login admin ───────────────────────────────────────────────
@router.post("/login")
def admin_login(request: LoginRequest):
    db = SessionLocal()
    admin = db.query(Admin).filter(Admin.username == request.username).first()
    db.close()

    if not admin or not verifier_mot_de_passe(request.password, admin.password):
        return {"erreur": "Identifiants incorrects"}

    token = creer_token({"username": admin.username})
    return {"token": token, "message": "Connexion réussie !"}

# ── Voir toutes les FAQ ───────────────────────────────────────
@router.get("/faq")
def get_all_faq():
    db = SessionLocal()
    faqs = db.query(FAQ).all()
    db.close()
    return [
        {
            "id": f.id,
            "categorie": f.categorie,
            "question": f.question,
            "reponse": f.reponse
        }
        for f in faqs
    ]

# ── Ajouter une FAQ ───────────────────────────────────────────
@router.post("/faq")
def add_faq(request: FAQRequest):
    db = SessionLocal()
    nouvelle_faq = FAQ(
        categorie=request.categorie,
        question=request.question,
        reponse=request.reponse
    )
    db.add(nouvelle_faq)
    db.commit()
    db.close()
    return {"message": "FAQ ajoutée avec succès !"}

# ── Modifier une FAQ ──────────────────────────────────────────
@router.put("/faq/{faq_id}")
def update_faq(faq_id: int, request: FAQRequest):
    db = SessionLocal()
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        db.close()
        return {"erreur": "FAQ introuvable"}
    faq.categorie = request.categorie
    faq.question  = request.question
    faq.reponse   = request.reponse
    db.commit()
    db.close()
    return {"message": "FAQ modifiée avec succès !"}

# ── Supprimer une FAQ ─────────────────────────────────────────
@router.delete("/faq/{faq_id}")
def delete_faq(faq_id: int):
    db = SessionLocal()
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        db.close()
        return {"erreur": "FAQ introuvable"}
    db.delete(faq)
    db.commit()
    db.close()
    return {"message": "FAQ supprimée avec succès !"}

# ── Voir les tickets avec filtre période ──────────────────────
@router.get("/tickets")
def get_tickets(periode: str = Query(None)):  # jour | semaine | mois
    db = SessionLocal()
    query = db.query(Ticket)

    if periode == "jour":
        debut = datetime.now() - timedelta(days=1)
        query = query.filter(Ticket.date >= debut)
    elif periode == "semaine":
        debut = datetime.now() - timedelta(weeks=1)
        query = query.filter(Ticket.date >= debut)
    elif periode == "mois":
        debut = datetime.now() - timedelta(days=30)
        query = query.filter(Ticket.date >= debut)

    tickets = query.order_by(Ticket.date.desc()).all()
    db.close()
    return [
        {
            "id": t.id,
            "client": t.client,
            "message": t.message,
            "statut": t.statut,
            "date": str(t.date)
        }
        for t in tickets
    ]

# ── Voir les questions non reconnues ──────────────────────────
@router.get("/questions-nr")
def get_questions_nr():
    db = SessionLocal()
    questions = db.query(QuestionNR).all()
    db.close()
    return [
        {
            "id": q.id,
            "question": q.question,
            "date": str(q.date)
        }
        for q in questions
    ]