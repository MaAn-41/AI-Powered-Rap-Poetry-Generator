
import streamlit as st
import whisper
import google.generativeai as genai
import requests
import torch
import numpy as np
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PLAY_HT_API_KEY = os.getenv("PLAY_HT_API_KEY")
PLAY_HT_USER_ID = os.getenv("PLAY_HT_USER_ID")

genai.configure(api_key=GEMINI_API_KEY)

# Initialize Whisper model
model = whisper.load_model("base")

# Function to transcribe the uploaded audio file
def transcribe_audio(audio_file):
    st.write("Transcribing audio...")
    audio = whisper.load_audio(audio_file)
    audio = whisper.pad_or_trim(audio)
    
    # Make a prediction
    result = model.transcribe(audio)
    transcription = result["text"]
    
    return transcription

# Streamlit UI
st.title("Real-Time Voice Poetry Generator")

# Upload file
uploaded_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "m4a"])

if uploaded_file is not None:
    st.audio(uploaded_file, format="audio/wav")

    # Transcribe uploaded audio
    transcription = transcribe_audio(uploaded_file)
    st.write(f"Transcription: {transcription}")

    # You can add your poetry generation code here if needed
    # For example, generate a response based on transcription using Google Generative AI or other models.
    if transcription:
        st.write("Generating poetry...")

        # Assuming you have a function for generating poetry based on the transcription
        try:
            response = genai.Completion.create(
                model="text-bison", prompt=f"Generate a poem based on the following text: {transcription}", temperature=0.7
            )
            generated_poem = response['choices'][0]['text']
            st.write(f"Generated Poetry: {generated_poem}")
        except Exception as e:
            st.error(f"Error generating poetry: {str(e)}")
else:
    st.write("Please upload an audio file to begin transcription.")
