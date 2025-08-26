# scripts/basic_info.py
import requests
import csv
import os
from datetime import datetime, timezone


HEADERS_CAFEF = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/127.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "https://cafef.vn/",
}

HEADERS_SSI = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/127.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "https://iboard.ssi.com.vn/",
}


def save_banks_info():
    url = "https://cafef.vn/du-lieu/ajax/pagenew/databusiness/BankList.ashx"
    csv_file = "./dataset/basic_info/banks_info.csv"
    fields_to_keep = ["Symbol", "FullName", "TradeCenterId"]

    resp = requests.get(url, headers=HEADERS_CAFEF)
    resp.raise_for_status()
    data = resp.json().get("Data", [])

    os.makedirs(os.path.dirname(csv_file), exist_ok=True)

    if isinstance(data, list) and data:
        data_sorted = sorted(data, key=lambda x: x.get("Symbol", ""))
        filtered_data = []
        for i, row in enumerate(data_sorted, start=1):
            filtered_row = {k: row.get(k, "") for k in fields_to_keep}
            filtered_row["Index"] = i
            filtered_data.append(filtered_row)

        keys = ["Index"] + fields_to_keep
        with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(filtered_data)

        print(f"Exported {len(filtered_data)} rows to {csv_file}")
    else:
        print("Banks info JSON is empty or invalid.")


def save_brokers_info():
    url = "https://cafef.vn/du-lieu/ajax/pagenew/databusiness/stocklist.ashx"
    csv_file = "./dataset/basic_info/brokers_info.csv"
    fields_to_keep = ["Symbol", "FullName", "TradeCenterId"]

    resp = requests.get(url, headers=HEADERS_CAFEF)
    resp.raise_for_status()
    data = resp.json().get("Data", [])

    os.makedirs(os.path.dirname(csv_file), exist_ok=True)

    if isinstance(data, list) and data:
        data_sorted = sorted(data, key=lambda x: x.get("Symbol", ""))
        filtered_data = []
        for i, row in enumerate(data_sorted, start=1):
            filtered_row = {k: row.get(k, "") for k in fields_to_keep}
            filtered_row["Index"] = i
            filtered_data.append(filtered_row)

        keys = ["Index"] + fields_to_keep
        with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(filtered_data)

        print(f"Exported {len(filtered_data)} rows to {csv_file}")
    else:
        print("Brokers info JSON is empty or invalid.")


def save_funds_info():
    url = "https://cafef.vn/du-lieu/ajax/pagenew/databusiness/fund.ashx"
    csv_file = "./dataset/basic_info/funds_info.csv"
    fields_to_keep = [
        "StockSymbol", "FullName", "ManagementCompany", "Type",
        "PlaceRegistration", "NetAssetsValue", "CurrencyName", "EstablishedDate"
    ]

    resp = requests.get(url, headers=HEADERS_CAFEF)
    resp.raise_for_status()
    data = resp.json().get("Data", [])

    os.makedirs(os.path.dirname(csv_file), exist_ok=True)

    def parse_date(json_date_str):
        try:
            timestamp = int(json_date_str.strip("/Date()/"))
            return datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc).date().isoformat()
        except Exception:
            return ""

    if isinstance(data, list) and data:
        data_sorted = sorted(data, key=lambda x: x.get("StockSymbol", ""))
        filtered_data = []
        for i, row in enumerate(data_sorted, start=1):
            filtered_row = {k: row.get(k, "") for k in fields_to_keep}
            filtered_row["EstablishedDate"] = parse_date(row.get("EstablishedDate", ""))
            filtered_row["Index"] = i
            filtered_data.append(filtered_row)

        keys = ["Index"] + fields_to_keep
        with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(filtered_data)

        print(f"Exported {len(filtered_data)} rows to {csv_file}")
    else:
        print("Funds info JSON is empty or invalid.")


def save_sectors_info():
    url = "https://iboard-api.ssi.com.vn/statistics/company/sectors-data"
    csv_file = "./dataset/basic_info/sectors_info.csv"

    resp = requests.get(url, headers=HEADERS_SSI)
    resp.raise_for_status()
    sectors_data = resp.json().get("data", [])

    os.makedirs(os.path.dirname(csv_file), exist_ok=True)

    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "industry_name_vi", "industry_name_vn", "industry_name_en",
            "industry_code", "industry_level", "industry_close_index", "company_symbols"
        ])

        for sector in sectors_data:
            industry_name = sector.get("industryName", {})
            company_symbols = [c.get("symbol", "") for c in sector.get("listCompany", [])]
            writer.writerow([
                industry_name.get("vi", ""),
                industry_name.get("vn", ""),
                industry_name.get("en", ""),
                sector.get("industryCode", ""),
                sector.get("industryLevel", ""),
                sector.get("industryCloseIndex", ""),
                ",".join(company_symbols)
            ])

    print(f"Exported {len(sectors_data)} rows to {csv_file}")


def save_companies_vnallshare():
    url = "https://cafef.vn/du-lieu/ajax/pagenew/databusiness/congtyniemyet.ashx?take=1661"
    csv_file = "./dataset/basic_info/companies_vnallshare.csv"
    fields_to_keep = ["Symbol", "TradeCenterId", "CategoryId", "CompanyName", "CategoryName"]

    resp = requests.get(url, headers=HEADERS_CAFEF)
    resp.raise_for_status()
    data = resp.json().get("Data", [])

    os.makedirs(os.path.dirname(csv_file), exist_ok=True)

    if isinstance(data, list) and data:
        data_sorted = sorted(data, key=lambda x: x.get("Symbol", ""))
        filtered_data = []
        for i, row in enumerate(data_sorted, start=1):
            filtered_row = {k: row.get(k, "") for k in fields_to_keep}
            filtered_row["Index"] = i
            filtered_data.append(filtered_row)

        keys = ["Index"] + fields_to_keep
        with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(filtered_data)

        print(f"Exported {len(filtered_data)} rows to {csv_file}")
    else:
        print("Companies VNAllshare JSON is empty or invalid.")


if __name__ == "__main__":
    save_banks_info()
    save_brokers_info()
    save_funds_info()
    save_sectors_info()
    save_companies_vnallshare()
