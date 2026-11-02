import streamlit as st
import google.generativeai as genai
from PIL import Image

# Konfigurasi Halaman
st.set_page_config(
    page_title="Gizi Tracker",
    page_icon="🥗",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS Kustom Tingkat Lanjut (Estetik & Modern Dark Mode)
st.markdown("""
    <style>
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
    }
    
    .hero-container {
        background: linear-gradient(135deg, #161b22 0%, #1f6feb22 100%);
        border: 1px solid #30363d;
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 24px rgba(0,0,0,0.4);
    }
    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #58a6ff, #3fb950);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .hero-subtitle {
        color: #8b949e;
        font-size: 1rem;
    }

    .stButton > button {
        width: 100%;
        border-radius: 10px;
        font-weight: 700;
        padding: 0.75rem 1.5rem;
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
        color: white;
        border: none;
        box-shadow: 0 4px 12px rgba(35, 134, 54, 0.4);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #2ea043 0%, #3fb950 100%);
        box-shadow: 0 6px 16px rgba(63, 185, 80, 0.6);
        transform: translateY(-2px);
    }

    .result-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1.5rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.3);
    }
    </style>
""", unsafe_allow_html=True)

# Mengambil API Key dari Streamlit Secrets
API_KEY = st.secrets.get("GEMINI_API_KEY", "").strip()

# Header Estetik
st.markdown("""
    <div class="hero-container">
        <div class="hero-title">🥗 Gizi Tracker</div>
        <div class="hero-subtitle">Analisis makanan atau dapatkan wawasan kebugaran tubuh.</div>
    </div>
""", unsafe_allow_html=True)

if API_KEY:
    genai.configure(api_key=API_KEY)

# Pilihan Input Mode
input_mode = st.radio(
    "Pilih metode input gambar:",
    ("📁 Upload dari Galeri", "📸 Kamera Langsung"),
    horizontal=True,
)

st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

image = None

if "Galeri" in input_mode:
    uploaded_file = st.file_uploader("Format yang didukung: JPG, JPEG, PNG, WEBP", type=["jpg", "jpeg", "png", "webp"])
    if uploaded_file:
        image = Image.open(uploaded_file)
else:
    camera_photo = st.camera_input("Ambil foto objek")
    if camera_photo:
        image = Image.open(camera_photo)

if image is not None:
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        st.image(image, caption="Preview Objek", use_container_width=True)
    
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    
    if st.button("Analisis"):
        if not API_KEY:
            st.error("Terjadi error di api key")
        else:
            with st.spinner("Loading"):
                try:
                    # Prompt universal cerdas yang otomatis mendeteksi apakah itu makanan atau orang
                    prompt = """
                    Periksa gambar yang dilampirkan ini dengan teliti. 
                    - KASUS A: Jika gambar ini adalah MAKANAN/MINUMAN, berikan analisis gizi mendetail mencakup: Nama Makanan, Perkiraan Porsi, Total Kalori (kcal), Makronutrisi (Karbohidrat, Protein, Lemak dalam gram), serta ringkasan saran kesehatan.
                    - KASUS B: Jika gambar ini adalah ORANG/MANUSIA (selfie/potret), jangan hitung gizi makanan. Berikan analisis kebugaran umum secara positif dan santai mencakup: Perkiraan tingkat energi/mood, estimasi kebutuhan hidrasi harian, serta tips kebugaran/motivasi kesehatan yang relevan.

                    Gunakan bahasa Indonesia dengan format markdown yang rapi, bersih, dan menarik.
                    """
                    
                    model = genai.GenerativeModel("gemini-3.8-flash")
                    response = model.generate_content([prompt, image])
                    
                    if response and response.text:
                        st.markdown("""
                            <div class="result-box">
                                <h3>📊 Hasil Pemindaian Cerdas AI</h3>
                                <hr style="border-color: #30363d;">
                        """, unsafe_allow_html=True)
                        st.markdown(response.text)
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.error("Gagal mendapatkan respons dari API.")
                        
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")
