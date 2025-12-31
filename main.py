from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
import uvicorn
import logging

# Import agent functions
from agent import get_response, listen, speak

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Talking Agent API",
    description="Backend API for AI talking agent with Google Speech Recognition",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thread pool for blocking operations
executor = ThreadPoolExecutor(max_workers=5)

# ==================== Request/Response Models ====================

class TextInput(BaseModel):
    """Model for text input"""
    text: str

class AudioResponse(BaseModel):
    """Model for audio recognition response"""
    status: str
    recognized_text: Optional[str] = None
    error: Optional[str] = None

class ChatResponse(BaseModel):
    """Model for chat response"""
    user_input: str
    agent_reply: str
    status: str

class TTSResponse(BaseModel):
    """Model for text-to-speech response"""
    status: str
    message: str
    error: Optional[str] = None

class HealthResponse(BaseModel):
    """Model for health check response"""
    status: str
    message: str
    version: str

# ==================== Health & Info Endpoints ====================

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="success",
        message="AI Talking Agent API is running",
        version="1.0.0"
    )

@app.get("/health")
async def health():
    """Health status endpoint"""
    return {
        "status": "healthy",
        "service": "AI Talking Agent",
        "version": "1.0.0"
    }

@app.get("/info")
async def get_info():
    """Get API information and available endpoints"""
    return {
        "name": "AI Talking Agent API",
        "version": "1.0.0",
        "description": "Backend API with Google Speech Recognition",
        "endpoints": {
            "GET /": "Health check",
            "GET /health": "Health status",
            "GET /info": "API information",
            "POST /listen": "Listen to audio and recognize speech (Google API)",
            "POST /process": "Process text and get AI response",
            "POST /speak": "Convert text to speech",
            "POST /chat": "Chat endpoint (combined process)",
        },
        "example_requests": {
            "/process": {"text": "hello"},
            "/speak": {"text": "Hello world"},
            "/chat": {"text": "What is your name?"}
        }
    }

# ==================== Speech Recognition Endpoint ====================

@app.post("/listen", response_model=AudioResponse)
async def listen_endpoint():
    """
    Listen to microphone input and recognize speech using Google Speech Recognition API
    
    Returns:
        AudioResponse: Recognized text or error message
    """
    loop = asyncio.get_event_loop()
    try:
        text = await loop.run_in_executor(executor, listen)
        
        if text:
            logger.info(f"Successfully recognized: {text}")
            return AudioResponse(
                status="success",
                recognized_text=text
            )
        else:
            return AudioResponse(
                status="error",
                error="Could not recognize audio. Please try again."
            )
    except Exception as e:
        logger.error(f"Listen endpoint error: {e}")
        return AudioResponse(
            status="error",
            error=f"Error during speech recognition: {str(e)}"
        )

# ==================== Response Processing Endpoint ====================

@app.post("/process", response_model=ChatResponse)
async def process_input(request: TextInput):
    """
    Process user text input and generate AI response
    
    Args:
        request: TextInput containing user message
        
    Returns:
        ChatResponse: User input and agent response
    """
    if not request.text or request.text.strip() == "":
        raise HTTPException(status_code=400, detail="Text field cannot be empty")
    
    try:
        reply = get_response(request.text)
        
        return ChatResponse(
            user_input=request.text,
            agent_reply=reply if reply else "I couldn't generate a response",
            status="success"
        )
    except Exception as e:
        logger.error(f"Process error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing input: {str(e)}")

# ==================== Text-to-Speech Endpoint ====================

@app.post("/speak", response_model=TTSResponse)
async def speak_endpoint(request: TextInput):
    """
    Convert text to speech using text-to-speech engine
    
    Args:
        request: TextInput containing text to speak
        
    Returns:
        TTSResponse: Success or error status
    """
    if not request.text or request.text.strip() == "":
        raise HTTPException(status_code=400, detail="Text field cannot be empty")
    
    loop = asyncio.get_event_loop()
    try:
        success = await loop.run_in_executor(executor, speak, request.text)
        
        if success:
            logger.info(f"Successfully spoke: {request.text}")
            return TTSResponse(
                status="success",
                message="Text spoken successfully"
            )
        else:
            return TTSResponse(
                status="error",
                message="Failed to speak",
                error="Text-to-speech engine encountered an error"
            )
    except Exception as e:
        logger.error(f"Speak error: {e}")
        return TTSResponse(
            status="error",
            message="Failed to speak",
            error=str(e)
        )

# ==================== Combined Chat Endpoint ====================

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: TextInput):
    """
    Full chat endpoint: process text and return agent response
    
    Args:
        request: TextInput containing user message
        
    Returns:
        ChatResponse: User input and agent response
    """
    if not request.text or request.text.strip() == "":
        raise HTTPException(status_code=400, detail="Text field cannot be empty")
    
    try:
        reply = get_response(request.text)
        
        return ChatResponse(
            user_input=request.text,
            agent_reply=reply if reply else "I couldn't generate a response",
            status="success"
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Error in chat: {str(e)}")

# ==================== Full Interaction Endpoint ====================

@app.post("/interact")
async def interact_endpoint(request: TextInput):
    """
    Full interaction: process input, get response, and speak it
    
    Args:
        request: TextInput containing user message
        
    Returns:
        dict: Combined response and speech status
    """
    if not request.text or request.text.strip() == "":
        raise HTTPException(status_code=400, detail="Text field cannot be empty")
    
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
        raise HTTPException(status_code=500, detail=f"Error in interaction: {str(e)}")

# ==================== Run the server ====================

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=5000,
        log_level="info"
    )