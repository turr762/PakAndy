import streamlit as st
from google import genai
from PIL import Image

st.set_page_config(page_title="Gizi Tracker AI", page_icon="🥗", layout="centered")

API_KEY = st.secrets.get("GEMINI_API_KEY", "")

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
        if not API_KEY:
            st.error("⚠️ GEMINI_API_KEY belum diatur di Streamlit Secrets!")
        else:
            with st.spinner("Sedang menganalisis gizi makanan..."):
                try:
                    client = genai.Client(api_key=API_KEY)

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

                    response = client.models.generate_content(
                        model="gemini-1.5-flash",
                        contents=[image, prompt]
                    )

                    if response and response.text:
                        st.success("Analisis Selesai!")
                        st.markdown("### Hasil Analisis Gizi")
                        st.write(response.text)
                    else:
                        st.error("Gagal mendapatkan respons dari Gemini API.")

                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")
