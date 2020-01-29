import imageio
import numpy as np

from .encoder import Encoder


class GIFEncoder(Encoder):
    def __init__(self, path, fps):
        self.writer = imageio.get_writer(path, mode="I", fps=fps, subrectangles=True)

    def write(self, image):
        self.writer.append_data(np.array(image))

    def stop(self):
        self.writer.close()
