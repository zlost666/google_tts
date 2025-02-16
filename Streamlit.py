import streamlit as st
from bs4 import BeautifulSoup
from google.cloud import texttospeech
from io import BytesIO
from pydub import AudioSegment
import os

# Initialize Google Cloud TTS client
tts_credentials = st.secrets["google_tts"]
client = texttospeech.TextToSpeechClient.from_service_account_info(tts_credentials)

def extract_chapter_text(file, chapter_number):
    soup = BeautifulSoup(file, 'xml')
    text = soup.find_all("section")
    if chapter_number < len(text):
        return str(text[chapter_number])
    else:
        return "Chapter number out of range."

def split_by_size(input_string, max_size=4970):
    words = input_string.split()
    chunks = []
    current_chunk = ''
    for word in words:
        temp_chunk = current_chunk + (word if current_chunk == '' else ' ' + word)
        if len(temp_chunk.encode('utf-8')) <= max_size:
            current_chunk = temp_chunk
        else:
            chunks.append(current_chunk)
            current_chunk = word
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

st.title("XML to Google_TTS")
uploaded_file = st.file_uploader("Upload an XML file", type=["xml"])

output_dir = "generated_mp3s"
os.makedirs(output_dir, exist_ok=True)

if 'chunks' not in st.session_state:
    st.session_state['chunks'] = {}
if 'mp3_files' not in st.session_state:
    st.session_state['mp3_files'] = []
if 'file_content' not in st.session_state:
    st.session_state['file_content'] = None

if uploaded_file is not None:
    st.session_state['file_content'] = uploaded_file.read()

# Create columns with specified width ratios
col1, col2 = st.columns([1, 1])  # Adjust the numbers to change the width ratios

# Place the inputs in the columns
with col1:
    first_chapter = st.number_input("Enter First Chapter Number", min_value=0, step=1)
with col2:
    last_chapter = st.number_input("Enter Last Chapter Number", min_value=0, step=1)

# Step 1: Extract Chapters and Split into Chunks
if st.button("Extract Chapters"):
    st.session_state['chunks'] = {}
    for chapter_number in range(first_chapter, last_chapter + 1):
        text_input = extract_chapter_text(st.session_state['file_content'], chapter_number)
        replace_dict = {' ': ' ', '***': ' ', '<p>': '', '</p>': ' ', '<p/>': ' ', '<section>': '', '</section>': '', '<title>': '', '</title>': '', '\n': ''}
        for old, new in replace_dict.items():
            text_input = text_input.replace(old, new)

        st.session_state['chunks'][chapter_number] = split_by_size(text_input)
        st.write(f"Chapter {chapter_number}:")
        for chunk in st.session_state['chunks'][chapter_number]:
            st.text(chunk)

# Step 2: Generate MP3 files
if len(st.session_state['chunks']) > 0 and st.button("Generate MP3s"):
    mp3_files = []
    for chapter_number in range(first_chapter, last_chapter + 1):
        chapter_chunks = st.session_state['chunks'][chapter_number]
        combined_audio = AudioSegment.empty()
        for chunk in chapter_chunks:
            input_text = texttospeech.SynthesisInput(text=chunk)
            voice = texttospeech.VoiceSelectionParams(language_code="ru-RU", name="ru-RU-Standard-C", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE)
            audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3, volume_gain_db=5.0, speaking_rate=1.0, pitch=5.0, sample_rate_hertz=48000)

            response = client.synthesize_speech(request={"input": input_text, "voice": voice, "audio_config": audio_config})
            audio_data = BytesIO(response.audio_content)
            audio_data.seek(0)

            audio = AudioSegment.from_mp3(audio_data)
            combined_audio += audio

        output_filename = os.path.join(output_dir, f"chapter_{chapter_number}.mp3")
        combined_audio.export(output_filename, format="mp3")
        mp3_files.append(output_filename)

    st.session_state['mp3_files'] = mp3_files
    st.success("MP3 files generated successfully!")

# Display audio links and download buttons
if len(st.session_state['mp3_files']) > 0:
    for file_path in st.session_state['mp3_files']:
        st.write(f"Chapter {file_path} - Listen:")
        st.audio(file_path)
        with open(file_path, "rb") as f:
            st.download_button(label=f"Download {file_path}", data=f, file_name=os.path.basename(file_path), mime="audio/mp3")
