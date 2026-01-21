import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import Flask, jsonify, request


app = Flask(__name__)


def get_env(name, default=None):
    value = os.getenv(name, default)
    return value if value not in ("", None) else default


def build_html(reason, phone_number, lead_id):
    html_env = get_env("EMAIL_HTML")
    if html_env:
        return html_env

    return f"""
    <html>
      <body>
        <p>Hello,</p>
        <p>We tried to reach you by phone but could not connect.</p>
        <p><strong>Reason:</strong> {reason}</p>
        <p><strong>Phone:</strong> {phone_number or "N/A"}</p>
        <p><strong>Lead ID:</strong> {lead_id or "N/A"}</p>
        <p>Reply to this email if you'd like us to call again.</p>
      </body>
    </html>
    """


def send_email(recipient, subject, html_content):
    sender_email = get_env("EMAIL_SENDER")
    sender_password = get_env("EMAIL_PASSWORD")
    smtp_server = get_env("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(get_env("SMTP_PORT", "587"))

    if not sender_email or not sender_password:
        raise ValueError("EMAIL_SENDER and EMAIL_PASSWORD are required")

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient, msg.as_string())


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/followup")
def followup():
    secret = get_env("FOLLOWUP_WEBHOOK_SECRET")
    if secret:
        provided = request.headers.get("x-webhook-secret")
        if provided != secret:
            return jsonify({"message": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    recipient = data.get("email")
    if not recipient:
        return jsonify({"message": "Email is required"}), 400

    reason = data.get("reason", "no-answer")
    phone_number = data.get("phoneNumber")
    lead_id = data.get("leadId")

    subject = get_env("EMAIL_SUBJECT", "We tried to reach you")
    html_content = build_html(reason, phone_number, lead_id)

    try:
        send_email(recipient, subject, html_content)
    except Exception as error:
        return jsonify({"message": "Failed to send email", "error": str(error)}), 500

    return jsonify({"sent": True})


if __name__ == "__main__":
    port = int(get_env("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
