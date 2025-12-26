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

if "awaiting_otp" not in st.session_state:
    st.session_state.awaiting_otp = False


if "demo_image" not in st.session_state:
    st.session_state.demo_image = None

if "demo_result" not in st.session_state:
    st.session_state.demo_result = None

if "paid_for_current" not in st.session_state:
    st.session_state.paid_for_current = False

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
    .navbar {{
        position: sticky;
        top: 0;
        z-index: 9999;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 14px 36px;
        background: linear-gradient(
            135deg,
            rgba(15,23,42,0.85),
            rgba(49,46,129,0.85)
        );
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border-bottom: 1px solid rgba(255,255,255,0.15);
        box-shadow: 0 12px 30px rgba(0,0,0,0.25);
    }}

    .nav-left {{
        display: flex;
        align-items: center;
        gap: 36px;
    }}

    .nav-logo {{
        font-size: 22px;
        font-weight: 700;
        color: white;
        letter-spacing: 0.5px;
    }}

    .nav-links {{
        display: flex;
        gap: 24px;
    }}

    .nav-links a {{
        text-decoration: none;
        color: rgba(255,255,255,0.9);
        font-weight: 500;
        position: relative;
    }}

    .nav-links a::after {{
        content: "";
        position: absolute;
        width: 0%;
        height: 2px;
        bottom: -4px;
        left: 0;
        background: #9F7BFF;
        transition: width 0.3s ease;
    }}

    .nav-links a:hover::after {{
        width: 100%;
    }}

    .nav-actions {{
        display: flex;
        gap: 14px;
    }}

    .nav-actions button {{
        padding: 8px 18px;
        border-radius: 10px;
        font-weight: 600;
        border: none;
        cursor: pointer;
    }}

    .btn-login {{
        background: transparent;
        border: 1px solid rgba(255,255,255,0.5);
        color: white;
    }}

    .btn-login:hover {{
        background: rgba(255,255,255,0.15);
    }}

    .btn-register {{
        background: linear-gradient(135deg, #7C5CFF, #9F7BFF);
        color: white;
        box-shadow: 0 0 20px rgba(159,123,255,0.6);
    }}

    .btn-register:hover {{
        opacity: 0.9;
    }}

    /* Remove Streamlit default button spacing */
    .navbar .stButton {{
        margin-top: 0;
    }}
    header[data-testid="stHeader"] {{
    display: none;
    }}

    /* Optional: hide Streamlit footer */
    footer {{
        display: none;
    }}

    /* Remove extra spacing after hiding header */
    .stApp {{
        padding-top: 0;
    }}
    /* REMOVE STREAMLIT DEFAULT TOP SPACE */
   
    .block-container {{
        padding-top: 0rem !important;
        max-width: 100% !important;
    }}

    /* ================= FIXED HEADER CARD ================= */

    .app-header {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        z-index: 9999;

        background: linear-gradient(
            135deg,
            rgba(15, 23, 42, 0.96),
            rgba(49, 46, 129, 0.96)
        );

        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);

        box-shadow: 0 14px 40px rgba(0,0,0,0.45);
    }}

    .header-inner {{
        max-width: 1200px;
        margin: auto;
        padding: 16px 32px;

        display: flex;
        align-items: center;
        justify-content: space-between;
    }}

    .header-title {{
        font-size: 30px;
        font-weight: 700;
        color: white;
        margin: 0;
    }}

    .app-header .stButton > button {{
        border-radius: 12px;
        font-weight: 600;
        padding: 8px 20px;
    }}

    /* Push page content below fixed header */
    .header-spacer {{
        height: 90px;
    }}

    .card {{
        background: rgba(255,255,255,0.96);
        color: #1F2937;
        padding: 28px;
        border-radius: 20px;
        box-shadow: 0 30px 60px rgba(0,0,0,0.35);
    }}
    .glass-image-card {{
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: 22px;
            border: 1px solid rgba(255, 255, 255, 0.35);
            padding: 18px;
            box-shadow: 0 35px 70px rgba(0,0,0,0.35);
        }}

    .glass-image-card img {{
        border-radius: 16px;
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
#===========navbar==============
def render_navbar():
    components.html(
    """
    <style>
    .navbar {
        position: sticky;
        top: 0;
        z-index: 9999;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 14px 36px;
        background: linear-gradient(135deg, rgba(15,23,42,0.9), rgba(49,46,129,0.9));
        backdrop-filter: blur(14px);
        border-bottom: 1px solid rgba(255,255,255,0.15);
        font-family: Inter, sans-serif;
    }

    .nav-left {
        display: flex;
        align-items: center;
        gap: 36px;
    }

    .logo {
        font-size: 22px;
        font-weight: 700;
        color: white;
    }

    .nav-links a {
        margin-right: 24px;
        text-decoration: none;
        color: rgba(255,255,255,0.9);
        font-weight: 500;
        position: relative;
    }

    .nav-links a::after {
        content: "";
        position: absolute;
        width: 0%;
        height: 2px;
        bottom: -4px;
        left: 0;
        background: #9F7BFF;
        transition: width 0.3s ease;
    }

    .nav-links a:hover::after {
        width: 100%;
    }

    .nav-actions a {
        margin-left: 12px;
        padding: 8px 18px;
        border-radius: 10px;
        font-weight: 600;
        text-decoration: none;
    }

    .login {
        border: 1px solid rgba(255,255,255,0.5);
        color: white;
    }

    .register {
        background: linear-gradient(135deg, #7C5CFF, #9F7BFF);
        color: white;
        box-shadow: 0 0 20px rgba(159,123,255,0.6);
    }
    </style>

    <div class="navbar">
        <div class="nav-left">
            <div class="logo">✨ Toonify</div>

            <div class="nav-links">
                <a href="#home">Home</a>
                <a href="#features">Features</a>
                <a href="#technology">Technology</a>
            </div>
        </div>

        <div class="nav-actions">
            <a href="?page=login" class="login">Login</a>
            <a href="?page=signup" class="register">Register</a>
        </div>
    </div>
    """,
    height=80,
    scrolling=False
)

    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Login", key="nav_login"):
            st.session_state.current_page = "login"
            st.rerun()

    with c2:
        if st.button("Register", key="nav_register"):
            st.session_state.current_page = "signup"
            st.rerun()

    st.markdown("</div></div>", unsafe_allow_html=True)


# ==================================================
# HEADER
# ==================================================
def render_header():
    st.markdown('<div class="app-header">', unsafe_allow_html=True)
    st.markdown('<div class="header-inner">', unsafe_allow_html=True)

    col1, col2 = st.columns([6, 3])

    with col1:
        st.markdown(
            '<h1 class="header-title">✨ Toonify</h1>',
            unsafe_allow_html=True
        )

    with col2:
        b1, b2 = st.columns(2)

        if not st.session_state.logged_in:
            b1.button("Login", key="header_login", on_click=set_page, args=("login",))
            b2.button("Register", key="header_register", on_click=set_page, args=("signup",))
        else:
            b2.button("Logout", key="header_logout", on_click=set_page, args=("landing",))

    st.markdown("</div></div>", unsafe_allow_html=True)

    # spacer so content doesn't go under header
    st.markdown('<div class="header-spacer"></div>', unsafe_allow_html=True)

# ==================================================
# IMAGE SLIDER (SAFE + 3 SECONDS)
# ==================================================
def render_slider():
    slides = [
        "assets/example1.webp",
        "assets/example2.webp",
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
    st.markdown('<div id="features"></div>', unsafe_allow_html=True)
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

    st.markdown("---")

    col_text, col_image = st.columns([3, 2])  # text wider than image

    with col_text:
        # ================= TECHNOLOGY STACK =================
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

        st.markdown("## 🔒 Privacy & Trust")
        st.markdown(
            """
    ✔ Images are processed securely  
    ✔ No permanent image storage  
    ✔ No third-party sharing  
    ✔ Ethical and responsible AI usage  
            """
        )

    with col_image:
        st.markdown("<br><br><br>", unsafe_allow_html=True)  # vertical alignment
        st.image(
            "assets/cns.webp",  # single image
            use_container_width=True
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

        # ✅ --------- ADMIN LOGIN OPTION (ADDED ONLY) ---------
        st.markdown("---")
        st.markdown(
            "<p style='font-size:14px;'>Are you an admin?</p>",
            unsafe_allow_html=True
        )
        if st.button("🔑 Click here for Admin Login", key="admin_login_btn"):
            set_page("admin_login")
        # -----------------------------------------------------

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


def admin_login_page():
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
                    set_page("admin_dashboard")
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
    
def admin_dashboard_page():
    total_earnings = 12500   # ₹
    total_downloads = 342

    users = [
        {"name": "Santhosh", "email": "santhosh@gmail.com", "downloads": 120, "spent": 4500},
        {"name": "Anjali", "email": "anjali@gmail.com", "downloads": 98, "spent": 3800},
        {"name": "Rahul", "email": "rahul@gmail.com", "downloads": 124, "spent": 4200},
    ]

    html = f"""
    <style>
    .admin-wrapper {{
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 90vh;
    }}

    .admin-card {{
        width: 1000px;
        background: linear-gradient(135deg, #020617, #312E81, #4C1D95);
        border-radius: 24px;
        padding: 45px 55px;
        color: white;
        box-shadow: 0 40px 90px rgba(0,0,0,0.55);
        font-family: Inter, sans-serif;
    }}

    .admin-header {{
        display: flex;
        align-items: center;
        gap: 22px;
        margin-bottom: 35px;
    }}

    .admin-avatar {{
        width: 82px;
        height: 82px;
        border-radius: 50%;
        background: linear-gradient(135deg, #22D3EE, #6366F1);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 34px;
        font-weight: bold;
    }}

    .admin-name {{
        font-size: 28px;
        font-weight: 700;
    }}

    .admin-role {{
        font-size: 14px;
        color: #CBD5E1;
    }}

    .section-title {{
        font-size: 20px;
        font-weight: 600;
        margin: 32px 0 18px;
    }}

    .stats-grid {{
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 22px;
    }}

    .stat-box {{
        background: rgba(255,255,255,0.09);
        border-radius: 16px;
        padding: 22px;
    }}

    .stat-label {{
        font-size: 14px;
        color: #CBD5E1;
    }}

    .stat-value {{
        font-size: 30px;
        font-weight: 700;
        margin-top: 6px;
    }}

    .user-table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
    }}

    .user-table th {{
        text-align: left;
        font-size: 14px;
        color: #CBD5E1;
        padding-bottom: 12px;
    }}

    .user-table td {{
        padding: 14px 0;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        font-size: 15px;
    }}

    .money {{
        color: #22C55E;
        font-weight: 600;
    }}
    </style>

    <div class="admin-wrapper">
      <div class="admin-card">

        <div class="admin-header">
          <div class="admin-avatar">🛡️</div>
          <div>
            <div class="admin-name">Admin Dashboard</div>
            <div class="admin-role">System Administrator</div>
          </div>
        </div>

        <div class="section-title">📊 Platform Overview</div>
        <div class="stats-grid">
          <div class="stat-box">
            <div class="stat-label">Total Earnings</div>
            <div class="stat-value money">₹ {total_earnings}</div>
          </div>

          <div class="stat-box">
            <div class="stat-label">Total Downloads</div>
            <div class="stat-value">{total_downloads}</div>
          </div>
        </div>

        <div class="section-title">👥 User Activity</div>

        <table class="user-table">
          <tr>
            <th>User</th>
            <th>Email</th>
            <th>Downloads</th>
            <th>Amount Spent</th>
          </tr>
    """

    for u in users:
        html += f"""
        <tr>
            <td>{u['name']}</td>
            <td>{u['email']}</td>
            <td>{u['downloads']}</td>
            <td class="money">₹ {u['spent']}</td>
        </tr>
        """

    html += """
        </table>

      </div>
    </div>
    """

    components.html(html, height=800)


def signup_page():
    set_background("assets/babaoi.png", overlay=True)
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
        if st.button("👤 Profile", key="open_profile"):
            st.session_state.page = "profile"


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

    if st.button("⬅ Back to convert images", key="back_app"):
        st.session_state.page = "app"


# ==================================================#
def app_page():
    set_background("assets/nano.png", overlay=True)
    render_topbar()

    st.markdown("### Upload an image")

    uploaded = st.file_uploader(
        "Drag & drop or click to upload",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=False,
    )

    # 🔹 RESET PAYMENT WHEN NEW IMAGE IS UPLOADED (STEP 2)
    if uploaded:
        st.session_state.paid_for_current = False

    style = st.radio(
        "Choose Cartoon Style",
        ["Anime", "Ghibli", "Portrait", "Sketch"],
        horizontal=True,
    )

    # 🔹 LOAD LOCAL DEMO IMAGES
    local_original = Image.open("assets/real2.jpg")
    local_cartoon = Image.open("assets/dush2.png")

    # -------- CONVERT BUTTON --------
    if uploaded and st.button("✨ Convert to Cartoon", key="convert_btn"):
        with st.spinner("Converting..."):
            st.session_state.demo_image = local_original
            st.session_state.demo_result = local_cartoon
            st.session_state.generated = True
            st.session_state.conversions += 1

            # Track converted images
            if "user_data" not in st.session_state:
                st.session_state.user_data = {
                    "converted_images": [],
                    "downloads": 0
                }

            if uploaded.name not in st.session_state.user_data["converted_images"]:
                st.session_state.user_data["converted_images"].append(uploaded.name)

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

        # -------- DOWNLOAD / PAYMENT LOGIC --------
        if st.session_state.paid_for_current:
            if st.download_button(
                "⬇ Download Cartoon Image",
                buf.getvalue(),
                file_name="toonified.png",
                mime="image/png",
            ):
                st.session_state.downloads += 1
                st.session_state.paid_for_current = False  # require payment again

        else:
            st.warning("🔒 To download this image, please pay ₹50")

            if st.button("💳 Pay ₹50", key="pay_btn"):
                st.session_state.page = "payment"



import streamlit as st
import base64

import streamlit as st
import base64

def render_payment_page():
    # Initialize session state for payment flow
    if "awaiting_otp" not in st.session_state:
        st.session_state.awaiting_otp = False
    if "paid_for_current" not in st.session_state:
        st.session_state.paid_for_current = False

    def load_bg(path):
        try:
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        except:
            return ""

    BG_IMAGE = load_bg("assets/jj.png")

    # --- INJECTING YOUR CUSTOM CSS ---
    st.markdown(
        f"""
        <style>
        /* Background setup */
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)),
                        url("data:image/jpg;base64,{BG_IMAGE}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        /* Adapted Profile Card Style for Payment */
        .payment-card {{
            background: linear-gradient(135deg, #0F172A, #3B0764, #7C2D12);
            border-radius: 24px;
            padding: 40px 50px;
            color: white;
            box-shadow: 0 40px 80px rgba(0,0,0,0.45);
            font-family: 'Inter', sans-serif;
            max-width: 900px;
            margin: auto;
        }}

        .payment-header {{
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 30px;
        }}

        .payment-icon {{
            width: 70px;
            height: 70px;
            border-radius: 50%;
            background: linear-gradient(135deg, #7C5CFF, #C084FC);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 30px;
        }}

        .section-title {{
            font-size: 22px;
            font-weight: 600;
            margin-top: 10px;
            margin-bottom: 20px;
            color: #E9D5FF;
        }}

        /* Stat Box Style for Amount */
        .stat-box {{
            background: rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.1);
            text-align: center;
        }}

        .stat-label {{ font-size: 14px; color: #CBD5E1; }}
        .stat-value {{ font-size: 32px; font-weight: bold; margin-top: 6px; color: #22C55E; }}

        /* Input Styling to match dark theme */
        .stTextInput input, .stSelectbox div[data-baseweb="select"] {{
            background-color: rgba(255,255,255,0.06) !important;
            color: white !important;
            border: 1px solid rgba(255,255,255,0.15) !important;
            border-radius: 12px !important;
        }}

        .stButton button {{
            background: linear-gradient(135deg, #7C5CFF, #C084FC) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 10px 24px !important;
            font-weight: 600 !important;
            width: 100%;
            transition: all 0.3s ease;
        }}

        .stButton button:hover {{
            transform: scale(1.02);
            box-shadow: 0 10px 20px rgba(124, 92, 255, 0.3);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    # Main UI wrapper
    st.markdown('<div class="payment-card">', unsafe_allow_html=True)
    
    # Header
    st.markdown("""
        <div class="payment-header">
            <div class="payment-icon">💳</div>
            <div>
                <div style="font-size: 26px; font-weight: 600;">Secure Checkout</div>
                <div style="font-size: 14px; color: #CBD5E1;">Complete your transaction safely</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1.5], gap="large")

    with col1:
        st.markdown('<div class="section-title">Method</div>', unsafe_allow_html=True)
        payment_method = st.radio(
            "Select Method",
            ["💳 Credit/Debit Card", "📱 UPI Transfer", "👛 Digital Wallet", "🏦 Net Banking"],
            label_visibility="collapsed"
        )

        st.markdown('<br>', unsafe_allow_html=True)
        st.markdown(f"""
            <div class="stat-box">
                <div class="stat-label">Total Payable</div>
                <div class="stat-value">₹50.00</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        def payment_success():
            st.session_state.paid_for_current = True
            st.session_state.awaiting_otp = False
            st.session_state.page = "app"

        if not st.session_state.awaiting_otp:
            st.markdown('<div class="section-title">Payment Details</div>', unsafe_allow_html=True)

            if "Card" in payment_method:
                st.text_input("Card Number", placeholder="xxxx xxxx xxxx xxxx")
                c1, c2 = st.columns(2)
                with c1: st.text_input("Expiry", placeholder="MM/YY")
                with c2: st.text_input("CVV", type="password", placeholder="***")
            
            elif "UPI" in payment_method:
                st.selectbox("Select App", ["Google Pay", "PhonePe", "Paytm"])
                st.text_input("UPI ID", placeholder="user@bank")
            
            elif "Wallet" in payment_method:
                st.selectbox("Select Wallet", ["Paytm", "Amazon Pay", "MobiKwik"])
            
            else:
                st.selectbox("Select Bank", ["SBI", "HDFC", "ICICI", "Axis"])

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Verify & Pay ₹50"):
                st.session_state.awaiting_otp = True
                st.rerun()

        else:
            # OTP Step
            st.markdown('<div class="section-title">🔐 OTP Verification</div>', unsafe_allow_html=True)
            st.write("A 6-digit code was sent to your phone.")
            otp = st.text_input("Enter OTP", max_chars=6)

            if st.button("Confirm Transaction"):
                if otp == "123456":
                    payment_success()
                    st.success("Payment Verified!")
                    st.balloons()
                else:
                    st.error("Invalid OTP.")
            
            if st.button("← Back to Details"):
                st.session_state.awaiting_otp = False
                st.rerun()

    st.markdown('<div style="text-align: center; margin-top: 30px; font-size: 12px; color: #94A3B8;">🔒 Encrypted by 256-bit SSL Security</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True) # End payment-card

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

# ==================================================
# ROUTING (MAIN APP CONTROLLER)
# ==================================================

# 🔹 Initialize page state (VERY IMPORTANT)
if "page" not in st.session_state:
    st.session_state.page = "landing"

page = st.session_state.page

# 🔹 Show header ONLY on landing page
if st.session_state.page == "landing":
    render_header()
    landing_page()

elif st.session_state.page == "login":
    login_page()

elif st.session_state.page == "signup":
    signup_page()

elif st.session_state.page == "app":
    app_page()
elif st.session_state.page == "profile":
    render_profile_page()

elif st.session_state.page == "payment":
    render_payment_page()

elif page == "admin_login":
    admin_login_page()

elif page == "admin_dashboard":
    admin_dashboard_page()

