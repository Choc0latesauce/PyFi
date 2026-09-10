import customtkinter
import mutagen
import vlc
import os
import io
import json
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from random import randint
from PIL import Image, ImageOps

buttonplay = True
playpause = "Play"
Translations = {"English":{"play":"Play", "pause":"Pause", "next": "Next", "previous":"Previous", "shuffle":"Shuffle", "loop":"Loop", "favourite":"Favourite", "pin":"Pin","upload":"Upload Files", "volume":"Volume", "app_colour": "App Colour", "eq_mode": "EQ mode", "language": "Language", "no_art": "No Album Art", "unknown_artist":"Unknown Artist",}, 
                "Svenska": {"play": "Spela", "pause": "Pausa", "next": "Nästa","previous": "Föregående", "shuffle": "Blanda", "loop": "Repetera", "favourite": "Favorit", "pin": "Fäst", "upload": "Ladda upp filer", "volume": "Ljud", "app_colour": "Appens färg", "eq_mode": "EQ Läge", "language": "Språk", "no_art": "Inget skivomslag", "unknown_artist": "Okänd artist",},
                "Español": {"play": "Reproducir", "pause": "Pausa", "next": "Siguiente","previous": "Anterior", "shuffle": "Alaetorio", "loop": "Repetir", "favourite": "Favorito", "pin": "Fijar", "upload": "Subir Archivos", "volume": "Volumen", "app_colour": "Color De Aplicacion", "eq_mode": "Modo EQ", "language": "Idioma", "no_art": "Sin Portada", "unknown_artist": "Artista desconsido",}}

art_cache = {}

def get_album_art(mp3_file_path, image_size=(180, 180)):
    songpath = os.path.abspath(mp3_file_path)
    cache_key = (songpath, image_size)
    if cache_key in art_cache:
        return art_cache[cache_key]
    pil_image = None
    try:
        audio = mutagen.File(songpath)
        if audio is not None:
            image_bytes = None
            if hasattr(audio, 'tags') and audio.tags:
                for key in audio.tags.keys():
                    if key.startswith('APIC'):
                        image_bytes = audio.tags[key].data
                        break
            if not image_bytes and hasattr(audio, "pictures") and audio.pictures:
                image_bytes = audio.pictures[0].data
            if not image_bytes and "covr" in audio:
                image_bytes = bytes(audio["covr"][0])
            if image_bytes:
                pil_image = Image.open(io.BytesIO(image_bytes))
    except Exception:
        print("No album art found")
        pass
    if not pil_image:
        folder_path = os.path.dirname(songpath)
        common_image_names = ["cover.jpg", "cover.png", "folder.jpg", "folder.png", "art.png", "art.jpg", "front.jpg", "fron.png", "album.jpg", "album.png"]
        for name in common_image_names:
            art_path = os.path.join(folder_path, name)
            if os.path.exists(art_path):
                try:
                    pil_image = Image.open(art_path)
                    break
                except Exception as e:
                    pass
    if pil_image:
        try:
            if pil_image.mode not in ("RGB", "RGBA"):
                pil_image = pil_image.convert("RGBA")
            pil_image = ImageOps.pad(pil_image, image_size, color="#242424", centering=(0.5,0.5))
            ctk_img = customtkinter.CTkImage(light_image=pil_image, dark_image=pil_image, size=image_size)
            art_cache[cache_key] = ctk_img
            return ctk_img
        except Exception as e:
            print(f"Error Processing Image: {e}")
    art_cache[cache_key] = None
    return None

class checkboxframe(customtkinter.CTkFrame):
    def __init__(self, master, values, command=None):
        super().__init__(master)
        self.values = values
        self.checkboxes = []
        self.command = command
        self.playlist = []
        self.current_index = 0                      
        for i, value in enumerate(values):
            checkbox = customtkinter.CTkCheckBox(self, text=value)
            checkbox.configure(command=lambda cb=checkbox: self._on_checkbox_toggle(cb))
            checkbox.grid(row=i, column=0, padx=10, pady=5, sticky="w")
            self.checkboxes.append(checkbox)
    def _on_checkbox_toggle(self, checkbox):
        name = checkbox.cget("text")
        is_checked = checkbox.get() == 1
        if self.command:
            self.command(name, is_checked)
    def get(self):
        checked_checkboxes = []
        for checkbox in self.checkboxes:
            if checkbox.get() == 1:
                checked_checkboxes.append(checkbox.cget("text"))
        return checked_checkboxes
    
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        vlc_args = ["--quiet", "--clock-jitter=0", "--file-caching=1000", "--network-caching=1000"]
                        
        self.title("PyFi")
        self.geometry("480x1000")
        self.resizable(width=False, height=True)
        
        self.is_dragging = False
        
        self.drag_data = {"index": None, "widget": None, "y": 0}
        
        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()
       
        self.playlist = [] 
        
        self.custom_playlists = {}
        self.favourites = []
        self.albums = {}
        
        self.tabview = customtkinter.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_player = self.tabview.add("Player View")
        self.tab_library = self.tabview.add("Library & Albums")
        
        self.tab_player.grid_columnconfigure(0, weight=1)
        self.tab_player.grid_columnconfigure(1, weight=0)
        self.tab_player.grid_columnconfigure(2, weight=1)
        
        self.tab_player.grid_columnconfigure(0, weight=1)
        self.tab_player.grid_columnconfigure(1, weight=0)
        self.tab_player.grid_columnconfigure(2, weight=1)
        self.tab_player.grid_rowconfigure(0, weight=2)
        self.tab_player.grid_rowconfigure(1, weight=1)
        self.tab_player.grid_rowconfigure(2, weight=0)
        self.tab_player.grid_rowconfigure(3, weight=0)
        self.tab_player.grid_rowconfigure(4, weight=2)
        self.tab_player.grid_rowconfigure(5, weight=0)
        self.tab_player.grid_rowconfigure(6, weight=0)
        self.tab_player.grid_rowconfigure(7, weight=0)
        
        self.is_playing = False
        song = "No_Geography.mp3"
        songpath = os.path.normpath(os.path.abspath(song))
        
        self.preset_map = {}
        preset_names = ["Off"]
        count = vlc.libvlc_audio_equalizer_get_preset_count()
        for i in range(count):
            name = vlc.libvlc_audio_equalizer_get_preset_name(i)
            if isinstance(name, bytes):
                name = name.decode("utf-8")
            formatted_name = name.capitalize()
            preset_names.append(formatted_name)
            self.preset_map[formatted_name] = i
        
        if os.path.exists(songpath):
            media = self.vlc_instance.media_new(songpath)
            self.player.set_media(media)
        else:
            print("Error: file not found")
        
        def checkboxes_callback(name, is_checked):
            print(f"Checkbox: '{name}' | Checked: {is_checked}")
            if name in ["Favourite", "Favorit", "Favorito"]:
                print("Pinned")
                self.favourite_toggle_callback(is_checked)
            elif name in ["Pin", "Fäst", "Fijar"]:
                print("Unpinned")
                self.attributes("-topmost", is_checked)
        
        def volume_callback(value):
            vlc_volume = int(value * 100)
            self.player.audio_set_volume(vlc_volume)
            percent = int(value * 100)
            self.volume_label.configure(text=f"Volume: {percent}%")
            print(f"Volume: {percent}%")
          
        def playpause_callback():
            global buttonplay, playpause
            current_lang = Translations.get(self.language_menu.get(), Translations["English"])
            if not self.is_playing:
                self.player.play()
                print("Played")
                self.is_playing = True
                buttonplay = False
                self.play_button.configure(text=current_lang["pause"])
            else:
                self.player.pause()
                print("Paused")
                self.is_playing = False
                buttonplay = True
                self.play_button.configure(text=current_lang["play"])
                            
        def previous_callback():
            print("Previous")
            if self.playlist:
                self.current_index = (self.current_index - 1) % len(self.playlist)
                self.load_track(self.current_index)

        self.play_button = customtkinter.CTkButton(self.tab_player, text=f"{playpause}", command=playpause_callback)
        self.play_button.grid(row=2, column=1, padx=10, pady=(10,5), sticky="ew")
        
        self.next_button = customtkinter.CTkButton(self.tab_player, text="⏭️", command=self.next_callback)
        self.next_button.grid(row=2, column=2, columnspan=1, padx=10, pady=(10,5), sticky="ew")
        self.next_button.bind("<Enter>", lambda event: self.next_button.configure(text="Next"))
        self.next_button.bind("<Leave>", lambda event: self.next_button.configure(text="⏭️"))
        
        self.previous_button = customtkinter.CTkButton(self.tab_player, text="⏮️", command=previous_callback)
        self.previous_button.grid(row=2, column=0, columnspan=1, padx=10, pady=(10,5), sticky="ew")
        self.previous_button.bind("<Enter>", lambda event: self.previous_button.configure(text="Previous"))
        self.previous_button.bind("<Leave>", lambda event: self.previous_button.configure(text="⏮️"))

        self.checkbox_frame_1 = checkboxframe(self.tab_player, values=["Shuffle", "Loop"], command=checkboxes_callback)
        self.checkbox_frame_1.grid(row=3, column=0, columnspan=1, pady=(10), sticky="nsw", padx=10)
        
        self.checkbox_frame_2 = checkboxframe(self.tab_player, values=["Favourite", "Pin"], command=checkboxes_callback)
        self.checkbox_frame_2.grid(row=3, column=2, columnspan=1, pady=(10), sticky="nse", padx=10)
        
        self.file_button = customtkinter.CTkButton(self.tab_player, text="Upload Files", command=self.upload_callback)
        self.file_button.grid(row=5, column=0, columnspan=3, sticky="nsew", pady=10, padx=10)
        
        self.playlist_frame = customtkinter.CTkScrollableFrame(self.tab_player, height=120)
        self.playlist_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
        
        self.volume_label = customtkinter.CTkLabel(self.tab_player, text="Volume: 70%", font=("Arial", 12))
        self.volume_label.grid(row=3, column=1, pady=(20,0), sticky="n")
        self.volume_slider = customtkinter.CTkSlider(self.tab_player, from_=0, to=1, number_of_steps=100, command=volume_callback)
        self.volume_slider.set(0.7)
        self.volume_slider.grid(row=3, column=1, pady=(40,10), sticky="ew")
        
        self.art_label = customtkinter.CTkLabel(self.tab_player, text="No Album Art", width=180, height=180)
        self.art_label.grid(row=0, column=0, columnspan=3, pady=10)

        cover_image = get_album_art(songpath)
        if cover_image:
            self.art_label.configure(image=cover_image, text="")
        else:
            self.art_label.configure(image=None, text="No Album Art")
            
        self.time_label = customtkinter.CTkLabel(self.tab_player, text="00:00 / 00:00", font=("Arial", 12))
        self.time_label.grid(row=1, column=2, padx=10, pady=(50,5), sticky="e")
        self.progress_slider = customtkinter.CTkSlider(self.tab_player, from_=0, to=1, command=self.on_seek)
        self.progress_slider.set(0.0)
        self.progress_slider.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky="ew")
        self.progress_slider.bind("<ButtonPress-1>", self.on_slider_press)
        self.progress_slider.bind("<ButtonRelease-1>", self.on_slider_release)
        
        self.language_label = customtkinter.CTkLabel(self.tab_player, text="Language", font=("Arial", 12))
        self.language_label.grid(row=6, column=2, padx=10, pady=(2,10), sticky="e")
        self.language_menu = customtkinter.CTkOptionMenu(self.tab_player, values=list(Translations.keys()), command=self.language_callback)
        self.language_menu.set("English")
        self.language_menu.grid(row=7, column=2, padx=10, pady=(2,10))
        
        self.eq_label = customtkinter.CTkLabel(self.tab_player, text="EQ Mode", font=("Arial", 12))
        self.eq_label.grid(row=6, column=1, pady=(5,10), sticky="ew")
        self.eq_menu = customtkinter.CTkOptionMenu(self.tab_player, values=preset_names, command=self.eq_callback)
        self.eq_menu.set("Flat")
        self.eq_menu.grid(row=7, column=1, pady=(2,10))
        
        self.colour_label = customtkinter.CTkLabel(self.tab_player, text="App Colour", font=("Arial", 12))
        self.colour_label.grid(row=6, column=0, padx=10, pady=(2,10), sticky="w")
        self.colour_menu = customtkinter.CTkOptionMenu(self.tab_player, values=["Blue", "Red", "Green", "Yellow", "Orange", "Pink", "Purple", "Turquoise"], command=self.colour_callback)
        self.colour_menu.set("Blue")
        self.colour_menu.grid(row=7, column=0, padx=10, pady=(2,10))
        
        self.setup_library_tab()
        
        self.protocol("WM_DELETE_WINDOW", self.save_on_close)
        
        saved_settings = self.load_settings()
        
        init_vol = saved_settings.get("volume", 0.7)
        self.volume_slider.set(init_vol)
        volume_callback(init_vol)
        
        init_colour = saved_settings.get("colour", "Blue")
        self.colour_menu.set(init_colour)
        self.colour_callback(init_colour)
        
        init_eq = saved_settings.get("eq", "Off")
        self.eq_menu.set(init_eq)
        self.eq_callback(init_eq)
        
        init_lang = saved_settings.get("langauge", "English")
        self.language_menu.set(init_lang)
        self.language_callback(init_lang)
        
        self.update_progress_loop()
        
        self.load_saved_playlist()
        
    def format_time(self, millisecs):
        if not millisecs or millisecs <= 0:
            return "00:00"
        total_secs = int(millisecs/1000)
        mins, secs = divmod(total_secs, 60)
        return f"{mins:02d}:{secs:02d}"

    def on_slider_press(self, event):
        self.is_dragging = True
        
    def on_slider_release(self, event):
        self.is_dragging = False           
        
    def on_seek(self, value):
        if self.player.get_media():
            self.player.set_position(value)
        
    def update_progress_loop(self):
        if (self.player.get_state() == vlc.State.Ended and getattr(self,"playlist", None)):
            self.player.stop()
            self.after(100, self.next_callback)
            self.after(200, self.update_progress_loop)
            return
            
        if self.player.is_playing() and not self.is_dragging:
            pos = self.player.get_position()
            if pos >=0:
                self.progress_slider.set(pos)
            current_ms = self.player.get_time()
            total_ms = self.player.get_length()
                
            current_str = self.format_time(current_ms)
            total_str = self.format_time(total_ms)
            self.time_label.configure(text=f"{current_str} / {total_str}")
            
        self.after(500, self.update_progress_loop)
        
    def eq_callback(self, choice):
        print(f"Selected {choice}")
        if choice == "Off":
            self.player.set_equalizer(None)
        else:
            preset_index = self.preset_map[choice]
            eq = vlc.libvlc_audio_equalizer_new_from_preset(preset_index)
            self.player.set_equalizer(eq)
            
    def update_playlist_callback(self):
        if not hasattr(self,"playlist_buttons"):
            return
        current_theme = self.colour_menu.get()
        colours = {"Blue": "#1f538d", "Red": "#c62828", "Green": "#2e7d32", "Yellow": "#fbc02d", "Orange": "#e65100", "Pink": "#d81b60", "Purple": "#7b1fa2", "Turquoise": "#00897b"}
        active_colour = colours.get(current_theme, "#1f538d")
        active_idx = getattr(self, "current_index", 0)
        for idx, btn in enumerate(self.playlist_buttons):
            if idx == active_idx:
                btn.configure(fg_color=active_colour)
            else:
                btn.configure(fg_color="transparent")
    
    def on_drag_start(self, event, index):
        self.drag_data["index"] = index
        self.drag_data["widget"] = event.widget
        self.drag_data["y"] = event.y
        
    def on_drag_motion(self,event):
        if self.drag_data["index"] is None:
            return
        target_widget = event.widget.winfo_containing(event.x_root, event.y_root)
        target_idx = None
        for idx, btn in enumerate(self.playlist_buttons):
            if target_widget == btn or target_widget in btn.winfo_children():
                target_idx = idx
                break
        if target_idx is not None and target_idx != self.drag_data["index"]:
            src_idx = self.drag_data["index"]
            song = self.playlist.pop(src_idx)
            self.playlist.insert(target_idx, song)
            if self.current_index == src_idx:
                self.current_index = target_idx
            elif src_idx < self.current_index <= target_idx:
                self.current_index -= 1 
            elif target_idx <= self.current_index < src_idx:
                self.current_index +=1
            self.drag_data["index"] = target_idx
            self.playlist_ui_callback()
        
    def on_drag_stop(self, event):
        if self.drag_data["index"] is not None:
            self.drag_data["index"] = None
            self.save_playlist()
    
    def playlist_ui_callback(self):
        for child in self.playlist_frame.winfo_children():
            child.destroy()
        self.playlist_buttons = []
        self.thumb_images = []
        current_lang = Translations.get(self.language_menu.get(), Translations["English"])
        default_artist = current_lang.get("unknown_artist", "Unknown Artist")
        for index, songpath in enumerate(self.playlist):
            title = os.path.splitext(os.path.basename(songpath))[0]
            artist = default_artist
            try:
                audio = mutagen.File(songpath, easy=True)
                if audio:
                    title = audio.get("title", [title])[0]
                    artist = audio.get("artist", ["Uknown Artist"])[0]
            except Exception:
                pass
            thumb_art = get_album_art(songpath, image_size=(40,40))
            self.thumb_images.append(thumb_art)
            row_btn = customtkinter.CTkButton(self.playlist_frame, text=f"{title}: {artist}", image=thumb_art, compound="left", anchor="w", height=50, fg_color="transparent", hover_color=("#3a3a3a", "#2b2b2b"), command=lambda idx=index: self.select_song(idx),)
            row_btn.pack(fill="x", padx=5, pady=2)
            row_btn.bind("<Button-1>", lambda e, idx=index: self.on_drag_start(e,idx), add="+")
            row_btn.bind("<B1-Motion>", self.on_drag_motion, add="+")
            row_btn.bind("<ButtonRelease-1>", self.on_drag_stop, add="+")
            self.playlist_buttons.append(row_btn)
        self.update_playlist_callback()
                     
    def select_song(self, index):
        self.current_index = index
        self.load_track(self.current_index)
            
    def upload_callback(self):
            files = customtkinter.filedialog.askopenfilenames(title="Select Songs", filetypes=[("Audio Files", "*.mp3 *.wav *.flac *.m4a *.ogg"), ("All Files", "*.*"),],)
            if files:
                if not hasattr(self, "playlist") or self.playlist is None:
                    self.playlist=[]
                combined_all = getattr(self, "all_tracks", []) + list(files)
                self.all_tracks = list(dict.fromkeys(combined_all))
                self.playlist =list(self.all_tracks)
                self.playlist_ui_callback()                
                self.save_playlist()
                self.setup_library_screens()
                if not self.is_playing:
                    self.load_track(0)

    def next_callback(self):
        print("Next")
        if not getattr(self, "playlist", None):
            return
        checked_options = (self.checkbox_frame_1.get() if hasattr(self, "checkbox_frame_1") else[])
        if "Loop" in checked_options and "Shuffle" not in checked_options:
            self.load_track(self.current_index)
        elif "Shuffle" in checked_options:
            if len(self.playlist) > 1:
                next_idx = self.current_index
                while next_idx == self.current_index:
                    next_idx = randint(0, len(self.playlist) - 1)
                self.current_index = next_idx
            self.load_track(self.current_index)
        else:
            self.current_index = (self.current_index + 1) % len(self.playlist)
            self.load_track(self.current_index)

    def load_track(self, index):
        if not self.playlist or index < 0 or index >= len(self.playlist):
            return
        self.current_index = index
        self.player.stop()
        current_lang =Translations.get(self.language_menu.get(), Translations["English"])
        songpath = os.path.normpath(self.playlist[index])    
        media = self.vlc_instance.media_new(songpath)
        self.player.set_media(media)
        self.cover_image = get_album_art(songpath)
        if self.cover_image:
            self.art_label.configure(image=self.cover_image, text ="")
        else:
            self.art_label.configure(image=None, text=current_lang["no_art"])
        track_name = os.path.basename(songpath)
        self.title(f"PyFi - {track_name}")
        self.player.play()
        self.is_playing = True
        self.play_button.configure(text="Pause")
        if hasattr(self, "update_playlist_callback"):
            self.update_playlist_callback()
        self.sync_favourite_checkbox()
        self.update_playlist_callback()

    def colour_callback(self, choice):
        colours = {"Blue": {"main": "#1f538d", "hover": "#14375e"}, "Red": {"main": "#c62828", "hover": "#8e0000"}, "Green": {"main": "#2e7d32", "hover": "#005005"}, "Yellow": {"main": "#fbc02d", "hover": "#c49000"}, "Orange": {"main": "#e65100", "hover": "#ac1900"}, "Pink": {"main": "#d81b60", "hover": "#a00037"}, "Purple": {"main": "#7b1fa2", "hover": "#4a0072"}, "Turquoise": {"main": "#00897b", "hover": "#005b4f"},}
        if choice not in colours:
            return
        main_colour = colours[choice]["main"]
        hover_colour = colours[choice]["hover"]
        buttons = [self.play_button, self.next_button, self.previous_button, self.file_button]
        for btn in buttons:
            btn.configure(fg_color=main_colour, hover_color=hover_colour)
        if hasattr(self, "fav_btn") and self.fav_btn.winfo_exists():
            self.fav_btn.configure(fg_color=main_colour, hover_color=hover_colour)
        if hasattr(self, "play_all_btn") and self.play_all_btn.winfo_exists():
            self.play_all_btn.configure(fg_color=main_colour, hover_color=hover_colour)
        menus = [self.language_menu, self.eq_menu, self.colour_menu]
        for menu in menus:
            menu.configure(button_color=main_colour, button_hover_color=hover_colour, fg_color=main_colour)
        sliders = [self.volume_slider, self.progress_slider]
        for slider in sliders:
            slider.configure(button_color=main_colour, button_hover_color=hover_colour, progress_color=main_colour,)
        for frame in [self.checkbox_frame_1, self.checkbox_frame_2]:
            for cb in frame.checkboxes:
                cb.configure(fg_color=main_colour, hover_color=hover_colour)
        self.tabview.configure(segmented_button_selected_color=main_colour, segmented_button_selected_hover_color=hover_colour)
        if hasattr(self, "update_playlist_callback"):
            self.update_playlist_callback()
    
    def load_settings(self):
        defaults = {"colour":"Blue", "volume": 0.7, "language" : "English", "eq": "Off"}
        if os.path.exists("settings.json"):
            try:
                with open("settings.json", "r") as f:
                    data = json.load(f)
                    defaults.update(data)
            except Exception as e:
                print(f"Failed to load settings: {e}")
        return defaults
    
    def language_callback(self, choice):
        lang = Translations.get(choice, Translations["English"])
        
        self.play_button.configure(text=lang["pause"] if self.is_playing else lang["play"])
        self.file_button.configure(text=lang["upload"])
        self.colour_label.configure(text=lang["app_colour"])
        self.eq_label.configure(text=lang["eq_mode"])
        self.language_label.configure(text=lang["language"])
        
        self.next_button.bind("<Enter>", lambda e: self.next_button.configure(text=lang["next"]))
        self.previous_button.bind("<Enter>", lambda e: self.previous_button.configure(text=lang["previous"]))
        
        if hasattr(self, "checkbox_frame_1"):
            self.checkbox_frame_1.checkboxes[0].configure(text=lang["shuffle"])
            self.checkbox_frame_1.checkboxes[1].configure(text=lang["loop"])
        if hasattr(self, "checkbox_frame_2"):
            self.checkbox_frame_2.checkboxes[0].configure(text=lang["favourite"])
            self.checkbox_frame_2.checkboxes[1].configure(text=lang["pin"])
        
        percent=int(self.volume_slider.get()*100)
        self.volume_label.configure(text=f"{lang['volume']}: {percent}%")
        
        if not getattr(self, "current_cover_image", None):
            self.art_label.configure(text=lang["no_art"])
        
        if getattr(self, "playlist", None):
            self.playlist_ui_callback()
    
    def save_settings(self):
        settings = {"colour": self.colour_menu.get(), "volume": self.volume_slider.get(), "language": self.language_menu.get(), "eq": self.eq_menu.get()}
        try:
            with open("settings.json", "w") as f:
                json.dump(settings, f, indent=4)
            print("Settings Saved")
        except Exception as e:
            print(f"Failed to save settings: {e}")
    
    def save_on_close(self):
        self.save_settings()
        self.destroy()
    
    def save_playlist(self):
        data = {"playlist": getattr(self, "all_tracks", getattr(self, "playlist", [])), "current_index": getattr(self, "current_index", 0),  "favourites": getattr(self, "favourites", [])}
        try: 
            with open("playlist_cache.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving playlist {e}")
    
    def load_saved_playlist(self):
        if os.path.exists("playlist_cache.json"):
            try:
                with open("playlist_cache.json", "r", encoding="utf-8") as f:
                    data=json.load(f)
                saved_tracks = [p for p in data.get("playlist", []) if os.path.exists(p)]
                saved_favs = [p for p in data.get("favourites", []) if os.path.exists(p)]
                self.favourites = saved_favs
                self.all_tracks = list(saved_tracks)
                self.playlist = list(saved_tracks)
                if self.playlist:
                    self.current_index = data.get("current_index", 0)
                    if self.current_index >= len(self.playlist):
                        self.current_index = 0
                    self.playlist_ui_callback()
                    songpath = os.path.normpath(self.playlist[self.current_index])
                    media = self.vlc_instance.media_new(songpath)
                    self.player.set_media(media)
                    self.current_cover_image = get_album_art(songpath)
                    if self.current_cover_image:
                        self.art_label.configure(image=self.current_cover_image, text="")
                    else:
                        current_lang = Translations.get(self.language_menu.get(), Translations["English"])
                        self.art_label.configure(image="", text=current_lang["no_art"])
                    self.title(f"PyFi - {os.path.basename(songpath)}")
                    self.sync_favourite_checkbox()
                    self.update_playlist_callback()
            except Exception as e:
                print(f"Error loading playlist save: {e}")
        self.setup_library_screens()
    
    def group_tracks_by_album(self):
        self.albums = {}
        tracks_source = getattr(self, "all_tracks", getattr(self, "playlist", []))
        for songpath in getattr(self, "playlist", []):
            for songpath in tracks_source:
                folder_name = os.path.basename(os.path.dirname(songpath))
                album_name = folder_name if folder_name else "Unknown Album"
                try:
                    audio = mutagen.File(songpath, easy=True)
                    if audio and "album" in audio:
                        album_name = audio["album"][0]
                except Exception:
                    pass
                if album_name not in self.albums:
                    self.albums[album_name] = []
                if songpath not in self.albums[album_name]:
                    self.albums[album_name].append(songpath)
    
    
    def _load_album_art_async(self, button, track_path):
        art = get_album_art(track_path, image_size=(50,50))
        if art and button.winfo_exists():
            self.after(0, lambda: button.configure(image=art, compound="left"))
    
    def favourite_toggle_callback(self, is_checked):
        if not self.playlist or self.current_index >= len(self.playlist):
            return
        current_track = self.playlist[self.current_index]
        if is_checked:
            if current_track not in self.favourites:
                self.favourites.append(current_track)
        else:
            if current_track in self.favourites:
                self.favourites.remove(current_track)
        self.save_playlist()
        self.setup_library_screens()
        
    def sync_favourite_checkbox(self):
        if hasattr(self, "checkbox_frame_2") and self.playlist and self.current_index < len(self.playlist):
            current_track = self.playlist[self.current_index]
            fav_checkbox = self.checkbox_frame_2.checkboxes[0]
            if current_track in self.favourites:
                fav_checkbox.select()
            else:
                fav_checkbox.deselect()
    
    def load_custom_queue(self, track_list):
        if not track_list:
            return
        self.playlist = list(track_list)
        self.current_index = 0
        self.playlist_ui_callback()
        self.load_track(0)
        self.tabview.set("Player View")
        
    def load_favourites_playlist(self):
        if self.favourites:
            self.load_custom_queue(self.favourites)
    
    def group_tracks_by_album(self):
        self.albums = {}
        for songpath in getattr(self, "playlist", []):
            folder_name = os.path.basename(os.path.dirname(songpath))
            album_name = folder_name if folder_name else "Uknown Album"
            try:
                audio = mutagen.File(songpath, easy=True)
                if audio and "album" in audio:
                    album_name = audio["album"][0]
            except Exception:
                pass
            if album_name not in self.albums:
                self.albums[album_name] = []
            if songpath not in self.albums[album_name]:
                self.albums[album_name].append(songpath)
    
    def setup_library_screens(self):
        for child in self.library_scroll.winfo_children():
            child.destroy()
        self.album_images = []
        self.group_tracks_by_album()
        current_theme = self.colour_menu.get() if hasattr(self, "colour_menu") else "Blue"
        colours = {"Blue": {"main": "#1f538d", "hover": "#14375e"}, "Red": {"main": "#c62828", "hover": "#8e0000"}, "Green": {"main": "#2e7d32", "hover": "#005005"}, "Yellow": {"main": "#fbc02d", "hover": "#c49000"}, "Orange": {"main": "#e65100", "hover": "#ac1900"}, "Pink": {"main": "#d81b60", "hover": "#a00037"}, "Purple": {"main": "#7b1fa2", "hover": "#4a0072"}, "Turquoise": {"main": "#00897b", "hover": "#005b4f"},}
        theme = colours.get(current_theme, colours["Blue"])
        self.fav_btn = customtkinter.CTkButton(self.library_scroll, text=f"❤️ Favourited Songs ({len(self.favourites)} tracks)", height=50, fg_color=theme["main"], hover_color=theme["hover"], font=("Arial", 14, "bold"), command=self.load_favourites_playlist)
        self.fav_btn.pack(fill="x", padx=10, pady=(10,5))
        self.play_all_btn = customtkinter.CTkButton(self.library_scroll, text=f"▶️ Play All Tracks ({len(getattr(self,'playlist', []))} tracks)", height=50, fg_color=theme["main"], hover_color=theme["hover"], font=("Arial", 14, "bold"), command=self.play_all_callback)
        self.play_all_btn.pack(fill="x", padx=10, pady=(0,15))
        customtkinter.CTkLabel(self.library_scroll, text="Albums & Folders", font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=(5,5))
        if not self.albums:
            customtkinter.CTkLabel(self.library_scroll, text="No albums added yet.", font=("Arial", 12)).pack(anchor="w", padx=10, pady=5)
            return
        for album_name, tracks in self.albums.items():
            first_track = tracks[0]
            album_art = get_album_art(first_track, image_size=(50,50))
            btn = customtkinter.CTkButton(self.library_scroll, text=f"{album_name}\n{len(tracks)} Songs", image=album_art, compound="left", anchor="w", height=60, fg_color="#2b2b2b", hover_color="#3a3a3a", command=lambda t=tracks: self.load_custom_queue(t))
            btn.pack(fill="x", padx=10, pady=4)
    
    def play_all_callback(self):
        tracks = getattr(self, "all_tracks", getattr(self, "playlist", []))
        if tracks:
            self.load_custom_queue(tracks)
    
    def setup_library_tab(self):
        self.library_scroll = customtkinter.CTkScrollableFrame(self.tab_library)
        self.library_scroll.pack(fill="both", expand=True, padx=5, pady=5)
                
if __name__ == "__main__":        
    app = App()
    app.mainloop()