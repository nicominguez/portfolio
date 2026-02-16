from typing import Literal, Union, Optional, Protocol
from dataclasses import dataclass
from .card import build_shoe, Card
from .hand import Hand
from .players.base import Player
from .rules import HouseRules


@dataclass
class GameEvent:
    pass


@dataclass
class CardDealtEvent(GameEvent):
    card: Card
    recipient: Literal["player", "dealer"]


@dataclass
class ShoeReshuffledEvent(GameEvent):
    num_decks: int


@dataclass
class DoubleDownEvent(GameEvent):
    original_bet: int
    new_bet: int


@dataclass
class RoundEndEvent(GameEvent):
    outcome: Literal["win", "loss", "push", "blackjack", "surr_loss", "broke"]
    player_hand: Optional[Hand]
    dealer_hand: Optional[Hand]
    bankroll: float


class GameObserver(Protocol):
    def on_event(self, event: GameEvent) -> None:
        ...


class Game:
    def __init__(self, rules: HouseRules, player: Player, bet: int):
        self.rules: HouseRules = rules
        self.player: Player = player
        self.shoe: list[Card] = build_shoe(num_decks=self.rules.num_decks)
        self.base_bet: int = bet
        self.bet: int = bet
        self.observers: list[GameObserver] = []

    def add_observer(self, observer: GameObserver) -> None:
        self.observers.append(observer)

    def remove_observer(self, observer: GameObserver) -> None:
        self.observers.remove(observer)

    def _notify(self, event: GameEvent) -> None:
        for observer in self.observers:
            observer.on_event(event)

    def _deal_card(self, hand: Hand, recipient: Literal["player", "dealer"]) -> None:
        card = self.shoe.pop()
        hand.add(card)
        self._notify(CardDealtEvent(card=card, recipient=recipient))

    def _check_reshuffle(self) -> None:
        if len(self.shoe) / (self.rules.num_decks * 52) <= self.rules.reshuffle_threshold:
            self.shoe = build_shoe(num_decks=self.rules.num_decks)
            self._notify(ShoeReshuffledEvent(num_decks=self.rules.num_decks))

    def _check_bankrupcy(self) -> Optional[dict[str, Union[str, Hand, None, float]]]:
        if self.player.bankroll < self.bet:
            return self._round_result("broke", None, None)
        return None

    def _deal(self) -> tuple[Hand, Hand]:
        player_hand = Hand()
        dealer_hand = Hand()
        self._deal_card(player_hand, "player")
        self._deal_card(dealer_hand, "dealer")
        self._deal_card(player_hand, "player")
        self._deal_card(dealer_hand, "dealer")
        return (player_hand, dealer_hand)

    def _player_turn(self, player_hand: Hand, dealer_hand: Hand) -> Optional[dict[str, Union[str, Hand, None, float]]]:
        if player_hand.is_blackjack and dealer_hand.is_blackjack:
            return self._round_result("push", player_hand, dealer_hand)
        elif player_hand.is_blackjack:
            return self._round_result("blackjack", player_hand, dealer_hand)
        
        while not player_hand.is_bust:
            move = self.player.decide_move(player_hand, dealer_hand.cards[0], self.rules)
            
            if move == "hit":
                self._deal_card(player_hand, "player")
            elif move == "surrender":
                return self._round_result("surr_loss", None, None)
            elif move == "double":
                if self.player.bankroll >= self.bet * 2:
                    original_bet = self.bet
                    self.bet *= 2
                    self._notify(DoubleDownEvent(original_bet=original_bet, new_bet=self.bet))
                    self._deal_card(player_hand, "player")
                    break
                else:
                    self._deal_card(player_hand, "player")
                    break
            elif move == "stand":
                break
            else:
                break

        if player_hand.is_bust:
            return self._round_result("loss", player_hand, dealer_hand)
        return None

    def _dealer_turn(self, player_hand: Hand, dealer_hand: Hand) -> Optional[dict[str, Union[str, Hand, None, float]]]:
        if dealer_hand.is_blackjack:
            return self._round_result("loss", player_hand, dealer_hand)
        
        while True:
            total = dealer_hand.best_total
            should_hit = total < 17 or (total == 17 and dealer_hand.is_soft and self.rules.dealer_hits_soft_17)
            if should_hit:
                self._deal_card(dealer_hand, "dealer")
            else:
                break

        if dealer_hand.is_bust:
            return self._round_result("win", player_hand, dealer_hand)
        return None

    def _compare_hands(self, player_hand: Hand, dealer_hand: Hand) -> dict[str, Union[str, Hand, None, float]]:
        if player_hand.best_total > dealer_hand.best_total:
            return self._round_result("win", player_hand, dealer_hand)
        elif player_hand.best_total < dealer_hand.best_total:
            return self._round_result("loss", player_hand, dealer_hand)
        else:
            return self._round_result("push", player_hand, dealer_hand)

    def _round_result(
        self,
        result: Literal["win", "loss", "push", "blackjack", "surr_loss", "broke"],
        player_hand: Optional[Hand],
        dealer_hand: Optional[Hand],
    ) -> dict[str, Union[str, Hand, None, float]]:
        if result == "loss":
            self.player.bankroll -= self.bet
        elif result == "win":
            self.player.bankroll += self.bet
        elif result == "blackjack":
            self.player.bankroll += self.bet * self.rules.blackjack_payout
        elif result == "surr_loss":
            self.player.bankroll -= self.bet * 0.5
        
        self.bet = self.base_bet
        self._notify(RoundEndEvent(
            outcome=result,
            player_hand=player_hand,
            dealer_hand=dealer_hand,
            bankroll=self.player.bankroll
        ))

        return {
            "outcome": result,
            "player": player_hand,
            "dealer": dealer_hand,
            "bankroll": self.player.bankroll,
        }

    def play_round(self) -> dict[str, Union[str, Hand, None, float]]:
        self._check_reshuffle()
        self.bet = self.player.decide_bet_amount(curr_bet_unit=self.base_bet, shoe_length=len(self.shoe))

        result = self._check_bankrupcy()
        if result:
            return result

        player_hand, dealer_hand = self._deal()

        result = self._player_turn(player_hand, dealer_hand)
        if result:
            return result

        result = self._dealer_turn(player_hand, dealer_hand)
        if result:
            return result

        return self._compare_hands(player_hand, dealer_hand)