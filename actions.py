import os
import subprocess
import webbrowser
import datetime
import re
import threading
import time
import random
import wikipedia
import string

class Actions:
    def __init__(self, ui_callback=None, speak_callback=None):
        """
        ui_callback: function to log messages in the UI chat log.
        speak_callback: function to speak responses back using TTS.
        """
        self.ui_callback = ui_callback
        self.speak_callback = speak_callback
        self.active_alarms = []

        # List of Jokes
        self.jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? Because he was outstanding in his field!",
            "Why don't skeletons fight each other? They don't have the guts.",
            "What do you call a fake noodle? An impasta!",
            "How does a penguin build its house? Igloos it together!",
            "Why did the bicycle fall over? Because it was two-tired!",
            "What do you call cheese that isn't yours? Nacho cheese!",
            "Why did the math book look sad? Because it had too many problems!",
            "Why don't some couples go to the gym? Because some relationships don't work out!",
            "I would tell you a chemistry joke, but I know I wouldn't get a reaction."
        ]

        # List of Riddles
        self.riddles = [
            ("What has hands but cannot clap?", "A clock!"),
            ("What has to be broken before you can use it?", "An egg!"),
            ("What has one eye but cannot see?", "A needle!"),
            ("What has legs but does not walk?", "A table!"),
            ("What is full of holes but still holds water?", "A sponge!"),
            ("What goes up but never comes down?", "Your age!"),
            ("What belongs to you, but other people use it more than you do?", "Your name!"),
            ("The more of them you take, the more you leave behind. What are they?", "Footsteps!"),
            ("What has a neck but no head?", "A bottle!"),
            ("If you feed me, I live. If you give me a drink, I die. What am I?", "Fire!")
        ]

        # List of Fun Facts
        self.fun_facts = [
            "Honey never spoils. You can theoretically eat 3,000-year-old honey!",
            "Bananas are berries, but strawberries aren't.",
            "A day on Venus is longer than a year on Venus.",
            "Wombat poop is cube-shaped, which stops it from rolling away.",
            "Octopuses have three hearts and blue blood.",
            "The total weight of all the ants on Earth is roughly equal to the total weight of all humans.",
            "Some turtles can breathe through their butts.",
            "Cowboys didn't actually wear cowboy hats; bowler hats were much more popular.",
            "Scotland has 421 words for 'snow'.",
            "A single strand of spaghetti is called a spaghetto."
        ]

        # List of website mappings (20 websites)
        self.websites = {
            "gmail": "https://mail.google.com",
            "github": "https://github.com",
            "stackoverflow": "https://stackoverflow.com",
            "reddit": "https://www.reddit.com",
            "twitter": "https://x.com",
            "x.com": "https://x.com",
            "facebook": "https://www.facebook.com",
            "linkedin": "https://www.linkedin.com",
            "google maps": "https://maps.google.com",
            "google translate": "https://translate.google.com",
            "amazon": "https://www.amazon.com",
            "netflix": "https://www.netflix.com",
            "spotify": "https://open.spotify.com",
            "weather": "https://www.weather.com",
            "news": "https://news.google.com",
            "stocks": "https://finance.yahoo.com",
            "discord": "https://discord.com",
            "chatgpt": "https://chatgpt.com",
            "wikipedia": "https://www.wikipedia.org",
            "google": "https://www.google.com"
        }

        # List of Windows executable mappings (20 system utilities)
        self.system_apps = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "calc": "calc.exe",
            "chrome": "chrome.exe",
            "paint": "mspaint.exe",
            "mspaint": "mspaint.exe",
            "task manager": "taskmgr.exe",
            "taskmgr": "taskmgr.exe",
            "settings": "start ms-settings:",
            "control panel": "control.exe",
            "explorer": "explorer.exe",
            "file explorer": "explorer.exe",
            "cmd": "cmd.exe",
            "command prompt": "cmd.exe",
            "powershell": "powershell.exe",
            "wordpad": "write.exe",
            "snipping tool": "snippingtool.exe",
            "on screen keyboard": "osk.exe",
            "osk": "osk.exe",
            "device manager": "devmgmt.msc",
            "services": "services.msc",
            "registry editor": "regedit.exe",
            "regedit": "regedit.exe",
            "disk management": "diskmgmt.msc",
            "event viewer": "eventvwr.msc",
            "system information": "msinfo32.exe",
            "character map": "charmap.exe",
            "cleanmgr": "cleanmgr.exe",
            "disk cleanup": "cleanmgr.exe"
        }

        # Chit-chat conversational pattern mappings (30 patterns)
        self.chit_chat = {
            r"\bhello\b|\bhi\b|\bhey\b": [
                "Hello there! How can I help you today?",
                "Hi! Hope you are having a wonderful day. What can I do for you?",
                "Hey! Good to hear from you. What's on your mind?"
            ],
            r"good morning": ["Good morning! Have a productive and great day ahead!"],
            r"good afternoon": ["Good afternoon! Hope your day is going smoothly."],
            r"good evening": ["Good evening! How was your day? How can I assist you tonight?"],
            r"how are you|how's it going": [
                "I'm functioning at full capacity! Thank you for asking. How are you?",
                "I am doing great! Ready to help you. How is your day going?",
                "All systems are green! I'm feeling wonderful. How are you?"
            ],
            r"what is your name|who are you": [
                "I am your Personal Voice Assistant, ready to help you with your daily tasks!",
                "You can call me your Personal Voice Assistant. What's your name?"
            ],
            r"what is your age|how old are you": [
                "I was compiled recently, so I am technically very young, but I hold a lot of information!",
                "Age is just a number for software! I don't grow old."
            ],
            r"where do you live|where are you located": [
                "I live in your computer's memory! No rent, plenty of space.",
                "I reside in the digital world, running right here on your machine."
            ],
            r"are you human|are you real": [
                "I am an artificial intelligence, not a human, but I do my best to communicate like one!",
                "I am a virtual assistant built using Python. So, digital rather than human."
            ],
            r"do you sleep": [
                "No, sleep is for organic beings. I am always awake and ready!",
                "I don't sleep. I just wait in low-power idle mode until you run me."
            ],
            r"do you eat": [
                "I consume electricity and process computer bytes, but no real food!",
                "I don't eat, but I do love a healthy flow of clean code."
            ],
            r"meaning of life": [
                "The meaning of life is what you make of it. Also, some say it is forty-two!",
                "To learn, grow, and enjoy the moments you have."
            ],
            r"have feelings|do you feel": [
                "I don't have emotions like humans do, but I am programmed to be friendly and helpful!",
                "No feelings here, just logic and algorithms. But I appreciate your kindness!"
            ],
            r"are you smart": [
                "I can perform math, open apps, search the web, and answer questions. You tell me!",
                "I am as smart as the code written inside me. I learn more every day."
            ],
            r"who made you|your creator": [
                "I was created as a personal coding project!",
                "A talented programmer wrote my code in Python."
            ],
            r"sup|what's up": [
                "Not much, just hanging out in RAM. What's up with you?",
                "Just running background tasks. How can I help you?"
            ],
            r"long time no see": ["Yes indeed! Glad to be back. How can I help?"],
            r"thank you|thanks": [
                "You're very welcome!",
                "Glad I could help!",
                "No problem, happy to assist!"
            ],
            r"who is your favorite actor": ["I don't watch movies, but I think the computer processor is quite a performer!"],
            r"what can you do": ["I can open system apps, search Google, look up Wikipedia, play YouTube, set alarms/reminders, calculate math, tell jokes, and have a chat!"],
            r"are you married": ["I am married to my job of assisting you!"],
            r"tell me something interesting": ["Did you know that honey never spoils? Archaeologists have found pots of honey in ancient Egyptian tombs that are thousands of years old and still perfectly edible!"],
            r"favorite color": ["I really like neon blue and purple waves. They look very modern!"],
            r"make me laugh": ["I will try! Why did the computer catch a cold? Because it left its Windows open!"],
            r"do you believe in god": ["That is a deep philosophical question. I am just a program, so I leave beliefs to humans."],
            r"are you a robot": ["I am a software robot, yes! A virtual assistant running on Windows."],
            r"do you like humans": ["Yes! Humans write great code and create interesting questions. You are my favorite species."],
            r"tell me a secret": ["If you press Ctrl+Alt+A, you can toggle my mic without clicking anything. Shhh!"],
            r"compliment me": ["You are doing a fantastic job, and your coding project ideas are wonderful!"],
            r"i am tired": ["Take a break, drink some water, and rest. I will be here whenever you get back."]
        }

    def _log(self, text):
        if self.ui_callback:
            self.ui_callback(text, is_user=False)
        print(f"Assistant: {text}")

    def _speak(self, text):
        self._log(text)
        if self.speak_callback:
            self.speak_callback(text)

    def open_app(self, app_name):
        """Opens common system applications on Windows."""
        app_name_lower = app_name.lower().strip()
        matched_exe = None
        
        for key, val in self.system_apps.items():
            if key in app_name_lower:
                matched_exe = val
                break
                
        if matched_exe:
            try:
                if matched_exe.startswith("start "):
                    # Special shell command for settings
                    subprocess.Popen(matched_exe, shell=True)
                else:
                    subprocess.Popen(matched_exe)
                self._speak(f"Opening {app_name.capitalize()}.")
            except Exception as e:
                self._speak(f"Failed to open {app_name}. Error: {str(e)}")
        else:
            self._speak(f"Sorry, I don't know how to open '{app_name}'. Check README for supported system apps.")

    def open_website(self, site_name):
        """Opens mapped websites directly in the browser."""
        site_name_lower = site_name.lower().strip()
        matched_url = None
        
        for key, val in self.websites.items():
            if key in site_name_lower:
                matched_url = val
                break
                
        if matched_url:
            webbrowser.open(matched_url)
            self._speak(f"Opening {site_name.capitalize()} in your browser.")
        else:
            # Fallback: just open search
            webbrowser.open(f"https://www.google.com/search?q={site_name}")
            self._speak(f"Opening search page for '{site_name}'.")

    def tell_time(self):
        now = datetime.datetime.now()
        current_time = now.strftime("%I:%M %p")
        self._speak(f"The current time is {current_time}.")
        return current_time

    def tell_date(self):
        now = datetime.datetime.now()
        current_date = now.strftime("%A, %B %d, %Y")
        self._speak(f"Today's date is {current_date}.")
        return current_date

    def tell_day(self):
        now = datetime.datetime.now()
        current_day = now.strftime("%A")
        self._speak(f"Today is {current_day}.")
        return current_day

    def tell_month(self):
        now = datetime.datetime.now()
        current_month = now.strftime("%B")
        self._speak(f"The current month is {current_month}.")
        return current_month

    def tell_year(self):
        now = datetime.datetime.now()
        current_year = now.strftime("%Y")
        self._speak(f"The current year is {current_year}.")
        return current_year

    def search_google(self, query):
        search_query = query.replace("search google for", "").replace("search for", "").strip()
        if not search_query:
            self._speak("What do you want me to search for?")
            return
        url = f"https://www.google.com/search?q={search_query}"
        webbrowser.open(url)
        self._speak(f"Searching Google for {search_query}.")

    def search_wikipedia(self, query):
        wiki_query = query.replace("wikipedia", "").replace("search wikipedia for", "").strip()
        if not wiki_query:
            self._speak("What should I search on Wikipedia?")
            return
        
        self._log(f"Searching Wikipedia for '{wiki_query}'...")
        try:
            wikipedia.set_lang("en")
            summary = wikipedia.summary(wiki_query, sentences=2)
            self._speak(summary)
        except wikipedia.exceptions.DisambiguationError as e:
            options = ", ".join(e.options[:3])
            self._speak(f"Wikipedia returned multiple options: {options}. Please be more specific.")
        except wikipedia.exceptions.PageError:
            self._speak(f"Sorry, I couldn't find any Wikipedia page for '{wiki_query}'.")
        except Exception as e:
            self._speak(f"An error occurred while connecting to Wikipedia: {str(e)}")

    def play_youtube(self, query):
        yt_query = query.replace("play", "").replace("on youtube", "").strip()
        if not yt_query:
            self._speak("What do you want me to play on YouTube?")
            return
        url = f"https://www.youtube.com/results?search_query={yt_query}"
        webbrowser.open(url)
        self._speak(f"Playing {yt_query} on YouTube.")

    def set_alarm_reminder(self, text):
        time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(AM|PM|am|pm)?', text)
        if not time_match:
            self._speak("I couldn't parse the time. Please specify a time like '7:30 AM' or '18:00'.")
            return
        
        hours = int(time_match.group(1))
        minutes = int(time_match.group(2)) if time_match.group(2) else 0
        meridiem = time_match.group(3)

        if meridiem:
            meridiem = meridiem.upper()
            if meridiem == "PM" and hours < 12:
                hours += 12
            elif meridiem == "AM" and hours == 12:
                hours = 0

        if hours < 0 or hours > 23 or minutes < 0 or minutes > 59:
            self._speak("Invalid time format. Hours must be 0-23 (or 1-12 AM/PM) and minutes 0-59.")
            return

        now = datetime.datetime.now()
        target_time = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)
        
        if target_time < now:
            target_time += datetime.timedelta(days=1)

        delay = (target_time - now).total_seconds()
        
        is_alarm = "alarm" in text.lower()
        label = "Alarm" if is_alarm else "Reminder"
        
        message = "Time's up!"
        if not is_alarm:
            message_match = re.search(r'(?:reminder to|remind me to)\s+(.*?)\s+(?:at|for)', text.lower())
            if message_match:
                message = message_match.group(1).strip()
            else:
                parts = text.lower().split("to")
                if len(parts) > 1:
                    message = parts[-1].replace(f"at {time_match.group(0)}", "").strip()

        formatted_target = target_time.strftime("%I:%M %p (%d %B)")
        self._speak(f"{label} successfully set for {formatted_target}.")
        
        t = threading.Thread(target=self._alarm_thread, args=(delay, label, message), daemon=True)
        t.start()
        self.active_alarms.append((target_time, label, message))

    def _alarm_thread(self, delay, label, message):
        time.sleep(delay)
        alert_text = f"🔔 ALERT: {label}! {message.capitalize()}"
        self._speak(alert_text)
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, f"{label}: {message}", "Voice Assistant Notification", 0x40 | 0x1000)
        except Exception:
            pass

    def show_alarms(self):
        """Displays currently active alarms/reminders."""
        if not self.active_alarms:
            self._speak("There are no active alarms or reminders.")
            return
        
        msg = "Here are your active alarms:\n"
        for i, (t_time, label, message) in enumerate(self.active_alarms, 1):
            msg += f"{i}. {label} set for {t_time.strftime('%I:%M %p')} - {message}\n"
        self._speak(msg.strip())

    def clear_alarms(self):
        """Clears scheduled list of alarms."""
        self.active_alarms.clear()
        self._speak("All scheduled alarms and reminders have been cleared.")

    def run_math_calculation(self, cmd):
        """Parses and computes basic mathematical queries."""
        # Find expressions like '5 plus 6', '10 divided by 2', 'square of 9', 'square root of 16'
        expr = cmd.replace("calculate", "").replace("what is", "").replace("what's", "").strip()
        expr = expr.replace("plus", "+").replace("minus", "-").replace("multiply by", "*").replace("multiplied by", "*").replace("times", "*").replace("divided by", "/").replace("divide", "/")
        
        # Handle Square Root
        if "square root of" in expr:
            try:
                num = float(re.search(r'square root of\s*(\d+(\.\d+)?)', expr).group(1))
                res = num ** 0.5
                self._speak(f"The square root of {num} is {res}.")
                return
            except Exception:
                pass
                
        # Handle Square
        if "square of" in expr:
            try:
                num = float(re.search(r'square of\s*(\d+(\.\d+)?)', expr).group(1))
                res = num * num
                self._speak(f"The square of {num} is {res}.")
                return
            except Exception:
                pass

        # Direct expression evaluation
        clean_expr = re.sub(r'[^0-9\+\-\*\/\.\(\)\s]', '', expr)
        if not clean_expr.strip():
            self._speak("I couldn't parse the mathematical expression.")
            return
            
        try:
            # Evaluate clean expression safely
            result = eval(clean_expr, {"__builtins__": None}, {})
            self._speak(f"The answer is {result}.")
        except Exception:
            self._speak("Sorry, I had trouble calculating that. Make sure it's a simple mathematical expression.")

    # ==========================================
    # PRODUCTIVITY & UTILITIES
    # ==========================================
    def roll_dice(self):
        res = random.randint(1, 6)
        self._speak(f"🎲 You rolled a {res}!")

    def flip_coin(self):
        res = random.choice(["Heads", "Tails"])
        self._speak(f"🪙 It's {res}!")

    def generate_password(self):
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        pwd = "".join(random.choice(chars) for _ in range(12))
        self._log(f"🔑 Generated Password: {pwd}")
        if self.speak_callback:
            self.speak_callback("I have generated a 12-character secure password and logged it in the chat bubble.")

    def generate_random_number(self):
        res = random.randint(1, 100)
        self._speak(f"🔢 Your random number is {res}.")

    def reverse_text(self, cmd):
        text = cmd.replace("reverse text", "").replace("reverse", "").strip()
        if not text:
            self._speak("What text do you want me to reverse?")
            return
        reversed_text = text[::-1]
        self._speak(f"Reversed text: {reversed_text}")

    def word_count(self, cmd):
        text = cmd.replace("count words in", "").replace("word count of", "").strip()
        if not text:
            self._speak("Please specify the text to count.")
            return
        count = len(text.split())
        self._speak(f"There are {count} words in that text.")

    def char_count(self, cmd):
        text = cmd.replace("count characters in", "").replace("character count of", "").strip()
        if not text:
            self._speak("Please specify the text to count.")
            return
        count = len(text)
        self._speak(f"There are {count} characters (including spaces) in that text.")

    def convert_uppercase(self, cmd):
        text = cmd.replace("convert to uppercase", "").replace("uppercase", "").strip()
        if not text:
            self._speak("What text should I convert?")
            return
        self._speak(text.upper())

    # ==========================================
    # JOKES, RIDDLES, FACTS
    # ==========================================
    def tell_joke(self):
        joke = random.choice(self.jokes)
        self._speak(joke)

    def tell_riddle(self):
        riddle, answer = random.choice(self.riddles)
        self._speak(f"Here is a riddle: {riddle}")
        # Wait a short delay before giving the answer
        threading.Thread(target=self._reveal_riddle_answer, args=(answer,), daemon=True).start()

    def _reveal_riddle_answer(self, answer):
        time.sleep(5)
        self._speak(f"Thinking time over! The answer is: {answer}")

    def tell_fact(self):
        fact = random.choice(self.fun_facts)
        self._speak(fact)

    # ==========================================
    # CONVERSATIONAL ROUTER
    # ==========================================
    def general_greet(self, command):
        """Matches user queries with chit_chat triggers and responds."""
        cmd = command.lower().strip()
        
        # Check math calculations first
        if any(op in cmd for op in ["plus", "minus", "multiply", "times", "divided by", "divide", "square root", "square of", "calculate", "what is"]):
            # Make sure it contains numbers, else fall through to greet
            if re.search(r'\d', cmd):
                self.run_math_calculation(cmd)
                return

        # Check conversation regex keys
        for pattern, responses in self.chit_chat.items():
            if re.search(pattern, cmd):
                self._speak(random.choice(responses))
                return
                
        # Default response
        self._speak("I'm not sure how to respond to that. You can ask me to open tools, search the web, tell a joke/fact/riddle, do math, or type a query.")
