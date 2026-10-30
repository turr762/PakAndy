import streamlit as st
from google import genai
from PIL import Image

st.set_page_config(page_title="Gizi Tracker AI", page_icon="🥗", layout="centered")

# Menggunakan API Key dari Google Cloud Service Account kamu
API_KEY = "AQ.Ab8RN6K_lT8VsFXit1A6n1_4iLFKgn-D02ur7UgGSfRZ-FrqrA"
client = genai.Client(api_key=API_KEY)

st.title("🥗 Gizi Tracker AI")
st.write("Upload atau ambil foto makanan untuk menganalisis kandungan gizinya.")

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
            
            # Daftar model yang dicoba secara otomatis jika salah satu 404
            candidate_models = [
                "gemini-3.8-flash",
                "gemini-2.0-flash",
                "gemini-1.5-flash"
            ]
            
            response = None
            used_model = ""
            
            for model_name in candidate_models:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=[image, prompt]
                    )
                    used_model = model_name
                    break
                except Exception as e:
                    continue
            
            if response is not None:
                st.markdown("### Hasil Analisis Gizi")
                st.write(response.text)
            else:
                st.error("Gagal terhubung dengan semua model. Pastikan API key dan kuota API aktif.")