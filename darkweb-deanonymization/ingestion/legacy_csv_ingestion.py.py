import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)

cursor = conn.cursor()

def insert_csv(file, table):
    df = pd.read_csv(file)
    for _, row in df.iterrows():
        cols = ",".join(df.columns)
        vals = tuple(row)
        placeholders = ",".join(["%s"] * len(row))

        query = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
        try:
            cursor.execute(query, vals)
        except Exception as e:
            print(f"Error in {table}:", e)
            conn.rollback()
            continue

    conn.commit()

insert_csv("data/actors.csv", "actors")
insert_csv("data/platforms.csv", "platforms")
insert_csv("data/handles.csv", "handles")
insert_csv("data/wallets.csv", "wallets")
insert_csv("data/posts.csv", "posts")
insert_csv("data/evidence.csv", "evidence")

cursor.close()
conn.close()

print("✅ Data inserted successfully")