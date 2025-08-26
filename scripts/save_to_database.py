# scripts/save_to_database.py

import sqlite3
import os
import pandas as pd
import logging

# Setup logging
def setup_logging():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    log_folder = os.path.join(project_root, "logs")
    os.makedirs(log_folder, exist_ok=True)

    log_file = os.path.join(log_folder, "save_to_database.txt")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, mode="a", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

def init_databases():
    """
    Initialize two SQLite databases: basic_info.db and price_history.db inside the database folder.
    If a database already exists, it will not be recreated.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    db_folder = os.path.join(project_root, "database")

    os.makedirs(db_folder, exist_ok=True)

    db_files = ["basic_info.db", "price_history.db"]
    db_paths = {}

    for db_name in db_files:
        db_path = os.path.join(db_folder, db_name)
        db_paths[db_name] = db_path

        if not os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            conn.close()
            logging.info(f"Created database: {db_path}")
        else:
            logging.info(f"Database already exists: {db_path}")

    return db_paths


def import_basic_info_db(db_path):
    """
    Import CSV files from dataset/basic_info into basic_info.db.
    - Each CSV corresponds to one table (table name = file name).
    - If a table exists, new rows are appended.
    - Duplicate rows are not inserted.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    dataset_folder = os.path.join(project_root, "dataset", "basic_info")

    if not os.path.exists(dataset_folder):
        logging.warning(f"Dataset folder not found: {dataset_folder}")
        return

    conn = sqlite3.connect(db_path)

    for file in os.listdir(dataset_folder):
        if file.endswith(".csv"):
            table_name = os.path.splitext(file)[0]
            file_path = os.path.join(dataset_folder, file)

            try:
                df_csv = pd.read_csv(file_path)

                # Check if the table already exists
                query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';"
                table_exists = pd.read_sql(query, conn).shape[0] > 0

                if table_exists:
                    df_db = pd.read_sql(f"SELECT * FROM {table_name}", conn)
                    before_count = len(df_db)

                    # Merge and drop duplicates
                    df_merged = pd.concat([df_db, df_csv], ignore_index=True).drop_duplicates()
                    after_count = len(df_merged)

                    df_merged.to_sql(table_name, conn, if_exists="replace", index=False)
                    logging.info(
                        f"Updated table '{table_name}': {after_count - before_count} new rows added "
                        f"({before_count} -> {after_count}, duplicates removed)"
                    )
                else:
                    df_csv.to_sql(table_name, conn, if_exists="replace", index=False)
                    logging.info(f"Created new table '{table_name}' from {file} with {len(df_csv)} rows")

            except Exception as e:
                logging.error(f"Error importing {file}: {e}")

    conn.close()


def import_price_history_db(db_path):
    """
    Import CSV files from dataset/{Symbol} into price_history.db.
    - Each subfolder (except 'basic_info') is treated as a stock symbol.
    - Each CSV file in the subfolder is imported as a table named {Symbol}_{filename}.
    - If a table exists, new rows are appended.
    - Duplicate rows are not inserted.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    dataset_root = os.path.join(project_root, "dataset")

    if not os.path.exists(dataset_root):
        logging.warning(f"Dataset root folder not found: {dataset_root}")
        return

    conn = sqlite3.connect(db_path)

    for symbol_folder in os.listdir(dataset_root):
        symbol_path = os.path.join(dataset_root, symbol_folder)

        # Skip non-folders and the "basic_info" folder
        if not os.path.isdir(symbol_path) or symbol_folder == "basic_info":
            continue

        symbol = symbol_folder
        logging.info(f"Processing symbol folder: {symbol}")

        for file in os.listdir(symbol_path):
            if file.endswith(".csv"):
                base_name = os.path.splitext(file)[0]
                table_name = f"{symbol}_{base_name}"
                file_path = os.path.join(symbol_path, file)

                try:
                    df_csv = pd.read_csv(file_path)

                    # Check if the table already exists
                    query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';"
                    table_exists = pd.read_sql(query, conn).shape[0] > 0

                    if table_exists:
                        df_db = pd.read_sql(f"SELECT * FROM {table_name}", conn)
                        before_count = len(df_db)

                        df_merged = pd.concat([df_db, df_csv], ignore_index=True).drop_duplicates()
                        after_count = len(df_merged)

                        df_merged.to_sql(table_name, conn, if_exists="replace", index=False)
                        logging.info(
                            f"Updated table '{table_name}': {after_count - before_count} new rows added "
                            f"({before_count} -> {after_count}, duplicates removed)"
                        )
                    else:
                        df_csv.to_sql(table_name, conn, if_exists="replace", index=False)
                        logging.info(f"Created new table '{table_name}' from {file} with {len(df_csv)} rows")

                except Exception as e:
                    logging.error(f"Error importing {file} for symbol {symbol}: {e}")

    conn.close()


if __name__ == "__main__":
    setup_logging()
    db_paths = init_databases()
    import_basic_info_db(db_paths["basic_info.db"])
    import_price_history_db(db_paths["price_history.db"])
