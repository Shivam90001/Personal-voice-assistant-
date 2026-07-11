import sys
from assistant import Assistant
from ui import AssistantUI

def main():
    print("==================================================")
    print("            PERSONAL VOICE ASSISTANT              ")
    print("==================================================")
    print("Starting Assistant Engine...")
    
    # Initialize Core Assistant Logic
    assistant = Assistant()
    
    # Initialize CustomTkinter UI
    print("Initializing GUI interface...")
    app = AssistantUI(assistant_instance=assistant)
    
    print("Application loaded successfully. Close window to exit.")
    print("==================================================")
    
    # Start Tkinter Event Loop
    app.mainloop()

if __name__ == "__main__":
    main()
