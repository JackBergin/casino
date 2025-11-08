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
bet_multiplier = st.sidebar.number_input("Bet multiplier after loss", value=2.0, min_value=1.0, max_value=10.0, step=0.1, help="Standard Martingale uses 2.0. Formula: bet * multiplier^(losses)")
num_decks = st.sidebar.slider("Number of decks", 1, 8, 6)
num_players = st.sidebar.slider("Number of players at table", 1, 6, 3)
num_hands = st.sidebar.number_input("Number of hands to simulate", value=200, step=50)
dealer_hits_soft_17 = st.sidebar.toggle("Dealer hits soft 17", value=False)

st.sidebar.markdown("---")
st.sidebar.subheader("Monte Carlo Simulation")
num_iterations = st.sidebar.number_input("Number of iterations (cycles)", value=1, min_value=1, max_value=10000, step=1, help="Run multiple simulations to see win/loss rates")
random_seed = st.sidebar.number_input("Random seed", value=42, step=1)

st.sidebar.markdown("---")
st.sidebar.info(f"""
**Martingale Betting Rules**
- Start at base bet.
- Multiply bet after every loss: B, {bet_multiplier}B, {bet_multiplier**2}B, {bet_multiplier**3}B, ...
- Formula: base_bet × multiplier^(consecutive_losses)
- Reset to base after a win.
- If required next bet exceeds bankroll → BUST.

**Game Rules**
- Player hits on <17, stands on ≥17.
- Dealer stands on 17 by default (toggle for soft 17).
- Aces count as 1 or 11 automatically.
- Blackjack pays 3:2.
""")

# Initialize numpy
import numpy as np


def simulate_martingale(bankroll_start, base_bet, bet_multiplier, shoe, num_players, num_hands, dealer_hits_soft_17):
    bankroll = bankroll_start
    loss_streak = 0
    records = []

    for hand_num in range(1, num_hands + 1):
        current_bet = base_bet * (bet_multiplier ** loss_streak)

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
    if num_iterations == 1:
        # Single simulation with detailed output
        with st.spinner("Simulating blackjack hands..."):
            np.random.seed(random_seed)
            shoe = Shoe(num_decks=num_decks)
            df = simulate_martingale(
                bankroll_start, base_bet, bet_multiplier, shoe, num_players, num_hands, dealer_hits_soft_17
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
        # Multiple iterations - Monte Carlo simulation
        with st.spinner(f"Running {num_iterations} simulations..."):
            iteration_results = []
            all_trajectories = []
            
            for i in range(num_iterations):
                # Set seed for reproducibility, but different for each iteration
                np.random.seed(random_seed + i)
                shoe = Shoe(num_decks=num_decks)
                
                df = simulate_martingale(
                    bankroll_start, base_bet, bet_multiplier, shoe, num_players, num_hands, dealer_hits_soft_17
                )
                
                bust = df["result"].eq("BUST").any()
                final_bankroll = df.iloc[-1]["bankroll"]
                total_profit = final_bankroll - bankroll_start
                hands_played = len(df)
                max_loss_streak = df['streak_losses'].max()
                
                iteration_results.append({
                    "iteration": i + 1,
                    "bust": bust,
                    "final_bankroll": final_bankroll,
                    "profit": total_profit,
                    "hands_played": hands_played,
                    "max_loss_streak": max_loss_streak,
                    "won": not bust and total_profit >= 0
                })
                
                # Store trajectory for visualization
                trajectory = df[["hand", "bankroll"]].copy()
                trajectory["iteration"] = i + 1
                all_trajectories.append(trajectory)
            
            results_df = pd.DataFrame(iteration_results)
            trajectories_df = pd.concat(all_trajectories, ignore_index=True)
            
            # Calculate statistics
            bust_count = results_df["bust"].sum()
            win_count = results_df["won"].sum()
            bust_rate = bust_count / num_iterations * 100
            win_rate = win_count / num_iterations * 100
            avg_profit = results_df["profit"].mean()
            avg_final_bankroll = results_df["final_bankroll"].mean()
            
            # Calculate profit statistics for outlier analysis
            profit_mean = results_df['profit'].mean()
            profit_std = results_df['profit'].std()
            profit_median = results_df['profit'].median()
            
            st.subheader("Monte Carlo Simulation Results")
            st.write(f"**{num_iterations} iterations completed**")
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Win Rate", f"{win_rate:.1f}%", help="Simulations that ended without bust")
            col2.metric("Bust Rate", f"{bust_rate:.1f}%", help="Simulations that busted")
            col3.metric("Avg Final Bankroll", f"${avg_final_bankroll:,.2f}")
            col4.metric("Avg Profit", f"${avg_profit:,.2f}")
            
            # Show profit distribution with std dev markers
            st.markdown("### Profit Distribution")
            
            # Display key statistics with visual indicators
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Mean Profit", f"${profit_mean:,.2f}")
                st.caption("📊 Average across all simulations")
            with col_b:
                st.metric("Median Profit", f"${profit_median:,.2f}")
                st.caption("📍 Middle value (50th percentile)")
            with col_c:
                st.metric("Std Deviation", f"${profit_std:,.2f}")
                st.caption("📏 Measure of spread")
            
            # Show standard deviation ranges
            st.markdown("**Standard Deviation Ranges:**")
            st.write(f"• **1σ Range**: ${profit_mean - profit_std:,.2f} to ${profit_mean + profit_std:,.2f} (contains ~68% of results)")
            st.write(f"• **2σ Range**: ${profit_mean - 2*profit_std:,.2f} to ${profit_mean + 2*profit_std:,.2f} (contains ~95% of results)")
            
            # Create histogram using Streamlit's bar chart
            st.markdown("**Profit Histogram:**")
            hist_data = pd.cut(results_df['profit'], bins=min(50, max(10, num_iterations // 2)))
            hist_counts = hist_data.value_counts().sort_index()
            hist_df = pd.DataFrame({
                'Profit Range': [f"${interval.left:,.0f}" for interval in hist_counts.index],
                'Frequency': hist_counts.values
            })
            hist_df = hist_df.set_index('Profit Range')
            st.bar_chart(hist_df)
            
            # Show final bankroll distribution
            st.markdown("### Final Bankroll Distribution")
            st.bar_chart(results_df["final_bankroll"].value_counts().sort_index())
            
            # Show sample trajectories (max 10)
            st.markdown("### Sample Bankroll Trajectories")
            sample_size = min(10, num_iterations)
            sample_trajectories = trajectories_df[trajectories_df["iteration"] <= sample_size]
            
            # Pivot for line chart
            pivot_df = sample_trajectories.pivot(index="hand", columns="iteration", values="bankroll")
            st.line_chart(pivot_df, use_container_width=True)
            
            # Detailed results table
            st.markdown("### Detailed Results by Iteration")
            st.dataframe(results_df[[
                "iteration", "bust", "won", "final_bankroll", "profit", 
                "hands_played", "max_loss_streak"
            ]])
            
            # Summary statistics
            st.markdown("### Statistical Summary")
            
            # Filter outliers (beyond 1 and 2 standard deviations)
            within_1_std = results_df[
                (results_df['profit'] >= profit_mean - profit_std) & 
                (results_df['profit'] <= profit_mean + profit_std)
            ]
            within_2_std = results_df[
                (results_df['profit'] >= profit_mean - 2*profit_std) & 
                (results_df['profit'] <= profit_mean + 2*profit_std)
            ]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**Overall Profit Statistics:**")
                st.write(f"- Mean Profit: ${profit_mean:,.2f}")
                st.write(f"- Median Profit: ${profit_median:,.2f}")
                st.write(f"- Std Dev: ${profit_std:,.2f}")
                st.write(f"- Min Profit: ${results_df['profit'].min():,.2f}")
                st.write(f"- Max Profit: ${results_df['profit'].max():,.2f}")
            
            with col2:
                st.write("**Profit Without Outliers:**")
                pct_within_1_std = len(within_1_std) / num_iterations * 100
                pct_within_2_std = len(within_2_std) / num_iterations * 100
                
                st.write(f"*Within 1σ ({pct_within_1_std:.1f}% of data):*")
                if len(within_1_std) > 0:
                    st.write(f"- Avg: ${within_1_std['profit'].mean():,.2f}")
                    st.write(f"- Range: ${within_1_std['profit'].min():,.2f} to ${within_1_std['profit'].max():,.2f}")
                else:
                    st.write("- No data")
                
                st.write(f"*Within 2σ ({pct_within_2_std:.1f}% of data):*")
                if len(within_2_std) > 0:
                    st.write(f"- Avg: ${within_2_std['profit'].mean():,.2f}")
                    st.write(f"- Range: ${within_2_std['profit'].min():,.2f} to ${within_2_std['profit'].max():,.2f}")
                else:
                    st.write("- No data")
            
            with col3:
                st.write("**Game Statistics:**")
                st.write(f"- Avg Hands Played: {results_df['hands_played'].mean():.1f}")
                st.write(f"- Avg Max Loss Streak: {results_df['max_loss_streak'].mean():.1f}")
                st.write(f"- Max Loss Streak (all): {results_df['max_loss_streak'].max()}")
                st.write(f"- Busts: {bust_count} / {num_iterations}")
                st.write(f"- Outliers (>2σ): {num_iterations - len(within_2_std)}")
            
            # Add visual representation of data distribution
            st.markdown("### Profit Distribution Analysis")
            st.write(f"""
            **Understanding the data:**
            - **Mean**: ${profit_mean:,.2f} - Average across all simulations
            - **Median**: ${profit_median:,.2f} - Middle value (50th percentile)
            - **1σ range**: ${profit_mean - profit_std:,.2f} to ${profit_mean + profit_std:,.2f} (contains ~68% of typical results)
            - **2σ range**: ${profit_mean - 2*profit_std:,.2f} to ${profit_mean + 2*profit_std:,.2f} (contains ~95% of typical results)
            
            💡 **Typical profit** (excluding extreme outliers beyond 2σ): **${within_2_std['profit'].mean():,.2f}** based on {len(within_2_std)} simulations
            """)

else:
    st.info("Set your parameters and click **Run Simulation** to begin.")
