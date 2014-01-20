import os

class MusicFinder:

    def __init__(self):
        self.music = "/home/paulocanedo/Music"
        self.fileList = []

    def list_files(self):
        del self.fileList[:]

        extensions = {".mp3", ".m4a", ".flac"}

        for root, subFolders, files in os.walk(self.music):
            for file in files:
                for extension in extensions:
                    if(file.endswith(extension)):
                        self.fileList.append(os.path.join(root,file))
        return self.fileList


finder = MusicFinder()
for file in finder.list_files():
    print file