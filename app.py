import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="Gizi Tracker AI", page_icon="🥗", layout="centered")

# Mengambil API Key dari Streamlit Secrets
API_KEY = st.secrets.get("GEMINI_API_KEY", "").strip()

st.title("🥗 Gizi Tracker AI")
st.write("Upload atau ambil foto makanan untuk menganalisis kandungan gizinya.")

# Konfigurasi API Key ke Google GenAI
if API_KEY:
    genai.configure(api_key=API_KEY)

option = st.radio("Pilih sumber gambar:", ("Upload dari Galeri", "Kamera Langsung"))

image = None

if option == "Upload dari Galeri":
    uploaded_file = st.file_uploader("Pilih gambar dari galeri", type=["jpg", "jpeg", "png", "webp"])
    if uploaded_file:
        image = Image.open(uploaded_file)
else:
    camera_photo = st.camera_input("Ambil foto makanan")
    if camera_photo:
        image = Image.open(camera_photo)

if image is not None:
    st.image(image, caption="Gambar Makanan", use_container_width=True)
    
    if st.button("🔍 Analisis Gizi"):
        if not API_KEY:
            st.error("⚠️ GEMINI_API_KEY belum diatur di Streamlit Secrets!")
        else:
            with st.spinner("Sedang menganalisis gizi makanan dengan Gemini..."):
                try:
                    prompt = """
                    Analisis makanan dalam gambar ini secara mendetail dalam bahasa Indonesia:
                    1. Nama Makanan / Hidangan.
                    2. Perkiraan Porsi.
                    3. Perkiraan Total Kalori (kcal).
                    4. Rincian Makronutrisi:
                       - Karbohidrat (gram)
                       - Protein (gram)
                       - Lemak (gram)
                    5. Ringkasan singkat apakah makanan ini seimbang dan saran kesehatan.

                    Gunakan format yang rapi dan mudah dibaca.
                    """
                    
                    # Menggunakan model Gemini Flash
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    response = model.generate_content([prompt, image])
                    
                    if response and response.text:
                        st.success("Analisis Selesai!")
                        st.markdown("### Hasil Analisis Gizi")
                        st.write(response.text)
                    else:
                        st.error("Gagal mendapatkan respons dari API.")
                        
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")
