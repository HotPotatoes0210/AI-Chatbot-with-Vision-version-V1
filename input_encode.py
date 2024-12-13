import speech_recognition as sr

r = sr.Recognizer()
is_listening = True
is_stop = True
real_prompt = ""
time = 1

def please_speak_here():
    global is_listening, real_prompt
    print("Speech recognizer is now active. Speak to the microphone.")
    
    for i in range(time):
        try:
            with sr.Microphone() as source2:
                print("Listening...")
                audio= r.listen(source2)

                # Recognize speech using Google Speech Recognition
                MyText = r.recognize_google(audio)
                MyText = MyText.lower()
                print(f"Recognized: {MyText}")

                # Store the recognized text
                real_prompt = MyText

        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition; {e}")
        except sr.UnknownValueError:
            print("Sorry, I didn't understand that. Please try again.")
        except KeyboardInterrupt:
            print("\nKeyboard interrupt detected. Terminating gracefully...")

def get_voice_prompt():
    global real_prompt
    return real_prompt
