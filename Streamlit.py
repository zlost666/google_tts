import streamlit as st
import subprocess
from io import BytesIO

# Set up the Streamlit app
st.title("Connect Several MP3 Files into One")
uploaded_files = st.file_uploader("Load several mp3", type="mp3", accept_multiple_files=True)

if len(uploaded_files) > 1:
    if st.button("Connect mp3 files"):
        # Create a temporary text file to list all input files for ffmpeg
        with open('filelist.txt', 'w') as f:
            for uploaded_file in uploaded_files:
                # Save the uploaded file to a temporary location and create the list for ffmpeg
                with open(f"temp_{uploaded_file.name}", 'wb') as temp_file:
                    temp_file.write(uploaded_file.getbuffer())
                # Add file path to the file list for ffmpeg
                f.write(f"file 'temp_{uploaded_file.name}'\n")

        # Use ffmpeg to concatenate the files listed in 'filelist.txt'
        try:
            subprocess.run(
                ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', 'filelist.txt', '-c', 'copy', 'combined.mp3'],
                check=True
            )
            
            # After successful concatenation, load the combined file into a BytesIO object
            with open('combined.mp3', 'rb') as combined_file:
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
        
        finally:
            # Clean up temporary files
            for uploaded_file in uploaded_files:
                try:
                    os.remove(f"temp_{uploaded_file.name}")
                except Exception as e:
                    print(f"Error removing temp file: {e}")
            os.remove('filelist.txt')

