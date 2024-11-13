import cv2
import os
import ollama
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
from PIL import Image, ImageTk

class WebcamApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Assistant with Webcam")
        self.root.geometry("800x600")
        
        # Set up a directory to store captured images
        os.makedirs("cache_data", exist_ok=True)

        # Initialize camera
        self.cap = cv2.VideoCapture(1)  # Change to '0' for default camera
        self.camera_running = False

        # Set up UI components
        self.create_widgets()
        
        # Start camera in a thread
        self.camera_thread = threading.Thread(target=self.update_camera_feed)
        self.camera_running = True
        self.camera_thread.start()

    def create_widgets(self):
        # Camera feed label
        self.camera_feed_label = tk.Label(self.root)
        self.camera_feed_label.pack(pady=10)

        # Capture button
        # self.capture_button = tk.Button(self.root, text="Capture Image", command=self.capture_image)
        # self.capture_button.pack(pady=5)

        # Input prompt entry
        self.prompt_entry = tk.Entry(self.root, width=80)
        self.prompt_entry.pack(pady=10)
        
        # Submit button for the prompt
        self.submit_button = tk.Button(self.root, text="Submit Prompt", command=self.submit_prompt)
        self.submit_button.pack(pady=5)

        # Output display for AI response
        self.response_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=80, height=20)
        self.response_text.pack(pady=10)
        self.response_text.config(state=tk.DISABLED)

    def update_camera_feed(self):
        while self.camera_running:
            ret, frame = self.cap.read()
            if ret:
                # Resize and convert frame for tkinter display
                resized_frame = cv2.resize(frame, (244, 244))
                image = Image.fromarray(cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB))
                imgtk = ImageTk.PhotoImage(image=image)
                self.camera_feed_label.imgtk = imgtk
                self.camera_feed_label.configure(image=imgtk)
            else:
                messagebox.showerror("Error", "Failed to access the camera.")
                self.camera_running = False
            self.root.update_idletasks()
        self.cap.release()

    def capture_image(self):
        ret, frame = self.cap.read()
        if ret:
            # Save the image to a file
            image_path = "cache_data/data.jpg"
            cv2.imwrite(image_path, frame)
        else:
            messagebox.showerror("Error", "Failed to capture image.")

    def submit_prompt(self):
        prompt = self.prompt_entry.get()
        if not prompt:
            messagebox.showwarning("Input Required", "Please enter a prompt.")
            return
        
        self.response_text.config(state=tk.NORMAL)
        self.response_text.insert(tk.END, "User: " + prompt + "\n")
        self.response_text.config(state=tk.DISABLED)
        WebcamApp.capture_image
        # Run AI assistant prompt in a separate thread
        threading.Thread(target=self.get_ai_response, args=(prompt,)).start()

    def get_ai_response(self, prompt):
        data = "cache_data/data.jpg"
        try:
            response = ollama.chat(
                model='llava',
                messages=[
                    {
                        'role': 'system',
                        'content': 'You are a witty assistant that will use the chat history and the real-time vision provided by the user to answer its questions. The image I provide will be your vision. Your job is to answer questions directly. Be friendly and helpful, with personality.'
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

        self.response_text.config(state=tk.NORMAL)
        self.response_text.insert(tk.END, "AI: " + message + "\n")
        self.response_text.config(state=tk.DISABLED)

    def close(self):
        self.camera_running = False
        self.root.quit()
        self.root.destroy()

# Create the Tkinter application
root = tk.Tk()
app = WebcamApp(root)

# Set up a protocol to handle window closing
root.protocol("WM_DELETE_WINDOW", app.close)
root.mainloop()
