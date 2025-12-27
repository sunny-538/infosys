from flask import Flask, request, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import io
import cv2
import numpy as np
from PIL import Image

app = Flask(__name__)
DB_PATH = "database.db"

# ================= DATABASE =================

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# ================= IMAGE FILTERS =================

def anime(image):
    img = cv2.bilateralFilter(image, 9, 200, 200)

    data = np.float32(img).reshape((-1, 3))
    K = 8
    _, labels, centers = cv2.kmeans(
        data, K, None,
        (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.001),
        10, cv2.KMEANS_RANDOM_CENTERS
    )

    centers = np.uint8(centers)
    quantized = centers[labels.flatten()].reshape(img.shape)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        9, 2
    )

    edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    cartoon = cv2.bitwise_and(quantized, edges)
    return cartoon

def ghibli(image):
    return cv2.bilateralFilter(image, 15, 80, 80)

def sketch(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    inv = cv2.bitwise_not(gray)
    blur = cv2.GaussianBlur(inv, (21, 21), 0)
    sketch = cv2.divide(gray, 255 - blur, scale=256)
    return cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)

def portrait(image):
    return cv2.detailEnhance(image, sigma_s=10, sigma_r=0.15)

# ================= ROUTES =================

@app.route("/", methods=["GET"])
def home():
    return {"message": "Backend running"}, 200

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    hashed_pw = generate_password_hash(data["password"], method="pbkdf2:sha256")

    try:
        conn = get_db()
        conn.execute(
            "INSERT INTO users (first_name, last_name, email, password) VALUES (?, ?, ?, ?)",
            (data["first_name"], data["last_name"], data["email"], hashed_pw)
        )
        conn.commit()
        conn.close()
        return {"message": "Signup successful"}, 201
    except sqlite3.IntegrityError:
        return {"message": "Email already registered"}, 409

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE email = ?", (data["email"],)
    ).fetchone()
    conn.close()

    if user and check_password_hash(user["password"], data["password"]):
        return {
            "message": "Login successful",
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "joined_on": user["created_at"]
        }, 200

    return {"message": "Invalid credentials"}, 401

@app.route("/convert", methods=["POST"])
def convert():
    file = request.files["image"]
    style = request.form["style"]

    image = np.array(Image.open(file).convert("RGB"))
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if style == "Anime":
        output = anime(image)
    elif style == "Ghibli":
        output = ghibli(image)
    elif style == "Sketch":
        output = sketch(image)
    else:
        output = portrait(image)

    output = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)
    result = Image.fromarray(output)

    buf = io.BytesIO()
    result.save(buf, format="PNG")
    buf.seek(0)

    return send_file(buf, mimetype="image/png")

# ================= MAIN =================

if __name__ == "__main__":
    init_db()
    app.run(debug=True)