from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# ── Connexion à PostgreSQL ────────────────────────────────────
DATABASE_URL = "postgresql://postgres:1702@localhost:5432/cca_chatbot"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ── Tables ────────────────────────────────────────────────────

class Admin(Base):
    __tablename__ = "admins"
    id       = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)

class FAQ(Base):
    __tablename__ = "faqs"
    id        = Column(Integer, primary_key=True)
    categorie = Column(String)
    question  = Column(Text)
    reponse   = Column(Text)

class QuestionNR(Base):
    __tablename__ = "questions_non_reconnues"
    id       = Column(Integer, primary_key=True)
    question = Column(Text)
    date     = Column(DateTime, default=datetime.now)

class Ticket(Base):
    __tablename__ = "tickets"
    id      = Column(Integer, primary_key=True)
    client  = Column(String, default="Client Web")
    message = Column(Text)
    statut  = Column(String, default="ouvert")
    date    = Column(DateTime, default=datetime.now)

class Plainte(Base):
    __tablename__ = "plaintes"
    id               = Column(Integer, primary_key=True)
    session_id       = Column(String(255))
    nom_client       = Column(String(255))
    email_client     = Column(String(255))
    telephone_client = Column(String(50))
    categorie        = Column(String(100))
    message          = Column(Text, nullable=False)
    statut           = Column(String(50), default="nouveau")  # nouveau | en_cours | resolu | ferme
    reponse_admin    = Column(Text)
    date_soumission  = Column(DateTime, default=datetime.now)
    date_mise_a_jour = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# ── Création des tables ───────────────────────────────────────
def init_db():
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    init_db()
    print("✅ Base de données initialisée !")