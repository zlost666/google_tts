import subprocess
import streamlit as st
import tempfile
import os
from io import BytesIO

# Try installing ffmpeg if not available
def install_ffmpeg():
    try:
        subprocess.run(['apt-get', 'update'], check=True)
        subprocess.run(['apt-get', 'install', '-y', 'ffmpeg'], check=True)
        st.success("ffmpeg installed successfully")
    except subprocess.CalledProcessError as e:
        st.error(f"Error installing ffmpeg: {e}")

# Attempt to install ffmpeg
install_ffmpeg()

# Set up the Streamlit app
st.title("Connect Several MP3 Files into One")
uploaded_files = st.file_uploader("Load several mp3", type="mp3", accept_multiple_files=True)

if len(uploaded_files) > 1:
    if st.button("Connect mp3 files"):
        # Create a temporary directory to store the uploaded files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a temporary text file to list all input files for ffmpeg
            filelist_path = os.path.join(temp_dir, 'filelist.txt')
            with open(filelist_path, 'w') as f:
                for uploaded_file in uploaded_files:
                    # Save the uploaded file to the temporary directory
                    temp_file_path = os.path.join(temp_dir, f"temp_{uploaded_file.name}")
                    with open(temp_file_path, 'wb') as temp_file:
                        temp_file.write(uploaded_file.getbuffer())
                    # Add file path to the file list for ffmpeg
                    f.write(f"file '{temp_file_path}'\n")

            # Use ffmpeg to concatenate the files listed in 'filelist.txt'
            try:
                subprocess.run(
                    ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', filelist_path, '-c', 'copy', os.path.join(temp_dir, 'combined.mp3')],
                    check=True
                )
                
                # After successful concatenation, load the combined file into a BytesIO object
                combined_file_path = os.path.join(temp_dir, 'combined.mp3')
                with open(combined_file_path, 'rb') as combined_file:
                    combined_audio = BytesIO(combined_file.read())
                    combined_audio.seek(0)

                # Provide the audio player in Streamlit
                st.audio(combined_audio, format='audio/mp3')

                # Provide download link for the concatenated file
                st.download_button(
                    label="Download Combined MP3",
                    data=combined_audio,
                    file_name="combined_audio.mp3",
                    mime="audio/mpeg"
                )
            
            except subprocess.CalledProcessError as e:
                st.error(f"Error during concatenation: {e}")


