import os
import datetime
import tkinter as tk
import threading
from tkinter import messagebox, filedialog
import customtkinter as ctk
from PIL import Image

class AssistantUI(ctk.CTk):
    def __init__(self, assistant_instance=None):
        super().__init__()
        
        self.assistant = assistant_instance
        
        # Configure window
        self.title("Personal Voice Assistant")
        self.geometry("850x650")
        self.minsize(700, 500)
        
        # Set default appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Icon loading
        self.load_app_icon()
        
        # Track history
        self.chat_history_file = "voice_assistant_history.txt"
        
        # Build UI layout
        self.create_widgets()
        
        # Tie assistant callbacks if instance exists
        if self.assistant:
            self.assistant.status_callback = self.update_status
            self.assistant.ui_log_callback = self.log_interaction
            
            # Populate initial values in settings
            if hasattr(self.assistant, 'mic_available') and not self.assistant.mic_available:
                self.log_interaction("Warning: Microphone not detected. Keyboard manual commands are enabled.", is_user=False)
        
        # Register global/app-level hotkey (Ctrl+Alt+A)
        self.bind("<Control-Alt-Key-a>", lambda event: self.toggle_voice_input())
        self.bind("<Control-Key-a>", lambda event: self.toggle_voice_input()) # Simple Ctrl+A shortcut for convenience

    def load_app_icon(self):
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.jpg")
        if os.path.exists(icon_path):
            try:
                # Set window icon
                self.iconbitmap(icon_path)
            except Exception:
                try:
                    img = Image.open(icon_path)
                    photo = tk.PhotoImage(img)
                    self.wm_iconphoto(True, photo)
                except Exception:
                    pass

    def create_widgets(self):
        # Configure Grid layout (1 row, 2 columns: Sidebar & Main Area)
        self.grid_columnconfigure(0, weight=1) # Sidebar
        self.grid_columnconfigure(1, weight=3) # Main chat area
        self.grid_rowconfigure(0, weight=1)
        
        # ==========================================
        # SIDEBAR (SETTINGS & OPTIONS)
        # ==========================================
        self.sidebar = ctk.CTkFrame(self, corner_radius=0, width=220)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar.grid_rowconfigure(9, weight=1) # Spacer
        
        # Title Label
        self.logo_label = ctk.CTkLabel(self.sidebar, text="VOICE ASSISTANT", font=ctk.CTkFont(size=18, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 5))
        self.sub_logo_label = ctk.CTkLabel(self.sidebar, text="Voice Assistant", font=ctk.CTkFont(size=12, slant="italic"))
        self.sub_logo_label.grid(row=1, column=0, padx=20, pady=(0, 20))
        
        # Theme Setting
        self.theme_label = ctk.CTkLabel(self.sidebar, text="Appearance Mode:", anchor="w")
        self.theme_label.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="w")
        self.theme_menu = ctk.CTkOptionMenu(self.sidebar, values=["Dark", "Light", "System"], command=self.change_theme)
        self.theme_menu.grid(row=3, column=0, padx=20, pady=(5, 10), sticky="ew")
        
        # Voice Settings Panel
        self.voice_settings_label = ctk.CTkLabel(self.sidebar, text="TTS Settings:", font=ctk.CTkFont(weight="bold"))
        self.voice_settings_label.grid(row=4, column=0, padx=20, pady=(15, 5), sticky="w")
        
        # Voice rate
        self.rate_label = ctk.CTkLabel(self.sidebar, text="Speed: 175 wpm")
        self.rate_label.grid(row=5, column=0, padx=20, pady=(5, 0), sticky="w")
        self.rate_slider = ctk.CTkSlider(self.sidebar, from_=100, to=300, number_of_steps=20, command=self.change_voice_rate)
        self.rate_slider.set(175)
        self.rate_slider.grid(row=6, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        # Voice volume
        self.volume_label = ctk.CTkLabel(self.sidebar, text="Volume: 90%")
        self.volume_label.grid(row=7, column=0, padx=20, pady=(5, 0), sticky="w")
        self.volume_slider = ctk.CTkSlider(self.sidebar, from_=0, to=100, number_of_steps=10, command=self.change_voice_volume)
        self.volume_slider.set(90)
        self.volume_slider.grid(row=8, column=0, padx=20, pady=(0, 15), sticky="ew")
        
        # Voice selection
        self.voice_gender_label = ctk.CTkLabel(self.sidebar, text="Voice Type:", anchor="w")
        self.voice_gender_label.grid(row=9, column=0, padx=20, pady=(5, 0), sticky="w")
        self.voice_gender_menu = ctk.CTkOptionMenu(self.sidebar, values=["Male", "Female"], command=self.change_voice_gender)
        self.voice_gender_menu.grid(row=10, column=0, padx=20, pady=(5, 15), sticky="ew")
        
        # System buttons
        self.clear_btn = ctk.CTkButton(self.sidebar, text="Clear Logs", fg_color="transparent", border_width=1, command=self.clear_logs)
        self.clear_btn.grid(row=11, column=0, padx=20, pady=5, sticky="ew")
        
        self.export_btn = ctk.CTkButton(self.sidebar, text="Export History", fg_color="transparent", border_width=1, command=self.export_history)
        self.export_btn.grid(row=12, column=0, padx=20, pady=(5, 20), sticky="ew")
        
        # ==========================================
        # MAIN AREA (CHAT & STATUS)
        # ==========================================
        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1) # Chat log gets the bulk of space
        
        # 1. Header / Status panel
        self.header_frame = ctk.CTkFrame(self.main_container, fg_color=("gray90", "gray13"), height=50)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        self.status_title = ctk.CTkLabel(self.header_frame, text="Assistant Status:", font=ctk.CTkFont(size=12))
        self.status_title.grid(row=0, column=0, padx=(15, 5), pady=10, sticky="w")
        
        self.status_indicator = ctk.CTkLabel(self.header_frame, text="Idle", text_color="gray", font=ctk.CTkFont(size=13, weight="bold"))
        self.status_indicator.grid(row=0, column=1, padx=(0, 20), pady=10, sticky="e")
        
        # Status light (small colored canvas circle)
        self.status_dot = tk.Canvas(self.header_frame, width=12, height=12, bg=self.header_frame.cget("fg_color")[1] or "gray13", highlightthickness=0)
        self.status_dot.grid(row=0, column=2, padx=(0, 15), pady=10, sticky="e")
        self._draw_status_dot("gray")
        
        # 2. Scrollable Chat area
        self.chat_container = ctk.CTkScrollableFrame(self.main_container, fg_color=("gray95", "gray10"))
        self.chat_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # 3. Wave Animation / Sub-bar
        self.animation_label = ctk.CTkLabel(self.main_container, text="", font=ctk.CTkFont(size=11), text_color="gray")
        self.animation_label.grid(row=2, column=0, pady=2)
        
        # 4. Input & Trigger Controls Frame
        self.input_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.input_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=(5, 10))
        self.input_frame.grid_columnconfigure(0, weight=1)
        
        # Manual Command Entry
        self.entry_command = ctk.CTkEntry(self.input_frame, placeholder_text="Type command here or click Mic...")
        self.entry_command.grid(row=0, column=0, padx=(5, 10), pady=5, sticky="ew")
        self.entry_command.bind("<Return>", lambda event: self.submit_manual_command())
        
        # Send Button
        self.send_btn = ctk.CTkButton(self.input_frame, text="Send", width=70, command=self.submit_manual_command)
        self.send_btn.grid(row=0, column=1, padx=5, pady=5)
        
        # Microphone Trigger Button (Big & Premium)
        self.mic_btn = ctk.CTkButton(self.input_frame, text="🎙️ Wake Mic", font=ctk.CTkFont(size=14, weight="bold"), width=120, fg_color="#1f538d", hover_color="#1a4473", command=self.toggle_voice_input)
        self.mic_btn.grid(row=0, column=2, padx=(5, 5), pady=5)
        
        # Continuous Wake-Word Checkbox
        self.continuous_var = tk.BooleanVar(value=False)
        self.continuous_checkbox = ctk.CTkCheckBox(self.main_container, text="Continuous Wake Word Detection ('hey assistant')", variable=self.continuous_var, command=self.toggle_continuous_mode)
        self.continuous_checkbox.grid(row=4, column=0, padx=10, pady=(0, 5), sticky="w")

    def _draw_status_dot(self, color):
        self.status_dot.delete("all")
        # Ensure we read background color properly
        bg = self.header_frame.cget("fg_color")
        bg_color = bg[1] if isinstance(bg, tuple) else bg
        self.status_dot.configure(bg=bg_color)
        self.status_dot.create_oval(2, 2, 10, 10, fill=color, outline="")

    def change_theme(self, new_theme):
        ctk.set_appearance_mode(new_theme.lower())
        # Redraw dot using the color appropriate for the theme
        self.after(100, lambda: self.update_status(self.status_indicator.cget("text")))

    def change_voice_rate(self, value):
        rate = int(value)
        self.rate_label.configure(text=f"Speed: {rate} wpm")
        if self.assistant:
            self.assistant.set_voice_rate(rate)

    def change_voice_volume(self, value):
        volume_pct = int(value)
        self.volume_label.configure(text=f"Volume: {volume_pct}%")
        if self.assistant:
            self.assistant.set_voice_volume(volume_pct / 100.0)

    def change_voice_gender(self, value):
        if self.assistant:
            self.assistant.set_voice_gender(value)

    def update_status(self, status):
        # Callback from assistant thread to update UI
        self.status_indicator.configure(text=status)
        
        # Update colors/dots/animations based on status
        if status == "Listening...":
            self._draw_status_dot("#4CAF50") # Green
            self.mic_btn.configure(text="🛑 Stop Mic", fg_color="#d32f2f", hover_color="#b71c1c")
            self.animation_label.configure(text="🔊 Recording audio... Speak now!")
        elif status == "Listening for Wake Word...":
            self._draw_status_dot("#2196F3") # Blue
            self.mic_btn.configure(text="🛑 Stop Wake", fg_color="#d32f2f", hover_color="#b71c1c")
            self.animation_label.configure(text="💤 Listening in background for 'Hey Assistant'...")
        elif status == "Thinking...":
            self._draw_status_dot("#FFC107") # Yellow
            self.animation_label.configure(text="⚙️ Processing voice commands...")
        elif status == "Speaking...":
            self._draw_status_dot("#9C27B0") # Purple
            self.animation_label.configure(text="🗣️ Talking back...")
        elif status == "Idle":
            self._draw_status_dot("gray")
            self.mic_btn.configure(text="🎙️ Wake Mic", fg_color="#1f538d", hover_color="#1a4473")
            self.animation_label.configure(text="")
        elif status == "Exit":
            # Assistant logic ordered app exit
            self.quit()

    def log_interaction(self, text, is_user=False):
        """Displays chat-like message bubbles in the UI log."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        sender = "You" if is_user else "Assistant"
        
        # Message bubble container frame
        bubble_frame = ctk.CTkFrame(self.chat_container, fg_color="transparent")
        bubble_frame.pack(fill="x", padx=10, pady=5, anchor="e" if is_user else "w")
        
        # Content frame with color dependent on sender
        bg_color = ("#1f538d", "#1f538d") if is_user else ("#2a2a2a", "#2e2e2e")
        text_color = "white"
        
        content_frame = ctk.CTkFrame(bubble_frame, fg_color=bg_color, corner_radius=10)
        content_frame.pack(side="right" if is_user else "left", padx=5)
        
        # Header (Name & Time) inside bubble frame
        header_text = f"{sender} • {timestamp}"
        header_lbl = ctk.CTkLabel(content_frame, text=header_text, font=ctk.CTkFont(size=9, weight="bold"), text_color="gray70")
        header_lbl.pack(anchor="w", padx=10, pady=(5, 0))
        
        # Text label
        msg_lbl = ctk.CTkLabel(content_frame, text=text, font=ctk.CTkFont(size=12), justify="left", wraplength=450, text_color=text_color)
        msg_lbl.pack(anchor="w", padx=10, pady=(2, 6))
        
        # Scroll to bottom
        self.after(50, self.chat_container._parent_canvas.yview_moveto, 1.0)
        
        # Save to local log file
        self._append_to_file(timestamp, sender, text)

    def _append_to_file(self, time_str, sender, text):
        try:
            with open(self.chat_history_file, "a", encoding="utf-8") as f:
                f.write(f"[{time_str}] {sender}: {text}\n")
        except Exception as e:
            print(f"Error saving chat log to file: {e}")

    def toggle_voice_input(self):
        if not self.assistant:
            return
            
        if self.assistant.listening_active:
            self.assistant.stop_listening()
            self.continuous_var.set(False)
        else:
            is_continuous = self.continuous_var.get()
            self.assistant.start_listening_thread(continuous=is_continuous)

    def toggle_continuous_mode(self):
        is_continuous = self.continuous_var.get()
        if self.assistant:
            if self.assistant.listening_active:
                self.assistant.stop_listening()
            
            # Start again with selected mode
            self.assistant.start_listening_thread(continuous=is_continuous)

    def submit_manual_command(self):
        command = self.entry_command.get().strip()
        if not command:
            return
            
        # Log command in UI as User
        self.log_interaction(command, is_user=True)
        self.entry_command.delete(0, tk.END)
        
        # Run execution on a background thread so UI doesn't freeze (actions may take time/TTS blocks)
        if self.assistant:
            t = threading.Thread(target=self.assistant.process_command, args=(command,), daemon=True)
            t.start()

    def clear_logs(self):
        for widget in self.chat_container.winfo_children():
            widget.destroy()
            
        # Delete history file if exists
        if os.path.exists(self.chat_history_file):
            try:
                os.remove(self.chat_history_file)
            except Exception:
                pass
        self.log_interaction("Chat history cleared.", is_user=False)

    def export_history(self):
        if not os.path.exists(self.chat_history_file):
            messagebox.showinfo("Export History", "No history found to export.")
            return
            
        save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if save_path:
            try:
                import shutil
                shutil.copy(self.chat_history_file, save_path)
                messagebox.showinfo("Success", f"History exported successfully to:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export history: {e}")
