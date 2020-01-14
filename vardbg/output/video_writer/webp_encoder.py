from .gif_encoder import GIFEncoder


class WebPEncoder(GIFEncoder):
    def stop(self):
        # WebP requires an integer duration
        frame_dur = round(1000 / self.fps)
        self.save(frame_dur)
