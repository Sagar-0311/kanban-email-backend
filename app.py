from flask_cors import CORS
from flask import Flask, request, jsonify
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import tempfile
import os

app = Flask(__name__)
CORS(app)

@app.route('/send-table-email', methods=['POST'])
def send_table_email():
    data = request.json
    emails = data.get('emails', [])
    subject = data.get('subject', 'Kanban Table Data')
    table = data.get('table', '')
    smtp_host = 'smtp.secureserver.net'
    smtp_port = 465
    smtp_user = 'sagar@sunidhiagrotech.com'
    smtp_pass = 'Sunidhi@2025#'

    # --- CSV attachment create ---
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmpfile:
        tmpfile.write(table.encode('utf-8'))
        tmpfile_path = tmpfile.name

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = ', '.join(emails)
    msg.attach(MIMEText("Find attached Kanban table data as CSV.", "plain", "utf-8"))

    # Attach CSV file
    with open(tmpfile_path, "rb") as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="kanban-table.csv"')
        msg.attach(part)

    # Send mail
    try:
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, emails, msg.as_string())
        os.unlink(tmpfile_path)  # Delete temp file
        return jsonify({'success': True, 'message': 'Email sent with attachment!'})
    except Exception as e:
        os.unlink(tmpfile_path)
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
