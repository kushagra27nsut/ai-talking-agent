import speech_recognition as sr
import pyttsx3
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize recognizer
r = sr.Recognizer()

# Thread pool for blocking operations
executor = ThreadPoolExecutor(max_workers=5)

def speak(text: str) -> bool:
    """
    Convert text to speech
    
    Args:
        text: Text to speak
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not text or text.strip() == "":
            return False
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)  # Speed of speech
        engine.say(text)
        engine.runAndWait()
        del engine
        logger.info(f"Spoke: {text}")
        return True
    except Exception as e:
        logger.error(f"Speak error: {e}")
        return False

def listen() -> Optional[str]:
    """
    Listen to microphone input and recognize speech using Google API
    
    Returns:
        Optional[str]: Recognized text or None if failed
    """
    try:
        with sr.Microphone() as source:
            logger.info("Listening...")
            r.adjust_for_ambient_noise(source, duration=0.5)
            r.energy_threshold = 3000
            r.dynamic_energy_threshold = False
            r.pause_threshold = 0.5
            r.phrase_threshold = 0.1
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
        text = r.recognize_google(audio)
        logger.info(f"Recognized: {text}")
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

def get_response(user_text: str) -> Optional[str]:
    """
    Generate AI response based on user input
    
    Args:
        user_text: User input text
        
    Returns:
        Optional[str]: Agent response
    """
    if user_text is None or user_text.strip() == "":
        return "I didn't catch that. Could you please repeat?"
    
    user_lower = user_text.lower()
    
    # Simple rule-based responses
    if "hello" in user_lower or "hi" in user_lower:
        return "Hello! How can I help you today?"
    elif "name" in user_lower:
        return "I am an AI talking agent. I'm here to assist you."
    elif "weather" in user_lower:
        return "I can help with weather information. Please tell me your city name."
    elif "time" in user_lower:
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M")
        return f"The current time is {current_time}."
    elif "help" in user_lower:
        return "I can help with greetings, tell you the time, weather info, and more. What would you like?"
    elif "quit" in user_lower or "exit" in user_lower:
        return "Goodbye! Have a great day!"
    else:
        return "That's interesting! I'm learning more about you. Can you tell me more?"