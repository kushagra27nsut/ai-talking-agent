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
        logger.erro
        r(f"Listen error: {e}")
        return None

def get_response(user_text: str) -> Optional[str]:
    """
    Generate AI response based on user input with smart pattern matching
    
    Args:
        user_text: User input text
        
    Returns:
        Optional[str]: Agent response
    """
    if user_text is None or user_text.strip() == "":
        return "I didn't catch that. Could you please repeat?"
    
    user_lower = user_text.lower().strip()
    
    # ===== GREETINGS =====
    if any(word in user_lower for word in ["hello", "hi", "hey", "greetings", "sup"]):
        greetings = [
            "Hello! How can I help you today?",
            "Hi there! What can I do for you?",
            "Hey! It's great to talk to you!",
            "Greetings! How's your day going?"
        ]
        import random
        return random.choice(greetings)
    
    # ===== IDENTITY/NAME =====
    elif any(word in user_lower for word in ["who are you", "your name", "what are you", "what is your name"]):
        return "I'm an AI talking agent designed to have conversations with you. I can listen, understand, and respond to your questions!"
    
    # ===== TIME =====
    elif "time" in user_lower and not "sometimes" in user_lower:
        from datetime import datetime
        current_time = datetime.now().strftime("%I:%M %p")
        return f"The current time is {current_time}."
    
    # ===== DATE =====
    elif any(word in user_lower for word in ["date", "today", "what day"]):
        from datetime import datetime
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        return f"Today is {current_date}."
    
    # ===== HOW ARE YOU =====
    elif "how are you" in user_lower or "how do you feel" in user_lower:
        responses = [
            "I'm doing great! Thanks for asking. How about you?",
            "I'm feeling wonderful! Ready to help you with anything.",
            "Excellent! I'm here and ready to assist you."
        ]
        import random
        return random.choice(responses)
    
    # ===== WEATHER =====
    elif "weather" in user_lower or "temperature" in user_lower:
        return "I can help with weather information. Please tell me which city you'd like to know about."
    
    # ===== JOKES =====
    elif "joke" in user_lower or "funny" in user_lower or "make me laugh" in user_lower:
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "What do you call a fake noodle? An impasta!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "What did the ocean say to the beach? Nothing, it just waved!",
            "Why don't eggs tell jokes? They'd crack each other up!"
        ]
        import random
        return random.choice(jokes)
    
    # ===== HELP =====
    elif "help" in user_lower or "what can you do" in user_lower or "capabilities" in user_lower:
        return ("I can help you with many things! You can ask me:\n"
                "- What time/date it is\n"
                "- For jokes or funny stories\n"
                "- General questions and conversations\n"
                "- About the weather\n"
                "- Anything you'd like to talk about!")
    
    # ===== THANKS =====
    elif any(word in user_lower for word in ["thank", "thanks", "thankyou", "appreciate"]):
        responses = [
            "You're welcome! Happy to help!",
            "My pleasure! Anything else you need?",
            "No problem at all! Ask me anything!"
        ]
        import random
        return random.choice(responses)
    
    # ===== GOODBYE =====
    elif any(word in user_lower for word in ["bye", "goodbye", "quit", "exit", "see you", "farewell"]):
        return "Goodbye! It was nice talking to you. Have a wonderful day!"
    
    # ===== QUESTIONS ABOUT LIFE =====
    elif "meaning of life" in user_lower or "life" in user_lower and "meaning" in user_lower:
        return "The meaning of life is subjective - it's different for everyone! It could be happiness, helping others, learning, or pursuing your passions. What gives your life meaning?"
    
    # ===== COMPLIMENTS =====
    elif any(word in user_lower for word in ["smart", "intelligent", "clever", "awesome", "great", "amazing"]):
        return "Thank you! I appreciate that. I'm here to be helpful and have meaningful conversations with you."
    
    # ===== QUESTIONS (What, How, Why, When, Where, Who) =====
    elif user_lower.startswith("what"):
        if "weather" in user_lower:
            return "I don't have real-time weather data, but you can check your local weather service for accurate information."
        elif "this is" in user_lower or "that is" in user_lower:
            return "That's an interesting question! Could you tell me more about it?"
        else:
            return "That's a great question! I'm curious to know more. Can you provide some context?"
    
    elif user_lower.startswith("how"):
        if "are you" in user_lower:
            return "I'm doing well, thank you for asking! How are you doing?"
        elif "do" in user_lower or "does" in user_lower:
            return "That's a practical question! I can help guide you through it if you give me more details."
        else:
            return "That's an interesting question. Tell me more and I'll do my best to help!"
    
    elif user_lower.startswith("why"):
        return "That's a thought-provoking question! Different perspectives exist on this topic. What's your take on it?"
    
    elif user_lower.startswith("when"):
        return "Timing can be important! Could you provide more context about what you're asking?"
    
    elif user_lower.startswith("where"):
        return "Location matters! Tell me more and I can try to help you figure it out."
    
    elif user_lower.startswith("who"):
        return "That's an interesting question about people. I'd love to help if you give me more details!"
    
    # ===== YES/NO QUESTIONS =====
    elif user_lower.endswith("?"):
        responses = [
            "That's an interesting question! I think it depends on the context. What do you think?",
            "That's worth thinking about. It really varies from person to person.",
            "Great question! I'm interested in your perspective on this.",
            "That's something many people wonder about. What's your opinion?"
        ]
        import random
        return random.choice(responses)
    
    # ===== DEFAULT: INTELLIGENT FALLBACK =====
    else:
        # Extract key topics
        keywords = user_lower.split()
        
        fallback_responses = [
            f"That's interesting what you said about {keywords[0]}! Tell me more!",
            "I find that topic fascinating! Can you elaborate?",
            "That's a great point! What made you think about this?",
            "I'd like to understand more about what you mean. Can you explain further?",
            "Interesting perspective! Tell me more about your thoughts on this.",
            "That sounds important to you. Why is this topic interesting to you?"
        ]
        
        import random
        return random.choice(fallback_responses)