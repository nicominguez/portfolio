from abc import ABC, abstractmethod
from typing import Literal

class Player(ABC):
    def __init__(self, bankroll: int = 1000):
        self.bankroll = bankroll

    @abstractmethod
    def decide_move(self, hand, dealer_up, rules) -> Literal[...]:
        pass

    @abstractmethod
    def decide_bet_amount(self, curr_bet_unit: int, shoe_length: int) -> int:
        pass