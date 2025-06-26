import os
import threading
import tkinter as tk
from tkinter import messagebox
import pyttsx3
import speech_recognition as sr
import openai
import json
import pyaudio
from vosk import Model, KaldiRecognizer
import webbrowser
import datetime
import psutil
import pyjokes

# Set your OpenAI key
openai.api_key = "your-openai-api-key-here"

# Text to Speech
engine = pyttsx3.init()
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Authentication Phrase
AUTH_PHRASE = "hello"
def authenticate_user():
    RATE = 16000
    CHUNK = 4096
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)

    if not os.path.exists("model"):
        speak("Vosk model not found.")
        return False

    model = Model("model")
    recognizer = KaldiRecognizer(model, RATE)

    speak("Say the authentication phrase:")
    for _ in range(int(RATE / CHUNK * 3)):
        data = stream.read(CHUNK, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            if AUTH_PHRASE in result.get("text", "").lower():
                speak("Authentication successful")
                stream.stop_stream()
                stream.close()
                audio.terminate()
                return True

    speak("Authentication failed")
    stream.stop_stream()
    stream.close()
    audio.terminate()
    return False

def get_ai_response(prompt):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003", prompt=prompt, max_tokens=100
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print("AI error:", e)
        return "AI is currently unavailable."

def respond_to_command(command):
    command = command.lower()
    if "notepad" in command:
        speak("Opening Notepad")
        os.system("notepad")
    elif "shutdown" in command:
        speak("Shutting down")
        os.system("shutdown /s /t 1")
    elif "browser" in command:
        speak("Opening browser")
        webbrowser.open("https://www.google.com")
    elif "search" in command:
        speak("What should I search for?")
        query = listen_for_command()
        if query:
            url = f"https://www.google.com/search?q={query}"
            webbrowser.open(url)
    elif "time" in command:
        now = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {now}")
    elif "joke" in command:
        speak(pyjokes.get_joke())
    elif "system info" in command:
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        speak(f"CPU: {cpu}%, RAM: {memory}%")
    elif "explorer" in command:
        os.system("explorer")
    elif "ask ai" in command:
        speak("What would you like to ask?")
        prompt = listen_for_command()
        if prompt:
            speak(get_ai_response(prompt))
    else:
        speak("I don't know that command.")

def listen_for_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        speak("Listening...")
        audio = r.listen(source, phrase_time_limit=10)
    try:
        return r.recognize_google(audio)
    except:
        speak("I didn't catch that.")
        return ""

# 🎨 Better GUI Design
class VoiceOSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VocalX - Voice OS")
        self.root.geometry("750x550")
        self.root.configure(bg="#121212")

        self.title_label = tk.Label(root, text="🎙️ VocalX - AI Voice OS", font=("Segoe UI", 26, "bold"),
                                    bg="#121212", fg="#00bcd4")
        self.title_label.pack(pady=40)

        self.status = tk.Label(root, text="🔄 Waiting for command...", font=("Segoe UI", 12),
                               bg="#121212", fg="#cfcfcf")
        self.status.pack(pady=10)

        btn_frame = tk.Frame(root, bg="#121212")
        btn_frame.pack(pady=30)

        self.listen_btn = tk.Button(btn_frame, text="🎧 Speak Command", font=("Segoe UI", 14, "bold"),
                                    bg="#00c853", fg="white", activebackground="#1b5e20",
                                    padx=30, pady=12, bd=0, relief=tk.FLAT,
                                    command=self.start_listening)
        self.listen_btn.grid(row=0, column=0, padx=20)

        self.exit_btn = tk.Button(btn_frame, text="❌ Exit", font=("Segoe UI", 14, "bold"),
                                  bg="#f44336", fg="white", activebackground="#c62828",
                                  padx=30, pady=12, bd=0, relief=tk.FLAT,
                                  command=self.root.quit)
        self.exit_btn.grid(row=0, column=1, padx=20)

    def start_listening(self):
        threading.Thread(target=self.voice_thread).start()

    def voice_thread(self):
        self.status.config(text="🔐 Authenticating...")
        if authenticate_user():
            self.status.config(text="🎙️ Listening...")
            command = listen_for_command()
            if command:
                respond_to_command(command)
                self.status.config(text=f"✅ Last Command: {command}")
        else:
            messagebox.showerror("Authentication", "Authentication failed")
            self.status.config(text="❌ Authentication failed")

# 🔁 Main Execution
if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceOSApp(root)
    root.mainloop()

