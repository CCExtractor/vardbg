import cv2
import numpy as np

from .encoder import Encoder


class OpenCVEncoder(Encoder):
    # noinspection PyUnresolvedReferences
    def __init__(self, path, fourcc, fps, w, h):
        cv_fourcc = cv2.VideoWriter_fourcc(*fourcc)
        self.writer = cv2.VideoWriter(path, cv_fourcc, fps, (w, h))

    def write(self, image):
        # Convert PIL -> Numpy array and RGB -> BGR colors
        # noinspection PyUnresolvedReferences
        cv_img = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
        # Write data
        self.writer.write(cv_img)

    def stop(self):
        self.writer.release()
