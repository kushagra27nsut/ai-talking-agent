"""
XCER AI Talking Agent - Core AI Logic
=====================================
Handles speech recognition, text-to-speech, and AI responses using Groq
"""

import speech_recognition as sr
import pyttsx3
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
import logging
import random
from datetime import datetime

# Try to import Groq
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("⚠️ groq not installed. Run: pip install groq")

# Groq API Key
GROQ_API_KEY = "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"
SPEECH_RATE = 150

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize recognizer
r = sr.Recognizer()

# Thread pool for blocking operations
executor = ThreadPoolExecutor(max_workers=5)

# ==============================================
# GROQ AI INITIALIZATION
# ==============================================
groq_client = None
groq_initialized = False
conversation_history = []

def initialize_groq():
    """Initialize Groq AI client"""
    global groq_client, groq_initialized
    
    if not GROQ_AVAILABLE:
        logger.warning("Groq library not available")
        return False
    
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
        groq_initialized = True
        logger.info("✅ Groq AI initialized successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize Groq: {e}")
        return False

# Initialize on module load
initialize_groq()

# ==============================================
# TEXT-TO-SPEECH
# ==============================================
def speak(text: str) -> bool:
    """Convert text to speech"""
    try:
        if not text or text.strip() == "":
            return False
        engine = pyttsx3.init()
        engine.setProperty('rate', SPEECH_RATE)
        engine.say(text)
        engine.runAndWait()
        del engine
        logger.info(f"🔊 Spoke: {text}")
        return True
    except Exception as e:
        logger.error(f"Speak error: {e}")
        return False

# ==============================================
# SPEECH-TO-TEXT
# ==============================================
def listen() -> Optional[str]:
    """Listen to microphone and recognize speech using Google API"""
    try:
        with sr.Microphone() as source:
            logger.info("🎤 Listening...")
            r.adjust_for_ambient_noise(source, duration=0.5)
            r.energy_threshold = 3000
            r.dynamic_energy_threshold = False
            r.pause_threshold = 0.5
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
        text = r.recognize_google(audio)
        logger.info(f"📝 Recognized: {text}")
        return text
    except sr.WaitTimeoutError:
        logger.warning("No audio detected")
        return None
    except sr.UnknownValueError:
        logger.warning("Could not understand audio")
        return None
    except sr.RequestError as e:
        logger.error(f"Google API error: {e}")
        return None
    except Exception as e:
        logger.error(f"Listen error: {e}")
        return None

# ==============================================
# GROQ AI RESPONSE
# ==============================================
def get_groq_response(user_text: str) -> Optional[str]:
    """Get response from Groq AI (LLaMA model)"""
    global conversation_history
    
    try:
        if not groq_initialized or groq_client is None:
            return None
        
        # Add user message to history
        conversation_history.append({
            "role": "user",
            "content": user_text
        })
        
        # Keep only last 10 messages
        if len(conversation_history) > 10:
            conversation_history = conversation_history[-10:]
        
        # Create chat completion
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are XCER AI, a helpful voice assistant. Be concise and friendly. Keep responses short (1-2 sentences) for voice calls. Don't use markdown or special formatting."
                }
            ] + conversation_history,
            temperature=0.7,
            max_tokens=150
        )
        
        reply = response.choices[0].message.content.strip()
        
        # Add assistant response to history
        conversation_history.append({
            "role": "assistant",
            "content": reply
        })
        
        logger.info(f"🤖 Groq: {reply}")
        return reply
        
    except Exception as e:
        logger.error(f"Groq error: {e}")
        return None

# ==============================================
# MAIN RESPONSE FUNCTION
# ==============================================
def get_response(user_text: str) -> Optional[str]:
    """Generate AI response using Groq"""
    if user_text is None or user_text.strip() == "":
        return "I didn't catch that. Could you please repeat?"
    
    # Try Groq
    if groq_initialized:
        groq_response = get_groq_response(user_text)
        if groq_response:
            return groq_response
    
    # Fallback
    return "I'm having trouble connecting to AI. Please try again."

# ==============================================
# UTILITY FUNCTIONS
# ==============================================
def reset_conversation():
    """Reset conversation history"""
    global conversation_history
    conversation_history = []
    logger.info("🔄 Conversation reset")
    return True

def is_ai_available() -> bool:
    """Check if AI is available"""
    return groq_initialized

