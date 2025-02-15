import streamlit as st
from google.cloud import texttospeech

# Fetch credentials from Streamlit secrets
tts_credentials = st.secrets["google_tts"]

# Initialize Google Cloud TTS client with credentials
client = texttospeech.TextToSpeechClient.from_service_account_info(tts_credentials)
st.write("Google Cloud TTS client initialized!")

# Define the text input and the voice configuration
input_text = texttospeech.SynthesisInput(text="Blya suka v rot")
voice = texttospeech.VoiceSelectionParams(
    language_code="ru-RU",  # Corrected to "ru-RU" for Russian
    name="ru-RU-Standard-C",
    ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
)

# Set the audio configuration (quality and format)
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3,  # Output format (MP3)
    volume_gain_db=5.0,  # Increase volume by 5 dB (default is 0, adjust from -96.0 to 16.0)
    speaking_rate=1.0,  # Adjust the speaking rate (0.25 to 4.0)
    pitch=5.0,  # Adjust the pitch (-20.0 to 20.0)
    sample_rate_hertz=48000  # Higher sample rate for better quality (default is 16000)
)

# Synthesize speech using the Google Cloud Text-to-Speech API
response = client.synthesize_speech(request={"input": input_text, "voice": voice, "audio_config": audio_config})

# Save the audio content to a temporary file
with open('temp_file.mp3', "wb") as out:
    out.write(response.audio_content)

# Provide a download link to the MP3 file
st.write("Click below to download the audio file:")
st.audio('temp_file.mp3', format='audio/mp3')

# Optionally, add a download button:
st.download_button(
    label="Download MP3 file",
    data=open('temp_file.mp3', 'rb').read(),
    file_name="output.mp3",
    mime="audio/mp3"
)
