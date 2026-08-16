import os
import glob
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

CSV_PATH = "data/raw/*.csv"

def load_file(conn, filepath):
    print(f"Loading {filepath}...")
    with open(filepath, "r") as f:
        cursor = conn.cursor()
        next(f)  # skip header row
        cursor.copy_expert(
            "COPY citibike_trips FROM STDIN WITH CSV",
            f
        )
        conn.commit()
        print(f"Done: {filepath}")

def main():
    conn = psycopg2.connect(DATABASE_URL)
    files = sorted(glob.glob(CSV_PATH))
    print(f"Found {len(files)} files")
    for filepath in files:
        load_file(conn, filepath)
    conn.close()
    print("All files loaded.")

if __name__ == "__main__":
    main()