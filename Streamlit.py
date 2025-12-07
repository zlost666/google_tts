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
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = word
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

st.title("XML to Google_TTS (Single MP3)")

uploaded_file = st.file_uploader("Upload an XML file", type=["xml"])

output_dir = "generated_mp3s"
os.makedirs(output_dir, exist_ok=True)

# Session state
if 'chunks' not in st.session_state:
    st.session_state['chunks'] = {}
if 'file_content' not in st.session_state:
    st.session_state['file_content'] = None
if 'final_mp3' not in st.session_state:
    st.session_state['final_mp3'] = None

if uploaded_file is not None:
    st.session_state['file_content'] = uploaded_file.read()

# Inputs
col1, col2 = st.columns([1, 1])
with col1:
    first_chapter = st.number_input("Enter First Chapter Number", min_value=0, step=1)
with col2:
    last_chapter = st.number_input("Enter Last Chapter Number", min_value=0, step=1)

# Step 1: Extract and split
if st.button("Extract Chapters"):
    st.session_state['chunks'] = {}
    if st.session_state['file_content'] is None:
        st.warning("Please upload an XML file first.")
    else:
        for chapter_number in range(first_chapter, last_chapter + 1):
            raw_text = extract_chapter_text(st.session_state['file_content'], chapter_number)

            # Clean minimal XML tags/content
            replace_dict = {
                '***': ' ',
                '<p>': '', '</p>': ' ',
                '<p/>': ' ',
                '<section>': '', '</section>': '',
                '<title>': '', '</title>': '',
                '\n': ''
            }
            for old, new in replace_dict.items():
                raw_text = raw_text.replace(old, new)

            chunks = split_by_size(raw_text)
            st.session_state['chunks'][chapter_number] = chunks

            # Show extracted text directly
            with st.expander(f"Chapter {chapter_number} text"):
                st.text(raw_text)

# Step 2: Generate a single merged MP3
if len(st.session_state['chunks']) > 0 and st.button("Generate Single MP3"):
    combined_audio = AudioSegment.empty()

    for chapter_number in range(first_chapter, last_chapter + 1):
        chapter_chunks = st.session_state['chunks'].get(chapter_number, [])
        for chunk in chapter_chunks:
            input_text = texttospeech.SynthesisInput(text=chunk)
            voice = texttospeech.VoiceSelectionParams(
                language_code="ru-RU",
                name="ru-RU-Standard-C",
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                volume_gain_db=5.0,
                speaking_rate=1.0,
                pitch=5.0,
                sample_rate_hertz=48000
            )

            response = client.synthesize_speech(
                request={"input": input_text, "voice": voice, "audio_config": audio_config}
            )
            audio_data = BytesIO(response.audio_content)
            audio_data.seek(0)

            audio = AudioSegment.from_mp3(audio_data)
            combined_audio += audio

    output_filename = os.path.join(output_dir, f"chapters_{first_chapter}_to_{last_chapter}.mp3")
    combined_audio.export(output_filename, format="mp3")
    st.session_state['final_mp3'] = output_filename
    st.success("Single MP3 file generated successfully!")

# Step 3: Download only (no listening)
if st.session_state['final_mp3']:
    with open(st.session_state['final_mp3'], "rb") as f:
        st.download_button(
            label="Download Merged MP3",
            data=f,
            file_name=os.path.basename(st.session_state['final_mp3']),
            mime="audio/mp3"
        )
