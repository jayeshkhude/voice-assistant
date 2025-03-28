import speech_recognition as sr
import pyttsx3
import pyautogui
import os
import threading
import tkinter as tk
import webbrowser
from serpapi import GoogleSearch

# Set up SerpAPI Key (DO NOT SHARE THIS PUBLICLY)
SERP_API_KEY = "616b98d445eee3430be78f8a559a72b014edc90d16e87d3bec7bf3db58525634"  # Replace with your actual key


# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 160)
engine.setProperty('volume', 1.0)
stop_speaking_flag = False  # Flag to stop speech mid-sentence

# Set voice (Handle different systems)
voices = engine.getProperty('voices')
if len(voices) > 1:
    engine.setProperty('voice', voices[1].id)

recognizer = sr.Recognizer()
listening = False  # Global flag to control listening state

def speak(text):
    """Convert text to speech and display in terminal."""
    global stop_speaking_flag
    print(f"🔊 Assistant: {text}")
    stop_speaking_flag = False  # Reset flag before speaking

    def run_speech():
        engine.say(text)
        engine.runAndWait()

    speech_thread = threading.Thread(target=run_speech)
    speech_thread.start()

    while speech_thread.is_alive():
        if stop_speaking_flag:
            engine.stop()
            break

def stop_speaking():
    """Stop the assistant from speaking immediately."""
    global stop_speaking_flag
    stop_speaking_flag = True

def ask_serpapi(query):
    """Fetch and return search results from SerpAPI."""
    if not SERP_API_KEY:
        speak("Error: SerpAPI key is missing!")
        return

    try:
        params = {
            "q": query,
            "api_key": SERP_API_KEY,
            "num": 3,
            "hl": "en",
        }
        search = GoogleSearch(params)
        results = search.get_dict()

        answer = ""
        if "answer_box" in results and "snippet" in results["answer_box"]:
            answer = results["answer_box"]["snippet"]
        elif "knowledge_graph" in results and "description" in results["knowledge_graph"]:
            answer = results["knowledge_graph"]["description"]
        elif "organic_results" in results and results["organic_results"]:
            answer = "\n".join(
                [res["snippet"] for res in results["organic_results"][:3] if "snippet" in res]
            )

        if answer:
            print(f"✅ Search Result:\n{answer}")
            speak(answer)
        else:
            speak("I couldn't find any results.")
            print("⚠️ No search results found.")

    except Exception as e:
        speak("There was an error fetching search results.")
        print(f"🔥 SerpAPI Error: {e}")

def listen():
    """Continuously listen for commands and execute them."""
    global listening
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        while listening:
            print("🎤 Listening...")
            try:
                audio = recognizer.listen(source, timeout=5)
                command = recognizer.recognize_google(audio).lower()
                print(f"🗣 You said: {command}")
                execute_command(command)
            except sr.UnknownValueError:
                speak("Sorry, I didn't understand.")
            except sr.RequestError:
                speak("Could not connect to the internet.")
            except sr.WaitTimeoutError:
                print("⏳ No speech detected, try again.")

def start_listening():
    """Start voice recognition in a separate thread."""
    global listening
    listening = True
    threading.Thread(target=listen, daemon=True).start()

def stop_listening():
    """Stop voice recognition."""
    global listening
    listening = False
    speak("Stopping listening mode.")

def search_youtube(query):
    """Search for something on YouTube and show the results."""
    search_query = query.replace("search on youtube", "").strip()
    if search_query:
        speak(f"Searching for {search_query} on YouTube.")
        search_url = f"https://www.youtube.com/results?search_query={search_query}"
        try:
            webbrowser.open(search_url)
        except Exception as e:
            speak("Sorry, I couldn't open YouTube.")
            print(f"⚠️ Error opening YouTube: {e}")
    else:
        speak("Please provide something to search for.")

def execute_command(command):
    """Process the command and take action."""
    if command.startswith("tell me"):
        query = command.replace("tell me", "").strip()
        speak(f"Searching for {query}...")
        ask_serpapi(query)
    
    elif "open google" in command:
        speak("Opening Google.")
        os.system("start https://www.google.com")

    elif "open youtube" in command:
        speak("Opening YouTube.")
        os.system("start https://www.youtube.com")

    elif "search on youtube" in command:
        search_youtube(command)

    elif "take screenshot" in command:
        screenshot = pyautogui.screenshot()
        screenshot.save("screenshot.png")
        speak("Screenshot saved.")

    elif "volume up" in command:
        pyautogui.press("volumeup", presses=5)

    elif "volume down" in command:
        pyautogui.press("volumedown", presses=5)

    elif "mute volume" in command:
        pyautogui.press("volumemute")

    elif "shutdown computer" in command:
        speak("Shutting down the computer.")
        os.system("shutdown /s /t 5")

    elif "restart computer" in command:
        speak("Restarting the computer.")
        os.system("shutdown /r /t 5")

    elif "exit" in command or "stop" in command:
        speak("Goodbye!")
        stop_listening()
        root.quit()

def create_gui():
    """Create the GUI for the assistant."""
    global root
    root = tk.Tk()
    root.title("Voice Assistant")
    root.geometry("300x300")  # Smaller window size for simplicity

    tk.Label(root, text="Voice Assistant", font=("Arial", 16)).pack(pady=10)

    tk.Button(root, text="Start Listening", command=start_listening, width=20, height=2).pack(pady=5)
    tk.Button(root, text="Stop Listening", command=stop_listening, width=20, height=2).pack(pady=5)
    tk.Button(root, text="Stop Speaking", command=stop_speaking, width=20, height=2, bg="orange").pack(pady=5)
    tk.Button(root, text="Exit", command=root.quit, width=20, height=2, bg="red", fg="white").pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
