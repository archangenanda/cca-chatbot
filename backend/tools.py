import unicodedata
from langchain.tools import tool
from database import SessionLocal, FAQ

def normaliser(texte: str) -> str:
    """Supprime les accents et met en minuscules pour une comparaison uniforme"""
    texte = texte.lower()
    return ''.join(
        c for c in unicodedata.normalize('NFD', texte)
        if unicodedata.category(c) != 'Mn'  # Mn = caractères accentués
    )

@tool
def chercher_faq(question: str) -> str:
    """Cherche une réponse dans la FAQ de CCA Bank"""
    
    # ── Connexion à la base de données ──────────────────────────
    db = SessionLocal()
    # Récupère uniquement les FAQs qui ont une réponse non vide
    data = db.query(FAQ).filter(FAQ.reponse != None, FAQ.reponse != "").all()
    db.close()
    
    # ── Normalisation de la question ─────────────────────────────
    question_normalisee = normaliser(question)
    
    # Mots courants à ignorer (n'apportent pas de sens)
    mots_vides = ["pour", "quels", "comment", "est", "les", "des", "une", "un", 
                  "que", "qui", "quoi", "sont", "ou"]
    
    # Garde uniquement les mots significatifs (longueur > 2, pas dans mots_vides)
    mots_question = [
        mot for mot in question_normalisee.split() 
        if mot not in mots_vides and len(mot) > 2
    ]
    
    print("Mots importants :", mots_question)
    
    # ── Recherche par score de correspondance ────────────────────
    meilleur_score = 0
    meilleure_reponse = None
    
    for item in data:
        # Normalise la catégorie + question de la FAQ pour comparaison sans accents
        texte = normaliser(f"{item.categorie} {item.question}")
        
        # Compte combien de mots de la question correspondent au texte de la FAQ
        score = sum(1 for mot in mots_question if mot in texte)
        print(f"Score {item.categorie}: {score}")
        
        # Garde la meilleure correspondance
        if score > meilleur_score:
            meilleur_score = score
            meilleure_reponse = item.reponse
    
    # ── Retourne la réponse ou un message par défaut ─────────────
    if meilleure_reponse:
        return meilleure_reponse
        
    return "Je n'ai pas trouvé d'information sur ce sujet."