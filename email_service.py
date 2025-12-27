import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime, timedelta
import psycopg2
from database import get_db_connection
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
ADMIN_EMAIL = "medha@example.com" # Replace with user's actual email if known, or use env var
TARGET_EMAIL = os.getenv("TARGET_EMAIL", SMTP_USER) # Default to sending to self if not specified

def get_daily_stats():
    """Fetch statistics for the past 24 hours."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    yesterday = datetime.now() - timedelta(days=1)
    
    # Total Chats
    cur.execute("SELECT COUNT(*) FROM chat_history WHERE timestamp > %s", (yesterday,))
    total_chats = cur.fetchone()['count']
    
    # Active Users (unique sessions)
    cur.execute("SELECT COUNT(DISTINCT session_id) FROM analytics_events WHERE timestamp > %s", (yesterday,))
    active_users = cur.fetchone()['count']
    
    # Top 5 Queries
    cur.execute("""
        SELECT user_query, COUNT(*) as freq 
        FROM chat_history 
        WHERE timestamp > %s 
        GROUP BY user_query 
        ORDER BY freq DESC 
        LIMIT 5
    """, (yesterday,))
    top_queries = cur.fetchall()
    
    conn.close()
    
    return {
        "total_chats": total_chats,
        "active_users": active_users,
        "top_queries": top_queries,
        "date": yesterday.strftime('%Y-%m-%d')
    }

def format_email_body(stats):
    body = f"""
    <h2>CitizenConnect Daily Report - {stats['date']}</h2>
    <p>Here is the summary of activity for the past 24 hours:</p>
    
    <ul>
        <li><strong>Total Chats:</strong> {stats['total_chats']}</li>
        <li><strong>Active Users:</strong> {stats['active_users']}</li>
    </ul>
    
    <h3>Top Queries:</h3>
    <ul>
    """
    for q in stats['top_queries']:
        body += f"<li>{q['user_query']} ({q['freq']} times)</li>"
        
    body += "</ul>"
    return body

async def send_daily_report():
    print("Generating daily report...")
    try:
        stats = get_daily_stats()
        html_body = format_email_body(stats)
        
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = TARGET_EMAIL
        msg['Subject'] = f"CitizenConnect Daily Analytics - {stats['date']}"
        
        msg.attach(MIMEText(html_body, 'html'))
        
        print(f"Connecting to SMTP: {SMTP_SERVER}:{SMTP_PORT}")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
            
        print("Daily report sent successfully.")
        return True
    except Exception as e:
        print(f"Failed to send daily report: {e}")
        return False
