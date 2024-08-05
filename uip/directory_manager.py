from pathlib import Path
import os


class DirectoryManager():

    def __init__(self, input_dir="input", output_dir="ouput", flatfield_dir="flatfield"):
        # set up the original input directory
        self._base_input_dir = os.path.join(Path(''), input_dir)
        os.makedirs(self._base_input_dir, exist_ok=True)
        self._base_output_dir = os.path.join(Path(''), output_dir)
        os.makedirs(self._base_output_dir, exist_ok=True)
        self._flatfield_dir = os.path.join(Path(''), flatfield_dir)
        os.makedirs(self._flatfield_dir, exist_ok=True)

        self.current_input_dirs = self._base_input_dir
        self.current_output_dir = self._base_output_dir

        self.input_dir_history = []
        # this stores the output dirs from the last called process
        self.output_dir_history = []

    @property
    def base_input_dir(self):
        return self._base_input_dir

    @property
    def base_output_dir(self):
        return self._base_output_dir

    @property
    def flatfield_dir(self):
        return self._flatfield_dir

    def set_output_dir(self, new_output_dir, base_output_dir='root', same_process=False):
        old_current_output_dir = self.current_output_dir

        if base_output_dir == 'root':
            self.current_output_dir = os.path.join(self.base_output_dir, new_output_dir)
        else:
            self.current_output_dir = os.path.join(base_output_dir, new_output_dir)
        os.makedirs(self.current_output_dir, exist_ok=True)

        # build history of different output dirs from the same process for later use as inputs
        # if old_current_output_dir != self.base_output_dir and same_process is True:
        if old_current_output_dir != self.base_output_dir:
            self.output_dir_history.append(self.current_output_dir)
        '''else:
            self.input_dir_history.append(self.output_dir_history)
            self.output_dir_history = []'''

        return self.current_output_dir
