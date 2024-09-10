import streamlit as st
import whisper
import openai
import subprocess
import os
import tempfile
import time
import logging
from dotenv import load_dotenv
from pathlib import Path
from typing import List, Dict, Any
import hashlib

# Streamlit sayfa yapılandırması
st.set_page_config(page_title="AI-Powered Video Translation App", page_icon="🎉", layout="wide")

# Logging konfigürasyonu
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Sabitler
SUPPORTED_LANGUAGES = {
    "Türkçe": "tr", "İngilizce": "en", "Fransızça": "fr",
    "Almanca": "de", "İspanyolca": "es", "İtalyanca": "it"
}
SUPPORTED_VIDEO_FORMATS = ["mp4", "mov", "avi", "mkv"]

# Uygulama konfigürasyonu
def load_config():
    load_dotenv()
    return {
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "whisper_model": "base",
        "gpt_model": "gpt-4"
    }

config = load_config()

# API anahtarı kontrolü
if not config["openai_api_key"]:
    st.error("OpenAI API anahtarı bulunamadı. Lütfen .env dosyanızı kontrol edin.")
    st.stop()

openai.api_key = config["openai_api_key"]

# Whisper modelini yükle
@st.cache_resource
def load_whisper_model():
    return whisper.load_model(config["whisper_model"])

whisper_model = load_whisper_model()

# Güvenlik fonksiyonları
def sanitize_filename(filename: str) -> str:
    return "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_')).rstrip()

def generate_file_hash(file_content: bytes) -> str:
    return hashlib.md5(file_content).hexdigest()

# Video işleme fonksiyonları
def convert_video_to_audio(video_path: str, audio_path: str) -> None:
    try:
        subprocess.run(['ffmpeg', '-i', video_path, '-vn', '-acodec', 'libmp3lame', audio_path], 
                       check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"FFmpeg error: {e.stderr}")
        raise RuntimeError("Video ses dönüşümü başarısız oldu.") from e

def transcribe_audio(audio_path: str) -> Dict[str, Any]:
    try:
        return whisper_model.transcribe(audio_path)
    except Exception as e:
        logging.error(f"Transcription error: {str(e)}")
        raise RuntimeError("Ses dosyası transkripsiyon işlemi başarısız oldu.") from e

def translate_text(text: str, target_lang: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model=config["gpt_model"],
            messages=[
                {"role": "system", "content": f"Translate the following text to {target_lang}."},
                {"role": "user", "content": text}
            ],
        )
        return response.choices[0].message.content
    except openai.error.OpenAIError as e:
        logging.error(f"OpenAI API error: {str(e)}")
        raise RuntimeError(f"{target_lang} diline çeviri sırasında bir hata oluştu.") from e

# Streamlit arayüzü
st.title("🎉 AI-Powered Video Translation App 🎉")

# Dil seçimi
st.sidebar.header("1. Dil Seçimi")
selected_languages = st.sidebar.multiselect(
    "Çevirilecek dilleri seçin",
    options=list(SUPPORTED_LANGUAGES.keys()),
    default=["Türkçe", "İngilizce"]
)

# Video yükleme
st.header("2. Video Yükleme")
uploaded_video = st.file_uploader("Bir video dosyası yükleyin", type=SUPPORTED_VIDEO_FORMATS)

if uploaded_video:
    start_time = time.time()
    
    # İşlem aşamalarını göster
    st.markdown("""
    ### İşlem Aşamaları:
    1. Video ses dosyasına dönüştürülüyor (ffmpeg)
    2. Ses dosyası metne çevriliyor (OpenAI Whisper)
    3. Metin seçilen dillere çevriliyor (ChatGPT 4)
    """)
    
    progress_bar = st.progress(0)
    
    try:
        # Video işleme
        with tempfile.TemporaryDirectory() as temp_dir:
            video_path = Path(temp_dir) / sanitize_filename(uploaded_video.name)
            audio_path = video_path.with_suffix('.mp3')
            
            with open(video_path, "wb") as f:
                f.write(uploaded_video.getbuffer())
            
            file_hash = generate_file_hash(uploaded_video.getvalue())
            logging.info(f"Processing video: {video_path.name}, Hash: {file_hash}")
            
            with st.spinner("Video işleniyor..."):
                # Video to audio conversion
                convert_video_to_audio(str(video_path), str(audio_path))
                progress_bar.progress(0.33)
                
                # Transcription
                result = transcribe_audio(str(audio_path))
                transcript = result["text"]
                st.markdown(f"**Transkript:** {transcript}")
                progress_bar.progress(0.66)
                
                # Translation
                translations = {}
                for lang in selected_languages:
                    target_language = SUPPORTED_LANGUAGES[lang]
                    translation = translate_text(transcript, lang)
                    translations[lang] = translation
                    
                    with st.expander(f"{lang} Çeviri"):
                        st.markdown(translation)
                        download_file_name = f"{video_path.stem}_{lang}_ceviri.txt"
                        st.download_button(
                            label=f"{lang} Çeviriyi İndir",
                            data=translation.encode("utf-8"),
                            file_name=sanitize_filename(download_file_name),
                            mime="text/plain"
                        )
                
                progress_bar.progress(1.0)
        
        st.success("Tüm işlemler başarıyla tamamlandı!")
        st.balloons()
        
    except Exception as e:
        st.error(f"İşlem sırasında bir hata oluştu: {str(e)}")
        logging.exception("An error occurred during processing")
    
    finally:
        end_time = time.time()
        st.sidebar.markdown("---")
        st.sidebar.subheader("İşlem Bilgileri")
        st.sidebar.info(f"Toplam İşlem Süresi: {end_time - start_time:.2f} saniye")
        if 'result' in locals() and isinstance(result, dict):
            confidence = result.get('confidence')
            if confidence is not None and isinstance(confidence, (int, float)):
                st.sidebar.info(f"Ses Tanıma Doğruluğu: {confidence:.2%}")
            else:
                st.sidebar.info("Ses Tanıma Doğruluğu: Mevcut değil")
        else:
            st.sidebar.info("Ses Tanıma Doğruluğu: Henüz hesaplanmadı")

# Hakkında bölümü
st.sidebar.markdown("---")
st.sidebar.info("""
Bu uygulama, yapay zeka teknolojilerini kullanarak video çevirisi yapmaktadır.
Geliştirici: Zülal Beyza Yaylı
Versiyon: 1.0.2
""")