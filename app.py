import streamlit as st
import google.generativeai as genai
from PIL import Image

# Konfigurasi Halaman
st.set_page_config(
    page_title="Gizi Tracker AI",
    page_icon="🥗",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom Minimalist Styling (Clean & Zero-Slop)
st.markdown("""
    <style>
    .main {
        padding: 2rem 1rem;
    }
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.6rem 1rem;
        background-color: #FF4B4B;
        color: white;
        border: none;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #E03E3E;
        box-shadow: 0 4px 12px rgba(255, 75, 75, 0.2);
    }
    div.stRadio > label {
        font-weight: 500;
    }
    .metric-card {
        background-color: #1E1E1E;
        border: 1px solid #333333;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Mengambil API Key dari Streamlit Secrets
API_KEY = st.secrets.get("GEMINI_API_KEY", "").strip()

# Header Minimalis
st.title("🥗 Gizi Tracker AI")
st.markdown("Analisis kandungan nutrisi dan kalori makanan Anda secara instan menggunakan kecerdasan buatan.")
st.markdown("---")

# Konfigurasi API Key ke Google GenAI
if API_KEY:
    genai.configure(api_key=API_KEY)

# Pemilihan Sumber Gambar dengan Tampilan Bersih
input_mode = st.radio(
    "Pilih metode input gambar:",
    ("Upload dari Galeri", "Kamera Langsung"),
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("")

image = None

if input_mode == "Upload dari Galeri":
    uploaded_file = st.file_uploader("Pilih file gambar (JPG, PNG, WEBP)", type=["jpg", "jpeg", "png", "webp"])
    if uploaded_file:
        image = Image.open(uploaded_file)
else:
    camera_photo = st.camera_input("Ambil foto makanan langsung")
    if camera_photo:
        image = Image.open(camera_photo)

# Area Tampilan & Aksi
if image is not None:
    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        st.image(image, caption="Foto Makanan Dipilih", use_container_width=True)
    
    st.markdown("")
    
    if st.button("🔍 Mulai Analisis Gizi"):
        if not API_KEY:
            st.error("⚠️ GEMINI_API_KEY belum diatur di Streamlit Secrets.")
        else:
            with st.spinner("Menganalisis kandungan gizi dengan Gemini 3.8 Flash..."):
                try:
                    prompt = """
                    Analisis makanan dalam gambar ini secara mendetail dalam bahasa Indonesia. Berikan informasi berikut dengan terstruktur:
                    1. Nama Makanan / Hidangan
                    2. Perkiraan Porsi
                    3. Perkiraan Total Kalori (kcal)
                    4. Rincian Makronutrisi:
                       - Karbohidrat (gram)
                       - Protein (gram)
                       - Lemak (gram)
                    5. Ringkasan singkat apakah makanan ini seimbang dan saran kesehatan.

                    Gunakan format markdown yang rapi, bersih, dan mudah dibaca.
                    """
                    
                    model = genai.GenerativeModel("gemini-3.8-flash")
                    response = model.generate_content([prompt, image])
                    
                    if response and response.text:
                        st.success("Analisis Berhasil!")
                        st.markdown("---")
                        st.markdown("### 📊 Hasil Analisis Nutrisi")
                        st.markdown(response.text)
                    else:
                        st.error("Gagal mendapatkan respons dari API.")
                        
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")
