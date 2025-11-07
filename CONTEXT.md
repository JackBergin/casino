# Blackjack Martingale Simulator — Context Overview

## 🎯 Purpose
This project simulates the **Martingale betting strategy** within a **realistic blackjack environment**, using **Streamlit** for visualization.  
It’s meant to model *how bankrolls evolve under doubling strategies*, and allow adjustable parameters (deck count, player count, dealer rules, etc.) for probability experimentation and risk analysis.

---

## ⚙️ Core Goals
1. **Accurate Blackjack Simulation**
   - Player hits when hand < 17 and stands when ≥ 17.
   - Dealer stands on 17 by default, with a toggle to **hit on soft 17**.
   - Aces count as **1 or 11** dynamically to prevent busts.
   - Blackjack pays **3:2**.
   - Optional number of players at the table (for shoe depletion realism).

2. **Martingale Betting Logic (Strict)**
   - Start with a **base bet B**.
   - On a **loss**, double the bet each subsequent hand: `B, 2B, 4B, 8B, ...`
   - On a **win**, reset bet to base bet.
   - If the *next required bet* exceeds bankroll → **BUST**.
   - Push (tie) does not change streak or bet.
   - Simulation ends only when bankroll ≤ 0 or cannot cover the next required bet.

3. **Visualization**
   - Each hand is one row in the table.
   - Show:
     - Hand number  
     - Result (win/lose/push/bust)  
     - Player hand cards + value  
     - Dealer hand cards + value  
     - Bet size  
     - Current bankroll  
     - Profit  
     - Current loss streak
   - Line chart of bankroll trajectory over time.

---

## 🧩 Architecture

blackjack_martingale/
├── app.py # Streamlit UI & simulation driver
├── blackjack_simulator.py # Core blackjack engine logic
└── CONTEXT.md # Project goals & context
---

## 🔍 Future Extensions
- Basic strategy toggle (dealer-facing vs standard).
- Multiple simulations for statistical outcomes (distribution of busts).
- Payout ratio visualization.
- Monte Carlo run aggregation for expected value over time.
