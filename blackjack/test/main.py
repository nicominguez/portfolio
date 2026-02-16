from src.simulation import run_sim, print_results
from src.rules import HouseRules
from src.players.basic import RandomStrategyPlayer, BasicStrategyPlayer  # noqa: F401
from src.players.chart import ChartPlayer2
from src.players.counting import RCHighLowPlayer  # noqa: F401
from src.players.learning import QLearningPlayer


def main():
    q_player = QLearningPlayer(bankroll=1000, training_mode=False)
    q_player.load_model("_models/q_learning_player.pkl")
    
    results = run_sim(
        players=[ChartPlayer2(bankroll=1000), q_player],
        rules=HouseRules(),
        num_hands=100000,
        base_bet=5,
        verbose=True,
    )
    
    print_results(results)


if __name__ == "__main__":
    main()