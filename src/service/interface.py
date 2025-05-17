from abc import ABC, abstractmethod


class Interface(ABC):
    @abstractmethod
    def show(self):
        raise NotImplementedError

    @abstractmethod
    def reveal(self):
        raise NotImplementedError

    @abstractmethod
    def guess(self, *inputs):
        raise NotImplementedError

    @abstractmethod
    def new_game(self):
        raise NotImplementedError
