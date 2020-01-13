import abc


class Encoder(abc.ABC):
    @abc.abstractmethod
    def write(self, image):
        pass

    @abc.abstractmethod
    def stop(self):
        pass
