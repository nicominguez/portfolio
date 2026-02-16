from typing import Literal, Union
from ..card import Card
from ..hand import Hand
from ..rules import HouseRules
from .base import Player
from ..utils.player_utils import map_result_char, get_dealer_index, HARD_MATRIX, SOFT_MATRIX

class RCHighLowPlayer(Player):
    def __init__(self, bankroll=1000):
        super().__init__(bankroll)
        self.running_count: int = 0

    def __repr__(self):
        return "Running Count High Low Player"

    def _update_running_count(self, card: Union[Card, str]) -> None:
        if isinstance(card, str):
            rank = card
        else:
            rank = card.rank
        if rank in ["2", "3", "4", "5", "6"]:
            self.running_count += 1
        elif rank in ["10", "J", "Q", "K", "A"]:
            self.running_count -= 1

    def _reset_running_count(self):
        self.running_count = 0

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
        true_count = self.running_count / max((shoe_length / 52), 1)
        return max(int(max(1, true_count) * curr_bet_unit), curr_bet_unit)
