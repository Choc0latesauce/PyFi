import customtkinter
buttonplay = True
playpause = "Play"

class checkboxframe(customtkinter.CTkFrame):
    def __init__(self, master, values):
        super().__init__(master)
        self.values = values
        self.checkboxes = []
        
        for i, value in enumerate(values):
            checkbox = customtkinter.CTkCheckBox(self, text=value)
            checkbox.grid(row=i, column=0, padx=10, pady=5, sticky="w")
            self.checkboxes.append(checkbox)
            
        def get(self):
            checked_checkboxes = []
            for checkbox in self.checkboxes:
                if checkbox.get() == 1:
                    checked_checkboxes.append(checkbox.cget("text"))
                return checked_checkboxes
            
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("PyFi")
        self.geometry("400x150")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        
        def playpause_callback():
            global buttonplay, playpause
            if buttonplay == True:
                print("Played")
                buttonplay = False
                self.play_button.configure(text="Pause")
            else:
                print("Paused")
                playpause = "Play"
                buttonplay = True
                self.play_button.configure(text="Play")
        
        def next_callback():
            print("Next")
            
        def previous_callback():
            print("Previous")

        self.play_button = customtkinter.CTkButton(self, text=f"{playpause}", command=playpause_callback)
        self.play_button.grid(row=0, column=1, padx=10, pady=(10,5), sticky="ew")
        
        self.next_button = customtkinter.CTkButton(self, text="Next", command=next_callback)
        self.next_button.grid(row=0, column=2, columnspan=1, padx=10, pady=(10,5), sticky="ew")
        self.previous_button = customtkinter.CTkButton(self, text="Previous", command=previous_callback)
        self.previous_button.grid(row=0, column=0, columnspan=1, padx=10, pady=(10,5), sticky="ew")

        self.checkbox_frame_1 = checkboxframe(self, values=["Shuffle", "Loop",])
        self.checkbox_frame_1.grid(row=1, column=0, columnspan=5, pady=(10,0), sticky="nsw")
        
        self.checkbox_frame_2 = checkboxframe(self, values=["Favourite", "Pin"])
        self.checkbox_frame_2.grid(row=1, column=2, columnspan=5, pady=(10,0), sticky="nse")
        
app = App()
app.attributes("-topmost", True)
app.mainloop()