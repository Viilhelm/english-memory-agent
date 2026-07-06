import os
import sqlite3

DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "memory.db"))

def get_db_connection():
    """Returns a sqlite3 connection with Row factory enabled."""
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

_EXPECTED_COLUMNS = {
    "part_of_speech": "TEXT",
    "definition": "TEXT",
}


def _run_column_migrations(conn: sqlite3.Connection) -> None:
    """Add any columns from _EXPECTED_COLUMNS that are missing from cards.

    Idempotent — safe to run on every init_db() call. Needed because older
    databases (created before word_card fields were introduced) already have
    the table, so the CREATE TABLE IF NOT EXISTS in schema.sql is a no-op
    and won't pick up the new columns on its own.
    """
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(cards)")
    existing = {row[1] for row in cursor.fetchall()}
    for col, col_type in _EXPECTED_COLUMNS.items():
        if col not in existing:
            cursor.execute(f"ALTER TABLE cards ADD COLUMN {col} {col_type}")
    conn.commit()


def init_db():
    """Initializes the cards table using schema.sql, then applies any pending column migrations."""
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Database schema file not found at: {schema_path}")

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = get_db_connection()
    try:
        conn.executescript(schema_sql)
        _run_column_migrations(conn)
    finally:
        conn.close()

def insert_card(card_data: dict) -> int:
    """Inserts a card into the cards table and returns its ID."""
    # Note: `ielts_version` still exists as a column for backward compatibility
    # with rows written before it was retired. New rows leave it NULL.
    sql = """
    INSERT INTO cards (
        card_type, original_input, corrected_version, natural_version,
        formal_version, chinese_explanation, key_expression,
        error_type, scenario, tags, part_of_speech, definition
    ) VALUES (
        :card_type, :original_input, :corrected_version, :natural_version,
        :formal_version, :chinese_explanation, :key_expression,
        :error_type, :scenario, :tags, :part_of_speech, :definition
    )
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, {
            "card_type": card_data.get("card_type", "expression_card"),
            "original_input": card_data.get("original_input"),
            "corrected_version": card_data.get("corrected_version"),
            "natural_version": card_data.get("natural_version"),
            "formal_version": card_data.get("formal_version"),
            "chinese_explanation": card_data.get("chinese_explanation"),
            "key_expression": card_data.get("key_expression"),
            "error_type": card_data.get("error_type"),
            "scenario": card_data.get("scenario"),
            "tags": card_data.get("tags"),
            "part_of_speech": card_data.get("part_of_speech"),
            "definition": card_data.get("definition"),
        })
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def query_cards(query_str: str = None) -> list[dict]:
    """Queries cards by keyword search in relevant text fields."""
    conn = get_db_connection()
    sql = "SELECT * FROM cards WHERE 1=1"
    params = {}
    if query_str:
        sql += """ AND (
            original_input LIKE :q
            OR corrected_version LIKE :q
            OR chinese_explanation LIKE :q
            OR key_expression LIKE :q
            OR tags LIKE :q
            OR scenario LIKE :q
            OR error_type LIKE :q
        )"""
        params["q"] = f"%{query_str}%"
    sql += " ORDER BY id DESC"
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def fetch_recent_cards(limit: int = 5) -> list[dict]:
    """Fetches the most recently created cards."""
    conn = get_db_connection()
    sql = "SELECT * FROM cards ORDER BY id DESC LIMIT ?"
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (limit,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def delete_card_by_id(card_id: int) -> bool:
    """Deletes a card by its ID and returns True if successful."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cards WHERE id = ?", (card_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()
