import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def envoyer_email_client(email_client: str, nom_client: str, message_admin: str, motif_plainte: str):
    """Envoie un email au client quand l'admin répond à sa plainte"""
    
    EMAIL_SENDER = os.getenv("EMAIL_SENDER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        print("❌ Variables EMAIL non configurées")
        return False
    
    try:
        # Créer le message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Réponse à votre plainte - CCA Bank"
        msg["From"] = EMAIL_SENDER
        msg["To"] = email_client
        
        # Corps de l'email en HTML
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #541454; padding: 20px; text-align: center;">
                <h1 style="color: white; margin: 0;">CCA Bank</h1>
                <p style="color: #d699d1; margin: 5px 0;">Service Client</p>
            </div>
            <div style="padding: 30px; background-color: #f9f9f9;">
                <p>Bonjour <strong>{nom_client}</strong>,</p>
                <p>Votre plainte concernant : <em>"{motif_plainte}"</em> a été traitée.</p>
                <div style="background-color: white; border-left: 4px solid #541454; padding: 15px; margin: 20px 0;">
                    <p><strong>Réponse de notre équipe :</strong></p>
                    <p>{message_admin}</p>
                </div>
                <p>Pour toute question supplémentaire, n'hésitez pas à nous contacter.</p>
                <p>Cordialement,<br><strong>L'équipe CCA Bank</strong></p>
            </div>
            <div style="background-color: #541454; padding: 10px; text-align: center;">
                <p style="color: #d699d1; font-size: 12px; margin: 0;">© 2026 CCA Bank - Tous droits réservés</p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html, "html"))
        
        # Envoyer via Gmail SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, email_client, msg.as_string())
        
        print(f"✅ Email envoyé à {email_client}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur envoi email: {e}")
        return False