from .encoder import Encoder


class GIFEncoder(Encoder):
    def __init__(self, path, fps):
        self.frames = []
        self.path = path
        self.fps = fps

    def write(self, image):
        self.frames.append(image)

    def save(self, frame_dur):
        self.frames[0].save(self.path, save_all=True, append_images=self.frames[1:], duration=frame_dur, loop=0)

    def stop(self):
        frame_dur = 1000 / self.fps
        self.save(frame_dur)
