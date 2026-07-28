import customtkinter
buttonplay = True
playpause = "Play"

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("PyFi")
        self.geometry("400x150")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        def button_callback():
            global buttonplay, playpause
            if buttonplay == True:
                print("Play")
                playpause = "Pause"
                buttonplay = False
            else:
                print("Pause")
                playpause = "Play"
                buttonplay = True
        
        def shuffle_callback():
            print("Shuffle")

        def loop_callback():
            print("Loop")

        button = customtkinter.CTkButton(self, text=f"{playpause}", command=button_callback)
        button.grid(row=0, column=0, padx=20, pady=20, sticky="ew", columnspan=2)

        self.checkbox_frame = customtkinter.CTkFrame(self)
        self.checkbox_frame.grid(row=0, column=0, pady=(10,0), sticky="nsw")
        shuffle = customtkinter.CTkCheckBox(self, text="Shuffle", command=shuffle_callback)
        shuffle.grid(row=0, column=0, padx=10, pady=(0,10), sticky = "w")
        loop = customtkinter.CTkCheckBox(self, text="Loop", command=loop_callback)
        loop.grid(row=1, column=0, padx=10, pady=(0,10), sticky = "w")

app = App()
app.mainloop()