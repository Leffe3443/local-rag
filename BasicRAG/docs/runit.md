# Running the Project (local-rag / basicrag)

Steps to get the RAG pipeline running from a clean machine: starting the database, installing Ollama, pulling the embedding model, and setting up the database schema.

## 1. Start Docker

Make sure Docker Desktop is running first (check the whale icon in your system tray). Then from the project folder, start the database container:

```bash
docker compose up -d
```

Confirm the Postgres/pgvector container is up:

```bash
docker compose ps
```

You should see a container running the `pgvector/pgvector:pg16` image, listening on port `5432`.

## 2. Install Ollama

If you don't already have Ollama installed:

- Download and install from https://ollama.com/download
- Confirm it's installed and running:

```bash
ollama --version
```

On Windows, Ollama runs as a background service automatically after install — no separate "start" step needed in most cases. If `ollama` commands fail to connect, check it's running via the system tray icon or relaunch the Ollama app.

## 3. Pull the embedding model

> Adjust this to match the actual model you're using — `768` dimensions matches models like `nomic-embed-text`. Update if you're using a different one.

```bash
ollama pull nomic-embed-text
```

Verify it's available:

```bash
ollama list
```

## 4. Set up the Python environment

```bash
cd basicrag
python -m venv env
env\Scripts\activate        # Windows
pip install -r requirements.txt
```

> Add a `requirements.txt` if you don't have one yet — at minimum it should include `psycopg` and whatever client library you're using to call Ollama (e.g. `ollama` or `requests`).

## 5. Fetch the source data

```bash
python 1_fetch_police_events.py
```

Pulls the raw event data into the database.

## 6. Generate and store embeddings

```bash
python 2_embed_rows.py
```

Reads rows from the `events` table, calls Ollama to embed the relevant text, and writes the result back to the `embedding` column.

> If your `events` table doesn't have an `embedding` column yet, add it first:
> ```sql
> ALTER TABLE events ADD COLUMN embedding vector(768);
> ```

## 7. Set up the database schema

Run the setup script to enable pgvector and create the `match_events` function:

```bash
python 3_match_events.py
```

This:
- Enables the `vector` extension (`CREATE EXTENSION IF NOT EXISTS vector;`)
- Creates the `match_events` SQL function used for similarity search

## 8. Run the project

```bash
python 4_ask.py
```

---

## Troubleshooting

**`failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine`**
Docker Desktop isn't running. Launch it and wait for it to fully start before retrying.

**`psycopg.errors.UndefinedObject: type vector does not exist`**
The pgvector extension hasn't been created in this database yet. Run `3_match_events.py`, or manually:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

**`psycopg.errors.UndefinedColumn: column e.embedding does not exist`**
The `embedding` column hasn't been added to your table yet:
```sql
ALTER TABLE events ADD COLUMN embedding vector(768);
```

More troubleshooting can be found in docs/Errors.md