from src.players.learning import QLearningPlayer
from src.game import Game
from src.rules import HouseRules
import time


player = QLearningPlayer(
    bankroll=10000,
    learning_rate=0.1,
    discount_factor=0.95,
    epsilon=0.3,
    training_mode=True,
)

game = Game(player=player, rules=HouseRules(), bet=5)

num_episodes = 10_000_000
start_time = time.time()
wins = 0

for episode in range(num_episodes):
    if episode == 50_000:
        player.epsilon = 0.15
    elif episode == 80_000:
        player.epsilon = 0.05
    
    outcome = game.play_round()
    player.learn_from_hand(outcome["outcome"])
    
    if outcome["outcome"] == "broke":
        player.bankroll = 10000
    elif outcome["outcome"] in ["win", "blackjack"]:
        wins += 1
    
    if (episode + 1) % 10_000 == 0:
        elapsed = time.time() - start_time
        win_rate = wins / (episode + 1)
        print(f"Episode {episode + 1:,}: {win_rate:.2%} win rate, "
              f"{len(player.q_table):,} states, ε={player.epsilon:.2f}, "
              f"{(episode + 1) / elapsed:.0f} hands/sec")

total_time = time.time() - start_time
print(f"\nTrained {num_episodes:,} episodes in {total_time:.1f}s")
print(f"Final: {len(player.q_table):,} states, {wins / num_episodes:.2%} win rate")

player.save_model("_models/q_learning_player.pkl")