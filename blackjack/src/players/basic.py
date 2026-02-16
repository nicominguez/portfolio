from typing import Literal
import random
from ..card import Card
from ..hand import Hand
from ..rules import HouseRules
from .base import Player

class RandomStrategyPlayer(Player):
    def __repr__(self):
        return "Random"

    def decide_move(
        self, hand: Hand, dealer_up: Card, rules: HouseRules
    ) -> Literal["hit", "stand", "double", "surrender"]:
        options = ["hit", "stand", "double", "surrender"]
        return random.choice(options)

    def decide_bet_amount(self, curr_bet_unit: int, shoe_length: int) -> int:
        return curr_bet_unit


class BasicStrategyPlayer(Player):
    def __repr__(self):
        return "Basic Hit/Stand"

    def decide_move(
        self, hand: Hand, dealer_up: Card, rules: HouseRules
    ) -> Literal["hit", "stand", "double", "surrender"]:
        if hand.best_total >= 17:
            return "stand"
        elif hand.best_total < 12:
            return "hit"
        else:
            if dealer_up.hard_value < 7:
                return "stand"
            else:
                return "hit"

    def decide_bet_amount(self, curr_bet_unit: int, shoe_length: int) -> int:
        return curr_bet_unit
