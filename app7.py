import os
import pickle
import joblib
import numpy as np
from flask import Flask, render_template, request, Response, session, redirect, url_for
import cv2
from insightface.app import FaceAnalysis
from sklearn.metrics.pairwise import cosine_similarity
import csv
from email.message import EmailMessage
import smtplib

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# --- Directories and files ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_IMAGE_FOLDER = os.path.join(BASE_DIR, "static", "placeholder")  # placeholder images
EMBEDDINGS_FILE_1 = os.path.join(BASE_DIR, "embeddingst1.pkl")
CSV_FILE = "user_data.csv"

EMAIL_SENDER = "youremail@gmail.com"
EMAIL_PASSWORD = "yourpassword"
TOP_K = 5  # limit matches for testing

# --- Load embeddings safely with joblib ---
if os.path.exists(EMBEDDINGS_FILE_1):
    try:
        embedding_data = joblib.load(EMBEDDINGS_FILE_1)
        embedding_list = embedding_data.get("embeddings", [])
        name_list = embedding_data.get("filenames", [])
        print(f"✅ Loaded {len(embedding_list)} embeddings")
    except Exception as e:
        print(f"❌ Failed to load embeddings: {e}")
        embedding_list, name_list = [], []
else:
    print("⚠️ No embeddings file found, starting empty.")
    embedding_list, name_list = [], []

# --- Initialize FaceAnalysis ---
face_app = FaceAnalysis(providers=['CPUExecutionProvider'])
face_app.prepare(ctx_id=0)
camera = cv2.VideoCapture(0)

# --- Helper functions ---
def save_user_data(name, phone, email):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Name', 'Phone', 'Email'])
        writer.writerow([name, phone, email])

def normalize_name(name):
    return name.replace("_", "-").lower()

def send_email_with_links(receiver_email, selected_filenames):
    msg = EmailMessage()
    msg["Subject"] = "Your Selected Face Matches"
    msg["From"] = EMAIL_SENDER
    msg["To"] = receiver_email

    html_content = "<h2>Here are your selected matches (placeholders):</h2><ul>"
    for filename in selected_filenames:
        html_content += f"<li>{filename} (placeholder)</li>"
    html_content += "</ul>"

    msg.add_alternative(html_content, subtype='html')

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"✅ Email sent to {receiver_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

# --- Routes ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/video_feed")
def video_feed():
    def generate_frames():
        while True:
            success, frame = camera.read()
            if not success:
                break
            ret, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/recognize", methods=["POST"])
def recognize():
    user_name = request.form.get("name")
    user_phone = request.form.get("phone")
    user_email = request.form.get("email")
    save_user_data(user_name, user_phone, user_email)

    # Placeholder match logic
    matches = [{"name": "Placeholder1", "score": 0.99},
               {"name": "Placeholder2", "score": 0.95}]

    return render_template("matches.html", matches=matches, email=user_email)

@app.route("/send_selected", methods=["POST"])
def send_selected():
    selected = request.form.getlist("selected_matches")
    user_email = request.form.get("email")
    if selected and user_email:
        send_email_with_links(user_email, selected)
        return "✅ Email sent (placeholder)"
    else:
        return "❌ No selection or email"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

