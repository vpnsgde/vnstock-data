# lib/data_collector.py
import os
import logging
import requests
import pandas as pd

# ---------------------------
# Logging configuration
# ---------------------------
LOG_DIR = "./logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "data_collector_log.txt")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# ---------------------------
# HTTP configuration
# ---------------------------
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/127.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "https://cafef.vn/",
}

URLS = {
    "price_history": "https://cafef.vn/du-lieu/Ajax/PageNew/DataHistory/PriceHistory.ashx",
    "foreign_trade": "https://cafef.vn/du-lieu/Ajax/PageNew/DataHistory/GDKhoiNgoai.ashx",
    "tu_doanh": "https://cafef.vn/du-lieu/Ajax/PageNew/DataHistory/GDTuDoanh.ashx",
}


class DataCollector:
    """Reusable data collector for CafeF endpoints."""

    def __init__(self, dataset_root: str = "./dataset"):
        self.dataset_root = dataset_root
        os.makedirs(self.dataset_root, exist_ok=True)

    # ---------------------------
    # Utility methods
    # ---------------------------
    def _log(self, symbol: str, message: str):
        print(f"[{symbol}] {message}")
        logging.info(f"[{symbol}] {message}")

    def _load_existing_csv(self, symbol: str, filename: str):
        """Load existing CSV if present; return (df, row_count, csv_path)."""
        sym_dir = os.path.join(self.dataset_root, symbol)
        os.makedirs(sym_dir, exist_ok=True)
        csv_path = os.path.join(sym_dir, filename)

        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            rows = len(df)
            self._log(symbol, f"Existing rows in {filename}: {rows}")
            return df, rows, csv_path
        else:
            self._log(symbol, f"No existing file {filename}, start with 0 rows.")
            return pd.DataFrame(), 0, csv_path

    def _fetch_json(self, url: str, symbol: str, pagesize: int):
        """Call CafeF endpoint and return parsed JSON."""
        params = {
            "Symbol": symbol,
            "StartDate": "",
            "EndDate": "",
            "PageIndex": 1,
            "PageSize": pagesize,
        }
        r = requests.get(url, headers=HEADERS, params=params, timeout=30)
        r.raise_for_status()
        return r.json()

    def _clean_date_records(self, records: list[dict], date_key: str) -> list[dict]:
        """
        Remove records with invalid or out-of-bounds dates.
        Rules:
          - Drop if date is '01/01/0001', empty, None
          - Drop if parsing with '%d/%m/%Y' fails
        """
        cleaned = []
        dropped = 0
        for item in records:
            raw_date = item.get(date_key)
            if raw_date in ("01/01/0001", None, "", "NaT"):
                dropped += 1
                continue
            try:
                pd.to_datetime(raw_date, format="%d/%m/%Y")
                cleaned.append(item)
            except Exception:
                dropped += 1
                continue
        return cleaned

    def _append_sort_dedup_save(
        self,
        symbol: str,
        csv_path: str,
        existing_df: pd.DataFrame,
        df_new: pd.DataFrame,
        date_col: str,
    ):
        """Append, de-duplicate by date, sort ascending by date, and save CSV."""
        if not existing_df.empty:
            final_df = pd.concat([existing_df, df_new], ignore_index=True)
        else:
            final_df = df_new

        # Remove duplicates by date, keep the last occurrence (newest fetch wins)
        final_df = final_df.drop_duplicates(subset=[date_col], keep="last")

        # Sort ascending by date and keep date as original string in CSV
        final_df[f"{date_col}_dt"] = pd.to_datetime(final_df[date_col], format="%d/%m/%Y")
        final_df = (
            final_df.sort_values(f"{date_col}_dt")
            .drop(columns=[f"{date_col}_dt"])
            .reset_index(drop=True)
        )

        final_df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        self._log(symbol, f"Saved {os.path.basename(csv_path)} with {len(final_df)} rows.")

    # ---------------------------
    # Fetchers
    # ---------------------------
    def fetch_price_history(self, symbol: str = "VNINDEX", pagesize: int = 20):
        """
        Price history:
          - JSON path: Data.TotalCount, Data.Data (list of dicts)
          - Date column: 'Ngay' (string 'dd/MM/yyyy')
          - CSV: ./dataset/{symbol}/PriceHistory.csv
        """
        filename = "PriceHistory.csv"
        try:
            existing_df, existing_rows, csv_path = self._load_existing_csv(symbol, filename)

            # Step 2: get TotalCount
            meta = self._fetch_json(URLS["price_history"], symbol, pagesize)
            total_count = meta["Data"]["TotalCount"]
            self._log(symbol, f"TotalCount from API: {total_count}")

            if existing_rows > total_count:
                self._log(
                    symbol,
                    "Existing rows greater than TotalCount. Will refetch all rows from API.",
                )
                existing_rows = 0

            need_rows = total_count - existing_rows
            if need_rows <= 0:
                self._log(symbol, "No new data. CSV is already up-to-date.")
                return

            self._log(symbol, f"New rows to fetch: {need_rows}")
            payload = self._fetch_json(URLS["price_history"], symbol, need_rows)
            new_records = payload["Data"]["Data"]

            # Clean and sort
            new_records = self._clean_date_records(new_records, date_key="Ngay")
            if not new_records:
                self._log(symbol, "No valid records after date cleaning.")
                return

            df_new = pd.DataFrame(new_records)
            df_new["Ngay_dt"] = pd.to_datetime(df_new["Ngay"], format="%d/%m/%Y")
            df_new = df_new.sort_values("Ngay_dt").drop(columns=["Ngay_dt"])

            # Append, de-duplicate, sort, save
            self._append_sort_dedup_save(symbol, csv_path, existing_df, df_new, "Ngay")

        except Exception as e:
            logging.error(f"[{symbol}] Error in fetch_price_history: {e}")
            print(f"[{symbol}] Error in fetch_price_history: {e}")

    def fetch_foreign_trade(self, symbol: str = "VNINDEX", pagesize: int = 20):
        """
        Foreign trade (Giao dịch khối ngoại):
          - JSON path: Data.TotalCount, Data.Data (list of dicts)
          - Date column: 'Ngay' (string 'dd/MM/yyyy')
          - CSV: ./dataset/{symbol}/GDKhoiNgoai.csv
        """
        filename = "GDKhoiNgoai.csv"
        try:
            existing_df, existing_rows, csv_path = self._load_existing_csv(symbol, filename)

            # Step 2: get TotalCount
            meta = self._fetch_json(URLS["foreign_trade"], symbol, pagesize)
            total_count = meta["Data"]["TotalCount"]
            self._log(symbol, f"TotalCount from API: {total_count}")

            if existing_rows > total_count:
                self._log(
                    symbol,
                    "Existing rows greater than TotalCount. Will refetch all rows from API.",
                )
                existing_rows = 0

            need_rows = total_count - existing_rows
            if need_rows <= 0:
                self._log(symbol, "No new data. CSV is already up-to-date.")
                return

            self._log(symbol, f"New rows to fetch: {need_rows}")
            payload = self._fetch_json(URLS["foreign_trade"], symbol, need_rows)
            new_records = payload["Data"]["Data"]

            # Clean and sort
            new_records = self._clean_date_records(new_records, date_key="Ngay")
            if not new_records:
                self._log(symbol, "No valid records after date cleaning.")
                return

            df_new = pd.DataFrame(new_records)
            df_new["Ngay_dt"] = pd.to_datetime(df_new["Ngay"], format="%d/%m/%Y")
            df_new = df_new.sort_values("Ngay_dt").drop(columns=["Ngay_dt"])

            # Append, de-duplicate, sort, save
            self._append_sort_dedup_save(symbol, csv_path, existing_df, df_new, "Ngay")

        except Exception as e:
            logging.error(f"[{symbol}] Error in fetch_foreign_trade: {e}")
            print(f"[{symbol}] Error in fetch_foreign_trade: {e}")

    def fetch_tu_doanh(self, symbol: str = "VNINDEX", pagesize: int = 20):
        """
        Proprietary trading (Tự doanh):
          - JSON path: Data.TotalCount, Data.Data.ListDataTudoanh (list of dicts)
          - Date column: 'Date' (string 'dd/MM/yyyy')
          - CSV: ./dataset/{symbol}/GDTuDoanh.csv
        """
        filename = "GDTuDoanh.csv"
        try:
            existing_df, existing_rows, csv_path = self._load_existing_csv(symbol, filename)

            # Step 2: get TotalCount
            meta = self._fetch_json(URLS["tu_doanh"], symbol, pagesize)
            total_count = meta["Data"]["TotalCount"]
            self._log(symbol, f"TotalCount from API: {total_count}")

            if existing_rows > total_count:
                self._log(
                    symbol,
                    "Existing rows greater than TotalCount. Will refetch all rows from API.",
                )
                existing_rows = 0

            need_rows = total_count - existing_rows
            if need_rows <= 0:
                self._log(symbol, "No new data. CSV is already up-to-date.")
                return

            self._log(symbol, f"New rows to fetch: {need_rows}")
            payload = self._fetch_json(URLS["tu_doanh"], symbol, need_rows)
            data_block = payload["Data"]["Data"]
            new_records = data_block.get("ListDataTudoanh", [])

            # Clean and sort
            new_records = self._clean_date_records(new_records, date_key="Date")
            if not new_records:
                self._log(symbol, "No valid records after date cleaning.")
                return

            df_new = pd.DataFrame(new_records)
            df_new["Date_dt"] = pd.to_datetime(df_new["Date"], format="%d/%m/%Y")
            df_new = df_new.sort_values("Date_dt").drop(columns=["Date_dt"])

            # Append, de-duplicate, sort, save
            self._append_sort_dedup_save(symbol, csv_path, existing_df, df_new, "Date")

        except Exception as e:
            logging.error(f"[{symbol}] Error in fetch_tu_doanh: {e}")
            print(f"[{symbol}] Error in fetch_tu_doanh: {e}")
