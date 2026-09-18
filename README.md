# Indian Market AI Scanner v2

Cloud/browser-ready whole-market scanner using a real market-data connector.

This build is designed for a Samsung Galaxy Tab browser. It does NOT fabricate prices.

## Setup
1. Create/use an Upstox developer API application and obtain an access token.
2. Set `UPSTOX_ACCESS_TOKEN` as a Streamlit secret/environment variable.
3. Install: `pip install -r requirements.txt`
4. Run: `streamlit run streamlit_app.py`

The scanner loads the NSE equity universe, fetches market snapshots in batches, and shows:
- market breadth
- gainers/losers
- momentum watch
- breakout watch
- high-movement stocks
- full market table

Next build can add WebSocket ticks, historical candles, RSI/EMA/MACD, sector analysis, F&O/OI, news and AI explanations.
