import os
import uvicorn
import requests
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Optional, List
from google import genai
from apscheduler.schedulers.background import BackgroundScheduler
from database import (
    get_all_representatives, 
    get_representative_by_location, 
    save_chat_interaction, 
    update_chat_rating, 
    get_high_quality_chats,
    create_session,
    update_session_heartbeat,
    log_analytics_event,
    get_daily_stats,
    get_advanced_stats,
    get_recent_chats
)
from email_service import send_daily_report
from security_utils import get_secret
from dotenv import load_dotenv
import json
import bcrypt
import secrets
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# --- Scheduler ---
scheduler = BackgroundScheduler()

# --- Config ---

# --- Config ---
load_dotenv()
GOOGLE_API_KEY = get_secret("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("CRITICAL WARNING: GOOGLE_API_KEY is not set. Chatbot will fail.")
    client = None
else:
    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
    except Exception as e:
        print(f"Error initializing Gemini Client: {e}")
        client = None

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from email_service import send_daily_report
from geopy.geocoders import Nominatim
from database import get_db_connection

# Initialize Scheduler
scheduler = AsyncIOScheduler()
geolocator = Nominatim(user_agent="citizen_connect_app")

# Global Context
MP_CONTEXT = ""

def load_mp_context():
    global MP_CONTEXT
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT name, constituency, state, party FROM representatives")
        mps = cur.fetchall()
        
        context_list = []
        for mp in mps:
            context_list.append(f"{mp['name']} ({mp['party']}) - {mp['constituency']}, {mp['state']}")
            
        MP_CONTEXT = "List of 18th Lok Sabha MPs:\n" + "\n".join(context_list)
        print(f"Loaded {len(mps)} MPs into context.")
        conn.close()
    except Exception as e:
        print(f"Error loading MP context: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        init_db()
        load_mp_context()
        
        # Schedule Daily Report at 8:45 AM IST (03:15 UTC) [TEMPORARY FOR TODAY]
        # IST is UTC+5:30. 8:45 AM IST = 03:15 AM UTC.
        scheduler.add_job(send_daily_report, 'cron', hour=3, minute=15)
        scheduler.start()
        print("Scheduler started. Daily email set for 03:15 UTC (8:45 AM IST).")
        
    except Exception as e:
        print(f"Startup Error: {e}")
    yield
    # Shutdown
    # (Optional: close connections if needed, though usually handled per request)

app = FastAPI(lifespan=lifespan)
security = HTTPBasic()

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = get_secret("ADMIN_USERNAME")
    stored_hash = os.getenv("ADMIN_PASSWORD_HASH") # Expects bcrypt hash
    
    if not correct_username or not stored_hash:
        # Fallback or Fail Safe
        print("Admin configuration missing")
        raise HTTPException(status_code=500, detail="Admin configuration missing")

    is_correct_username = secrets.compare_digest(credentials.username, correct_username)
    
    # Verify password against hash
    is_correct_password = False
    try:
        if bcrypt.checkpw(credentials.password.encode('utf-8'), stored_hash.encode('utf-8')):
            is_correct_password = True
    except Exception as e:
        print(f"Auth Error: {e}")

    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# --- Models ---
class ChatRequest(BaseModel):
    query: str
    context_rep_id: Optional[int] = None

class RatingRequest(BaseModel):
    chat_id: int
    rating: int

class AnalyticsEvent(BaseModel):
    session_id: str
    event_type: str
    details: Optional[str] = ""

class AnalyticsHeartbeat(BaseModel):
    session_id: str

# --- Helpers ---
def get_location_from_ip(ip):
    if ip in ["127.0.0.1", "::1"]:
        return "Localhost, Dev", 20.5937, 78.9629 # Mock (India center)
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}", timeout=2)
        if res.status_code == 200:
            data = res.json()
            if data['status'] == 'success':
                loc_str = f"{data['city']}, {data['country']}"
                return loc_str, data['lat'], data['lon']
    except:
        pass
    return "Unknown", None, None

# Helper for Retry
@retry(
    stop=stop_after_attempt(3), 
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry_error_callback=lambda retry_state: "RateLimitExceeded"
)
def generate_gemini_response(prompt):
    system_instruction = """
    You are CitizenConnect AI, an expert on Indian politics and civic duties.
    
    RULES:
    1. Your knowledge is based on the provided list of 18th Lok Sabha MPs.
    2. STRICTLY ANSWER ONLY questions related to Indian representatives (MPs/MLAs), the CitizenConnect website, government schemes, or civic rights.
    3. If asked about unrelated topics (e.g., "height of Mount Everest", "movie recommendations"), POLITELY REFUSE and gently steer the user back to civic topics.
    4. Provide factual, concise answers.
    5. At the very end of your response, provide a list of 3 suggested follow-up questions in this JSON-like format: 
       SUGGESTIONS: ["Question 1", "Question 2", "Question 3"]
    """
    
    full_prompt = f"{system_instruction}\n\nCONTEXT:\n{MP_CONTEXT}\n\nUSER QUERY: {prompt}"
    
    return client.models.generate_content(
        model='gemini-1.5-flash',
        contents=full_prompt
    )

# --- API Endpoints ---

# --- Helpers for Dynamic Data ---
def fetch_dynamic_local_reps(location_str):
    """
    Uses Gemini to find the current MLA and Councillor for a specific location.
    Returns a dict with 'mla' and 'councillor'.
    """
    if not client:
        return None
        
    try:
        prompt = f"""
        I need the current Member of Legislative Assembly (MLA) and Municipal Councillor for: {location_str}, India.
        Return strictly a JSON object with keys: "mla_name", "mla_party", "councillor_name", "councillor_party".
        If unknown, use "Unknown". Do not add markdown.
        """
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt
        )
        if response.text:
            cleaned = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(cleaned)
    except Exception as e:
        print(f"Dynamic Fetch Error: {e}")
    return None

# --- API Endpoints ---

@app.get("/api/representatives")
def get_representatives(search: Optional[str] = None):
    if search:
        # Check for PIN Code (6 digits)
        if search.isdigit() and len(search) == 6:
            try:
                location = geolocator.geocode(search + ", India")
                if location:
                    # Use the address to find MP
                    # Nominatim address dict is complex, but display_name is usually "Area, City, State, PIN, Country"
                    print(f"PIN Resolved: {location.address}")
                    address_parts = location.address.split(",")
                    # Try searching interesting parts (District/State)
                    # For simplicity, we search the whole address string or key parts
                    terms = [term.strip() for term in address_parts]
                    
                    # Try finding rep by district/city (terms before state)
                    # This is heuristical.
                    found_reps = []
                    conn = get_db_connection()
                    cur = conn.cursor()
                    
                    for term in terms:
                         cur.execute("SELECT * FROM representatives WHERE constituency ILIKE %s OR state ILIKE %s", (f"%{term}%", f"%{term}%"))
                         rows = cur.fetchall()
                         if rows:
                             found_reps.extend([dict(row) for row in rows])
                             
                    conn.close()
                    
                    # Deduplicate by ID
                    seen = set()
                    unique_reps = []
                    for r in found_reps:
                        if r['id'] not in seen:
                            unique_reps.append(r)
                            seen.add(r['id'])
                            
                    return unique_reps
            except Exception as e:
                print(f"PIN Search Error: {e}")

        return get_representative_by_location(search)
    return get_all_representatives()

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    if not client:
         raise HTTPException(status_code=500, detail="AI Service Config Missing")

    context_str = ""
    reps = get_all_representatives()
    context_str += "Reps:\n"
    for rep in reps:
        context_str += f"- {rep['name']} ({rep['role']}, {rep['party']}) from {rep['constituency']}, {rep['state']}. Bio: {rep['bio']}\n"
    
    good_chats = get_high_quality_chats()
    examples_str = ""
    if good_chats:
        examples_str = "Examples:\n"
        for chat in good_chats:
            examples_str += f"User: {chat['user_query']}\nYou: {chat['ai_response']}\n\n"

    system_prompt = f"""
    You are 'CitizenConnect', a helpful assistant for Indian citizens.
    Data: {context_str}
    {examples_str}
    Be concise, helpful, and non-partisan.
    """
    
    full_prompt = f"{system_prompt}\n\nUser: {request.query}\nResponse:"

    try:
        response = generate_gemini_response(full_prompt)
        
        # Debugging: Print full response to logs
        print(f"DEBUG: Gemini Response: {response}")

        # Check for Safety/Other Blocks (Candidates logic)
        if hasattr(response, 'candidates') and response.candidates:
            first_candidate = response.candidates[0]
            if hasattr(first_candidate, 'finish_reason') and first_candidate.finish_reason != "STOP":
                 print(f"DEBUG: Finish Reason: {first_candidate.finish_reason}")
                 if "SAFETY" in str(first_candidate.finish_reason):
                     return {"response": "I cannot answer this question as it may violate safety guidelines.", "chat_id": 0}

        # Check for Prompt Feedback (Blocked before candidates)
        if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
            pf = response.prompt_feedback
            if hasattr(pf, 'block_reason') and pf.block_reason:
                print(f"DEBUG: Prompt Feedback Block: {pf.block_reason}")
                return {"response": f"Input info blocked. Reason: {pf.block_reason}", "chat_id": 0}

        # Check if response text is accessible directly
        if hasattr(response, 'text') and response.text:
             ai_text = response.text
        else:
             # Try to extract text from parts if .text helper failed but parts exist
             try:
                 if hasattr(response, 'candidates') and response.candidates:
                     parts = response.candidates[0].content.parts
                     if parts:
                         ai_text = "".join([p.text for p in parts if hasattr(p, 'text')])
                     else:
                         reason = response.candidates[0].finish_reason if hasattr(response.candidates[0], 'finish_reason') else 'Unknown'
                         ai_text = f"No content generated. (Finish Reason: {reason})"
                 else:
                     # Check if it was prompt feedback blocked (handled above, but fallback)
                     if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                         ai_text = f"Request blocked. {response.prompt_feedback}"
                     else:
                         ai_text = "Empty response from AI service."
             except Exception as e:
                 print(f"Error parsing fallback: {e}")
                 ai_text = "I'm having trouble processing the AI response structure."

        chat_id = save_chat_interaction(request.query, ai_text)
        return {"response": ai_text, "chat_id": chat_id}

    except Exception as e:
        print(f"Gemini Error: {e}")
        error_msg = str(e)
        if "429" in error_msg:
             return {"response": "I'm currently receiving too many requests. Please try again in a minute.", "chat_id": 0}
        elif "401" in error_msg or "API key" in error_msg or "Unauthenticated" in error_msg:
             return {"response": "Configuration Error: API Key missing or invalid. Please check server logs.", "chat_id": 0}
        else:
             return {"response": f"I encountered an error: {error_msg}. Please try again.", "chat_id": 0}

@app.post("/api/feedback")
def feedback_endpoint(request: RatingRequest):
    update_chat_rating(request.chat_id, request.rating)
    return {"status": "success"}

# --- Analytics Endpoints ---

@app.post("/api/analytics/heartbeat")
def heartbeat(request: AnalyticsHeartbeat, req: Request):
    ip = req.client.host
    user_agent = req.headers.get('user-agent')
    # Resolve location
    location, lat, lon = get_location_from_ip(ip)

    create_session(request.session_id, ip, user_agent, location, lat, lon)
    update_session_heartbeat(request.session_id)
    return {"status": "ok"}

@app.post("/api/analytics/event")
def track_event(request: AnalyticsEvent):
    log_analytics_event(request.session_id, request.event_type, request.details)
    return {"status": "ok"}

@app.get("/api/admin/stats")
def get_stats(username: str = Depends(verify_admin)):
    daily = get_daily_stats()
    advanced = get_advanced_stats()
    chats = get_recent_chats()
    # Merge dicts
    return {**daily, **advanced, "recent_chats": chats}

@app.post("/api/admin/login")
def login(username: str = Depends(verify_admin)):
    return {"status": "logged_in", "username": username}

@app.get("/healthChecker")
def health_check():
    return {"status": "ok"}

@app.get("/api/test-email")
async def test_email_endpoint():
    success = await send_daily_report()
    if success:
        return {"status": "success", "message": "Email sent"}
    return {"status": "error", "message": "Failed to send email"}

@app.post("/api/detect-location")
async def detect_location(request: Request):
    data = await request.json()
    lat = data.get("latitude")
    lon = data.get("longitude")
    
    if not lat or not lon:
        return {"status": "error", "message": "Missing coordinates"}
        
    try:
        # Reverse geocode to get address
        location = geolocator.reverse((lat, lon), language='en')
        address = location.raw.get('address', {})
        state = address.get('state', '')
        district = address.get('state_district', '') or address.get('county', '')
        location_str = f"{district}, {state}"
        
        # Simple heuristic mapping: Try to find MP by district or state
        # In a real app, we need a shapefile mapper. For now, we search the DB.
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Try finding constituency matches (fuzzy or direct)
        mp_info = None
        
        # 1. Search by district name as constituency
        if district:
             district_clean = district.replace("District", "").strip()
             cur.execute("SELECT * FROM representatives WHERE constituency ILIKE %s", (f"%{district_clean}%",))
             mp_info = cur.fetchone()
             
        # 2. If not found, just return state info
        if not mp_info and state:
             cur.execute("SELECT * FROM representatives WHERE state ILIKE %s LIMIT 1", (f"%{state}%",))
             mp_info = cur.fetchone()
             
        conn.close()
        
        # Dynamic Fetch for MLA/Councillor
        local_reps = fetch_dynamic_local_reps(location_str)
        
        if mp_info:
            response_data = {
                "status": "success",
                "location": location_str,
                "mp": {
                    "name": mp_info['name'],
                    "constituency": mp_info['constituency'],
                    "party": mp_info['party'],
                    "state": mp_info['state']
                },
                "message": f"You are in {state}. Your likely representative context found."
            }
        else:
            response_data = {"status": "success", "location": location_str, "message": "No specific MP found for this location yet."}
            
        if local_reps:
            response_data['local_reps'] = local_reps
            
        return response_data
            
    except Exception as e:
        print(f"Location Error: {e}")
        return {"status": "error", "message": str(e)}

# --- Static Files ---
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

@app.get("/admin")
async def read_admin():
    return FileResponse('static/admin.html')

# Initialize DB on import to ensure tables exist
from database import init_db

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
