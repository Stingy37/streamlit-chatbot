import sqlite3

def get_db_connection():
    conn = sqlite3.connect("chat_history.db", check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # chats table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            document_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # main messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            role TEXT,
            content TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(chat_id) REFERENCES chats(id) ON DELETE CASCADE
        );
    """)

    # helper chat messages (per main chat)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS helper_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            main_chat_id INTEGER,
            role TEXT,
            content TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(main_chat_id) REFERENCES chats(id) ON DELETE CASCADE
        );
    """)

    # RAG entries table: store snippet + embedding JSON
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rag_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            content TEXT,
            embedding TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(chat_id) REFERENCES chats(id) ON DELETE CASCADE
        );
    """)

    conn.commit()
    conn.close()

def load_chat_messages(chat_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT role, content FROM messages
        WHERE chat_id = ?
        ORDER BY timestamp ASC
    """, (chat_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"role": r, "content": c} for r, c in rows]

def save_message(chat_id, role, content):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO messages (chat_id, role, content)
        VALUES (?, ?, ?)
    """, (chat_id, role, content))
    conn.commit()
    conn.close()

def load_helper_messages(main_chat_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT role, content FROM helper_messages
        WHERE main_chat_id = ?
        ORDER BY timestamp ASC
    """, (main_chat_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"role": r, "content": c} for r, c in rows]

def save_helper_message(main_chat_id, role, content):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO helper_messages (main_chat_id, role, content)
        VALUES (?, ?, ?)
    """, (main_chat_id, role, content))
    conn.commit()
    conn.close()

def save_document_text(chat_id, document_text):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE chats SET document_text = ? WHERE id = ?
    """, (document_text, chat_id))
    conn.commit()
    conn.close()

def load_document_text(chat_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT document_text FROM chats WHERE id = ?
    """, (chat_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row and row[0] else ""

def save_rag_entry(chat_id, content, embedding_json):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO rag_entries (chat_id, content, embedding)
        VALUES (?, ?, ?)
    """, (chat_id, content, embedding_json))
    conn.commit()
    conn.close()

def load_rag_entries(chat_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT content, embedding FROM rag_entries
        WHERE chat_id = ?
    """, (chat_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"content": r[0], "embedding": r[1]} for r in rows]

def get_all_chats():
    """Return list of all chat IDs."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM chats ORDER BY created_at ASC;")
    ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return ids

def create_chat(name: str = "New Chat") -> int:
    """Create a new chat row and return its new ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chats (name) VALUES (?);",
        (name,)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id
