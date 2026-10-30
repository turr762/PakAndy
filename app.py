import streamlit as st
import google.generativeai as genai
from google.oauth2 import service_account
from PIL import Image

st.set_page_config(page_title="Gizi Tracker AI", page_icon="🥗", layout="centered")

st.title("🥗 Gizi Tracker AI")
st.write("Upload atau ambil foto makanan untuk menganalisis kandungan gizinya.")

# Menghubungkan Autentikasi Service Account dari Streamlit Secrets
@st.cache_resource
def init_gemini():
    if "gcp_service_account" in st.secrets:
        creds_info = dict(st.secrets["gcp_service_account"])
        credentials = service_account.Credentials.from_service_account_info(
            creds_info,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        genai.configure(credentials=credentials)
    else:
        st.error("⚠️ Service Account credentials belum diatur di Streamlit Secrets.")

init_gemini()

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
        with st.spinner("Sedang menganalisis gizi makanan..."):
            
            prompt = """
            Analisis makanan dalam gambar ini secara mendetail:
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
            
            candidate_models = [
                "gemini-1.5-flash",
                "gemini-1.5-pro"
            ]
            
            response = None
            used_model = ""
            last_error = ""
            
            for model_name in candidate_models:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content([prompt, image])
                    used_model = model_name
                    break
                except Exception as e:
                    last_error = str(e)
                    continue
            
            if response is not None:
                st.success(f"Analisis Selesai! (Model: {used_model})")
                st.markdown("### Hasil Analisis Gizi")
                st.write(response.text)
            else:
                st.error(f"Gagal terhubung dengan API. Detail error: {last_error}")
