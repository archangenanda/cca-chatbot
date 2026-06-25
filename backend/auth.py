from passlib.context import CryptContext
from jose import jwt

SECRET_KEY = "cca_bank_secret_key"
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

def verifier_mot_de_passe(mot_de_passe, hash):
    return pwd_context.verify(mot_de_passe, hash)

def hasher_mot_de_passe(mot_de_passe):
    return pwd_context.hash(mot_de_passe)

def creer_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm="HS256")

def decoder_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])