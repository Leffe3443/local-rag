"""
step2_embed_rows.py
────────────────────
Run once to embed all existing rows in the `events_db` table.
Re-run any time you insert new rows — it skips already-embedded ones.

Dependencies: pip install "psycopg[binary]" python-dotenv ollama pgvector
Requires:
  • Ollama running locally with nomic-embed-text pulled
      ollama pull nomic-embed-text
  • The pgvector extension installed in Postgres
      CREATE EXTENSION IF NOT EXISTS vector;

References:
  Ollama Python SDK:  https://github.com/ollama/ollama-python
  nomic-embed-text:   https://ollama.com/library/nomic-embed-text
  psycopg 3 docs:     https://www.psycopg.org/psycopg3/docs/
  pgvector:           https://github.com/pgvector/pgvector
"""

import os
import psycopg
from psycopg.rows import dict_row
import ollama
from dotenv import load_dotenv

load_dotenv()

# ── Database connection ──────────────────────────────────────────────────────
# psycopg 3 takes a single connection string (or keyword args, like here).
conn = psycopg.connect(
    host="localhost",
    port=5432,
    dbname="events_db",
    user="postgres",
    password="testpassword123",
)

# ── Embedding model ──────────────────────────────────────────────────────────
# nomic-embed-text: 768 dimensions, ~274MB, excellent quality.
# It is NOT a chat model — only use it for embeddings.
# CRITICAL: use this exact same model in step3_ask.py
EMBED_MODEL = "nomic-embed-text"
EMBED_DIM = 768  # nomic-embed-text outputs 768 floats per text


def ensure_schema():
    """
    Make sure the pgvector extension and the `embedding` column exist.

    WHY THIS MATTERS:
    Your `events_db` table was created without an embedding column.
    pgvector adds a `vector` column type; we size it to match the model
    (768). Running this is idempotent — safe to call every time.
    """
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        cur.execute(
            f"ALTER TABLE events_db ADD COLUMN IF NOT EXISTS embedding vector({EMBED_DIM})"
        )
    conn.commit()


def build_document(event: dict) -> str:
    """
    Convert one row into a single string for embedding.

    WHY THIS MATTERS:
    The model sees one string — not individual columns. Be explicit
    with field labels so it encodes rich, queryable meaning.
    Include every field a user might ask about in natural language.

    NOTE: field names below match the *actual* columns in events_db
    (title, type, date, summary) — not the original example's names.
    The gps lat/lon are numeric and not semantically useful to embed,
    so they're left out of the document text.
    """
    parts = []
    if event.get("title"):    parts.append(f"Event: {event['title']}")
    if event.get("type"):     parts.append(f"Type: {event['type']}")
    if event.get("date"):     parts.append(f"Date: {event['date']}")
    if event.get("summary"):  parts.append(f"Summary: {event['summary']}")
    return "\n".join(parts)


def get_embedding(text: str) -> list[float]:
    """
    Call Ollama's local embedding endpoint.
    Returns 768 floats representing the meaning of the text.
    Docs: https://github.com/ollama/ollama/blob/main/docs/api.md#generate-embeddings
    """
    response = ollama.embeddings(model=EMBED_MODEL, prompt=text)
    return response["embedding"]


def embed_all_events():
    ensure_schema()

    # dict_row makes each fetched row a dict keyed by column name,
    # which is what build_document() expects.
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute("SELECT * FROM events_db WHERE embedding IS NULL")
        events = cur.fetchall()

        if not events:
            print("All rows already embedded. Nothing to do.")
            return

        print(f"Embedding {len(events)} rows...\n")

        for i, event in enumerate(events, 1):
            doc = build_document(event)
            print(f"[{i}/{len(events)}] {event.get('title', event['id'])!r}")

            vector = get_embedding(doc)

            # pgvector accepts a Python list, but psycopg needs to know how to
            # adapt it. The simplest portable approach is to pass the vector as
            # its string form, e.g. "[0.1,0.2,...]", which pgvector parses.
            cur.execute(
                "UPDATE events_db SET embedding = %s WHERE id = %s",
                (str(vector), event["id"]),
            )
            conn.commit()

    print("\nDone! Run step3_ask.py to query in natural language.")
    conn.close()


if __name__ == "__main__":
    embed_all_events()