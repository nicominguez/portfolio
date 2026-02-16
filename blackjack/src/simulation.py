from typing import Union
from dataclasses import dataclass, field
from .players.base import Player
from .rules import HouseRules
from .game import Game, GameEvent, RoundEndEvent, DoubleDownEvent


@dataclass
class SimulationStatistics:
    wins: int = 0
    losses: int = 0
    pushes: int = 0
    doubles: int = 0
    bankroll_history: list[float] = field(default_factory=list)
    starting_bankroll: float = 0
    _cumulative_winrates: list[float] = field(default_factory=list)
    
    def on_event(self, event: GameEvent) -> None:
        if isinstance(event, RoundEndEvent):
            self._track_outcome(event)
        elif isinstance(event, DoubleDownEvent):
            self.doubles += 1
    
    def _track_outcome(self, event: RoundEndEvent) -> None:
        outcome = event.outcome
        if outcome in ["win", "blackjack"]:
            self.wins += 1
        elif outcome in ["loss", "surr_loss"]:
            self.losses += 1
        elif outcome == "push":
            self.pushes += 1
        
        self.bankroll_history.append(event.bankroll)
        total = self.wins + self.losses + self.pushes
        if total > 0:
            self._cumulative_winrates.append(self.wins / total)
    
    @property
    def total_hands(self) -> int:
        return self.wins + self.losses + self.pushes
    
    @property
    def win_rate(self) -> float:
        decisive = self.wins + self.losses
        return self.wins / decisive if decisive > 0 else 0.0
    
    @property
    def final_bankroll(self) -> float:
        return self.bankroll_history[-1] if self.bankroll_history else self.starting_bankroll
    
    @property
    def net_profit(self) -> float:
        return self.final_bankroll - self.starting_bankroll
    
    def get_results(self, player_name: str) -> dict[str, Union[int, float, list]]:
        return {
            "player": player_name,
            "wins": self.wins,
            "losses": self.losses,
            "pushes": self.pushes,
            "doubles": self.doubles,
            "total_games": self.total_hands,
            "win_rate": self.win_rate,
            "final_bankroll": self.final_bankroll,
            "net_profit": self.net_profit,
            "bankroll_history": self.bankroll_history,
            "cum_winrate": self._cumulative_winrates,
        }


def run_sim(
    players: list[Player],
    rules: HouseRules = None,
    num_hands: int = 1000,
    base_bet: int = 5,
    verbose: bool = False,
) -> list[dict[str, Union[int, float, list]]]:
    if rules is None:
        rules = HouseRules()
    
    results = []
    for player in players:
        game = Game(player=player, rules=rules, bet=base_bet)
        stats = SimulationStatistics()
        stats.starting_bankroll = player.bankroll
        
        game.add_observer(stats)
        if hasattr(player, 'on_event'):
            game.add_observer(player)
        
        for hand_num in range(num_hands):
            outcome = game.play_round()
            if outcome.get("outcome") == "broke":
                if verbose:
                    print(f"{repr(player)} broke at hand {hand_num}")
                break
        
        results.append(stats.get_results(player_name=repr(player)))
    
    return results


def print_results(results: list[dict]) -> None:
    for r in results:
        print(f"\n{'='*60}")
        print(f"Player: {r['player']}")
        print(f"{'='*60}")
        print(f"Hands:     {r['total_games']:,}")
        print(f"Wins:      {r['wins']:,} ({r['wins']/r['total_games']:.2%})")
        print(f"Losses:    {r['losses']:,} ({r['losses']/r['total_games']:.2%})")
        print(f"Pushes:    {r['pushes']:,} ({r['pushes']/r['total_games']:.2%})")
        print(f"Doubles:   {r['doubles']:,}")
        print(f"Win rate:  {r['win_rate']:.2%}")
        print(f"Bankroll:  ${r['final_bankroll']:.2f}")
        print(f"Profit:    ${r['net_profit']:+.2f}")
    print(f"{'='*60}\n")