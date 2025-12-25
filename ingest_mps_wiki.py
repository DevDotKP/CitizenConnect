import requests
from bs4 import BeautifulSoup
import os
import psycopg2
from dotenv import load_dotenv

# Load env to get DATABASE_URL
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("Error: DATABASE_URL not found in .env")
    exit(1)

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def scrape_wikipedia():
    url = "https://en.wikipedia.org/wiki/List_of_members_of_the_18th_Lok_Sabha"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    print(f"Fetching {url}...")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch page: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    
    mps = []
    
    # The page usually separates MPs by state in headers (h2 or h3) followed by a table
    # Or one giant table. 
    # Current structure of "List of members of the 18th Lok Sabha":
    # It lists states sections and then tables.
    
    # Let's find all tables with class 'wikitable'
    tables = soup.find_all('table', {'class': 'wikitable'})
    
    print(f"Found {len(tables)} tables.")
    
    for table in tables:
        # Try to identify state from the preceding header
        # This is heuristics based.
        # Alternatively, sometimes the state is in the table or the table is just the list.
        # On this specific page, tables usually correspond to states or "Nominated".
        
        # Iterating rows
        rows = table.find_all('tr')
        if not rows: 
            continue
            
        # Check headers to see if it looks like an MP list
        headers = [th.text.strip().lower() for th in rows[0].find_all('th')]
        
        # We look for "constituency", "name" or "member", "party"
        has_constituency = any("constituency" in h for h in headers)
        has_name = any("member" in h or "name" in h for h in headers)
        
        if not has_constituency or not has_name:
            continue

        # Map column indices
        idx_const = -1
        idx_name = -1
        idx_party = -1
        
        for i, h in enumerate(headers):
            if "constituency" in h: idx_const = i
            elif "member" in h or "name" in h: idx_name = i
            elif "party" in h: idx_party = i
            
        if idx_const == -1 or idx_name == -1:
            continue
            
        # State inference: usually the heading before the table
        state_name = "Unknown"
        prev = table.find_previous(['h2', 'h3', 'h4'])
        if prev:
            state_name = prev.text.strip().replace('[edit]', '')

        for row in rows[1:]:
            cols = row.find_all(['td', 'th'])
            # Sometimes 1st col is number, so we use mapped indices
            # But indices from th might not match td if there are rowspans. 
            # Wikipedia tables are tricky with rowspans (usually for Party or State).
            # For 18th Lok Sabha page, usually simple tables per state.
            
            if len(cols) <= max(idx_const, idx_name, idx_party):
                continue
                
            try:
                constituency = cols[idx_const].text.strip()
                name = cols[idx_name].text.strip()
                party = cols[idx_party].text.strip() if idx_party != -1 else "Unknown"
                
                # Cleanup
                if "[" in name: name = name.split("[")[0]
                if "[" in party: party = party.split("[")[0]
                
                mps.append({
                    "name": name,
                    "constituency": constituency,
                    "party": party,
                    "state": state_name,
                    "role": "MP (Lok Sabha)"
                })
            except Exception as e:
                # print(f"Skipping row: {e}")
                pass

    print(f"Scraped {len(mps)} MPs.")
    return mps

def ingest_data(mps):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("Inserting data into database...")
    count = 0
    for mp in mps:
        try:
            # Check if exists (by name and constituency)
            cursor.execute("SELECT id FROM representatives WHERE name = %s AND constituency = %s", (mp['name'], mp['constituency']))
            if cursor.fetchone():
                continue
                
            cursor.execute("""
                INSERT INTO representatives (name, role, party, constituency, state, bio, years_in_office, funds_spent_crores, funds_total_crores, attendance_percentage)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                mp['name'], 
                mp['role'], 
                mp['party'], 
                mp['constituency'], 
                mp['state'], 
                "Member of the 18th Lok Sabha", 
                0, 0.0, 5.0, 0
            ))
            count += 1
        except Exception as e:
            print(f"Error inserting {mp['name']}: {e}")
            conn.rollback()
    
    conn.commit()
    conn.close()
    print(f"Inserted {count} new MPs.")

if __name__ == "__main__":
    from database import init_db
    print("Initializing Database Schema...")
    init_db()
    
    data = scrape_wikipedia()
    if data:
        ingest_data(data)
