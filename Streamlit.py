import streamlit as st
from google.cloud import texttospeech

tts_credentials = st.secrets["google_tts"]["my_project_settings"]
# Convert the AttrDict to a regular Python dictionary
tts_credentials_dict = dict(tts_credentials)
# Initialize Google Cloud TTS client with credentials
client = texttospeech.TextToSpeechClient(credentials=tts_credentials_dict)
st.write("Google Cloud TTS client initialized!")

input_text = texttospeech.SynthesisInput(text="Blya suka v rot")
voice = texttospeech.VoiceSelectionParams(language_code="ru-Ru",name="ru-RU-Standard-C",
                                          ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,)
# Set the audio configuration (quality and format)
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3,  # Output format (MP3, LINEAR16, OGG_OPUS, etc.)
    volume_gain_db=5.0,  # Increase volume by 5 dB (default is 0, adjust from -96.0 to 16.0)
    speaking_rate=1.0,  # Adjust the speaking rate (0.25 to 4.0)
    pitch=5.0,  # Adjust the pitch (-20.0 to 20.0)
    sample_rate_hertz=48000  # Higher sample rate for better quality (default is 16000)
)
response = client.synthesize_speech(request={"input": input_text, "voice": voice, "audio_config": audio_config})
with open('temp_file.mp3', "wb") as out:
    out.write(response.audio_content)
