import sys
import threading
import queue
import time
import speech_recognition as sr
import pyttsx3
from actions import Actions

class Assistant:
    def __init__(self, status_callback=None, ui_log_callback=None):
        """
        status_callback: function(status_string) - updates UI status (Listening, Thinking, Speaking, Idle)
        ui_log_callback: function(text, is_user) - logs text messages in the chat UI
        """
        self.status_callback = status_callback
        self.ui_log_callback = ui_log_callback
        
        # Audio functionality flags
        self.mic_available = False
        self.tts_available = False
        
        # Initialize text-to-speech
        self._init_tts()
        
        # Initialize speech recognizer
        self._init_speech_recognizer()

        # Core Action class
        self.actions = Actions(ui_callback=self.ui_log_callback, speak_callback=self.speak)

        # Threading/State control
        self.listening_active = False
        self.continuous_listening = False
        self.command_queue = queue.Queue()
        self.assistant_thread = None
        self.wake_word = "hey assistant"

    def _init_tts(self):
        try:
            self.tts_engine = pyttsx3.init()
            # Set default rate and volume
            self.tts_engine.setProperty('rate', 175)
            self.tts_engine.setProperty('volume', 0.9)
            
            # Select default English voice
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                if "en" in voice.languages or "english" in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
            self.tts_available = True
        except Exception as e:
            print(f"Warning: TTS initialization failed: {e}", file=sys.stderr)
            self.tts_engine = None

    def _init_speech_recognizer(self):
        try:
            self.recognizer = sr.Recognizer()
            self.recognizer.dynamic_energy_threshold = True
            # Check for microphone availability
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            self.mic_available = True
        except Exception as e:
            print(f"Warning: Microphone initialization failed (SpeechRecognition/PyAudio issues): {e}", file=sys.stderr)
            self.recognizer = None
            self.mic_available = False

    def set_voice_rate(self, rate):
        if self.tts_available and self.tts_engine:
            try:
                self.tts_engine.setProperty('rate', int(rate))
            except Exception:
                pass

    def set_voice_volume(self, volume):
        if self.tts_available and self.tts_engine:
            try:
                # volume is expected to be a float between 0.0 and 1.0
                self.tts_engine.setProperty('volume', float(volume))
            except Exception:
                pass

    def set_voice_gender(self, gender):
        if self.tts_available and self.tts_engine:
            try:
                voices = self.tts_engine.getProperty('voices')
                for voice in voices:
                    name_lower = voice.name.lower()
                    if gender == "Female" and ("female" in name_lower or "zira" in name_lower or "hazel" in name_lower):
                        self.tts_engine.setProperty('voice', voice.id)
                        return
                    elif gender == "Male" and ("male" in name_lower or "david" in name_lower or "mark" in name_lower):
                        self.tts_engine.setProperty('voice', voice.id)
                        return
            except Exception:
                pass

    def update_status(self, status):
        if self.status_callback:
            self.status_callback(status)

    def speak(self, text):
        """Speaks out loud using TTS engine (runs inside background thread)."""
        if self.tts_available and self.tts_engine:
            self.update_status("Speaking...")
            try:
                # Ensure engine starts loop safely
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"TTS speak error: {e}", file=sys.stderr)
        self.update_status("Idle")

    def start_listening_thread(self, continuous=False):
        """Starts a background thread to handle speech listening."""
        if not self.mic_available or not self.recognizer:
            self.ui_log_callback("Error: Audio input (Microphone/PyAudio) is not working. Please use the manual text command bar.", is_user=False)
            return

        self.continuous_listening = continuous
        self.listening_active = True
        
        if self.assistant_thread is None or not self.assistant_thread.is_alive():
            self.assistant_thread = threading.Thread(target=self._run_assistant_loop, daemon=True)
            self.assistant_thread.start()

    def stop_listening(self):
        """Stops the listening thread loop."""
        self.listening_active = False
        self.continuous_listening = False
        self.update_status("Idle")

    def _run_assistant_loop(self):
        while self.listening_active:
            if self.continuous_listening:
                self._listen_for_wake_word()
            else:
                self._listen_once()
                self.listening_active = False # Listen once and stop
                
        self.update_status("Idle")

    def _listen_once(self):
        self.update_status("Listening...")
        with sr.Microphone() as source:
            try:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
                self.update_status("Thinking...")
                
                command = self.recognizer.recognize_google(audio)
                if self.ui_log_callback:
                    self.ui_log_callback(command, is_user=True)
                self.process_command(command)
                
            except sr.WaitTimeoutError:
                self._log_and_speak("Listening timed out. No speech detected.")
            except sr.UnknownValueError:
                self._log_and_speak("Sorry, I could not understand what you said.")
            except sr.RequestError as e:
                self._log_and_speak("Could not request results from Google Speech Recognition; check your internet connection.")
            except Exception as e:
                self._log_and_speak(f"Error occurred while listening: {str(e)}")

    def _listen_for_wake_word(self):
        self.update_status("Listening for Wake Word...")
        with sr.Microphone() as source:
            try:
                # Shorter timeouts for wake word checks
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=4)
                
                text = self.recognizer.recognize_google(audio).lower()
                
                # Check for wake word
                if self.wake_word in text:
                    self._log_and_speak("Yes, how can I help you?")
                    
                    # Wait briefly for follow-up command
                    self.update_status("Listening...")
                    audio_cmd = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
                    self.update_status("Thinking...")
                    
                    command = self.recognizer.recognize_google(audio_cmd)
                    if self.ui_log_callback:
                        self.ui_log_callback(command, is_user=True)
                    self.process_command(command)
            except (sr.WaitTimeoutError, sr.UnknownValueError):
                pass # Just continue loop silently
            except Exception as e:
                print(f"Wake word loop error: {e}", file=sys.stderr)
                time.sleep(1)

    def _log_and_speak(self, msg):
        if self.ui_log_callback:
            self.ui_log_callback(msg, is_user=False)
        self.speak(msg)

    def process_command(self, command):
        """Routes parsed text commands to corresponding Actions methods."""
        cmd = command.lower().strip()
        self.update_status("Thinking...")
        
        # Check command intents
        if "open" in cmd:
            name = cmd.replace("open", "").strip()
            # Check if it's in the list of website keywords
            if any(site in name for site in self.actions.websites.keys()):
                self.actions.open_website(name)
            else:
                self.actions.open_app(name)
        
        elif "time" in cmd:
            self.actions.tell_time()
            
        elif "date" in cmd:
            self.actions.tell_date()

        elif "day" in cmd:
            self.actions.tell_day()

        elif "month" in cmd:
            self.actions.tell_month()

        elif "year" in cmd:
            self.actions.tell_year()

        elif "search google for" in cmd or "search for" in cmd:
            self.actions.search_google(cmd)
            
        elif "wikipedia" in cmd:
            self.actions.search_wikipedia(cmd)
            
        elif "play" in cmd and "youtube" in cmd:
            self.actions.play_youtube(cmd)
            
        elif "alarm" in cmd or "reminder" in cmd:
            if "show" in cmd or "active" in cmd or "list" in cmd:
                self.actions.show_alarms()
            elif "clear" in cmd or "remove" in cmd or "delete" in cmd:
                self.actions.clear_alarms()
            else:
                self.actions.set_alarm_reminder(cmd)
                
        elif "joke" in cmd:
            self.actions.tell_joke()

        elif "riddle" in cmd:
            self.actions.tell_riddle()

        elif "fact" in cmd:
            self.actions.tell_fact()

        elif "roll" in cmd and ("dice" in cmd or "die" in cmd):
            self.actions.roll_dice()

        elif "flip" in cmd or "toss" in cmd:
            self.actions.flip_coin()

        elif "password" in cmd:
            self.actions.generate_password()

        elif "random number" in cmd:
            self.actions.generate_random_number()

        elif "reverse" in cmd:
            self.actions.reverse_text(cmd)

        elif "count words" in cmd or "word count" in cmd:
            self.actions.word_count(cmd)

        elif "count characters" in cmd or "character count" in cmd:
            self.actions.char_count(cmd)

        elif "uppercase" in cmd:
            self.actions.convert_uppercase(cmd)
            
        elif cmd in ["exit", "stop", "quit", "close"]:
            self._log_and_speak("Goodbye! Have a nice day.")
            if self.status_callback:
                # Send special status to let UI know it should quit
                self.status_callback("Exit")
        
        else:
            # Default fallback to conversation
            self.actions.general_greet(cmd)
