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
load_dotenv()
GOOGLE_API_KEY = get_secret("GOOGLE_API_KEY")

client = genai.Client(api_key=GOOGLE_API_KEY)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        init_db()
    except Exception as e:
        print(f"Startup DB Error: {e}")
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
    return client.models.generate_content(
        model='gemini-1.5-flash',
        contents=prompt
    )

# --- API Endpoints ---

@app.get("/api/representatives")
def get_representatives(search: Optional[str] = None):
    if search:
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
        # Note: New SDK exception handling might be different, but retry wrapper catches general exceptions
        
        # Check if response text is accessible directly
        if hasattr(response, 'text') and response.text:
             ai_text = response.text
        else:
             # Fallback if structure is different
             ai_text = "I'm having trouble thinking right now."

        chat_id = save_chat_interaction(request.query, ai_text)
        return {"response": ai_text, "chat_id": chat_id}

    except Exception as e:
        print(f"Gemini Error: {e}")
        return {"response": "I'm currently receiving too many requests. Please try again in a minute.", "chat_id": 0}

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
