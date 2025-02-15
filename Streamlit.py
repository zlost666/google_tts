import streamlit as st
from google.cloud import texttospeech
from io import BytesIO
from pydub import AudioSegment
import io

# Fetch credentials from Streamlit secrets
tts_credentials = st.secrets["google_tts"]

# Initialize Google Cloud TTS client with credentials
client = texttospeech.TextToSpeechClient.from_service_account_info(tts_credentials)
st.write("Google Cloud TTS client initialized!")

# Define the text input and the voice configuration
input_text = texttospeech.SynthesisInput(text="Хань Ли не собирался гоняться за Серебрянокрылым Ночным Демоном в этом новом месте. Без сдерживающего демона барьера убить его было не так просто, даже с помощью Веера Трёх Огней. Хань Ли повернулся и взглянул на Зверя Плачущей Души, который размахивал белым предметом руке, и улыбнулся. Присмотревшись, он увидел маленькую лошадь с двумя зелеными глазами и ростом в полфута. Это была Призрачная Иньская Лошадь — цель их опасного путешествия.")
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

# Use BytesIO to store the audio content in memory
audio_data = BytesIO(response.audio_content)
audio_data.seek(0)  # Reset pointer to the start of the BytesIO object

# Load the audio using pydub to perform any manipulation (if needed)
audio = AudioSegment.from_mp3(audio_data)

# Optionally, you can modify the audio here (e.g., change volume, speed, etc.)
# For example, increasing the volume by 5 dB
audio = audio + 5

# Convert the modified audio to a byte stream again
buffer = io.BytesIO()
audio.export(buffer, format="mp3")
buffer.seek(0)

# Provide a download link for the audio file
st.write("Click below to download the audio file:")
st.audio(buffer, format='audio/mp3')

# Optionally, add a download button:
st.download_button(
    label="Download MP3 file",
    data=buffer,
    file_name="output.mp3",
    mime="audio/mp3"
)
