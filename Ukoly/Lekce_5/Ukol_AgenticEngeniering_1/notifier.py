import smtplib
from email.message import EmailMessage
from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, NOTIFY_EMAIL


def send_reminder(todos: list) -> None:
    if not NOTIFY_EMAIL or not SMTP_USER:
        print("Notifier: SMTP není nakonfigurován, přeskakuji.")
        return

    body = "Dnešní úkoly:\n\n" + "\n".join(
        f"  [{row['id']}] {row['title']}" for row in todos
    )

    msg = EmailMessage()
    msg["Subject"] = f"TODO připomínka — {len(todos)} úkol(ů) na dnes"
    msg["From"] = SMTP_USER
    msg["To"] = NOTIFY_EMAIL
    msg.set_content(body)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

    print(f"Notifier: odesláno na {NOTIFY_EMAIL}")
