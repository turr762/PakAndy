import streamlit as st
import vertexai
from vertexai.generative_models import GenerativeModel, Image as VertexImage
from google.oauth2 import service_account
import io
from PIL import Image

st.set_page_config(page_title="Gizi Tracker AI", page_icon="🥗", layout="centered")

st.title("🥗 Gizi Tracker AI")
st.write("Upload atau ambil foto makanan untuk menganalisis kandungan gizinya.")

# 1. Inisialisasi Kredensial Vertex AI dari Streamlit Secrets
@st.cache_resource
def init_vertex_ai():
    if "gcp_service_account" in st.secrets:
        creds_info = dict(st.secrets["gcp_service_account"])
        credentials = service_account.Credentials.from_service_account_info(
            creds_info,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        project_id = creds_info.get("project_id", "gemini-513203")
        
        # Inisialisasi Vertex AI
        vertexai.init(project=project_id, location="us-central1", credentials=credentials)
        return True
    else:
        st.error("⚠️ Secrets `gcp_service_account` belum diatur di Streamlit Cloud!")
        return False

is_ready = init_vertex_ai()

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
    
    if st.button("🔍 Analisis Gizi") and is_ready:
        with st.spinner("Sedang menganalisis gizi makanan via Vertex AI..."):
            try:
                # Konversi gambar PIL ke bytes untuk Vertex AI Image
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format=image.format if image.format else "JPEG")
                img_bytes = img_byte_arr.getvalue()
                
                vertex_image = VertexImage.from_data(img_bytes)

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

                # Menggunakan model Gemini resmi di Vertex AI
                model = GenerativeModel("gemini-1.5-flash-002")
                response = model.generate_content([vertex_image, prompt])

                if response and response.text:
                    st.success("Analisis Selesai! (Vertex AI)")
                    st.markdown("### Hasil Analisis Gizi")
                    st.write(response.text)
                else:
                    st.error("Gagal mendapatkan respon dari Vertex AI.")

            except Exception as e:
                st.error(f"Terjadi kesalahan saat memproses gambar: {e}")
