import sqlite3

def init_db():
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()

    # Create chats table with document_text column
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            document_text TEXT,  -- New column to store document_text
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Create messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            role TEXT,
            content TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(chat_id) REFERENCES chats(id)
        );
    """)

    conn.commit()
    conn.close()

def load_chat_messages(chat_id):
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT role, content FROM messages
        WHERE chat_id = ?
        ORDER BY timestamp ASC
    """, (chat_id,))
    messages = cursor.fetchall()
    conn.close()
    return [{"role": role, "content": content} for role, content in messages]

def save_message(chat_id, role, content):
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)
    """, (chat_id, role, content))
    conn.commit()
    conn.close()

def save_document_text(chat_id, document_text):
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE chats SET document_text = ? WHERE id = ?
    """, (document_text, chat_id))
    conn.commit()
    conn.close()

def load_document_text(chat_id):
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT document_text FROM chats WHERE id = ?
    """, (chat_id,))
    result = cursor.fetchone()
    conn.close()
    if result and result[0]:
        return result[0]
    else:
        return ""
