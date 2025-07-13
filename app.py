from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
CORS(app)
@app.route('/send-table-email', methods=['POST'])
def send_table_email():
    data = request.json
    emails = data.get('emails', [])
    subject = data.get('subject', 'Kanban Table Data')
    table = data.get('table', '')
    smtp_host = 'smtpout.secureserver.net'  # GoDaddy SMTP host (change this)
    smtp_port = 465                    # GoDaddy SMTP port (usually 465)
    smtp_user = 'sagar@sunidhiagrotech.com'       # GoDaddy email (change this)
    smtp_pass = 'Sunidhi@2025#'       # GoDaddy password (change this)

    msg = MIMEText(table, "plain", "utf-8")
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = ', '.join(emails)

    try:
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, emails, msg.as_string())
        return jsonify({'success': True, 'message': 'Email sent!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
