
# China Market Hedge Calculator

A Flask-based web application for calculating hedge positions to offset Chinese market exposure in UK sterling share portfolios.

## Overview

This tool helps traders who hold UK sterling shares calculate appropriate hedge positions using Chinese market instruments. It:

1.  Analyzes your UK portfolio to **estimate its total exposure to the Chinese market**.
2.  Calculates optimal hedge ratios based on historical **correlation and volatility**.
3.  Recommends specific Chinese instruments (stocks, ETFs) and position sizes for hedging.

## How It Works

The application uses a two-part process: first, it estimates your portfolio's financial exposure to China, and second, it calculates how to hedge that specific amount.

### Part 1: How China Exposure is Estimated

Since companies don't report a simple "China exposure" number, the application creates a **simplified, data-driven estimate** for each UK stock in your portfolio.

The logic works as follows:

1.  **Sector-Based Analysis**: The tool starts with a baseline assumption that different industries have different levels of dependency on the Chinese economy.
    *   **High Exposure**: `Basic Materials` (40%), `Industrials` (35%)
    *   **Medium Exposure**: `Technology` (30%), `Energy` (20%)
    *   **Low Exposure**: `Financial Services` (15%), `Utilities` (5%)
    *   **Default**: Any unclassified sector defaults to a conservative `15%`.

2.  **Market Capitalization Adjustment**: It then refines this baseline by assuming larger companies have more international (and thus Chinese) exposure.
    *   If a company's market cap is over £100 billion, its base exposure is increased by 30%.
    *   If it's over £10 billion, the exposure is increased by 10%.

3.  **Calculating the Exposed Value (£)**: The final estimated percentage is multiplied by your position value to get a sterling amount.

**Example Calculation:**

Imagine you hold **£50,000** in Rio Tinto (`RIO.L`).
1.  The tool identifies `RIO.L` in the **Basic Materials** sector, giving it a base exposure of **40%**.
2.  Rio Tinto is a very large company (market cap > £100B), so this exposure is adjusted upwards.
3.  The final estimated exposure for this stock might be ~45%.
4.  **China Exposed Value** = `£50,000 × 45%` = **£22,500**.

This process is repeated for every stock, and all the "China Exposed Values" are summed up to get your **Total China Exposure**—the amount you need to hedge.

### Part 2: How the Hedge is Calculated

Once the tool knows your Total China Exposure, it runs a statistical analysis (using 6 months of historical data) for each Chinese hedge candidate you provide.

1.  **Correlation Analysis**: It measures how closely a Chinese instrument (e.g., the `FXI` ETF) moves in relation to your UK portfolio. A high positive correlation means they tend to move up and down together.

2.  **Volatility Matching**: It calculates the volatility (price fluctuation risk) for both your UK portfolio and the Chinese instrument.

3.  **Optimal Hedge Ratio Formula**: It combines these metrics into a single formula to find the ideal hedge size:
    `Hedge Ratio = (UK Volatility / China Volatility) × Correlation`
    This ratio balances the relative risk (volatility) and relationship (correlation) between your assets and the hedge.

4.  **Recommendation**: The tool then provides:
    *   **Direction**:
        *   **SHORT**: If the correlation is positive. You are betting against the Chinese instrument to offset a potential drop in your UK portfolio. This is the most common scenario.
        *   **LONG**: If the correlation is negative. You buy the instrument because it tends to rise when your portfolio falls.
    *   **Notional Amount (£)**: The recommended position size, calculated as:
        `Notional Amount = Total China Exposure × Hedge Ratio`
    *   **Effectiveness Score**: A simple percentage based on the strength of the correlation. A higher score suggests a more reliable hedge.

## Example Scenario

**Your UK Portfolio:**
*   £100,000 in HSBC (`HSBA.L`) - Banking sector
*   £50,000 in Rio Tinto (`RIO.L`) - Mining sector
*   £75,000 in Unilever (`ULVR.L`) - Consumer goods

**Step 1: The App Estimates Your China Exposure**
*   HSBC (Financials, 15%): `£100,000 × 15%` = £15,000
*   Rio Tinto (Basic Materials, ~40%): `£50,000 × 40%` = £20,000
*   Unilever (Consumer Defensive, 10%): `£75,000 × 10%` = £7,500
*   **Total China Exposed Value: £42,500**

**Step 2: The App Calculates a Hedge Recommendation**
Let's say you use the `FXI` (China Large-Cap ETF) as a hedge candidate. The app finds:
*   Correlation between your portfolio and FXI = `0.75` (strong positive relationship)
*   Your Portfolio's Annualized Volatility = `22%`
*   FXI's Annualized Volatility = `28%`

It then calculates:
1.  **Hedge Ratio** = `(0.22 / 0.28) × 0.75` = **0.59**
2.  **Direction** = **SHORT** (because the correlation is positive)
3.  **Notional Amount** = `£42,500 × 0.59` = **£25,075**

**Final Recommendation:** To hedge your £42,500 of China exposure, you should **SHORT £25,075 of FXI**.

## Installation

1.  Clone or download this repository.
2.  Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

1.  Activate your virtual environment (if using one):
    ```bash
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

2.  Start the Flask server:
    ```bash
    python app.py
    ```

3.  Open your web browser and go to: `http://localhost:5000`

## Using the Application

### Step 1: Enter UK Portfolio

1.  Enter your UK share tickers (e.g., `BP.L`, `HSBA.L`). Use the `.L` suffix for London Stock Exchange listings.
2.  Enter the position value in GBP for each share.
3.  Click "Add UK Share" to add more positions.

### Step 2: Enter Chinese Hedge Candidates

1.  Enter Chinese market tickers you want to consider for hedging (e.g., `BABA`, `FXI`, `ASHR`, `000001.SS`).
2.  Click "Add China Hedge" to add more candidates.

### Step 3: Calculate Hedges

Click "Calculate Hedge Requirements" to get your results.

### Step 4: Interpret Results

**UK Portfolio Analysis Table:**
*   Shows each UK position's estimated China exposure percentage and value in GBP.

**Hedge Recommendations Table:**
*   **Ticker**: The Chinese instrument to trade.
*   **Correlation**: How closely it moves with your UK portfolio's China risk.
*   **Hedge Ratio**: The multiplier used for calculating position size.
*   **Direction**: **SHORT** (sell) or **LONG** (buy).
*   **Notional (£)**: The recommended position size in GBP.
*   **Effectiveness**: Higher percentage = better hedge (based on correlation strength).

## Important Notes

1.  **Data Source**: Uses Yahoo Finance for market data (6 months historical).
2.  **Simplifications**: China exposure estimates are simplified. Actual exposure may vary. Consider transaction costs and market impact.
3.  **Risk Management**: These are theoretical calculations. Always consider your risk tolerance. Hedges may not be perfect. Monitor and adjust positions regularly.

## Troubleshooting

*   **"Could not fetch data" errors**: Check ticker symbols are correct and that you have an internet connection. Some tickers may not be on Yahoo Finance.
*   **Unexpected results**: Low correlations may indicate poor hedge candidates. Try different instruments (e.g., broad market ETFs like `FXI` or `MCHI`).

## Disclaimer

This tool provides theoretical hedge calculations for educational and analytical purposes. Always consult with a qualified financial professional and consider all risks before implementing any trading strategy.
