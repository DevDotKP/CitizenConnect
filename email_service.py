import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime
from database import get_daily_stats
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
RECIPIENT_EMAIL = "dev.kp271828@gmail.com" # Updated to assumed format or just use the user provided handle

def send_daily_report():
    from database import get_daily_stats, get_advanced_stats
    stats = get_daily_stats()
    adv_stats = get_advanced_stats()
    
    # 1. Generate Report
    today = datetime.now().strftime("%Y-%m-%d")
    subject = f"CitizenConnect Daily Analytics Report - {today}"
    
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; }}
            .header {{ background-color: #6C63FF; color: white; padding: 15px; text-align: center; }}
            .stat-box {{ border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
            .highlight {{ color: #6C63FF; font-weight: bold; font-size: 1.2em; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>CitizenConnect Analytics</h2>
            <p>{today}</p>
        </div>
        
        <div class="stat-box">
            <p>New Users Today: <span class="highlight">{stats['new_users']}</span></p>
            <p>Average Session Duration: <span class="highlight">{stats['avg_duration']}s</span></p>
        </div>
        
        <div class="stat-box">
            <h3>Top Actions</h3>
            <ul>
                {"".join([f"<li>{x['event_type']}: {x['count']}</li>" for x in stats['top_actions']])}
            </ul>
        </div>

        <div class="stat-box">
            <h3>Geographic Distribution</h3>
            <ul>
                 {"".join([f"<li>{x['location']}: {x['count']}</li>" for x in adv_stats['top_locations']])}
            </ul>
        </div>
        
        <div class="stat-box">
            <h3>Top Drop-off Points</h3>
            <ul>
                 {"".join([f"<li>{x['event_type']}: {x['count']}</li>" for x in adv_stats['drop_offs']])}
            </ul>
        </div>
        
        <p><small>This is an automated message from your Admin Dashboard.</small></p>
    </body>
    </html>
    """
    
    # 2. Send Email
    if not SMTP_USER or not SMTP_PASSWORD:
        print("--- [MOCK EMAIL SENT] ---")
        print(f"To: {RECIPIENT_EMAIL}")
        print(f"Subject: {subject}")
        print("Body: (HTML content hidden for brevity)")
        print("--- End Mock Email ---")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(html_content, 'html'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Daily report email sent to {RECIPIENT_EMAIL}")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    send_daily_report()
