import streamlit as st
from google import genai
from google.genai import types
import json
import os

# 1. Konfigurasi Halaman Web
st.set_page_config(
    page_title="Ultra-Curated US Creator Paraphraser",
    page_icon="🔥",
    layout="wide"
)

# 2. Inisialisasi API Google Gemini (Membaca dari Environment / Secrets)
def get_gemini_client():
    # Sistem akan membaca otomatis dari sistem environment variabel saat dideploy
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        st.error("❌ GEMINI_API_KEY tidak ditemukan! Sila masukkan API Key Anda di kolom bawah untuk mencoba lokal.")
        # Opsi input manual jika belum disetting di environment variable
        api_key = st.text_input("Masukkan Gemini API Key Anda secara manual:", type="password")
        if not api_key:
            return None
            
    return genai.Client(api_key=api_key)

# 3. Fungsi Utama dengan Sistem Kurasi Multi-Tahap Internal
def strict_creator_paraphrase(text, style_option):
    client = get_gemini_client()
    if not client:
        return None
    
    # Instruksi sistem yang memaksa AI melakukan self-editing dan kurasi super ketat
    system_instruction = (
        "You are a master American Scriptwriter, Lead Editor, and Content Retention Expert. "
        "Your standard for content is extremely high. You never produce raw or loose drafts. "
        "Your task is to rewrite the user's text and execute a rigorous internal curation loop "
        "before delivering the final output.\n\n"
        
        "CRITICAL CURATION RULES:\n"
        "1. FLOW & SYNCHRONICITY: Ensure a flawless logical thread from the very first hook line to the final conclusion. "
        "The ending must perfectly tie back to or resolve the beginning. No sudden jumps in thought.\n"
        "2. NATIVE AMERICAN CADENCE: Write in smooth, modern, conversational US English. Use active voice only. "
        "It must sound like an elite creator talking naturally, but with zero wasted words.\n"
        "3. RIGOROUS EDITING: Cut all conversational 'fluff' that doesn't add value. Every single sentence must earn its place.\n"
        "4. NO ROBOTIC TRANSITIONS: Never use words like 'Furthermore', 'Therefore', 'In conclusion'. "
        "Use seamless narrative transitions instead.\n\n"
        
        "You MUST respond ONLY in a valid JSON format with these exact keys:\n"
        "- 'rewritten_text': The final polished, hyper-curated text that flows perfectly from start to finish.\n"
        "- 'retention_score': Integer (0-100) reflecting its power to keep viewers till the very end.\n"
        "- 'readability': Comprehension level (e.g., 'Flawless & Conversational').\n"
        "- 'pacing': Tempo evaluation (e.g., 'Perfect Pacing & Seamless Flow').\n"
        "- 'curator_notes': A brief insight on how the beginning and the conclusion were synchronized for maximum impact."
    )
    
    # Menyusun konteks gaya penulisan
    if style_option == "Short-Form (TikTok/Reels/Shorts Script)":
        style_prompt = "Rewrite this into a high-retention short-form video script. It needs an instant hook, a highly synchronized core point, and a snappy punchy ending."
    elif style_option == "Engaging Narrative (YouTube/Newsletter)":
        style_prompt = "Rewrite this into a tight, highly engaging narrative flow for a full video or newsletter. The transition from introduction to conclusion must be seamless and deeply satisfying."
    else:
        style_prompt = "Rewrite this into a crystal clear, punchy, and highly effective message for an American audience. Deliver maximum value with a flawless logical thread."

    prompt = f"{style_prompt}\n\nOriginal Text:\n'{text}'"

    try:
        # Menggunakan model gemini-2.5-flash (Model Pro tercepat & terbaru pengganti Gemini 1.5 Pro)
        response = client.models.generate_content(
       model='gemini-pro-latest',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.5, 
                response_mime_type="application/json" 
            )
        )
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Terjadi kesalahan saat mengkurasi data: {e}")
        return None

# 4. Tampilan Antarmuka (UI) Aplikasi
st.title("🔥 Ultra-Curated US Creator Paraphraser")
st.write("Sistem parafrase tingkat lanjut yang menyelaraskan alur logika dari awal hingga akhir dengan standar kurasi konten kreator Amerika.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 Teks Asli / Ide Mentah")
    user_input = st.text_area(
        "Masukkan teks Bahasa Inggris yang ingin dikurasi:",
        placeholder="Type or paste your text here...",
        height=250
    )
    
    st.subheader("⚙️ Format Output")
    style = st.selectbox(
        "Pilih Format Konten:",
        [
            "Punchy & Direct (Pesan Efektif & Padat)", 
            "Short-Form (TikTok/Reels/Shorts Script)", 
            "Engaging Narrative (YouTube/Newsletter)"
        ]
    )
    
    submit_button = st.button("Curate & Polish Teks! ✨", type="primary")

with col2:
    st.subheader("💎 Hasil Akhir yang Sudah Matang")
    
    if submit_button:
        if user_input.strip() == "":
            st.warning("Silakan masukkan teks terlebih dahulu!")
        else:
            with st.spinner("Editor AI sedang menyelaraskan alur dan memotong fluff..."):
                data = strict_creator_paraphrase(user_input, style)
                
                if data:
                    st.success("**Hasil Akhir (Siap Pakai):**")
                    st.write(data['rewritten_text'])
                    st.code(data['rewritten_text'], language="text")
                    
                    st.markdown("---")
                    
                    st.subheader("📊 Quality & Flow Report")
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Retention Score", f"{data['retention_score']}%")
                    m2.metric("Readability", data['readability'])
                    m3.metric("Pacing", data['pacing'])
                    
                    st.progress(data['retention_score'] / 100)
                    st.markdown(f"🧠 **How It Was Synchronized:** {data['curator_notes']}")
    else:
        st.info("Teks yang sudah matang dan laporan penyelarasan alur akan muncul di sini.")
