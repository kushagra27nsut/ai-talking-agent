"""
XCER AI Talking Agent - FastAPI Backend with Twilio Integration
================================================================
Handles web API requests AND real phone calls via Twilio
"""

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from typing import Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
import uvicorn
import logging

# Twilio imports
try:
    from twilio.twiml.voice_response import VoiceResponse, Gather
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    print("⚠️ Twilio not installed. Run: pip install twilio")

# Import agent functions
from agent import get_response, listen, speak, reset_conversation, is_ai_available

# Import configuration
try:
    from config import (
        TWILIO_ACCOUNT_SID,
        TWILIO_AUTH_TOKEN,
        TWILIO_PHONE_NUMBER,
        SERVER_HOST,
        SERVER_PORT,
        PUBLIC_URL
    )
except ImportError:
    TWILIO_ACCOUNT_SID = "YOUR_TWILIO_ACCOUNT_SID"
    TWILIO_AUTH_TOKEN = "YOUR_TWILIO_AUTH_TOKEN"
    TWILIO_PHONE_NUMBER = "+1234567890"
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = 8080
    PUBLIC_URL = "https://your-ngrok-url.ngrok.io"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="XCER AI Talking Agent API",
    description="Backend API with Gemini AI and Twilio Phone Call Integration",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thread pool for blocking operations
executor = ThreadPoolExecutor(max_workers=5)

# Twilio client
twilio_client = None
if TWILIO_AVAILABLE and TWILIO_ACCOUNT_SID != "YOUR_TWILIO_ACCOUNT_SID":
    try:
        twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        logger.info("✅ Twilio client initialized!")
    except Exception as e:
        logger.error(f"Twilio init error: {e}")

# Store conversation states for phone calls
call_conversations = {}

# ==================== Request/Response Models ====================

class TextInput(BaseModel):
    text: str

class AudioResponse(BaseModel):
    status: str
    recognized_text: Optional[str] = None
    error: Optional[str] = None

class ChatResponse(BaseModel):
    user_input: str
    agent_reply: str
    status: str

class TTSResponse(BaseModel):
    status: str
    message: str
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    message: str
    version: str

class CallRequest(BaseModel):
    to_number: str
    message: Optional[str] = None

# ==================== Health & Info Endpoints ====================

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="success",
        message="XCER AI Talking Agent API is running",
        version="2.0.0"
    )

@app.get("/health")
async def health():
    """Health status with feature availability"""
    return {
        "status": "healthy",
        "service": "XCER AI Talking Agent",
        "version": "2.0.0",
        "features": {
            "groq_ai": is_ai_available(),
            "twilio": TWILIO_AVAILABLE and twilio_client is not None,
            "speech_recognition": True,
            "text_to_speech": True
        }
    }

@app.get("/info")
async def get_info():
    """Get API information"""
    return {
        "name": "XCER AI Talking Agent API",
        "version": "2.0.0",
        "team": "XCER - IEEE NSUT",
        "description": "AI Voice Agent with Twilio Phone Integration",
        "endpoints": {
            "Web API": {
                "GET /": "Health check",
                "GET /health": "Feature status",
                "POST /chat": "Chat with AI",
                "POST /listen": "Speech recognition",
                "POST /speak": "Text-to-speech"
            },
            "Twilio Phone": {
                "POST /twilio/voice": "Handle incoming calls",
                "POST /twilio/gather": "Process speech input",
                "POST /twilio/call": "Make outbound call"
            }
        }
    }

# ==================== Web Chat Endpoints ====================

@app.post("/listen", response_model=AudioResponse)
async def listen_endpoint():
    """Listen to microphone and recognize speech"""
    loop = asyncio.get_event_loop()
    try:
        text = await loop.run_in_executor(executor, listen)
        
        if text:
            return AudioResponse(status="success", recognized_text=text)
        else:
            return AudioResponse(status="error", error="Could not recognize audio")
    except Exception as e:
        logger.error(f"Listen error: {e}")
        return AudioResponse(status="error", error=str(e))

@app.post("/process", response_model=ChatResponse)
async def process_input(request: TextInput):
    """Process text input and get AI response"""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        reply = get_response(request.text)
        return ChatResponse(
            user_input=request.text,
            agent_reply=reply or "I couldn't generate a response",
            status="success"
        )
    except Exception as e:
        logger.error(f"Process error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/speak", response_model=TTSResponse)
async def speak_endpoint(request: TextInput):
    """Convert text to speech"""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    loop = asyncio.get_event_loop()
    try:
        success = await loop.run_in_executor(executor, speak, request.text)
        
        if success:
            return TTSResponse(status="success", message="Text spoken successfully")
        else:
            return TTSResponse(status="error", message="TTS failed", error="Engine error")
    except Exception as e:
        logger.error(f"Speak error: {e}")
        return TTSResponse(status="error", message="Failed", error=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: TextInput):
    """Main chat endpoint - process text and return AI response"""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        reply = get_response(request.text)
        return ChatResponse(
            user_input=request.text,
            agent_reply=reply or "I couldn't generate a response",
            status="success"
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/interact")
async def interact_endpoint(request: TextInput):
    """Full interaction: process input, get response, and speak it"""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        reply = get_response(request.text)
        loop = asyncio.get_event_loop()
        speak_success = await loop.run_in_executor(executor, speak, reply)
        
        return {
            "status": "success",
            "user_input": request.text,
            "agent_reply": reply,
            "spoken": speak_success
        }
    except Exception as e:
        logger.error(f"Interact error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== TWILIO PHONE CALL ENDPOINTS ====================

@app.post("/twilio/voice", response_class=PlainTextResponse)
async def twilio_voice_webhook(request: Request):
    """
    Twilio webhook for incoming phone calls
    This is called when someone calls your Twilio number
    """
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "unknown")
    caller = form_data.get("From", "unknown")
    
    logger.info(f"📞 Incoming call from {caller} (SID: {call_sid})")
    
    # Reset conversation for new call
    reset_conversation()
    call_conversations[call_sid] = []
    
    # Create TwiML response
    response = VoiceResponse()
    
    # Greet the caller
    response.say(
        "Hello! Welcome to XCER AI Agent. How can I help you today?",
        voice="Polly.Joanna",
        language="en-US"
    )
    
    # Gather speech input from caller
    gather = Gather(
        input="speech",
        action=f"{PUBLIC_URL}/twilio/gather",
        method="POST",
        speech_timeout="auto",
        language="en-US"
    )
    response.append(gather)
    
    # If no input, ask again
    response.say("I didn't hear anything. Please try again.")
    response.redirect(f"{PUBLIC_URL}/twilio/voice")
    
    return Response(content=str(response), media_type="application/xml")

@app.post("/twilio/gather", response_class=PlainTextResponse)
async def twilio_gather_webhook(request: Request):
    """
    Twilio webhook for processing gathered speech
    This is called after the caller speaks
    """
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "unknown")
    speech_result = form_data.get("SpeechResult", "")
    
    logger.info(f"🎤 Caller said: {speech_result}")
    
    # Get AI response
    ai_response = get_response(speech_result)
    logger.info(f"🤖 AI response: {ai_response}")
    
    # Store in conversation history
    if call_sid in call_conversations:
        call_conversations[call_sid].append({
            "user": speech_result,
            "agent": ai_response
        })
    
    # Create TwiML response
    response = VoiceResponse()
    
    # Check for goodbye
    if any(word in speech_result.lower() for word in ["bye", "goodbye", "quit", "exit", "hang up"]):
        response.say(
            "Thank you for calling XCER AI. Goodbye!",
            voice="Polly.Joanna"
        )
        response.hangup()
    else:
        # Speak the AI response
        response.say(ai_response, voice="Polly.Joanna", language="en-US")
        
        # Continue listening for more input
        gather = Gather(
            input="speech",
            action=f"{PUBLIC_URL}/twilio/gather",
            method="POST",
            speech_timeout="auto",
            language="en-US"
        )
        response.append(gather)
        
        # If no input, prompt again
        response.say("Is there anything else I can help with?")
        response.redirect(f"{PUBLIC_URL}/twilio/voice")
    
    return Response(content=str(response), media_type="application/xml")

@app.post("/twilio/call")
async def make_outbound_call(request: CallRequest):
    """
    Make an outbound phone call using Twilio
    The AI will speak to the person who answers
    """
    if not TWILIO_AVAILABLE or not twilio_client:
        raise HTTPException(status_code=503, detail="Twilio not configured")
    
    if not request.to_number:
        raise HTTPException(status_code=400, detail="Phone number required")
    
    try:
        # Create the call
        call = twilio_client.calls.create(
            to=request.to_number,
            from_=TWILIO_PHONE_NUMBER,
            url=f"{PUBLIC_URL}/twilio/outbound",
            method="POST"
        )
        
        logger.info(f"📱 Outbound call initiated to {request.to_number}")
        
        return {
            "status": "success",
            "message": f"Call initiated to {request.to_number}",
            "call_sid": call.sid
        }
    except Exception as e:
        logger.error(f"Outbound call error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/twilio/outbound", response_class=PlainTextResponse)
async def twilio_outbound_webhook(request: Request):
    """
    Twilio webhook for outbound calls
    This is the script for when someone answers your outbound call
    """
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "unknown")
    
    logger.info(f"📞 Outbound call answered (SID: {call_sid})")
    
    # Reset conversation
    reset_conversation()
    
    response = VoiceResponse()
    
    # Introduce the AI
    response.say(
        "Hello! This is XCER AI Agent calling. How can I assist you today?",
        voice="Polly.Joanna"
    )
    
    # Gather speech
    gather = Gather(
        input="speech",
        action=f"{PUBLIC_URL}/twilio/gather",
        method="POST",
        speech_timeout="auto",
        language="en-US"
    )
    response.append(gather)
    
    response.say("I didn't hear a response. Goodbye!")
    response.hangup()
    
    return Response(content=str(response), media_type="application/xml")

@app.get("/twilio/status")
async def twilio_status():
    """Check Twilio configuration status"""
    return {
        "twilio_available": TWILIO_AVAILABLE,
        "client_configured": twilio_client is not None,
        "phone_number": TWILIO_PHONE_NUMBER if twilio_client else None,
        "webhook_url": f"{PUBLIC_URL}/twilio/voice",
        "instructions": {
            "1": "Get Twilio account at https://www.twilio.com",
            "2": "Add credentials to config.py",
            "3": "Use ngrok to expose local server: ngrok http 8080",
            "4": "Set ngrok URL as PUBLIC_URL in config.py",
            "5": "Configure Twilio webhook to: {PUBLIC_URL}/twilio/voice"
        }
    }

# ==================== Run Server ====================

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 XCER AI Talking Agent Server")
    print("=" * 50)
    print(f"📡 Server: http://{SERVER_HOST}:{SERVER_PORT}")
    print(f"📚 API Docs: http://{SERVER_HOST}:{SERVER_PORT}/docs")
    print(f"🤖 Groq AI: {'✅ Ready' if is_ai_available() else '❌ Not configured'}")
    print(f"📞 Twilio: {'✅ Ready' if twilio_client else '❌ Not configured'}")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host=SERVER_HOST,
        port=SERVER_PORT,
        log_level="info"
    )
