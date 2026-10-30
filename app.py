import json
import streamlit as st
from PIL import Image
from google import genai

# 1. Konfigurasi Halaman & Tema
st.set_page_config(
    page_title="KantinSehat AI",
    page_icon="🥗",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS Perbaikan Warna Teks & Background (Mendukung Dark & Light Mode Browser)
st.markdown("""
    <style>
    /* Paksa background halaman & warna teks utama */
    .stAppViewContainer, .stApp {
        background-color: #f4f8f5 !important;
        color: #18332a !important;
    }
    
    /* Paksa warna teks judul, subjudul, dan paragraf agar selalu gelap */
    h1, h2, h3, h4, h5, h6, p, span, label, div {
        color: #18332a !important;
    }
    
    /* Warna teks khusus untuk banner header */
    .main-header {
        background: linear-gradient(135deg, #176b4d, #2c9069);
        padding: 22px;
        border-radius: 18px;
        margin-bottom: 20px;
    }
    .main-header h1, .main-header div, .main-header p, .main-header span {
        color: #ffffff !important;
    }

    /* Styling Kartu Metrik */
    .metric-card {
        background: #ffffff !important;
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #e1eae4;
        box-shadow: 0 3px 10px rgba(25, 60, 41, 0.05);
        text-align: center;
    }
    .metric-card h2 {
        color: #18332a !important;
    }
    .metric-card small {
        color: #687b73 !important;
    }

    /* Styling Tab Menu */
    .stTabs [data-baseweb="tab"] p {
        color: #176b4d !important;
        font-weight: bold;
    }

    /* Styling Tombol */
    .stButton>button {
        background-color: #176b4d !important;
        color: #ffffff !important;
        border-radius: 12px;
        font-weight: bold;
        border: none;
        width: 100%;
    }
    .stButton>button p {
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Ambil API Key dari Streamlit Secrets atau Session State
SECRET_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

if "entries" not in st.session_state:
    st.session_state.entries = []
if "api_key" not in st.session_state:
    st.session_state.api_key = SECRET_API_KEY
if "daily_goal" not in st.session_state:
    st.session_state.daily_goal = 2000

# Banner Header
st.markdown("""
    <div class="main-header">
        <span style="float:right; border:1px solid rgba(255,255,255,0.4); padding:3px 8px; border-radius:12px; font-size:10px;">PROTOTIPE GEMINI AI</span>
        <div style="font-weight:bold; font-size:18px;">🥗 KantinSehat AI</div>
        <h1 style="margin-top:10px;">Kenali makananmu.<br>Bangun kebiasaan sehat.</h1>
        <p>Catat makanan kantin dengan bantuan Gemini AI Vision. Hitung kebutuhan gizi harianmu secara presisi.</p>
    </div>
""", unsafe_allow_html=True)

# Navigation Bar / Tabs
tab1, tab2, tab3, tab4 = st.tabs(["⌂ Beranda", "＋ Catat", "▥ Rekap", "◉ Profil"])

# ==================== TAB 1: BERANDA ====================
with tab1:
    st.subheader("Ringkasan Hari Ini")
    
    total_kcal = sum(e["total"] for e in st.session_state.entries)
    item_count = len(st.session_state.entries)
    goal = st.session_state.daily_goal

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <small>Asupan Tercatat</small>
                <h2 style="margin:5px 0;">{int(total_kcal)} <span style="font-size:12px;">kkal</span></h2>
                <small>Target {goal} kkal</small>
            </div>
        """, unsafe_allow_html=True)
        progress = min(1.0, total_kcal / goal) if goal > 0 else 0
        st.progress(progress)

    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <small>Jumlah Makanan</small>
                <h2 style="margin:5px 0;">{item_count} <span style="font-size:12px;">item</span></h2>
                <small>Dari jurnal hari ini</small>
            </div>
        """, unsafe_allow_html=True)

    st.write("---")
    st.subheader("Jurnal Hari Ini")
    if not st.session_state.entries:
        st.info("Belum ada makanan tercatat hari ini. Buka tab 'Catat' untuk memulai.")
    else:
        for idx, entry in enumerate(reversed(st.session_state.entries)):
            col_a, col_b = st.columns([4, 1])
            with col_a:
                st.write(f"**{entry['icon']} {entry['name']}**")
                st.caption(f"{entry['meal']} · {entry['portion']} porsi · {int(entry['total'])} kkal")
            with col_b:
                if st.button("Hapus", key=f"del_{idx}"):
                    st.session_state.entries.pop(len(st.session_state.entries) - 1 - idx)
                    st.rerun()

# ==================== TAB 2: CATAT (AI SCAN & MANUAL) ====================
with tab2:
    st.subheader("📷 Scan Foto dengan Gemini AI")
    
    input_source = st.radio("Pilih Sumber Foto:", ["Upload dari Galeri", "Kamera Langsung"], horizontal=True)
    
    image = None
    if input_source == "Kamera Langsung":
        camera_file = st.camera_input("Ambil foto makanan")
        if camera_file:
            image = Image.open(camera_file)
    else:
        uploaded_file = st.file_uploader("Pilih gambar makanan", type=["jpg", "jpeg", "png", "webp"])
        if uploaded_file:
            image = Image.open(uploaded_file)

    detected_name = ""
    detected_kcal = 350
    detected_note = ""

    if image is not None:
        st.image(image, caption="Pratinjau Foto", use_container_width=True)
        
        if st.button("✨ Analisis Foto Makanan"):
            current_api_key = st.session_state.api_key or SECRET_API_KEY
            if not current_api_key:
                st.error("⚠️ Masukkan Gemini API Key terlebih dahulu di tab **Profil** atau di Streamlit Secrets.")
            else:
                with st.spinner("Gemini AI sedang menganalisis foto makanan..."):
                    try:
                        client = genai.Client(api_key=current_api_key)
                        prompt = """
                        Analisis foto makanan/minuman ini. Kembalikan respons HANYA dalam format JSON berikut (tanpa markdown backtick):
                        {
                          "nama_makanan": "Nama makanan dalam Bahasa Indonesia",
                          "kalori_per_porsi": 350,
                          "catatan_gizi": "Ringkasan kandungan gizi singkat"
                        }
                        """
                        
                        candidate_models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
                        response = None
                        
                        for m in candidate_models:
                            try:
                                response = client.models.generate_content(
                                    model=m,
                                    contents=[image, prompt]
                                )
                                if response:
                                    break
                            except Exception:
                                continue

                        if response:
                            clean_json = response.text.replace("```json", "").replace("```", "").strip()
                            data = json.loads(clean_json)
                            detected_name = data.get("nama_makanan", "")
                            detected_kcal = int(data.get("kalori_per_porsi", 350))
                            detected_note = data.get("catatan_gizi", "")
                            
                            st.success(f"✨ Terdeteksi: {detected_name}")
                            st.info(f"💡 Catatan Gizi: {detected_note}")
                        else:
                            st.error("Gagal memproses gambar dari API.")
                    except Exception as e:
                        st.error(f"Terjadi kesalahan: {e}")

    st.write("---")
    st.subheader("🔎 Detail Simpan Jurnal")
    
    food_name = st.text_input("Nama Makanan", value=detected_name, placeholder="Contoh: Nasi Goreng, Bakso...")
    portion = st.number_input("Jumlah Porsi", min_value=0.25, max_value=10.0, value=1.0, step=0.25)
    kcal_per_portion = st.number_input("Kalori per Porsi (kkal)", min_value=0, max_value=5000, value=detected_kcal)
    meal_type = st.selectbox("Waktu Makan", ["Sarapan", "Jajan Pagi", "Makan Siang", "Jajan Sore", "Makan Malam"])
    
    total_est = int(portion * kcal_per_portion)
    st.success(f"Estimasi Total: **{total_est} kkal**")

    if st.button("＋ Simpan ke Jurnal"):
        if not food_name.strip():
            st.warning("Nama makanan tidak boleh kosong.")
        else:
            st.session_state.entries.append({
                "name": food_name.strip(),
                "icon": "🍱",
                "meal": meal_type,
                "portion": portion,
                "kcal_each": kcal_per_portion,
                "total": total_est
            })
            st.success("Berhasil disimpan ke jurnal!")
            st.rerun()

# ==================== TAB 3: REKAP ====================
with tab3:
    st.subheader("Rekap Asupan Harian")
    
    if not st.session_state.entries:
        st.info("Belum ada data rekap harian.")
    else:
        st.metric("Total Kalori Hari Ini", f"{int(total_kcal)} kkal")
        st.write("### Detail Catatan")
        for e in st.session_state.entries:
            st.write(f"• **{e['name']}** ({e['meal']}) - {e['portion']} porsi = {e['total']} kkal")

# ==================== TAB 4: PROFIL & BMR ====================
with tab4:
    st.subheader("Pengaturan Profil & API Key")
    
    api_key_input = st.text_input(
        "🔑 Gemini API Key (Opsional jika sudah ada di Secrets)",
        value=st.session_state.api_key or SECRET_API_KEY,
        type="password",
        help="API Key dari Google Cloud atau AI Studio."
    )
    if api_key_input != st.session_state.api_key:
        st.session_state.api_key = api_key_input

    st.write("---")
    st.write("### Hitung Kebutuhan Kalori (BMR & TDEE)")
    
    col_g, col_a = st.columns(2)
    with col_g:
        gender = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
    with col_a:
        age = st.number_input("Usia (Tahun)", min_value=10, max_value=100, value=16)

    col_w, col_h = st.columns(2)
    with col_w:
        weight = st.number_input("Berat Badan (kg)", min_value=20.0, max_value=300.0, value=55.0)
    with col_h:
        height = st.number_input("Tinggi Badan (cm)", min_value=80.0, max_value=250.0, value=165.0)

    goal_type = st.selectbox("Tujuan Fitness", ["Makan seimbang / Jaga BB", "Diet (Fat Loss)", "Bulking (Tambah Otot)"])

    bmr = (10 * weight) + (6.25 * height) - (5 * age) + (5 if gender == "Laki-laki" else -161)
    tdee = bmr * 1.375
    if goal_type == "Diet (Fat Loss)":
        tdee -= 400
    elif goal_type == "Bulking (Tambah Otot)":
        tdee += 350

    calculated_goal = int(tdee)
    st.session_state.daily_goal = calculated_goal

    st.info(f"💡 **BMR Kamu:** {int(bmr)} kkal\n\n🎯 **Target Kalori Harian Direkomendasikan:** {calculated_goal} kkal/hari")

    if st.button("Hapus Semua Data Jurnal"):
        st.session_state.entries = []
        st.success("Data jurnal berhasil dibersihkan.")
        st.rerun()
