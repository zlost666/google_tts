import streamlit as st
from pydub import AudioSegment
from io import BytesIO

# Set up the Streamlit app
st.title("Connect Several MP3 Files into One")
uploaded_files = st.file_uploader("Load several mp3", type="mp3", accept_multiple_files=True)

if len(uploaded_files) > 1:
    if st.button("Connect mp3 files"):
        # Create an empty audio segment for concatenation
        combined = AudioSegment.empty()

        # Loop through uploaded files and concatenate them
        for file in uploaded_files:
            audio = AudioSegment.from_mp3(file)
            combined += audio

        # Export the combined audio to a BytesIO object
        output = BytesIO()
        combined.export(output, format="mp3")
        output.seek(0)  # Reset pointer to the start of the BytesIO object

        st.audio(output, format='audio/mp3')

        # Provide download link for the concatenated file
        st.download_button(
            label="Download Combined MP3",
            data=output,
            file_name="combined_audio.mp3",
            mime="audio/mpeg"
        )
