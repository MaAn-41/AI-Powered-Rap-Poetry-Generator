import streamlit as st
import whisper
import google.generativeai as genai 
import requests
import tempfile
import os
import pyaudio
import wave
import speech_recognition as sr
from dotenv import load_dotenv

load_dotenv()

model = whisper.load_model("base")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PLAY_HT_API_KEY = os.getenv("PLAY_HT_API_KEY")
PLAY_HT_USER_ID = os.getenv("PLAY_HT_USER_ID")

genai.configure(api_key=GEMINI_API_KEY)

def transcribe_audio(file_path):
    result = model.transcribe(file_path)
    return result['text']

def record_audio(duration=10, sample_rate=44100):
    st.info("Recording... Speak now!")
    
    # Initialize recognizer class in speech_recognition
    recognizer = sr.Recognizer()
    mic = sr.Microphone(sample_rate=sample_rate)

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        st.info("Start speaking...")
        audio = recognizer.listen(source, timeout=duration)
        st.info("Recording stopped.")
    
    file_path = "realtime_recording.wav"
    with open(file_path, "wb") as f:
        f.write(audio.get_wav_data())
    return file_path

def generate_poetry(poetry_text):
    prompt = f"'{poetry_text}' ka aik behtareen aur rhyming continuation likhiye Urdu ya English mein."
    try:
        model = genai.GenerativeModel("gemini-pro") 
        response = model.generate_content(prompt)
        if response and hasattr(response, "text"):
            return response.text
        else:
            return "No Poetry generated."
    except Exception as e:
        st.error(f"Error in Gemini API: {e}")
        return "Poetry generation failed."

def text_to_speech(text):
    url = "https://api.play.ht/api/v2/tts/stream"
    headers = {
        "X-USER-ID": PLAY_HT_USER_ID,
        "AUTHORIZATION": PLAY_HT_API_KEY,
        "accept": "audio/mpeg",
        "content-type": "application/json",
    }
    data = {
        "text": text,
        "voice_engine": "PlayDialog",
        "voice": "aiq-urdu-female",
        "output_format": "mp3"
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        audio_file_path = "output.mp3"
        with open(audio_file_path, 'wb') as f:
            f.write(response.content)
        return audio_file_path
    else:
        return None

st.title("🎤 AI-Powered Rap & Poetry Generator")

option = st.radio("Choose an input method:", ["Upload Audio File", "Record Real-Time Voice"])

if option == "Upload Audio File":
    uploaded_file = st.file_uploader("Upload your freestyle rap or poetry (MP3, WAV, M4A)", type=["mp3", "wav", "m4a"])
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_path = temp_file.name
        
        st.audio(temp_path, format='audio/mp3')
        
        with st.spinner("Transcribing your poetry..."):
            poetry_text = transcribe_audio(temp_path)
            st.write("### Your Original Poetry:")
            st.write(poetry_text)
        
        with st.spinner("Generating continuation..."):
            generated_poetry = generate_poetry(poetry_text)
            st.write("### AI-Generated Continuation:")
            st.write(generated_poetry)

        with st.spinner("Generating AI narration..."):
            text_to_speech(generated_poetry)

        audio_file_path = "output.mp3"
        if os.path.exists(audio_file_path):
            st.success("Audio generated successfully!")
            st.audio(audio_file_path, format="audio/mp3")
        else:
            st.error("Audio file not found. Please check the generation process.")

elif option == "Record Real-Time Voice":
    if st.button("Start Recording"):
        recorded_file_path = record_audio()
        st.audio(recorded_file_path, format='audio/wav')
        with st.spinner("Transcribing your poetry..."):
            poetry_text = transcribe_audio(recorded_file_path)
            st.write("### Your Original Poetry:")
            st.write(poetry_text)
        with st.spinner("Generating continuation..."):
            generated_poetry = generate_poetry(poetry_text)
            st.write("### AI-Generated Continuation:")
            st.write(generated_poetry)
        with st.spinner("Generating AI narration..."):
            text_to_speech(generated_poetry)
        audio_file_path = "result1.mp3"
        if os.path.exists(audio_file_path):
            st.success("Audio generated successfully!")
            st.audio(audio_file_path, format="audio/mp3")
        else:
            st.error("Audio file not found. Please check the generation process.")
