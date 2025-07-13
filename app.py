from flask_cors import CORS
from flask import Flask, request, jsonify
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import tempfile
import os
import random

app = Flask(__name__)
CORS(app)

SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 465
SMTP_USER = 'satgpt2025@gmail.com'         # अपना Gmail डालें
SMTP_PASS = 'guln ujyg jzff arag'          # अपना Gmail App Password डालें (या Render में env variable से लो)

@app.route('/send-table-email', methods=['POST'])
def send_table_email():
    data = request.json
    emails = data.get('emails', [])
    subject = data.get('subject', 'Kanban Table Data')
    table = data.get('table', '')

    try:
        # Step 1: Save table string to temp CSV file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmpfile:
            tmpfile.write(table.encode('utf-8'))
            tmpfile_path = tmpfile.name
        print("[DEBUG] CSV file created:", tmpfile_path)

        # Step 2: Create the email message
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = SMTP_USER
        msg['To'] = ', '.join(emails)
        msg.attach(MIMEText("Find attached Kanban table data as CSV.", "plain", "utf-8"))

        # Step 3: Attach CSV file
        with open(tmpfile_path, "rb") as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="kanban-table.csv"')
            msg.attach(part)
        print("[DEBUG] CSV file attached.")

        # Step 4: Connect & Send Email with Timeout (15s)
        print("[DEBUG] Connecting to SMTP...")
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            print("[DEBUG] Logging in SMTP...")
            server.login(SMTP_USER, SMTP_PASS)
            print("[DEBUG] Sending mail to:", emails)
            server.sendmail(SMTP_USER, emails, msg.as_string())
            print("[DEBUG] Mail sent.")

        os.unlink(tmpfile_path)  # Cleanup
        return jsonify({'success': True, 'message': 'Email sent with attachment!'})

    except Exception as e:
        print("[ERROR] Mail sending error:", str(e))
        try:
            if tmpfile_path and os.path.exists(tmpfile_path):
                os.unlink(tmpfile_path)
        except:
            pass
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.json
    email = data.get('email')
    if not email:
        return jsonify({'success': False, 'message': 'Email required'}), 400

    # Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))
    subject = "Your OTP for Card Deletion"
    body = f"Your OTP for card deletion is: {otp}"

    try:
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = SMTP_USER
        msg['To'] = email
        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            print("[DEBUG] Logging in SMTP for OTP...")
            server.login(SMTP_USER, SMTP_PASS)
            print("[DEBUG] Sending OTP mail to:", email)
            server.sendmail(SMTP_USER, [email], msg.as_string())
            print("[DEBUG] OTP Mail sent.")

        return jsonify({'success': True, 'otp': otp})
    except Exception as e:
        print("[ERROR] OTP sending error:", str(e))
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
