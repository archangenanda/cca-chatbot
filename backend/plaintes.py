from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from database import SessionLocal, Plainte
from email_service import envoyer_email_client

router = APIRouter()

# ── Modèles de données ────────────────────────────────────────
class PlainteCreate(BaseModel):
    session_id:       Optional[str] = None
    nom_client:       Optional[str] = None
    email_client:     Optional[str] = None
    telephone_client: Optional[str] = None
    categorie:        Optional[str] = None
    message:          str

class PlainteUpdate(BaseModel):
    statut:        Optional[str] = None
    reponse_admin: Optional[str] = None

# ── Soumettre une plainte (depuis le chatbot) ─────────────────
@router.post("/")
def creer_plainte(data: PlainteCreate):
    db = SessionLocal()
    plainte = Plainte(
        session_id       = data.session_id,
        nom_client       = data.nom_client,
        email_client     = data.email_client,
        telephone_client = data.telephone_client,
        categorie        = data.categorie,
        message          = data.message,
    )
    db.add(plainte)
    db.commit()
    db.refresh(plainte)
    db.close()
    return {"message": "Plainte enregistrée avec succès", "id": plainte.id}

# ── Debug — compter les plaintes ──────────────────────────────
@router.get("/all/count")
def debug_plaintes():
    db = SessionLocal()
    plaintes = db.query(Plainte).all()
    count = len(plaintes)
    db.close()
    return {"total": count}

# ── Lister les plaintes avec filtre période ───────────────────
@router.get("/")
def lister_plaintes(periode: str = Query(None)):
    db = SessionLocal()
    query = db.query(Plainte)

    if periode == "jour":
        debut = datetime.now() - timedelta(days=1)
        query = query.filter(Plainte.date_soumission >= debut)
    elif periode == "semaine":
        debut = datetime.now() - timedelta(weeks=1)
        query = query.filter(Plainte.date_soumission >= debut)
    elif periode == "mois":
        debut = datetime.now() - timedelta(days=30)
        query = query.filter(Plainte.date_soumission >= debut)

    plaintes = query.order_by(Plainte.date_soumission.desc()).all()
    db.close()
    return plaintes

# ── Détail d'une plainte ──────────────────────────────────────
@router.get("/{plainte_id}")
def get_plainte(plainte_id: int):
    db = SessionLocal()
    plainte = db.query(Plainte).filter(Plainte.id == plainte_id).first()
    db.close()
    if not plainte:
        raise HTTPException(status_code=404, detail="Plainte introuvable")
    return plainte

# ── Mettre à jour statut / réponse admin et envoyer email ─────
@router.put("/{plainte_id}")
def mettre_a_jour_plainte(plainte_id: int, data: PlainteUpdate):
    db = SessionLocal()
    plainte = db.query(Plainte).filter(Plainte.id == plainte_id).first()
    if not plainte:
        db.close()
        raise HTTPException(status_code=404, detail="Plainte introuvable")

    if data.statut:
        plainte.statut = data.statut
    if data.reponse_admin is not None:
        plainte.reponse_admin = data.reponse_admin
    plainte.date_mise_a_jour = datetime.now()

    db.commit()

    # Envoyer email si réponse admin et email client disponible
    if data.reponse_admin and plainte.email_client:
        envoyer_email_client(
            email_client=plainte.email_client,
            nom_client=plainte.nom_client or "Client",
            message_admin=data.reponse_admin,
            motif_plainte=plainte.message
        )

    db.close()
    return {"message": "Plainte mise à jour"}