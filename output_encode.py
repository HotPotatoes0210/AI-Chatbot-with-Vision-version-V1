from elevenlabs import play
from elevenlabs.client import ElevenLabs

def voice_output(answer):
    client = ElevenLabs(
    api_key="sk_ff904ff7574d740993b47ec8a1dd1e51c206bd4455a78d74", 
    )
    audio = client.generate(
    text=answer,
    voice="Brian",
    model="eleven_multilingual_v2"
    )
    play(audio)