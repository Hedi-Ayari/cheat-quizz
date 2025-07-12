import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'G:\Tesseract-OCR\tesseract.exe'  # Update path if needed
import mss
import threading
import tkinter as tk

import keyboard
import requests
import time
from plyer import notification
from PIL import Image

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral:latest"  

def extract_text_from_screen():
    with mss.mss() as sct:
        screenshot = sct.grab(sct.monitors[1])  
        img = Image.frombytes('RGB', (screenshot.width, screenshot.height), screenshot.rgb)
        text = pytesseract.image_to_string(img)
        return text


def ask_ollama(question_text):
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": OLLAMA_MODEL,
            "prompt": f"Answer this multiple choice quiz question briefly and clearly with small phrase max 1 line:\n\n{question_text}",
            "stream": False
        })

        if response.status_code == 200:
            return response.json().get('response', '').strip()
        else:
            return f"❌ Ollama Error: {response.text}"

    except Exception as e:
        return f"⚠️ Failed to connect to Ollama: {str(e)}"

def show_notification(answer):
    def popup():
        root = tk.Tk()
        root.overrideredirect(True)  # No window borders
        root.attributes("-topmost", True)  # Stay on top
        root.attributes("-alpha", 0.6)  # More transparent
        root.configure(bg="#222222")  # Darker background for subtlety

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        width, height = 350, 80
        x = screen_width - width - 20
        y = screen_height - height - 60
        root.geometry(f"{width}x{height}+{x}+{y}")

        label = tk.Label(
            root,
            text=answer,
            font=("Segoe UI", 9),  # Smaller font
            fg="#888888",          # Less contrast (gray text)
            bg="#222222",          # Match background
            wraplength=320,
            justify="left"
        )
        label.pack(padx=10, pady=10)

        root.after(3000, root.destroy)  # Close after 3 seconds
        root.mainloop()

    threading.Thread(target=popup).start()

def main():
    print("▶️ QuizBot (Ollama Mode) is running. Press the '²' key to capture a question.")
    while True:
        if keyboard.is_pressed('²'):
            print("🔍 Capturing screen...")
            question = extract_text_from_screen()
            if not question.strip():
                print("⚠️ No text detected on screen. Please ensure the question is visible.")
                show_notification("No text detected. Ensure question is visible.")
                time.sleep(1)
                continue
            print("🧠 Sending to Mistral (Ollama)...")
            answer = ask_ollama(question)
            print("", answer)
            show_notification(answer)
            time.sleep(5)
        time.sleep(0.1)

if __name__ == "__main__":
    main()
