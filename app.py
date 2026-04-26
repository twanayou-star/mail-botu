from flask import Flask, render_template, jsonify
import imaplib
import email
import re

app = Flask(__name__)

# --- AYARLAR ---
IMAP_SERVER = "imap.gmail.com"
EMAIL_USER = "twanayou@gmail.com" 
EMAIL_PASS = "nqjpzkmaleglhcwt" # Boşlukları silmeden buraya yapıştır
SENDER_FILTER = "info@account.netflix.com" # ÖRNEK: Hangi adresten mail geliyorsa onu yaz (Örn: noreply@mail.instagram.com)

def mail_den_kod_cek():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")

        status, messages = mail.search(None, f'FROM "{SENDER_FILTER}"')
        
        if not messages[0]:
            return "Mail bulunamadı."

        last_msg_id = messages[0].split()[-1]
        status, data = mail.fetch(last_msg_id, '(RFC822)')
        msg = email.message_from_bytes(data[0][1])

        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
        else:
            body = msg.get_payload(decode=True).decode()

        code_match = re.search(r'\b\d{4,6}\b', body)
        mail.logout()
        
        if code_match:
            return code_match.group(0)
        else:
            return "Kod bulunamadı."
            
    except Exception as e:
        return f"Hata oluştu: {str(e)}"

@app.route('/')
def ana_sayfa():
    return render_template('index.html')

@app.route('/get-code')
def get_code():
    kod = mail_den_kod_cek()
    return jsonify({"code": kod})

if __name__ == '__main__':
    app.run(debug=True)