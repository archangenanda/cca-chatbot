import json
import os
from langchain.tools import tool

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FAQ_PATH = os.path.join(BASE_DIR, "Base_de_Connaissance", "faq.json")

@tool
def chercher_faq(question: str) -> str:
    """Cherche une réponse dans la FAQ de CCA Bank"""
    
    with open(FAQ_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    question_lower = question.lower()
    
    # Mots clés à ignorer
    mots_vides = ["pour", "quels", "comment", "est", "les", "des", "une", "un", "que", "qui", "quoi"]
    
    # Extraire les mots importants de la question
    mots_question = [
        mot for mot in question_lower.split() 
        if mot not in mots_vides and len(mot) > 2
    ]
    
    print("Mots importants :", mots_question)
    
    meilleur_score = 0
    meilleure_reponse = None
    
    for item in data:
        if not item["reponse"]:
            continue
            
        # Texte à comparer
        texte = f"{item['categorie']} {item['question']}".lower()
        
        # Compter combien de mots correspondent
        score = sum(1 for mot in mots_question if mot in texte)
        print(f"Score {item['categorie']}: {score}")
        
        if score > meilleur_score:
            meilleur_score = score
            meilleure_reponse = item["reponse"]
    
    if meilleure_reponse:
        return meilleure_reponse
        
    return "Je n'ai pas trouvé d'information sur ce sujet."