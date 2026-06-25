from database import SessionLocal, Admin
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

db = SessionLocal()

admin = Admin(
    username="admin",
    password=pwd_context.hash("admin123")
)

db.add(admin)
db.commit()
db.close()

print("✅ Compte admin créé !")