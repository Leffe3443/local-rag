"""
step3_ask.py — interactive natural language query loop
Run any time: python step3_ask.py

Each question goes through four stages:
  A. Embed the question (nomic-embed-text via Ollama)
  B. Vector search in Postgres (match_events SQL function)
  C. Format retrieved rows as readable context
  D. Pass context + question to a local LLM (llama3.2 via Ollama)

This is RAG — Retrieval-Augmented Generation.
Reference: https://ollama.com/library

Dependencies: pip install "psycopg[binary]" python-dotenv ollama pgvector
"""

import os
import psycopg
from psycopg.rows import dict_row
import ollama
from dotenv import load_dotenv

load_dotenv()

# ── Config ───────────────────────────────────────────────────────────────────
EMBED_MODEL = "nomic-embed-text"  # must match step2 exactly
CHAT_MODEL = "llama3.2"          # any `ollama pull <name>` chat model
MATCH_THRESHOLD = 0.5                 # min similarity (0–1). Tune this.
MATCH_COUNT     = 5                   # top-K results to retrieve

conn = psycopg.connect(
    host="localhost",  port=5432,
    dbname="events_db",   user="postgres",
    password="testpassword123",
)


def embed_question(question: str) -> list[float]:
    """Embed the user's question. Must use the same model as step2."""
    response = ollama.embeddings(model=EMBED_MODEL, prompt=question)
    return response["embedding"]


def search_events(question_vector: list[float]) -> list[dict]:
    """
    Call the match_events Postgres function and return matching rows.

    pgvector compares vectors with the `<=>` operator (cosine DISTANCE).
    Similarity is just 1 - distance, so a higher `similarity` = closer match.
    We pass the vector as its string form ("[0.1,0.2,...]"), which pgvector
    parses into a vector literal. dict_row gives us dict rows by column name.
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "SELECT * FROM match_events(%s, %s, %s)",
            (str(question_vector), MATCH_THRESHOLD, MATCH_COUNT),
        )
        return cur.fetchall()


def format_context(events: list[dict]) -> str:
    """
    Format retrieved rows as readable text for the LLM.

    NOTE: field names match the *actual* events_db columns
    (title, type, date) — not the original example's names.
    There is no location name stored (only gps lat/lon), so we
    surface the coordinates instead.
    """
    if not events:
        return "No relevant events found."
    blocks = []
    for i, ev in enumerate(events, 1):
        gps = "N/A"
        if ev.get("lat") is not None and ev.get("lon") is not None:
            gps = f"{ev['lat']},{ev['lon']}"
        blocks.append(f"""Event {i} (similarity: {ev['similarity']:.2f})
Title:    {ev.get('title', 'N/A')}
Type:     {ev.get('type', 'N/A')}
When:     {ev.get('date', 'N/A')}
GPS:      {gps}
Summary:  {ev.get('summary', 'N/A')}
URL:      {ev.get('url', 'N/A')}""")
    return "\n\n---\n\n".join(blocks)


def generate_answer(question: str, context: str) -> str:
    """
    Send context + question to a local Ollama chat model.
    The system prompt constrains the model to the retrieved context only,
    preventing hallucination. temperature=0.1 = factual, not creative.
    """
    system_prompt = f"""You are a helpful assistant answering questions about events.
Use ONLY the event records below to answer. If the answer isn't in the records, say so.
When relevant, mention the event title, date, location, and URL.

RETRIEVED EVENTS:
{context}"""

    response = ollama.chat(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": question},
        ],
        options={"temperature": 0.1},
    )
    return response["message"]["content"]


def main():
    print("=" * 56)
    print("  Events DB — natural language search (fully local)")
    print("  Type a question, or 'quit' to exit.")
    print("=" * 56 + "\n")

    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye."); break

        if not question: continue
        if question.lower() in {"quit", "exit", "q"}: break

        print("\n→ Embedding question...")
        vec = embed_question(question)

        print("→ Searching Postgres...")
        events = search_events(vec)

        if not events:
            print(f"  No matches above threshold ({MATCH_THRESHOLD}).")
            print("  Try rephrasing, or lower MATCH_THRESHOLD.\n")
            continue

        print(f"  Found {len(events)} match(es):")
        for ev in events:
            print(f"    • {ev['title']}  (sim: {ev['similarity']:.2f})")

        context = format_context(events)

        print("\n→ Generating answer (local LLM)...\n")
        answer = generate_answer(question, context)

        print("Assistant:", answer)
        print("\n" + "-" * 56 + "\n")

    conn.close()


if __name__ == "__main__":
    main()