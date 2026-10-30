import streamlit as st
import requests
import base64
from PIL import Image
import io

st.set_page_config(page_title="Gizi Tracker AI", page_icon="🥗", layout="centered")

API_KEY = st.secrets.get("OPENROUTER_API_KEY", "").strip()

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
            st.error("⚠️ OPENROUTER_API_KEY belum diatur di Streamlit Secrets!")
        else:
            with st.spinner("Sedang menganalisis gizi makanan..."):
                try:
                    # Konversi gambar ke format JPEG & base64
                    buffered = io.BytesIO()
                    image.convert("RGB").save(buffered, format="JPEG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()

                    headers = {
                        "Authorization": f"Bearer {API_KEY}",
                        "Content-Type": "application/json"
                    }
                    
                    payload = {
                        "model": "google/gemini-2.0-flash-lite-001",
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": """
                                        Analisis makanan dalam gambar ini secara mendetail:
                                        1. Nama Makanan / Hidangan.
                                        2. Perkiraan Porsi.
                                        3. Perkiraan Total Kalori (kcal).
                                        4. Rincian Makronutrisi:
                                           - Karbohidrat (gram)
                                           - Protein (gram)
                                           - Lemak (gram)
                                        5. Ringkasan singkat apakah makanan ini seimbang dan saran kesehatan.
                                        
                                        Gunakan format yang rapi dan mudah dibaca dalam bahasa Indonesia.
                                        """
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{img_str}"
                                        }
                                    }
                                ]
                            }
                        ]
                    }

                    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
                    result = response.json()

                    if "choices" in result and len(result["choices"]) > 0:
                        st.success("Analisis Selesai!")
                        st.markdown("### Hasil Analisis Gizi")
                        st.write(result["choices"][0]["message"]["content"])
                    else:
                        st.error(f"Gagal memproses. Respon server: {result}")

                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")
