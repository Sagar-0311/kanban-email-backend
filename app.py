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
    smtp_host = 'smtp.secureserver.net'         # GoDaddy SMTP host
    smtp_port = 465                             # GoDaddy SMTP SSL port
    smtp_user = 'sagar@sunidhiagrotech.com'     # Your GoDaddy email
    smtp_pass = 'Sunidhi@2025#'                 # Your GoDaddy email password

    # -- Step 1: Save table string to temp CSV file --
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmpfile:
            tmpfile.write(table.encode('utf-8'))
            tmpfile_path = tmpfile.name
        print("[DEBUG] CSV file created:", tmpfile_path)

        # -- Step 2: Create the email message --
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = smtp_user
        msg['To'] = ', '.join(emails)
        msg.attach(MIMEText("Find attached Kanban table data as CSV.", "plain", "utf-8"))

        # -- Step 3: Attach CSV file --
        with open(tmpfile_path, "rb") as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="kanban-table.csv"')
            msg.attach(part)
        print("[DEBUG] CSV file attached.")

        # -- Step 4: Connect & Send Email with Timeout (15s) --
        print("[DEBUG] Connecting to SMTP...")
        with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=15) as server:
            print("[DEBUG] Logging in SMTP...")
            server.login(smtp_user, smtp_pass)
            print("[DEBUG] Sending mail to:", emails)
            server.sendmail(smtp_user, emails, msg.as_string())
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

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
