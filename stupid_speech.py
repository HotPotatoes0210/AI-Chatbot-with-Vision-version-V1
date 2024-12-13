from gtts import gTTS
from playsound import playsound

def run_speech_audio(input):
    text = input
    language = "en"
    
    speech = gTTS(text=text,lang=language,slow=False)
    speech.save("cache_data/output.mp3")
    playsound("cache_data/output.mp3")
