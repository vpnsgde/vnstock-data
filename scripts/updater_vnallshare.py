import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import pandas as pd
from lib.data_collector import DataCollector

def main():
    csv_path = "./dataset/basic_info/companies_vnallshare.csv"
    if not os.path.exists(csv_path):
        print(f"File {csv_path} does not exist.")
        return

    # Load VN-ALLSHARE companies
    df = pd.read_csv(csv_path)
    if "Symbol" not in df.columns:
        print("CSV file is missing column 'Symbol'.")
        return

    symbols = df["Symbol"].dropna().unique().tolist()
    print(f"Starting data update for {len(symbols)} VN-ALLSHARE symbols...")

    collector = DataCollector()

    for idx, symbol in enumerate(symbols, start=1):
        print(f"\n=== [{idx}/{len(symbols)}] Processing {symbol} ===")
        try:
            collector.fetch_price_history(symbol, pagesize=20)
            collector.fetch_foreign_trade(symbol, pagesize=20)
            collector.fetch_tu_doanh(symbol, pagesize=20)
        except Exception as e:
            print(f"Error while processing {symbol}: {e}")
            continue

    print("\nCompleted VN-ALLSHARE data update.")

if __name__ == "__main__":
    main()
