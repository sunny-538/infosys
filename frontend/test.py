# app.py
import streamlit as st
import re
import io
from PIL import Image, ImageEnhance
import time
import base64, hashlib, time
from pathlib import Path
import json
from streamlit.components.v1 import html
import streamlit.components.v1 as components
import requests
import datetime


BACKEND_URL = "http://127.0.0.1:5000"

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Profile", layout="wide")


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "downloads" not in st.session_state:
    st.session_state.downloads = 0
if "conversions" not in st.session_state:
    st.session_state.conversions = 0

if "show_profile" not in st.session_state:
    st.session_state.show_profile = False

if "generated" not in st.session_state:
    st.session_state.generated = False

if "demo_image" not in st.session_state:
    st.session_state.demo_image = None

if "demo_result" not in st.session_state:
    st.session_state.demo_result = None

if "paid" not in st.session_state:
    st.session_state.paid = False

if "ask_payment" not in st.session_state:
    st.session_state.ask_payment = False


@st.cache_data
def load_lottie(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="Toonify AI",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================================================
# LOAD BACKGROUND IMAGE (BASE64)
# ==================================================
def set_background(image_path, overlay=True):
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    gradient = (
        "linear-gradient(rgba(0,0,0,0.45), rgba(0,0,0,0.65)),"
        if overlay else ""
    )

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: {gradient}
            url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: white;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ==================================================
# GLOBAL CSS
# ==================================================
st.markdown(
    f"""
<style>

.app-header {{
    margin-top: 0.10rem;
    margin-bottom: 0.10rem;
}}

.card {{
    background: rgba(255,255,255,0.96);
    color: #1F2937;
    padding: 28px;
    border-radius: 20px;
    box-shadow: 0 30px 60px rgba(0,0,0,0.35);
}}

/* ===== SAFE GLOWING BUTTON EFFECT ===== */
.stButton > button {{
    position: relative !important;
    background: linear-gradient(135deg, #7C5CFF, #9F7BFF) !important;
    color: white !important;
    border-radius: 10px !important;
    border: none !important;
    font-weight: 600 !important;

    /* Glow */
    box-shadow: 0 0 14px rgba(124, 92, 255, 0.6);
    transition: box-shadow 0.3s ease, transform 0.2s ease;
}}

/* Hover glow */
.stButton > button:hover {{
    box-shadow: 0 0 28px rgba(124, 92, 255, 0.95);
    transform: translateY(-1px);
}}

/* Click */
.stButton > button:active {{
    box-shadow: 0 0 18px rgba(124, 92, 255, 0.8);
    transform: scale(0.97);
}}

.section {{
    padding: 3rem 2rem;
    border-radius: 20px;
    margin-bottom: 2.5rem;
}}

.section-light {{
    background: rgba(255, 255, 255, 0.95);
    color: #1F2937;
}}

.section-dark {{
    background: rgba(15, 23, 42, 0.85);
    color: #1f2937;
}}

.section-gradient {{
    background: linear-gradient(135deg, #7C5CFF, #9F7BFF);
    color: #1f2937;
}}

.animated-bg {{
    background: linear-gradient(
        -45deg,
        #7C5CFF,
        #9F7BFF,
        #22d3ee,
        #a78bfa
    );
    background-size: 400% 400%;
    animation: gradientMove 12s ease infinite;
}}

/* Animation */
@keyframes gradientMove {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}

.center {{
    text-align: center;
}}
</style>
""",
    unsafe_allow_html=True
)

# ==================================================
# SESSION STATE
# ==================================================
st.session_state.setdefault("page", "landing")
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("users", {})
st.session_state.setdefault("free_demo_used", False)

# ==================================================
# HELPERS
# ==================================================
def hash_pwd(p):
    return hashlib.sha256(p.encode()).hexdigest()

def set_page(p):
    st.session_state.page = p

# ==================================================
# HEADER
# ==================================================
def render_header():
    st.markdown('<div class="app-header">', unsafe_allow_html=True)
    c1, c2 = st.columns([7, 3])

    with c1:
        st.markdown("<h1>Toonify🖌️</h1>", unsafe_allow_html=True)

    with c2:
        b1, b2 = st.columns(2)
        if not st.session_state.logged_in:
            b1.button("Login", key="header_login", on_click=set_page, args=("login",))
            b2.button("Register", key="header_register", on_click=set_page, args=("signup",))
        else:
            b2.button("Logout", key="header_logout", on_click=set_page, args=("landing",))

    st.markdown("</div>", unsafe_allow_html=True)
# ==================================================
# IMAGE SLIDER (SAFE + 3 SECONDS)
# ==================================================
def render_slider():
    slides = [
        "assets/example1.webp",
        "assets/example2.webp",
        "assets/example3.webp",
    ]

    slides = [s for s in slides if Path(s).exists()]
    if not slides:
        return

    idx = int(time.time() / 0.8) % len(slides)
    img = Image.open(slides[idx]).resize((600, 400))

    left, right = st.columns([5, 4])

    # LEFT → IMAGE
    with left:
        st.image(img, use_container_width=False)

    # RIGHT → TEXT (NO TOP MARGIN)
    from streamlit.components.v1 import html

    with right:
        html(
        """
        <div style="
            margin-top: -8px;
            color: white;
            max-width: 420px;
            font-family: system-ui, -apple-system, BlinkMacSystemFont;
        ">
            <h1 style="margin-top:0; font-size:2.6rem;">
                Turn Photos into Cartoons 🎨
            </h1>

            <p style="font-size:1.1rem; line-height:1.6;">
                Transform your photos into stunning cartoon artwork using AI.
                Perfect for profile pictures, gifts, and creative content.
            </p>

            <ul style="font-size:1rem; line-height:1.8; padding-left:1.2rem;">
                <li>⚡ Fast AI processing</li>
                <li>🎨 Multiple cartoon styles</li>
                <li>📥 High-quality downloads</li>
                <li>🔒 Privacy-friendly</li>
            </ul>

            <p style="margin-top:14px;">
                🎁 <strong>One free demo available.</strong><br>
                Login to unlock unlimited conversions.
            </p>
        </div>
        """,
        height=420,
    )

def api_login(email, password):
    try:
        response = requests.post(
            f"{BACKEND_URL}/login",
            json={"email": email, "password": password},
            timeout=5
        )
        return response.status_code, response.json()
    except requests.exceptions.RequestException:
        return 500, {"message": "Backend not reachable"}


def api_signup(first_name, last_name, email, password):
    try:
        response = requests.post(
            f"{BACKEND_URL}/signup",
            json={
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "password": password,
            },
            timeout=5
        )
        return response.status_code, response.json()
    except requests.exceptions.RequestException:
        return 500, {"message": "Backend not reachable"}

# ==================================================
# LANDING PAGE
# ==================================================
import streamlit as st
from PIL import Image, ImageEnhance

def landing_page():
    set_background("assets/jjj.png", overlay=True)

    # ================= HERO SECTION =================
    st.markdown("<h1 class='center'>Turn Photos into Cartoons Instantly 🎨</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='center' style='font-size:1.15rem;'>AI-powered cartoon conversion for portraits, pets, and objects.</p>",
        unsafe_allow_html=True
    )

    # ================= HOW IT WORKS =================
    st.markdown("### How Toonify Works")
    c1, c2, c3 = st.columns(3)
    c1.markdown("📤 **Upload Image**  \nChoose any photo")
    c2.markdown("🎨 **AI Transformation**  \nCartoon-style rendering")
    c3.markdown("⬇️ **Download & Share**  \nSave instantly")

    # ================= PREVIEW SECTION =================
    st.markdown("### See what Toonify can do")
    render_slider()

    # ================= ABOUT SECTION (NEW) =================
    st.markdown("---")
    st.markdown(
        """
        <div class="section animated-bg" style="color:white;">
            <h2>🚀 Why Toonify AI?</h2>
            <p>
            AI-powered cartoon generation with fast, secure, and beautiful results.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


    # ================= FEATURES SECTION (NEW) =================
    st.markdown("## 🚀 Key Features")

    f1, f2, f3 = st.columns(3)

    with f1:
        st.markdown("🧠 **AI Powered**")
        st.write("Uses deep learning & image processing techniques")

    with f2:
        st.markdown("⚡ **Fast & Efficient**")
        st.write("Cartoon images generated within seconds")

    with f3:
        st.markdown("🔐 **Safe & Secure**")
        st.write("Images are not stored permanently")

    # ================= DEMO SECTION (UNCHANGED LOGIC) =================
    st.markdown("---")
    st.markdown("### 🎁 One Free Demo")

    # Initialize state safely
    if "free_demo_used" not in st.session_state:
        st.session_state.free_demo_used = False

    if "demo_generated" not in st.session_state:
        st.session_state.demo_generated = False

    if st.session_state.free_demo_used and not st.session_state.demo_generated:
        st.warning("Free demo already used. Please login to generate more images.")
    else:
        img = st.file_uploader(
            "Upload one image (JPG / PNG)",
            type=["jpg", "jpeg", "png"],
            key="demo_uploader"
        )

        if img:
            image = Image.open(img)

            if st.button("Generate Demo Cartoon", key="demo_generate"):
                cartoon = ImageEnhance.Color(image).enhance(1.4)

                st.session_state.free_demo_used = True
                st.session_state.demo_generated = True
                st.session_state.demo_original = image
                st.session_state.demo_cartoon = cartoon

    # ================= RESULT DISPLAY (UNCHANGED) =================
    if st.session_state.demo_generated:
        spacer, col1, col2, spacer2 = st.columns([1, 2, 2, 1])

        with col1:
            st.image(st.session_state.demo_original, caption="Original", width=260)

        with col2:
            st.image(st.session_state.demo_cartoon, caption="Cartoonified", width=260)

        st.markdown("")

        if st.button("⬇ Download Cartoon", key="demo_download"):
            st.warning("🔒 Please login to download this image")

    # ================= TECHNOLOGY STACK (NEW) =================
    st.markdown("---")
    st.markdown("## 🧪 Technology Behind Toonify")

    st.markdown(
        """
- **Frontend:** Streamlit, HTML, CSS  
- **Backend:** Python  
- **AI & Image Processing:** OpenCV, PIL, NumPy  
- **Enhancement Techniques:** Color adjustment, edge detection  
- **Security:** Controlled demo access & authentication  
        """
    )

    # ================= PRIVACY SECTION (NEW) =================
    st.markdown("## 🔒 Privacy & Trust")

    st.markdown(
        """
✔ Images are processed securely  
✔ No permanent image storage  
✔ No third-party sharing  
✔ Ethical and responsible AI usage  
        """
    )

    # ================= FINAL CTA =================
    st.markdown("---")
    st.markdown("## 🎨 Ready to Create Amazing Cartoons?")
    st.markdown("Try the free demo above or login to unlock full features 🚀")
        # ================= FOOTER SECTION =================
    st.markdown("---")

    f_col1, f_col2, f_col3 = st.columns([1.2, 1, 1])

    # 🔹 About Project
    with f_col1:
        st.markdown("### 🎨 Toonify AI")
        st.markdown(
            """
**Toonify AI** is an AI-based image-to-cartoon converter that transforms real
images into artistic cartoon styles using computer vision and deep learning.

This project demonstrates the practical application of AI in image processing
and creative media.
            """
        )

    # 🔹 Contact Info
    with f_col2:
        st.markdown("### 📞 Contact")
        st.markdown(
            """
📧 Email: toonify.ai@gmail.com  
🌐 Website: Toonify AI  
📍 Project Type: Academic / Demo  
            """
        )

    # 🔹 Quick Info
    with f_col3:
        st.markdown("### ℹ️ Quick Info")
        st.markdown(
            """
🔒 Secure & Private  
🎓 Final Year CSE Project  
🚀 AI Powered Application  
🖼️ Image to Cartoon Converter  
            """
        )

    st.markdown("")

    # 🔹 Copyright
    st.markdown(
        "<p style='text-align:center; font-size:0.9rem; color:gray;'>"
        "© 2025 Toonify AI | All Rights Reserved"
        "</p>",
        unsafe_allow_html=True
    )

        # ================================================================

def style_image_card(img_path, title):
    st.image(img_path, use_container_width=True)
    st.markdown(
        f"<p style='text-align:center; font-weight:600;'>{title}</p>",
        unsafe_allow_html=True
    )


# ==================================================
# LOGIN PAGE
# ==================================================
def login_page():
    set_background("assets/bn.png", overlay=True)
    st.button("⬅ Back to Home", key="back_login", on_click=set_page, args=("landing",))
    st.markdown("## Welcome back 👋")
    st.markdown("Login to continue using Toonify")

    left_col, right_col = st.columns([1.2, 1])

    with left_col:
        # 🔐 Login form here
        st.subheader("Login to Toonify")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pwd")

        if st.button("Login", key="login_btn"):
            if not email or not password:
                st.warning("Please enter email and password")
            else:
                status, response = api_login(email, password)

                if status == 200:
                    # ✅ Login success
                    st.session_state.logged_in = True
                    st.session_state.current_user = {
                        "first_name": response.get("first_name", "User"),
                        "last_name": response.get("last_name", ""),
                        "joined_on": response.get("joined_on", ""),
                    }
                    st.success("Login successful 🎉")
                    set_page("app")
                    st.rerun()
                else:
                    st.error(response.get("message", "Login failed"))

        st.markdown("### Why Login?")
        st.markdown(" 🔒 End-to-end encrypted login")
        st.markdown("🛡️ Your data is safe & private")
        st.markdown("🔐 Protected with secure authentication")
        st.markdown("✅ No data shared with third parties")

    with right_col:
        st.markdown("### 🎨 Cartoon Styles Available")

        r1c1, r1c2 = st.columns(2)
        with r1c1:
            style_image_card("assets/anime.png", "Anime Style")
        with r1c2:
            style_image_card("assets/ghibli.png", "Ghibli Style")

        r2c1, r2c2 = st.columns(2)
        with r2c1:
            style_image_card("assets/portrait.png", "Portrait Style")
        with r2c2:
            style_image_card("assets/sketch.png", "Sketch Style")



# ==================================================
# SIGNUP PAGE
# ==================================================
def password_strength(password: str):
    score = 0
    if len(password) >= 8:
        score += 1
    if re.search(r"[A-Z]", password):
        score += 1
    if re.search(r"[a-z]", password):
        score += 1
    if re.search(r"[0-9]", password):
        score += 1
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        score += 1

    if score <= 2:
        return "Weak ❌", "red"
    elif score == 3 or score == 4:
        return "Medium ⚠️", "orange"
    else:
        return "Strong ✅", "green"


def signup_page():
    set_background("assets/jjj.png", overlay=True)
    st.button("⬅ Back", key="back_signup", on_click=set_page, args=("landing",))

    left, right = st.columns([5, 4], gap="large")

    # ---------------- LEFT COLUMN → SIGNUP FORM ----------------
    with left:
        st.subheader("Create Account")

        # Name fields side by side
        fn_col, ln_col = st.columns(2)
        first_name = fn_col.text_input("First Name", key="signup_fname")
        last_name = ln_col.text_input("Last Name", key="signup_lname")

        dob = st.date_input(
            "Date of Birth",
            key="signup_dob",
            min_value=datetime.date(1999, 1, 1),
            max_value=datetime.date.today(),
        )


        email = st.text_input("Email", key="signup_email")

        p1 = st.text_input("Password", type="password", key="signup_p1")
        p2 = st.text_input("Confirm Password", type="password", key="signup_p2")

        if p1:
            strength, color = password_strength(p1)
            st.markdown(
                f"<span style='color:{color}; font-weight:600;'>Password strength: {strength}</span>",
                unsafe_allow_html=True
            )
            st.caption(
                "Use at least 8 characters with uppercase, lowercase, numbers & symbols."
            )

        if st.button("Create Account", key="signup_submit"):
            first_name = first_name.strip()
            last_name = last_name.strip()
            email = email.strip()

            if not first_name or not last_name or not email or not p1 or not p2:
                st.error("All fields are required")

            elif p1 != p2:
                st.error("Passwords do not match")

            else:
                status, response = api_signup(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=p1
                )

                if status in (200, 201):
                    st.success("Account created successfully 🎉")
                    set_page("login")
                    st.rerun()
                else:
                    st.error(response.get("message", "Signup failed"))

    # ---------------- RIGHT COLUMN → IMAGES / GIF ----------------
    with right:
        lottie_path = "assets/signup_animation.json"

        try:
            from streamlit_lottie import st_lottie
            lottie_json = load_lottie(lottie_path)

            st_lottie(
                lottie_json,
                speed=1,
                loop=True,
                quality="high",
                height=380,
                key="register_lottie",
            )

        except Exception:
            # HTML fallback (NO BLACK BARS)
            with open(lottie_path, "r", encoding="utf-8") as f:
                lottie_raw = f.read()

            html(
                f"""
                <script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>

                <div style="
                    display:flex;
                    justify-content:center;
                    align-items:center;
                    width:100%;
                    height:400px;
                    background: transparent;
                    overflow: hidden;
                ">
                    <lottie-player
                        autoplay
                        loop
                        mode="normal"
                        background="transparent"
                        style="width:100%; height:100%;"
                    >
                        {lottie_raw}
                    </lottie-player>
                </div>
                """,
                height=420,
            )

def logout():
    st.session_state.logged_in = False
    st.session_state.show_profile = False
    st.session_state.page = "landing"
    st.rerun()

def render_topbar():
    col1, col2, col3 = st.columns([3, 4, 2])

    with col2:
        st.markdown(
            """
            <div style="text-align: center;">
                <h2 style="margin-bottom: 4px;">Welcome back Santhosh!</h2>
                <p style="font-size: 14px; color: #9CA3AF;">
                    Ready to transform your images into amazing cartoons?
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        if st.button("👤 Profile"):
            st.session_state.show_profile = True


def render_profile_page():

    user_name = "santhosh"
    user_email = "santhoshpittala04@gmail.com"
    converted = 10
    downloads = 5

    html = f"""
    <style>
    body {{
        background: transparent;
    }}

    .profile-wrapper {{
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 90vh;
    }}

    .profile-card {{
        width: 900px;
        background: linear-gradient(135deg, #0F172A, #3B0764, #7C2D12);
        border-radius: 24px;
        padding: 40px 50px;
        color: white;
        box-shadow: 0 40px 80px rgba(0,0,0,0.45);
        font-family: Inter, sans-serif;
    }}

    .profile-header {{
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 30px;
    }}

    .profile-avatar {{
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background: linear-gradient(135deg, #7C5CFF, #C084FC);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 34px;
        font-weight: bold;
    }}

    .profile-name {{
        font-size: 26px;
        font-weight: 600;
    }}

    .profile-email {{
        font-size: 14px;
        color: #CBD5E1;
    }}

    .section-title {{
        font-size: 20px;
        font-weight: 600;
        margin-top: 30px;
        margin-bottom: 16px;
    }}

    .stats-grid {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        margin-bottom: 30px;
    }}

    .stat-box {{
        background: rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 20px;
    }}

    .stat-label {{
        font-size: 14px;
        color: #CBD5E1;
    }}

    .stat-value {{
        font-size: 28px;
        font-weight: 600;
        margin-top: 6px;
    }}

    .status-active {{
        color: #22C55E;
    }}

    .recent-box {{
        background: rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 18px;
        color: #93C5FD;
    }}
    </style>

    <div class="profile-wrapper">
      <div class="profile-card">

        <div class="profile-header">
          <div class="profile-avatar">👤</div>
          <div>
            <div class="profile-name">{user_name}</div>
            <div class="profile-email">{user_email}</div>
          </div>
        </div>

        <div class="section-title">📊 Activity Summary</div>
        <div class="stats-grid">
          <div class="stat-box">
            <div class="stat-label">Converted Images</div>
            <div class="stat-value">{converted}</div>
          </div>
          <div class="stat-box">
            <div class="stat-label">Downloads</div>
            <div class="stat-value">{downloads}</div>
          </div>
          <div class="stat-box">
            <div class="stat-label">Account Status</div>
            <div class="stat-value status-active">Active</div>
          </div>
        </div>

        <div class="section-title">🖼 Recent Conversions</div>
        <div class="recent-box">No images converted yet</div>

      </div>
    </div>
    """

    components.html(html, height=700)

        # ----- CENTER LOGOUT BUTTON -----
    col1, col2, col3 = st.columns([4, 2, 4])

    with col2:
        if st.button("🚪 Logout"):
            st.session_state.clear()
            st.rerun()

import streamlit.components.v1 as components
import base64

def render_profile_page():

    # ---------- USER DATA ----------
    user_name = "santhosh"
    user_email = "santhoshpittala04@gmail.com"
    converted = 10
    downloads = 3

    # ---------- LOAD LOCAL IMAGE ----------
    def img_to_base64(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    img1 = img_to_base64("assets/dush.png")
    img2 = img1
    img3 = img1

    html = f"""
    <style>
    body {{
        background: transparent;
    }}

    .profile-wrapper {{
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 90vh;
    }}

    .profile-card {{
        width: 900px;
        background: linear-gradient(135deg, #0F172A, #3B0764, #7C2D12);
        border-radius: 24px;
        padding: 40px 50px;
        color: white;
        box-shadow: 0 40px 80px rgba(0,0,0,0.45);
        font-family: Inter, sans-serif;
    }}

    .profile-header {{
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 30px;
    }}

    .profile-avatar {{
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background: linear-gradient(135deg, #7C5CFF, #C084FC);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 34px;
        font-weight: bold;
    }}

    .profile-name {{
        font-size: 26px;
        font-weight: 600;
    }}

    .profile-email {{
        font-size: 14px;
        color: #CBD5E1;
    }}

    .section-title {{
        font-size: 20px;
        font-weight: 600;
        margin-top: 30px;
        margin-bottom: 16px;
    }}

    .stats-grid {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        margin-bottom: 30px;
    }}

    .stat-box {{
        background: rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 20px;
    }}

    .stat-label {{
        font-size: 14px;
        color: #CBD5E1;
    }}

    .stat-value {{
        font-size: 28px;
        font-weight: 600;
        margin-top: 6px;
    }}

    .status-active {{
        color: #22C55E;
    }}

    .recent-box {{
        background: rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 18px;
    }}

    .recent-grid {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 14px;
        margin-bottom: 14px;
    }}

    .recent-img {{
        width: 100%;
        height: 120px;
        object-fit: cover;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.15);
    }}

    .view-more {{
        text-align: center;
        font-size: 14px;
        color: #CBD5E1;
        cursor: pointer;
    }}

    .view-more:hover {{
        color: #E9D5FF;
        text-decoration: underline;
    }}
    </style>

    <div class="profile-wrapper">
      <div class="profile-card">

        <div class="profile-header">
          <div class="profile-avatar">👤</div>
          <div>
            <div class="profile-name">{user_name}</div>
            <div class="profile-email">{user_email}</div>
          </div>
        </div>

        <div class="section-title">📊 Activity Summary</div>
        <div class="stats-grid">
          <div class="stat-box">
            <div class="stat-label">Converted Images</div>
            <div class="stat-value">{converted}</div>
          </div>
          <div class="stat-box">
            <div class="stat-label">Downloads</div>
            <div class="stat-value">{downloads}</div>
          </div>
          <div class="stat-box">
            <div class="stat-label">Account Status</div>
            <div class="stat-value status-active">Active</div>
          </div>
        </div>

        <div class="section-title">🖼 Recent Conversions</div>
        <div class="recent-box">
            <div class="recent-grid">
                <img src="data:image/png;base64,{img1}" class="recent-img"/>
                <img src="data:image/png;base64,{img2}" class="recent-img"/>
                <img src="data:image/png;base64,{img3}" class="recent-img"/>
            </div>
            <div class="view-more">View more conversions →</div>
        </div>

      </div>
    </div>
    """

    components.html(html, height=780)




def app_page():
    set_background("assets/jjj.png", overlay=True)
    render_topbar()

    if st.session_state.get("show_profile"):
        render_profile_page()

    st.markdown("### Upload an image")

    # ✅ uploaded is DEFINED HERE
    uploaded = st.file_uploader(
        "Drag & drop or click to upload",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=False,
        key="image_uploader"
    )

    style = st.radio(
        "Choose Cartoon Style",
        ["Anime", "Ghibli", "Portrait", "Sketch"],
        horizontal=True,
    )
    if uploaded is not None:
        if st.button("✨ Convert to Cartoon", key="convert_btn"):
            with st.spinner("Converting..."):

                result = convert_image_backend(uploaded, style)

                if result is not None:
                    st.session_state.demo_image = Image.open(uploaded)
                    st.session_state.demo_result = result
                    st.session_state.generated = True
                    st.session_state.conversions += 1
                else:
                    st.error("❌ Backend conversion failed")
    
    # -------- SHOW IMAGES --------
    if st.session_state.generated:
        spacer_l, col1, col2, spacer_r = st.columns([1, 2, 2, 1])

        with col1:
            st.image(
                st.session_state.demo_image,
                caption="Original",
                width=260
            )

        with col2:
            st.image(
                st.session_state.demo_result,
                caption=f"{style} Style",
                width=260
            )
def convert_image_backend(image_file, style):
    try:
        files = {
            "image": image_file
        }
        data = {
            "style": style
        }

        response = requests.post(
            f"{BACKEND_URL}/convert",
            files=files,
            data=data,
            timeout=60
        )

        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
        else:
            return None

    except Exception as e:
        print("Backend error:", e)
        return None



    # -------- SHOW IMAGES (PERSISTENT) --------
    if st.session_state.generated:
        spacer_l, col1, col2, spacer_r = st.columns([1, 2, 2, 1])

        with col1:
            st.image(
                st.session_state.demo_image,
                caption="Original",
                width=260
            )

        with col2:
            st.image(
                st.session_state.demo_result,
                caption=f"{style} Style",
                width=260
            )

        buf = io.BytesIO()
        st.session_state.demo_result.save(buf, format="PNG")

        # -------- DOWNLOAD / PAYMENT FLOW --------
        if st.session_state.paid:
            if st.download_button(
                "⬇ Download Cartoon Image",
                buf.getvalue(),
                file_name="toonified.png",
                mime="image/png",
            ):
                st.session_state.downloads += 1

        else:
            if st.button("⬇ Download Cartoon Image", key="download_btn"):
                st.session_state.ask_payment = True

            if st.session_state.ask_payment:
                st.warning("🔒 To download this image, please pay ₹50")

                col_pay, col_cancel = st.columns(2)

                with col_pay:
                    if st.button("💳 Pay ₹50", key="pay_btn"):
                        st.session_state.paid = True
                        st.session_state.ask_payment = False
                        st.success("✅ Payment successful! Download enabled.")

                with col_cancel:
                    if st.button("❌ Cancel", key="cancel_btn"):
                        st.session_state.ask_payment = False

# ==================================================
# MAIN APP (AFTER LOGIN)
# ==================================================
def main_app():
    st.title("Cartoonify Your Images")

    img = st.file_uploader(
        "Upload an image",
        type=["jpg", "jpeg", "png"],
        key="main_uploader"
    )


    if img:
        image = Image.open(img)
        st.image(image, caption="Original", width=300)

        if st.button("Generate Cartoon", key="main_generate"):
            cartoon = ImageEnhance.Color(image).enhance(1.4)
            st.image(cartoon, caption="Cartoonified", width=300)

# ==================================================
# ROUTING
# ==================================================
# 🔑 Show header ONLY on landing page

if st.session_state.page == "landing":
    render_header()


if st.session_state.page == "landing":
    landing_page()
elif st.session_state.page == "login":
    login_page()
elif st.session_state.page == "signup":
    signup_page()
elif st.session_state.page == "app":
    app_page()