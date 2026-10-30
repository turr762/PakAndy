import streamlit as st
import requests
import base64
from PIL import Image
import io

st.set_page_config(page_title="Gizi Tracker AI", page_icon="🥗", layout="centered")

# Mengambil OpenRouter API Key dari Streamlit Secrets
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
            with st.spinner("Sedang menganalisis gizi makanan dengan AI..."):
                try:
                    # Konversi gambar ke JPEG & base64
                    buffered = io.BytesIO()
                    image.convert("RGB").save(buffered, format="JPEG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()

                    headers = {
                        "Authorization": f"Bearer {API_KEY}",
                        "Content-Type": "application/json"
                    }

                    # Daftar model Vision aktif di OpenRouter
                    candidate_models = [
                        "google/gemini-2.0-flash-exp:free",
                        "google/gemini-flash-1.5-exp",
                        "qwen/qwen-2-vl-72b-instruct:free",
                        "openrouter/auto"
                    ]

                    prompt_text = """
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

                    result = None
                    used_model = ""
                    last_error_msg = ""

                    for model_name in candidate_models:
                        payload = {
                            "model": model_name,
                            "messages": [
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": prompt_text},
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

                        response = requests.post(
                            "https://openrouter.ai/api/v1/chat/completions",
                            headers=headers,
                            json=payload
                        )
                        
                        res_json = response.json()

                        if "choices" in res_json and len(res_json["choices"]) > 0:
                            result = res_json
                            used_model = model_name
                            break
                        else:
                            last_error_msg = str(res_json)

                    if result:
                        st.success(f"Analisis Selesai! (Model: {used_model})")
                        st.markdown("### Hasil Analisis Gizi")
                        st.write(result["choices"][0]["message"]["content"])
                    else:
                        st.error(f"Gagal memproses dengan model pilihan. Error: {last_error_msg}")

                except Exception as e:
                    st.error(f"Terjadi kesalahan sistem: {e}")
