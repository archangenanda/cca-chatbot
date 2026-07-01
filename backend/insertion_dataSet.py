import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from docx import Document
from database import SessionLocal, FAQ

def importer_dataset():
    # ── Ouvrir le fichier Word ─────────────────────────────
    doc = Document("DATASET_CHATBOT.docx")
    
    # ── Connexion à la base de données ────────────────────
    db = SessionLocal()

    # ── Récupérer le premier tableau du document ──────────
    table = doc.tables[0]
    
    # ── Parcourir les lignes en sautant l'en-tête (ligne 0) ──
    for row in table.rows[1:]:
        # Extraire le texte de chaque cellule
        categorie = row.cells[0].text.strip()  # 1ère colonne
        question  = row.cells[1].text.strip()  # 2ème colonne
        reponse   = row.cells[2].text.strip()  # 3ème colonne

        # ── Insérer seulement si les 3 champs sont remplis ──
        if categorie and question and reponse:
            
            # ── Vérifier si la question existe déjà ───────
            existe = db.query(FAQ).filter(FAQ.question == question).first()
            
            if existe:
                print(f"⏭️  Déjà existant : {question[:50]}...")
            else:
                db.add(FAQ(
                    categorie=categorie,
                    question=question,
                    reponse=reponse
                ))
                print(f"✅ Ajouté : {question[:50]}...")

    # ── Sauvegarder tous les enregistrements en une fois ──
    db.commit()
    db.close()
    print("\n🎉 Import terminé !")

if __name__ == "__main__":
    importer_dataset()