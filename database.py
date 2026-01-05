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
    


    # Migration for existing table (idempotent)
    try:
        cursor.execute("ALTER TABLE representatives ADD COLUMN achievements TEXT")
    except Exception:
        pass 

    try:
        cursor.execute("ALTER TABLE representatives ADD COLUMN image_url TEXT")
    except Exception:
        pass

    try:
        cursor.execute("ALTER TABLE representatives ADD COLUMN news TEXT")
    except Exception:
        pass

    try:
        cursor.execute("ALTER TABLE representatives ADD COLUMN sources TEXT")
    except Exception:
        pass

    try:
        cursor.execute("ALTER TABLE representatives ADD COLUMN funds_spent_crores REAL")
    except Exception:
        pass

    try:
        cursor.execute("ALTER TABLE representatives ADD COLUMN funds_total_crores REAL")
    except Exception:
        pass

    try:
        cursor.execute("ALTER TABLE representatives ADD COLUMN attendance_percentage INTEGER")
    except Exception:
        pass

    conn.commit()
    
    conn.commit()

    # --- Analytics Tables ---
    # Chat History
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS chat_history (
        id {pk_type},
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        user_query TEXT,
        ai_response TEXT,
        rating INTEGER
    )
    ''')
    
    # User Sessions
    # session_id matches client-side UUID
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_sessions (
        session_id TEXT PRIMARY KEY,
        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        duration_seconds REAL DEFAULT 0,
        ip_address TEXT,
        user_agent TEXT,
        location TEXT,
        latitude REAL,
        longitude REAL
    )
    ''')
    
    # Analytics Events
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS analytics_events (
        id {pk_type},
        session_id TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        event_type TEXT,
        details TEXT
    )
    ''')

    conn.commit()
    
    # --- SEED DATA (If Empty) ---
    print("Checking if database needs seeding...")
    # Use alias 'inc' (item count) to be safe across drivers
    cursor.execute("SELECT COUNT(*) as inc FROM representatives")
    count_res = cursor.fetchone()
    
    # Handle PG vs SQLite return type
    try:
        if is_postgres:
            count = count_res['inc']
        else:
             # SQLite Row object supports dict-like access or index
             count = count_res['inc'] if 'inc' in count_res.keys() else count_res[0]
    except Exception as e:
        print(f"Error reading count: {e}. Defaulting to 0 to attempt seed.")
        count = 0

    print(f"Current representative count: {count}")

    if count == 0:
        print("Seeding database with initial representatives...")
        rps = [
            (
                "Narendra Modi", "Prime Minister", "BJP", "Varanasi", "Uttar Pradesh",
                "India's 14th Prime Minister, focus on economic development and national security. Led BJP to third consecutive term in 2024. Launched initiatives like PM Awas Yojana (Housing).",
                10, 50.5, 50.5, 98,
                '["3rd Term as PM", "G20 Presidency", "Digital India Expansion"]',
                "https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Prime_Minister_Narendra_Modi_in_New_Delhi_on_June_09%2C_2024_%28cropeed%29.jpg/440px-Prime_Minister_Narendra_Modi_in_New_Delhi_on_June_09%2C_2024_%28cropeed%29.jpg",
                '[{"headline": "PM Modi inaugurates new infrastructure projects", "date": "2024-12-20"}, {"headline": "Address to the nation on Republic Day", "date": "2025-01-26"}]',
                '["PMO India", "The Hindu", "ANI"]'
            ),
            (
                "Rahul Gandhi", "Leader of Opposition", "INC", "Rae Bareli", "Uttar Pradesh",
                "Leader of the Opposition in Lok Sabha (2024-). Spearheaded Bharat Jodo Yatra. Focus on social justice and caste census advocacy. Won from Wayanad and Rae Bareli in 2024.",
                20, 12.0, 15.0, 85,
                '["Bharat Jodo Yatra", "Leader of Opposition 2024", "Caste Census Advocacy"]',
                "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Rahul_Gandhi_2024.jpg/440px-Rahul_Gandhi_2024.jpg",
                '[{"headline": "Rahul Gandhi speaks on unemployment in Lok Sabha", "date": "2024-12-15"}, {"headline": "Bharat Jodo Nyay Yatra concludes", "date": "2024-03-20"}]',
                '["INC India", "The Indian Express", "NDTV"]'
            ),
            (
                "Amit Shah", "Home Minister", "BJP", "Gandhinagar", "Gujarat",
                "Union Home Minister and Minister of Cooperation. Key strategist for BJP. Oversaw abrogation of Article 370 and new criminal laws. Longest serving Home Minister.",
                5, 25.0, 25.0, 92,
                '["Abrogation of Article 370", "New Criminal Laws", "Cooperation Ministry"]',
                "https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Amit_Shah_in_New_Delhi_on_June_09%2C_2024_%28cropped%29.jpg/440px-Amit_Shah_in_New_Delhi_on_June_09%2C_2024_%28cropped%29.jpg",
                '[{"headline": "Amit Shah reviews security situation in J&K", "date": "2024-12-22"}, {"headline": "New criminal laws to be implemented", "date": "2024-07-01"}]',
                '["MHA", "Times of India", "News18"]'
            ),
            (
                "Shashi Tharoor", "MP", "INC", "Thiruvananthapuram", "Kerala",
                "Diplomat, author, and politician. Chairman of Parliamentary Committee on External Affairs. Former UN Under-Secretary-General. Known for literary works and articulate speeches.",
                15, 8.5, 10.0, 90,
                '["Sahitya Akademi Award", "Chairman External Affairs", "Diplomatic Service"]',
                "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Shashi_Tharoor_in_2024_%28cropped%29.jpg/440px-Shashi_Tharoor_in_2024_%28cropped%29.jpg",
                '[{"headline": "Tharoor discusses foreign policy challenges", "date": "2024-11-10"}, {"headline": "Launch of new book on Indian politics", "date": "2024-10-05"}]',
                '["Shashi Tharoor Official", "The Print", "Hindustan Times"]'
            ) 
        ]
        
        # Postgres uses %s, SQLite uses ?
        if is_postgres:
            insert_sql = """
            INSERT INTO representatives (name, role, party, constituency, state, bio, years_in_office, funds_spent_crores, funds_total_crores, attendance_percentage, achievements, image_url, news, sources)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
        else:
            insert_sql = """
            INSERT INTO representatives (name, role, party, constituency, state, bio, years_in_office, funds_spent_crores, funds_total_crores, attendance_percentage, achievements, image_url, news, sources)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
        for rp in rps:
            cursor.execute(insert_sql, rp)
            
        conn.commit()
        print("Seeding complete.")

    else:
        # Patch Update: Ensure Real Representatives exist and have rich data
        print("Verifying core representatives...")
        
        # FORCE CLEANUP: Remove broken dummy data (empty party, etc) to ensure clean demo
        try:
            # Delete entries where party is missing or empty, which causes the UI bug
            cursor.execute("DELETE FROM representatives WHERE party IS NULL OR party = ''")
            conn.commit()
            print("Cleaned up broken/dummy data.")
        except Exception as e:
            print(f"Cleanup warning: {e}")

        # We'll define the core reps with their full data
        core_reps = [
            (
                "Narendra Modi", "Prime Minister", "BJP", "Varanasi", "Uttar Pradesh",
                "India's 14th Prime Minister, focus on economic development and national security. Led BJP to third consecutive term in 2024. Launched initiatives like PM Awas Yojana (Housing).",
                10, 50.5, 50.5, 98,
                '["3rd Term as PM", "G20 Presidency", "Digital India Expansion"]',
                "https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Prime_Minister_Narendra_Modi_in_New_Delhi_on_June_09%2C_2024_%28cropeed%29.jpg/440px-Prime_Minister_Narendra_Modi_in_New_Delhi_on_June_09%2C_2024_%28cropeed%29.jpg",
                '[{"headline": "PM Modi inaugurates new infrastructure projects", "date": "2024-12-20"}, {"headline": "Address to the nation on Republic Day", "date": "2025-01-26"}]',
                '["PMO India", "The Hindu", "ANI"]'
            ),
            (
                "Rahul Gandhi", "Leader of Opposition", "INC", "Rae Bareli", "Uttar Pradesh",
                "Leader of the Opposition in Lok Sabha (2024-). Spearheaded Bharat Jodo Yatra. Focus on social justice and caste census advocacy. Won from Wayanad and Rae Bareli in 2024.",
                20, 12.0, 15.0, 85,
                '["Bharat Jodo Yatra", "Leader of Opposition 2024", "Caste Census Advocacy"]',
                "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Rahul_Gandhi_2024.jpg/440px-Rahul_Gandhi_2024.jpg",
                '[{"headline": "Rahul Gandhi speaks on unemployment in Lok Sabha", "date": "2024-12-15"}, {"headline": "Bharat Jodo Nyay Yatra concludes", "date": "2024-03-20"}]',
                '["INC India", "The Indian Express", "NDTV"]'
            ),
            (
                "Amit Shah", "Home Minister", "BJP", "Gandhinagar", "Gujarat",
                "Union Home Minister and Minister of Cooperation. Key strategist for BJP. Oversaw abrogation of Article 370 and new criminal laws. Longest serving Home Minister.",
                5, 25.0, 25.0, 92,
                '["Abrogation of Article 370", "New Criminal Laws", "Cooperation Ministry"]',
                "https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Amit_Shah_in_New_Delhi_on_June_09%2C_2024_%28cropped%29.jpg/440px-Amit_Shah_in_New_Delhi_on_June_09%2C_2024_%28cropped%29.jpg",
                '[{"headline": "Amit Shah reviews security situation in J&K", "date": "2024-12-22"}, {"headline": "New criminal laws to be implemented", "date": "2024-07-01"}]',
                '["MHA", "Times of India", "News18"]'
            ),
            (
                "Shashi Tharoor", "MP", "INC", "Thiruvananthapuram", "Kerala",
                "Diplomat, author, and politician. Chairman of Parliamentary Committee on External Affairs. Former UN Under-Secretary-General. Known for literary works and articulate speeches.",
                15, 8.5, 10.0, 90,
                '["Sahitya Akademi Award", "Chairman External Affairs", "Diplomatic Service"]',
                "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Shashi_Tharoor_in_2024_%28cropped%29.jpg/440px-Shashi_Tharoor_in_2024_%28cropped%29.jpg",
                '[{"headline": "Tharoor discusses foreign policy challenges", "date": "2024-11-10"}, {"headline": "Launch of new book on Indian politics", "date": "2024-10-05"}]',
                '["Shashi Tharoor Official", "The Print", "Hindustan Times"]'
            )
        ]

        if is_postgres:
            check_sql = "SELECT id FROM representatives WHERE name = %s"
            insert_sql = """
            INSERT INTO representatives (name, role, party, constituency, state, bio, years_in_office, funds_spent_crores, funds_total_crores, attendance_percentage, achievements, image_url, news, sources)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            update_sql = "UPDATE representatives SET image_url = %s, news = %s, sources = %s WHERE name = %s"
        else:
            check_sql = "SELECT id FROM representatives WHERE name = ?"
            insert_sql = """
            INSERT INTO representatives (name, role, party, constituency, state, bio, years_in_office, funds_spent_crores, funds_total_crores, attendance_percentage, achievements, image_url, news, sources)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            update_sql = "UPDATE representatives SET image_url = ?, news = ?, sources = ? WHERE name = ?"

        for rp in core_reps:
            name = rp[0]
            cursor.execute(check_sql, (name,))
            existing = cursor.fetchone()
            
            if existing:
                # Update with new rich data if it exists
                # indices: 11=image_url, 12=news, 13=sources. name is 0.
                cursor.execute(update_sql, (rp[11], rp[12], rp[13], name))
            else:
                # Insert
                cursor.execute(insert_sql, rp)
                
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
    cursor.execute(f"SELECT COUNT(*) as count FROM user_sessions WHERE {date_q}")
    new_users = cursor.fetchone()['count'] if is_postgres else cursor.fetchone()[0]
    
    # 2. Avg Session Duration
    cursor.execute(f"SELECT AVG(duration_seconds) as avg FROM user_sessions WHERE {date_q}")
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
