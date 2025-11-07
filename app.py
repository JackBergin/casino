import streamlit as st
import pandas as pd
from blackjack_simulator import Shoe, simulate_blackjack_hand

st.set_page_config(page_title="Blackjack Martingale Strategy Simulator", layout="wide")

st.title("🎰 Blackjack Martingale Strategy Simulator")
st.caption("Accurate blackjack engine, strict Martingale logic, and detailed hand printouts.")

# Sidebar Parameters
st.sidebar.header("Simulation Parameters")
bankroll_start = st.sidebar.number_input("Starting bankroll ($)", value=6000, step=100)
base_bet = st.sidebar.number_input("Base bet ($)", value=25, step=5)
num_decks = st.sidebar.slider("Number of decks", 1, 8, 6)
num_players = st.sidebar.slider("Number of players at table", 1, 6, 3)
num_hands = st.sidebar.number_input("Number of hands to simulate", value=200, step=50)
dealer_hits_soft_17 = st.sidebar.toggle("Dealer hits soft 17", value=False)
random_seed = st.sidebar.number_input("Random seed", value=42, step=1)

st.sidebar.markdown("---")
st.sidebar.info("""
**Martingale Betting Rules**
- Start at base bet.
- Double bet after every loss (B, 2B, 4B, 8B, ...).
- Reset to base after a win.
- If required next bet exceeds bankroll → BUST.

**Game Rules**
- Player hits on <17, stands on ≥17.
- Dealer stands on 17 by default (toggle for soft 17).
- Aces count as 1 or 11 automatically.
- Blackjack pays 3:2.
""")

# Initialize shoe
import numpy as np
np.random.seed(random_seed)
shoe = Shoe(num_decks=num_decks)


def simulate_martingale(bankroll_start, base_bet, shoe, num_players, num_hands, dealer_hits_soft_17):
    bankroll = bankroll_start
    loss_streak = 0
    records = []

    for hand_num in range(1, num_hands + 1):
        current_bet = base_bet * (2 ** loss_streak)

        # If next required bet exceeds bankroll, bust
        if current_bet > bankroll:
            records.append({
                "hand": hand_num,
                "result": "BUST",
                "player_hand": "",
                "dealer_hand": "",
                "player_value": "",
                "dealer_value": "",
                "bet": current_bet,
                "bankroll": bankroll,
                "profit": bankroll - bankroll_start,
                "streak_losses": loss_streak,
            })
            break

        result, payout, hands = simulate_blackjack_hand(
            shoe, num_players=num_players, bet=current_bet, dealer_hits_soft_17=dealer_hits_soft_17
        )

        if result == "win":
            bankroll += payout
            loss_streak = 0
        elif result == "push":
            pass
        else:  # lose
            bankroll -= current_bet
            loss_streak += 1

        records.append({
            "hand": hand_num,
            "result": result,
            "player_hand": hands["player"],
            "dealer_hand": hands["dealer"],
            "player_value": hands["player_value"],
            "dealer_value": hands["dealer_value"],
            "bet": current_bet,
            "bankroll": bankroll,
            "profit": bankroll - bankroll_start,
            "streak_losses": loss_streak,
        })

        if bankroll <= 0:
            break

    return pd.DataFrame(records)


if st.button("Run Simulation"):
    with st.spinner("Simulating blackjack hands..."):
        df = simulate_martingale(
            bankroll_start, base_bet, shoe, num_players, num_hands, dealer_hits_soft_17
        )

    bust = df["result"].eq("BUST").any()
    final_bankroll = df.iloc[-1]["bankroll"]
    total_profit = final_bankroll - bankroll_start

    st.subheader("Simulation Results")
    col1, col2, col3 = st.columns(3)
    col1.metric("Final Bankroll", f"${final_bankroll:,.2f}")
    col2.metric("Total Profit", f"${total_profit:,.2f}")
    col3.metric("Bust Occurred?", "✅ No" if not bust else "❌ Yes")

    st.line_chart(df.set_index("hand")["bankroll"], use_container_width=True)

    st.markdown("### Hand History")
    st.dataframe(df[[
        "hand", "result", "player_hand", "dealer_hand",
        "player_value", "dealer_value", "bet", "bankroll", "profit", "streak_losses"
    ]])

    st.markdown("### Summary Stats")
    st.write(f"Hands Played: {len(df)}")
    st.write(f"Max Loss Streak: {df['streak_losses'].max()}")
else:
    st.info("Set your parameters and click **Run Simulation** to begin.")
