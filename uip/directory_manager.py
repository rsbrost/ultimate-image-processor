from pathlib import Path
import os


class DirectoryManager():
    
    def __init__(self, input_dir="input"):
        # set up the original input directory
        self.og_input_dir = os.path.join(Path(''), input_dir)

