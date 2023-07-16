class FileReader:
    def __init__(self):
        pass

    @staticmethod
    def read_songs(file_path):
        songs = []
        with open(file_path, "r") as file:
            for line in file:
                songs.append(line)
        return songs