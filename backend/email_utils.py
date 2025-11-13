import smtplib
from email.message import EmailMessage

def send_email(from_email: str, app_password: str, to_email: str, subject: str, body: str):
    try:
        print(f"📤 Отправка от {from_email} к {to_email}")

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email
        msg.set_content(body, charset="utf-8")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(from_email, app_password)
            smtp.send_message(msg)

        print("✅ Письмо отправлено!")

    except smtplib.SMTPAuthenticationError as e:
        print("❌ Ошибка авторизации:", e)
    except Exception as e:
        print("❌ Ошибка отправки:", e)