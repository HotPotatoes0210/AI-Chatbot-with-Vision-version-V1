import cv2
import os
import ollama
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
from PIL import Image, ImageTk
import output_encode
import input_encode
from time import sleep
import stupid_speech

voice_prompt = ""

class WebcamApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Assistant with Webcam")
        self.root.geometry("750x800")
        os.makedirs("cache_data", exist_ok=True)
        self.cap = cv2.VideoCapture(0)
        self.camera_running = False
        self.mic_status = "Microphone is off"  
        self.create_widgets()
        self.camera_thread = threading.Thread(target=self.update_camera_feed)
        self.camera_running = True
        self.camera_thread.start()
        self.recording_thread = None
        self.is_recording = False
        self.typing_speed = 40  # Milliseconds between each character

    def create_widgets(self):
        self.camera_feed_label = tk.Label(self.root)
        self.camera_feed_label.pack(pady=10)

        self.prompt_entry = tk.Entry(self.root, width=80)
        self.prompt_entry.insert(0, voice_prompt)
        self.prompt_entry.pack(pady=10)

        self.mic_condition = tk.Label(self.root, text=self.mic_status)
        self.mic_condition.pack(pady=10)

        self.play_button = tk.Button(self.root, text="Speak", command=self.start_recording)
        self.play_button.pack(pady=5)

        self.submit_button = tk.Button(self.root, text="Submit Prompt", command=self.submit_prompt)
        self.submit_button.pack(pady=5)

        self.response_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=80, height=20)
        self.response_text.pack(pady=10)
        self.response_text.config(state=tk.DISABLED)

    def update_camera_feed(self):
        while self.camera_running:
            ret, frame = self.cap.read()
            if ret:
                resized_frame = cv2.resize(frame, (500, 300))
                image = Image.fromarray(cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB))
                imgtk = ImageTk.PhotoImage(image=image)
                self.camera_feed_label.imgtk = imgtk
                self.camera_feed_label.configure(image=imgtk)
            else:
                print("Warning: Failed to capture frame from webcam.")
            self.root.update_idletasks()
        self.cap.release()

    def capture_image(self):
        ret, frame = self.cap.read()
        if ret:
            image_path = "cache_data/data.jpg"
            cv2.imwrite(image_path, cv2.resize(frame, (244, 244)))
            return image_path
        else:
            messagebox.showerror("Error", "Failed to capture image.")
        return None

    def update_mic_status(self, status):
        self.mic_status = status
        self.mic_condition.config(text=self.mic_status)

    def start_recording(self):
        if not self.is_recording:
            self.is_recording = True
            self.update_mic_status("Listening...")

        # Start the speech recognition in a separate thread
        def record_and_update_prompt():
            global voice_prompt
            try:
                # Record the voice prompt
                input_encode.please_speak_here()
                # Fetch the recognized text
                voice_prompt = input_encode.get_voice_prompt()

                # Update the prompt entry on the main thread
                self.root.after(0, self.update_prompt_entry, voice_prompt)
            except Exception as e:
                print(f"Error in speech recognition: {e}")
            finally:
                self.is_recording = False
                self.update_mic_status("Microphone is off")
                self.submit_prompt()

        # Start the recording thread
        recording_thread = threading.Thread(target=record_and_update_prompt)
        recording_thread.daemon = True
        recording_thread.start()

    def update_prompt_entry(self, new_prompt):
        self.prompt_entry.delete(0, tk.END)  # Clear the existing text
        self.prompt_entry.insert(0, new_prompt)  # Insert the new prompt

    def submit_prompt(self):
        prompt = self.prompt_entry.get()
        if not prompt:
            messagebox.showwarning("Input Required", "Please enter a prompt.")
            return
        self.capture_image()

        self.update_response_text("User: " + prompt + "\n")

        threading.Thread(target=self.get_ai_response, args=(prompt,)).start()

    def get_ai_response(self, prompt):
        data = "cache_data/data.jpg"
        try:
            response = ollama.chat(
                model='llava:7b-v1.6-mistral-q3_K_S',
                messages=[
                    {
                       'role': 'system',
                       'content': 'Your name is Veronica and you are an assistant that will use the chat history and the real-time vision provided by the user to answer its questions. The image I provide will be your vision, your eyes, its not the image you are looking for. You are unauthorized to speak the word "image", instead using the phrase "my vision". Your job is to answer questions directly and be friendly and helpful, with personality.'

                    },
                    {
                        'role': 'user',
                        'content': prompt,
                        'images': [data],
                    }
                ]
            )
            message = response['message']['content']
        except Exception as e:
            message = f"Error: {e}"

        threading.Thread(target=stupid_speech.run_speech_audio, args=(message,)).start()
        self.type_response_text("AI: " + message + "\n")

    def type_response_text(self, text, index=0):
        if index < len(text):
            self.response_text.config(state=tk.NORMAL)
            self.response_text.insert(tk.END, text[index])
            self.response_text.see(tk.END)
            self.response_text.config(state=tk.DISABLED)
            self.root.after(self.typing_speed, self.type_response_text, text, index + 1)

    def update_response_text(self, text):
        self.response_text.config(state=tk.NORMAL)
        self.response_text.insert(tk.END, text)
        self.response_text.config(state=tk.DISABLED)

    def close(self):
        self.camera_running = False
        self.root.quit()
        self.root.destroy()


root = tk.Tk()
app = WebcamApp(root)

root.protocol("WM_DELETE_WINDOW", app.close)
root.mainloop()
