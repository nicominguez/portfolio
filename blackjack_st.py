import streamlit as st

from projects.blackjack.src.main import run_sim
from projects.blackjack.src.static.player import RandomStrategyPlayer, BasicStrategyPlayer, ChartPlayer1, ChartPlayer2, RCHighLowPlayer
from projects.blackjack.src.static.rules import HouseRules

st.set_page_config(
    page_title="Blackjack Simulation",
    page_icon="🃏",
    layout="wide",
)

# Title
st.title("Blackjack")
st.markdown("Simulate different blackjack player strategies and analyze their performance.")

# Simulation Settings Section
st.header("Simulation Settings")

st.subheader(":blue[Player 1]", divider="blue")

col1, col2, col3 = st.columns(3)

player_options = {
    "Random Strategy": RandomStrategyPlayer,
    "Basic Hit/Stand": BasicStrategyPlayer,
    "Chart Player 1": ChartPlayer1,
    "Chart Player 2": ChartPlayer2,
    "Running Count High Low": RCHighLowPlayer,
}
with col1:
    selected_player_name = st.radio(
        "Select Player Strategy",
        options=list(player_options.keys()),
        help="Choose the strategy the player will use during the simulation"
    )

rule_options = {
    "Standard House Rules": HouseRules(),
}
with col2:
    selected_rule_name = st.radio(
        "Select House Rules",
        options=list(rule_options.keys()),
        help="Select the house rules for the simulation"
    )

with col3:
    num_hands = st.slider(
        "Number of Hands to Simulate",
        min_value=10,
        max_value=10000,
        value=1000,
        step=10,
        help="How many hands should each player play?"
    )

st.divider()

# Start simulation
if st.button("Run Simulation", key="run_sim_button", type="primary", use_container_width=True):
    player = player_options[selected_player_name]()
    initial_bankroll = player.bankroll
    rules = rule_options[selected_rule_name]
    
    with st.spinner("Running simulation..."):
        results = run_sim(
            players=[player],
            rules=rules,
            num_hands=num_hands,
        )
    
    st.header("Simulation Results")
    
    if results:
        result = results[0]
        bankroll_history = result.get("bankroll_history", [])
        
        if bankroll_history:
            st.line_chart(
                bankroll_history,
                use_container_width=True,
            )
            
            initial_bankroll = 1000
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Final Bankroll", f"${bankroll_history[-1]:.0f}")
            
            with col2:
                st.metric("Starting Bankroll", f"${initial_bankroll:.0f}")
            
            with col3:
                max_bankroll = max(bankroll_history)
                st.metric("Peak Bankroll", f"${max_bankroll:.0f}")
            
            with col4:
                min_bankroll = min(bankroll_history)
                st.metric("Minimum Bankroll", f"${min_bankroll:.0f}")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Hands", result.get("total_games", 0))
            
            with col2:
                win_rate = (result.get("wins", 0) / result.get("total_games", 1)) * 100
                st.metric("Win Rate", f"{win_rate:.1f}%")
            
            with col3:
                st.metric("Wins", result.get("wins", 0))
            
            with col4:
                st.metric("Losses", result.get("losses", 0))
            
            final_profit = bankroll_history[-1] - bankroll_history[0]
            profit_pct = (final_profit / bankroll_history[0]) * 100 if bankroll_history[0] > 0 else 0
            
            if final_profit >= 0:
                st.success(f"**Profit/Loss:** ${final_profit:+.0f} ({profit_pct:+.1f}%)")
            else:
                st.error(f"**Profit/Loss:** ${final_profit:+.0f} ({profit_pct:+.1f}%)")
        else:
            st.warning("No bankroll history generated. The player may have gone broke.")
    else:
        st.error("Simulation failed to produce results.")