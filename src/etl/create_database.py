import sqlite3
from pathlib import Path


DB_PATH = Path("db/nifty100.db")
SCHEMA_PATH = Path("sql/schema.sql")


def create_database():

    DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    conn = sqlite3.connect(DB_PATH)

    conn.execute(
        "PRAGMA foreign_keys = ON;"
    )

    with open(
        SCHEMA_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        schema = file.read()

    conn.executescript(schema)

    conn.commit()
    conn.close()

    print("\nDatabase created successfully")
    print(f"Location: {DB_PATH}")


if __name__ == "__main__":
    create_database()