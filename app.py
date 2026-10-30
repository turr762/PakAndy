import streamlit as st
from google import genai
from PIL import Image

# Konfigurasi Halaman
st.set_page_config(page_title="Gizi Tracker AI", page_icon="🥗", layout="centered")

# Mengambil API Key dari Streamlit Secrets (jika di-deploy) atau Session State
SECRET_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

st.title("🥗 Gizi Tracker AI")
st.write("Upload atau ambil foto makanan untuk menganalisis kandungan gizinya.")

# Pilihan sumber gambar: Galeri atau Kamera
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

# Jika gambar sudah dimuat
if image is not None:
    st.image(image, caption="Gambar Makanan", use_container_width=True)
    
    if st.button("🔍 Analisis Gizi"):
        # Prioritaskan API Key dari Secrets, lalu dari input manual jika ada
        api_key_to_use = SECRET_API_KEY
        
        if not api_key_to_use:
            st.error("⚠️ API Key belum dikonfigurasi di Streamlit Secrets.")
        else:
            with st.spinner("Sedang menganalisis gizi makanan dengan Gemini AI..."):
                try:
                    client = genai.Client(api_key=api_key_to_use)
                    
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
                    
                    Gunakan format yang rapi dan mudah dibaca (bullet points / tabel).
                    """
                    
                    # Daftar model yang dicoba secara otomatis
                    candidate_models = [
                        "gemini-2.5-flash",
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
                        except Exception:
                            continue
                    
                    if response is not None:
                        st.success(f"Analisis Selesai! (Model: {used_model})")
                        st.markdown("### Hasil Analisis Gizi")
                        st.write(response.text)
                    else:
                        st.error("Gagal terhubung dengan API. Pastikan API key aktif.")
                        
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat menghubungi API: {e}")
