
# INR ⇄ USD Settlement Ledger (Streamlit)

A lightweight local web app to record INR paid to customers vs USD received from them, and calculate profit/loss using a market rate.

## Features
- Add transactions (Date, Customer, INR Paid, USD Received, Market Rate, Notes)
- Auto-calculates: Realized Rate, Value @ Market (INR), Profit/Loss (INR)
- Filter by customer and date range
- Customer-wise and overall summaries
- Delete selected transactions
- Data saved locally in `ledger.csv`
- Export CSV

## How to run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the app:
   ```bash
   streamlit run app.py
   ```
3. Your browser will open to the app. If not, visit the URL shown in the terminal (usually http://localhost:8501).

## Notes
- The data file `ledger.csv` will be created in the same folder as `app.py`.
- You can move `ledger.csv` to back it up or open it in Excel.
