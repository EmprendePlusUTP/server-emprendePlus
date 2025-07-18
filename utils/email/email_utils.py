# utils/email_utils.py
import smtplib
from email.mime.text import MIMEText
from os import getenv
from dotenv import load_dotenv

load_dotenv()

def send_welcome_email(to_email: str, name: str):
    smtp_email = getenv("SMTP_EMAIL")
    smtp_pass = getenv("SMTP_PASS")

    if not smtp_email or not smtp_pass:
        raise ValueError("SMTP credentials are not set")

    subject = "🎉 ¡Bienvenido a EmprendePlus!"
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: auto; padding: 20px; border-radius: 10px; background: #f9f9f9;">
                <h2 style="color: #4CAF50;">Hola {name},</h2>
                <p>
                    ¡Bienvenido a <strong>EmprendePlus</strong>! 🎉<br><br>
                    Nos alegra tenerte en esta comunidad de emprendedores que, como tú, están construyendo algo grande.
                </p>
                <p>
                    A partir de ahora, estamos contigo en cada venta, cada reto y cada logro.
                </p>
                <hr style="margin: 30px 0;">
                <p style="font-size: 0.9em;">
                    Si tienes preguntas o necesitas ayuda, no dudes en responder a este correo.
                </p>
                <p style="font-size: 1em; color: #4CAF50;">
                    ¡Mucho éxito! 🚀<br>
                    El equipo de EmprendePlus
                </p>
            </div>
        </body>
    </html>
    """

    msg = MIMEText(html_content, "html")
    msg["Subject"] = subject
    msg["From"] = smtp_email
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(smtp_email, smtp_pass)
        server.send_message(msg)

    print("Correo de bienvenida enviado")
