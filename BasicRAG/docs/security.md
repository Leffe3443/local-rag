# Using `.env` Files Instead of Hardcoding

The hardcoded values are only for lowering the overhead of starting the project. ALWAYS use .env files
when running in production. 

## 1. Install python-dotenv

```bash
pip install python-dotenv
```

## 2. Create a `.env` file

In your project root:

```
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=testpassword123
DB_NAME=events_db
```

No quotes, no spaces around `=`.

## 3. Add `.env` to `.gitignore`

```
.env
```

Never commit this file — it holds secrets.

## 4. Load it in Python

```python
from dotenv import load_dotenv
import os

load_dotenv()

db_host = os.getenv("DB_HOST")
db_password = os.getenv("DB_PASSWORD")
```

## 5. Use the variables instead of hardcoded values

```python
import psycopg

conn = psycopg.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    dbname=os.getenv("DB_NAME"),
)
```

## 6. (Optional) Provide an `.env.example`

Commit a template with no real values, so others know what variables are needed:

```
DB_HOST=
DB_PORT=
DB_USER=
DB_PASSWORD=
DB_NAME=
```