from typing import Literal
from ..card import Card
from ..hand import Hand
from ..rules import HouseRules
from .base import Player
from ..utils.player_utils import map_result_char, get_dealer_index, BASIC_MATRIX, HARD_MATRIX, SOFT_MATRIX

class ChartPlayer1(Player):
    def __repr__(self):
        return "Chart Player 1"

    def decide_move(
        self, hand: Hand, dealer_up: Card, rules: HouseRules
    ) -> Literal["hit", "stand", "double", "surrender"]:
        return map_result_char(
            BASIC_MATRIX[hand.best_total - 4][get_dealer_index(card_val=dealer_up.rank)]
        )

    def decide_bet_amount(self, curr_bet_unit: int, shoe_length: int) -> int:
        return curr_bet_unit


class ChartPlayer2(Player):
    def __repr__(self):
        return "Chart Player 2"

    def decide_move(
        self, hand: Hand, dealer_up: Card, rules: HouseRules
    ) -> Literal["hit", "stand", "double", "surrender"]:
        if hand.is_soft:
            return map_result_char(
                SOFT_MATRIX[hand.best_total - 13][
                    get_dealer_index(card_val=dealer_up.rank)
                ]
            )
        else:
            return map_result_char(
                HARD_MATRIX[hand.best_total - 4][
                    get_dealer_index(card_val=dealer_up.rank)
                ]
            )

    def decide_bet_amount(self, curr_bet_unit: int, shoe_length: int) -> int:
        return curr_bet_unit
