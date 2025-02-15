import streamlit as st
from google.cloud import texttospeech

tts_credentials = st.secrets["google_tts"]["my_project_settings"]
# Convert the AttrDict to a regular Python dictionary
tts_credentials_dict = dict(tts_credentials)
# Initialize Google Cloud TTS client with credentials
client = texttospeech.TextToSpeechClient(credentials=tts_credentials_dict)
st.write("Google Cloud TTS client initialized!")
