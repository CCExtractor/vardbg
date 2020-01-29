from .encoder import Encoder


class WebPEncoder(Encoder):
    def __init__(self, path, fps):
        self.frames = []
        self.path = path
        self.fps = fps

    def write(self, image):
        self.frames.append(image)

    def stop(self):
        # WebP requires an integer duration
        frame_dur = round(1000 / self.fps)
        self.frames[0].save(self.path, save_all=True, append_images=self.frames[1:], duration=frame_dur, loop=0)
