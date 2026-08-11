import customtkinter
buttonplay = True
playpause = "Play"

class checkboxframe1(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        def shuffle_callback():
            print("Shuffle")

        def loop_callback():
            print("Loop")
        
        def fave_callback():
            print("Favourite")
        
        shuffle = customtkinter.CTkCheckBox(self, text="Shuffle", command=shuffle_callback)
        shuffle.grid(row=0, column=0, padx=10, pady=(0,10), sticky = "w")
        loop = customtkinter.CTkCheckBox(self, text="Loop", command=loop_callback)
        loop.grid(row=0, column=1, padx=10, pady=(0,10), sticky = "w")
        fave = customtkinter.CTkCheckBox(self, text="Favourite", command=fave_callback)
        fave.grid(row=0, column=2, padx=10, pady=(0,10), sticky = "w")


class checkboxframe2(customtkinter.CTkFrame):
    def __init__(self,master):
        super().__init__(master)
        
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("PyFi")
        self.geometry("400x150")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        def playpause_callback():
            global buttonplay, playpause
            if buttonplay == True:
                print("Play")
                playpause = "Pause"
                buttonplay = False
                return playpause
            else:
                print("Pause")
                playpause = "Play"
                buttonplay = True
                return playpause
        
        def next_callback():
            print("Next")
            
        def previous_callback():
            print("Previous")


        button = customtkinter.CTkButton(self, text=f"{playpause}", command=playpause_callback)
        button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        button = customtkinter.CTkButton(self, text="Next", command=next_callback)
        button.grid(row=0, column=2, columnspan=1, padx=10, pady=10, sticky="e")
        button = customtkinter.CTkButton(self, text="Previous", command=previous_callback)
        button.grid(row=0, column=0, columnspan=1, padx=10, pady=10, sticky="w")

        self.checkbox_frame = checkboxframe1(self)
        self.checkbox_frame.grid(row=1, column=0, columnspan=5, pady=(10,0))
app = App()
app.mainloop()