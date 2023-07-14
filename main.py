from tkinter import Tk, messagebox, StringVar, filedialog
from tkinter import Entry, Button, Label
from SpotifyUtil import SpotifyUtil

class SpotifyUtilToolkit(Tk):
    def __init__(self) -> None:
        super().__init__()
        self.spotify = SpotifyUtil()
        self.title("Spotify Util")
        self.iconbitmap("statics\spotify_icon.ico")
        self.geometry("500x500")

        self.name = StringVar()
        self.url = StringVar()
        self.playlist_url = StringVar()
        
        self.name_label = Label(self, text="Name")
        self.name_box = Entry(self, textvariable=self.name, font=("Arial",18,""), width=20)
        self.name_label.pack()
        self.name_box.pack()

        self.url_label = Label(self, text="From")
        self.url_box = Entry(self, textvariable=self.url, font=("Arial",18,""), width=20)
        self.url_label.pack()
        self.url_box.pack()

        self.playlist_url_label = Label(self, text="To")
        self.playlist_url_box = Entry(self, textvariable=self.playlist_url, font=("Arial",18,""), width=20)
        self.playlist_url_label.pack()
        self.playlist_url_box.pack()

        btn_to_add_tracks_from_one_playlist_to_another = Button(self, text="Add from playlist", command=self.add_tracks_from_one_playlist_to_another)
        btn_to_add_tracks_from_one_playlist_to_another.pack()

        self.label_file_explorer = Label(self,
                            text = "Search file to create playlist",
                            width = 100, height = 4,
                            fg = "blue")
        self.file_explore_button = Button(self,
                        text = "Browse Files",
                        command = self.browse_files)
        self.label_file_explorer.pack()
        self.file_explore_button.pack()

        btn_to_add_tracks_from_file_to_playlist = Button(self, text="Add from file", command=self.add_tracks_from_file_to_playlist)
        btn_to_add_tracks_from_file_to_playlist.pack()

    def confirm(self):
        messagebox.askokcancel(message="Are you sure?")

    def add_tracks_from_one_playlist_to_another(self):
        self.confirm()
        playlist_url = self.playlist_url.get()
        from_url = self.url.get()
        name = self.name.get()
        self.spotify.add_songs_to_playlist(playlist_url=playlist_url if len(playlist_url)>0 else None,
                                            from_url=from_url if len(from_url)>0 else None,
                                            name=name if len(name)>0 else None)
        messagebox.showinfo(message="Done", icon="info")

    def add_tracks_from_file_to_playlist(self):
        self.confirm()
        playlist_url = self.playlist_url.get()
        filepath = self.label_file_explorer.cget("text")
        name = self.name.get()
        self.spotify.add_songs_to_playlist_from_file(playlist_url=playlist_url if len(playlist_url)>0 else None,
                                                    file_path=filepath if len(filepath)>0 else None,
                                                    name=name if len(name)>0 else None)
        messagebox.showinfo(message="Done", icon="info")

    def browse_files(self):
        filename = filedialog.askopenfilename(initialdir = "/",
                                        title = "Select a File",
                                        filetypes = (("Text files",
                                                    "*.txt*"),
                                                    ("all files",
                                                    "*.*")))
        self.label_file_explorer.configure(text=filename)

if __name__ == "__main__":
    toolkit = SpotifyUtilToolkit()
    toolkit.mainloop()