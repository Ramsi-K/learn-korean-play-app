import os
from groq import Groq

client = Groq()
speech_file_path = Path(__file__).parent / "speech.wav"
response = client.audio.speech.create(
    model="playai-tts",
    voice="Aaliyah-PlayAI",
    response_format="wav",
    input="",
)
response.stream_to_file(speech_file_path)
