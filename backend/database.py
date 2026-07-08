from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey, Date, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, date, time
from dotenv import load_dotenv
import os

load_dotenv(override=False)

# ── Connexion à PostgreSQL ────────────────────────────────────
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:1702@localhost:5432/cca_chatbot")

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

# ── Table Client ──────────────────────────────────────────────
class Client(Base):
    __tablename__ = "clients"
    id               = Column(Integer, primary_key=True)
    nom              = Column(String(100), nullable=False)
    prenom           = Column(String(100), nullable=False)
    telephone        = Column(String(20), nullable=False)
    date_connexion   = Column(Date, default=date.today)
    heure_connexion  = Column(Time, default=lambda: datetime.now().time())

    # Relations
    tickets  = relationship("Ticket", back_populates="client_ref")
    plaintes = relationship("Plainte", back_populates="client_ref")

class Ticket(Base):
    __tablename__ = "tickets"
    id         = Column(Integer, primary_key=True)
    client_id  = Column(Integer, ForeignKey("clients.id"), nullable=True)
    client     = Column(String, default="Client Web")  # gardé pour compatibilité
    message    = Column(Text)
    statut     = Column(String, default="ouvert")
    date       = Column(DateTime, default=datetime.now)

    # Relation
    client_ref = relationship("Client", back_populates="tickets")

class Plainte(Base):
    __tablename__ = "plaintes"
    id               = Column(Integer, primary_key=True)
    client_id        = Column(Integer, ForeignKey("clients.id"), nullable=True)
    session_id       = Column(String(255))
    nom_client       = Column(String(255))
    prenom_client    = Column(String(255))
    telephone_client = Column(String(50))
    email_client     = Column(String(255))
    categorie        = Column(String(100))
    message          = Column(Text, nullable=False)
    statut           = Column(String(50), default="nouveau")
    reponse_admin    = Column(Text)
    date_soumission  = Column(DateTime, default=datetime.now)
    date_mise_a_jour = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relation
    client_ref = relationship("Client", back_populates="plaintes")

# ── Création des tables ───────────────────────────────────────
def init_db():
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    init_db()
    print("✅ Base de données initialisée !")