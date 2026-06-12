import sqlite3

DB_NAME = "options_tracker.db"

# =========================
# CREATE TABLE
# =========================

def create_table():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS positions (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        symbol TEXT,

        strike REAL,

        option_type TEXT,

        side TEXT,

        broker TEXT,

        strategy TEXT,

        quantity INTEGER,

        premium REAL,

        current_premium REAL,

        expiry TEXT,

        notes TEXT,

        status TEXT,

        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()

# =========================
# ADD POSITION
# =========================

def add_position(
    symbol,
    strike,
    option_type,
    side,
    broker,
    strategy,
    quantity,
    premium,
    current_premium,
    expiry,
    notes,
    created_at
):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO positions (

        symbol,
        strike,
        option_type,
        side,
        broker,
        strategy,
        quantity,
        premium,
        current_premium,
        expiry,
        notes,
        status,
        created_at

    )

    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

    """, (

        symbol,
        strike,
        option_type,
        side,
        broker,
        strategy,
        quantity,
        premium,
        current_premium,
        expiry,
        notes,
        "OPEN",
        created_at

    ))

    conn.commit()
    conn.close()

# =========================
# GET POSITIONS
# =========================

def get_positions():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM positions
    """)

    data = cursor.fetchall()

    conn.close()

    return data

# =========================
# UPDATE POSITION
# =========================

def update_position(
    position_id,
    current_premium
):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
    UPDATE positions

    SET current_premium = ?

    WHERE id = ?
    """, (
        current_premium,
        position_id
    ))

    conn.commit()
    conn.close()

# =========================
# CLOSE POSITION
# =========================

def close_position(position_id):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
    UPDATE positions

    SET status = 'CLOSED'

    WHERE id = ?
    """, (
        position_id,
    ))

    conn.commit()
    conn.close()

# =========================
# DELETE POSITION
# =========================

def delete_position(position_id):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM positions

    WHERE id = ?
    """, (
        position_id,
    ))

    conn.commit()
    conn.close()