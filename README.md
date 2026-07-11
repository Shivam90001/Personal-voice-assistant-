# Personal Voice Assistant 🎙️

A modern, offline-supported Personal Voice Assistant built using Python, CustomTkinter, and SpeechRecognition. It runs smoothly on Windows, supporting system commands, web searches, Wikipedia querying, playing YouTube videos, setting alarms, and manual text fallback options.

---

## 🇮🇳 Hinglish Setup & Run Guide (आसान शब्दों में)

Aapka voice assistant project fully design aur write ho chuka hai. Isko chalane ke liye niche diye steps ko follow karein:

### 1. Project ko VS Code me khole (Open in VS Code)
- Apne computer me VS Code open karein.
- **File -> Open Folder** pe click karein.
- Folder select karein: `C:\Users\abc\.gemini\antigravity\scratch\Personal_Voice_Assistant`.

### 2. Dependencies Install Karein (Required Libraries)
- VS Code me integrated terminal khole (`Ctrl + ~` ya `Ctrl + Shift + \`` daba kar).
- Niche likhi command run karein dependencies install karne ke liye:
  ```bash
  pip install -r requirements.txt
  ```
  *(Important Tip: Agar **PyAudio** library install karne me koi error aaye, toh pehle terminal me `pip install pipwin` run karein, aur fir `pipwin install pyaudio` run karein).*

### 3. Application Run Karein
- Terminal me command likhein aur Enter dabayein:
  ```bash
  python main.py
  ```

### 4. Kaise Chalayein (How to Use)
App start hone ke baad ek sleek, dark-themed UI window khulegi:
- **Mic Activate Karein**: Bottom right me **"🎙️ Wake Mic"** button pe click karein ya keyboard pe `Ctrl+Alt+A` shortcut dabayein. Assistant sunna start kar dega (Status bar me "Listening..." show hoga).
- **Wake Word Detection**: Agar aap auto-listen chahte hain, toh window me niche **"Continuous Wake Word Detection"** ka checkbox tick kar dein. Ab jab bhi aap *"Hey Assistant"* bolenge, mic active ho jayega.
- **Manual Type**: Agar aapka microphone kaam nahi kar raha hai, toh input box me command type karke **"Send"** button click karein.
- **Settings Adjust Karein**: Left side panel se aap **Voice Speed (Speed slider)**, **Volume (Volume slider)**, **Male/Female Voice (Voice Type dropdown)**, aur **Dark/Light Theme** change kar sakte hain.

---

## 🇬🇧 English Setup & Usage Guide

### Features & Supported Commands

1. **System Operations**:
   - *Command*: "open notepad", "open calculator", "open chrome"
   - *Action*: Launces Notepad, Calculator, or Google Chrome.
2. **Time & Date Query**:
   - *Command*: "what's the time?", "tell me date"
   - *Action*: Reads and speaks the current time/date.
3. **Web Search**:
   - *Command*: "search google for [query]"
   - *Action*: Opens default web browser searching Google.
4. **Wikipedia Search**:
   - *Command*: "wikipedia [query]"
   - *Action*: Searches Wikipedia and speaks a concise 2-sentence summary.
5. **Play YouTube Videos**:
   - *Command*: "play lo-fi beats on youtube"
   - *Action*: Automatically opens YouTube search results.
6. **Alarms & Reminders**:
   - *Command*: "set alarm for 7:30 PM", "set reminder to study at 18:00"
   - *Action*: Parses time, schedules a background thread, displays a pop-up alert, and plays warning sound when time is reached.

### Technical Architecture
- `main.py`: Entry point coordinating initialization.
- `assistant.py`: Background thread core handling speech recognition (STT) and offline text-to-speech engine (TTS) without freezing the GUI.
- `ui.py`: CustomTkinter GUI layout incorporating status indicator canvas dots, logs, and settings.
- `actions.py`: Commands parsers and target handlers.
- `requirements.txt`: Specified library version controls.
- `tests/test_actions.py`: Python unit tests mocking network/system calls.
