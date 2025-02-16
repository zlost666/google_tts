import streamlit as st
from bs4 import BeautifulSoup
from google.cloud import texttospeech
from io import BytesIO
from pydub import AudioSegment
import os

# Fetch credentials from Streamlit secrets
tts_credentials = st.secrets["google_tts"]

# Initialize Google Cloud TTS client with credentials
client = texttospeech.TextToSpeechClient.from_service_account_info(tts_credentials)
st.write("Google Cloud TTS client initialized!")

def extract_chapter_text(file, chapter_number):
    soup = BeautifulSoup(file, 'xml')
    text = soup.find_all("section")
    if chapter_number < len(text):
        return str(text[chapter_number])
    else:
        return "Chapter number out of range."

def byte_size(s):
    return len(s.encode('utf-8'))

def split_by_size(input_string, max_size=40):
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

st.title("XML Chapter Viewer")
uploaded_file = st.file_uploader("Upload an XML file", type=["xml"])

# Output directory for MP3 files
output_dir = "generated_mp3s"
os.makedirs(output_dir, exist_ok=True)

if 'chunks' not in st.session_state:
    st.session_state['chunks'] = {}
if 'mp3_files' not in st.session_state:
    st.session_state['mp3_files'] = []
if 'file_content' not in st.session_state:
    st.session_state['file_content'] = None

# Load file content into session state if a file is uploaded
if uploaded_file is not None:
    st.session_state['file_content'] = uploaded_file.read()

# User inputs for first and last chapter
first_chapter = st.number_input("Enter First Chapter Number", min_value=0, step=1)
last_chapter = st.number_input("Enter Last Chapter Number", min_value=0, step=1)

# Step 1: Extract Chapters and Split into Chunks
if st.button("Extract Chapters"):
    st.session_state['chunks'] = {}  # Reset the chunks for each extraction
    for chapter_number in range(first_chapter, last_chapter + 1):
        text_input = extract_chapter_text(st.session_state['file_content'], chapter_number)
        replace_dict = {' ': ' ', '***': ' ', '<p>': '', '</p>': ' ', '<section>': '',
                        '</section>': '', '<title>': '', '</title>': '', '\n': ''}
        for old, new in replace_dict.items():
            text_input = text_input.replace(old, new)

        # Split text into chunks and store in session state
        st.session_state['chunks'][chapter_number] = split_by_size(text_input)

        # Display the chunks of text for the current chapter
        st.write(f"Chapter {chapter_number}:")
        for chunk in st.session_state['chunks'][chapter_number]:
            st.text(chunk)

# Step 2: Generate MP3 files
if len(st.session_state['chunks']) > 0 and st.button("Generate MP3s"):
    with st.spinner("Generating MP3 files..."):
        # Process each chapter
        for chapter_number in range(first_chapter, last_chapter + 1):
            chapter_chunks = st.session_state['chunks'][chapter_number]

            # Concatenate the chunks of the current chapter
            combined_audio = AudioSegment.empty()
            for chunk in chapter_chunks:
                # Define the text input and the voice configuration
                input_text = texttospeech.SynthesisInput(text=chunk)
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
                response = client.synthesize_speech(
                    request={"input": input_text, "voice": voice, "audio_config": audio_config})

                # Use BytesIO to store the audio content in memory
                audio_data = BytesIO(response.audio_content)
                audio_data.seek(0)  # Reset pointer to the start of the BytesIO object

                # Load the audio using pydub to perform any manipulation (if needed)
                audio = AudioSegment.from_mp3(audio_data)

                # Concatenate the current chunk to the chapter audio
                combined_audio += audio

            # Save the combined audio for this chapter to a new MP3 file
            output_filename = os.path.join(output_dir, f"chapter_{chapter_number}.mp3")
            combined_audio.export(output_filename, format="mp3")

            # Store the MP3 file in session state for later access
            st.session_state['mp3_files'].append(output_filename)

            # Display the audio player for the chapter
            st.write(f"Chapter {chapter_number} - Listen:")
            st.audio(output_filename)

# Display download buttons for all generated MP3 files
if len(st.session_state['mp3_files']) > 0:
    for file_path in st.session_state['mp3_files']:
        with open(file_path, "rb") as f:
            st.download_button(
                label=f"Download {file_path}",
                data=f,
                file_name=os.path.basename(file_path),
                mime="audio/mp3"
            )
