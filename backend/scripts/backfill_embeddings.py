import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time

import openai
import psycopg2
from app.core.config import settings
from psycopg2.extras import execute_values

# Set OpenAI API key from config
openai.api_key = settings.OPENAI_API_KEY
EMBED_MODEL = "text-embedding-3-small"

# DB connection string from config
DB_DSN = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

TABLES = [
    {"table": "employee_skills", "id_col": "id", "text_col": "skill_name", "emb_col": "embedding"},
    {"table": "designations", "id_col": "id", "text_col": "title", "emb_col": "embedding"},
    {"table": "projects", "id_col": "id", "text_col": "name", "emb_col": "embedding"},
]

BATCH_SIZE = 50


def embed_texts(texts):
    """Call OpenAI API to embed a list of texts."""
    if not texts:
        return []
    response = openai.embeddings.create(input=texts, model=EMBED_MODEL)
    return [d.embedding for d in response.data]


def backfill_table(conn, table, id_col, text_col, emb_col):
    with conn.cursor() as cur:
        print(f"\nProcessing table: {table}")
        cur.execute(
            f"SELECT {id_col}, {text_col} FROM {table} WHERE {emb_col} IS NULL AND {text_col} IS NOT NULL"
        )
        rows = cur.fetchall()
        print(f"  Found {len(rows)} rows to embed.")
        for i in range(0, len(rows), BATCH_SIZE):
            batch = rows[i : i + BATCH_SIZE]
            ids = [r[0] for r in batch]
            texts = [r[1] for r in batch]
            try:
                embeddings = embed_texts(texts)
            except Exception as e:
                print(f"  Error embedding batch {i//BATCH_SIZE+1}: {e}")
                continue
            # Prepare data for bulk update
            data = list(zip(embeddings, ids))
            cur.executemany(f"UPDATE {table} SET {emb_col} = %s WHERE {id_col} = %s", data)
            conn.commit()
            print(f"  Embedded batch {i//BATCH_SIZE+1} ({len(batch)} rows)")
            time.sleep(0.5)  # avoid rate limits


def main():
    conn = psycopg2.connect(DB_DSN)
    try:
        for t in TABLES:
            backfill_table(conn, t["table"], t["id_col"], t["text_col"], t["emb_col"])
        print("\nAll embeddings backfilled successfully.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
