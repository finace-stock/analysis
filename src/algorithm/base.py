from abc import ABCMeta, abstractclassmethod


class Algorithm(metaclass=ABCMeta):
    @abstractclassmethod
    def analyze(self):
        pass
