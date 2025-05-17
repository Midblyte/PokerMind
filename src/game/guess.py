from enum import Enum


class Guess(Enum):
    WRONG   = -1
    PARTIAL = +0
    CORRECT = +1
