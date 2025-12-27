import sqlite3
import json
from datetime import datetime
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# --- Database Connection & Adapter ---

class SQLiteConnection:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.conn.row_factory = sqlite3.Row

    def cursor(self):
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

class PostgresCursorProxy:
    def __init__(self, cursor):
        self.cursor = cursor
        self.lastrowid = None # Logic differs in PG

    def execute(self, sql, params=None):
        # Convert SQLite '?' placeholder to Postgres '%s'
        pg_sql = sql.replace('?', '%s')
        try:
            if params:
                self.cursor.execute(pg_sql, params)
            else:
                self.cursor.execute(pg_sql)
            
            # Simulate lastrowid if needed (limited support)
            # In production PG usage, we'd use RETURNING id, but for this hybrid setup 
            # we might skip strictly relying on lastrowid for analytics or just accept limitations.
        except Exception as e:
            print(f"DB Error: {e}")
            raise e
    
    def fetchone(self):
        return self.cursor.fetchone()
    
    def fetchall(self):
        return self.cursor.fetchall()
    
    @property
    def rowcount(self):
        return self.cursor.rowcount

class PostgresConnection:
    def __init__(self, db_url):
        self.conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)

    def cursor(self):
        return PostgresCursorProxy(self.conn.cursor())

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

def get_db_connection():
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return PostgresConnection(db_url)
    return SQLiteConnection("citizenconnect.db")

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Note: SQLite and Postgres have slightly different DDL (AutoInc vs SERIAL).
    # For a robust hybrid, we'd use SQLAlchemy. 
    # For this quick migration, we use a "compatible enough" approach or separate logic.
    # However, 'CREATE TABLE IF NOT EXISTS' with simple types often works for both (mostly).
    # TEXT, INTEGER, REAL are standard. 
    # PRIMARY KEY might need 'SERIAL' in PG vs 'INTEGER PRIMARY KEY AUTOINCREMENT' in SQLite.
    
    # We will assume the Schema is initialized Manually or via script for PG to avoid DDL hell here.
    # But let's try a best-effort standard SQL.
    
    is_postgres = os.getenv("DATABASE_URL") is not None
    
    # Users/Reps Table
    # PG: id SERIAL PRIMARY KEY
    # SQ: id INTEGER PRIMARY KEY AUTOINCREMENT
    pk_type = "SERIAL PRIMARY KEY" if is_postgres else "INTEGER PRIMARY KEY AUTOINCREMENT"
    
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS representatives (
        id {pk_type},
        name TEXT NOT NULL,
        role TEXT NOT NULL,
        party TEXT,
        constituency TEXT,
        state TEXT,
        bio TEXT,
        years_in_office INTEGER,
        funds_spent_crores REAL,
        funds_total_crores REAL,
        attendance_percentage INTEGER
    )
    ''')
    
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS chat_history (
        id {pk_type},
        user_query TEXT,
        ai_response TEXT,
        rating INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # user_sessions (session_id is TEXT PK, reliable on both)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_sessions (
        session_id TEXT PRIMARY KEY,
        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        duration_seconds INTEGER DEFAULT 0,
        ip_address TEXT,
        location TEXT, 
        latitude REAL,
        longitude REAL,
        user_agent TEXT
    )
    ''')

    # analytics_events (id PK)
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS analytics_events (
        id {pk_type},
        session_id TEXT,
        event_type TEXT,
        details TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(session_id) REFERENCES user_sessions(session_id)
    )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized.")

def create_session(session_id, ip=None, user_agent=None, location=None, lat=None, lon=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    is_postgres = os.getenv("DATABASE_URL") is not None
    
    if is_postgres:
        sql = """
        INSERT INTO user_sessions (session_id, ip_address, user_agent, location, latitude, longitude) 
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT (session_id) DO NOTHING
        """
    else:
        sql = "INSERT OR IGNORE INTO user_sessions (session_id, ip_address, user_agent, location, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?)"
        
    cursor.execute(sql, (session_id, ip, user_agent, location, lat, lon))
    conn.commit()
    conn.close()

def update_session_heartbeat(session_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    is_postgres = os.getenv("DATABASE_URL") is not None
    
    if is_postgres:
        # Postgres: EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - start_time))
        # Note: We need to cast timestamp to standard if needed, but CURRENT_TIMESTAMP works.
        sql = '''
            UPDATE user_sessions 
            SET last_heartbeat = CURRENT_TIMESTAMP,
                duration_seconds = EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - start_time))
            WHERE session_id = ?
        '''
    else:
        # SQLite: strftime('%s', ...)
        sql = '''
            UPDATE user_sessions 
            SET last_heartbeat = CURRENT_TIMESTAMP,
                duration_seconds = (strftime('%s', CURRENT_TIMESTAMP) - strftime('%s', start_time))
            WHERE session_id = ?
        '''

    cursor.execute(sql, (session_id,))
    conn.commit()
    conn.close()

def log_analytics_event(session_id, event_type, details=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO analytics_events (session_id, event_type, details) VALUES (?, ?, ?)", (session_id, event_type, details))
    conn.commit()
    conn.close()

def get_daily_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    is_postgres = os.getenv("DATABASE_URL") is not None
    
    if is_postgres:
        date_q = "date(start_time) = CURRENT_DATE"
        date_q_ts = "date(timestamp) = CURRENT_DATE"
    else:
        date_q = "date(start_time) = date('now')"
        date_q_ts = "date(timestamp) = date('now')"
    
    # 1. New Users Today
    cursor.execute(f"SELECT COUNT(*) FROM user_sessions WHERE {date_q}")
    new_users = cursor.fetchone()['count'] if is_postgres else cursor.fetchone()[0]
    
    # 2. Avg Session Duration
    cursor.execute(f"SELECT AVG(duration_seconds) FROM user_sessions WHERE {date_q}")
    row = cursor.fetchone()
    # Postgres returns dictionary in RealDictCursor, SQLite row/tuple
    val = row['avg'] if is_postgres and row else (row[0] if row else 0)
    avg_duration = val or 0
    
    # 3. Top Actions
    cursor.execute(f"SELECT event_type, COUNT(*) as count FROM analytics_events WHERE {date_q_ts} GROUP BY event_type ORDER BY count DESC LIMIT 5")
    top_actions = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return {
        "new_users": new_users,
        "avg_duration": round(avg_duration, 2),
        "top_actions": top_actions
    }

def get_advanced_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    is_postgres = os.getenv("DATABASE_URL") is not None
    
    if is_postgres:
        # Postgres uses TO_CHAR for formatting and CURRENT_DATE
        date_q = "date(timestamp) = CURRENT_DATE"
        hour_q = "TO_CHAR(timestamp, 'HH24') as hour"
    else:
        # SQLite uses strftime and date('now')
        date_q = "date(timestamp) = date('now')"
        hour_q = "strftime('%H', timestamp) as hour"
    
    # 1. Traffic by Hour (Today)
    cursor.execute(f"SELECT {hour_q}, COUNT(*) as count FROM analytics_events WHERE {date_q} GROUP BY hour ORDER BY hour")
    traffic_by_hour = [dict(row) for row in cursor.fetchall()]
    
    # 2. Top Locations
    cursor.execute("SELECT location, latitude, longitude, COUNT(*) as count FROM user_sessions WHERE location IS NOT NULL GROUP BY location ORDER BY count DESC LIMIT 10")
    top_locations = [dict(row) for row in cursor.fetchall()]

    # 3. Drop-off Points (Last event in session)
    # We find the max timestamp for each session, then get the event type
    cursor.execute('''
        SELECT event_type, COUNT(*) as count 
        FROM analytics_events 
        WHERE (session_id, timestamp) IN (
            SELECT session_id, MAX(timestamp) 
            FROM analytics_events 
            GROUP BY session_id
        )
        GROUP BY event_type 
        ORDER BY count DESC 
        LIMIT 5
    ''')
    drop_offs = [dict(row) for row in cursor.fetchall()]
    

    
    conn.close()
    return {
        "traffic_by_hour": traffic_by_hour,
        "top_locations": top_locations,
        "drop_offs": drop_offs
    }

def get_recent_chats(limit=10):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, user_query, ai_response, rating FROM chat_history ORDER BY timestamp DESC LIMIT ?", (limit,))
    chats = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return chats


def get_representative_by_location(constituency):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM representatives WHERE constituency LIKE ?", (f"%{constituency}%",))
    reps = cursor.fetchall()
    conn.close()
    return [dict(row) for row in reps]

def get_all_representatives():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM representatives")
    reps = cursor.fetchall()
    conn.close()
    return [dict(row) for row in reps]

def save_chat_interaction(user_query, ai_response):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_history (user_query, ai_response) VALUES (?, ?)", (user_query, ai_response))
    chat_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return chat_id

def update_chat_rating(chat_id, rating):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE chat_history SET rating = ? WHERE id = ?", (rating, chat_id))
    conn.commit()
    conn.close()

def get_high_quality_chats():
    # Retrieve chats with 5-star ratings for few-shot learning
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_query, ai_response FROM chat_history WHERE rating = 5 ORDER BY id DESC LIMIT 5")
    chats = cursor.fetchall()
    conn.close()
    return [dict(row) for row in chats]
