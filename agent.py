import speech_recognition as sr
import pyttsx3
import time

r = sr.Recognizer()

def speak(text):
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        del engine
    except Exception as e:
        print(f"Speak error: {e}")

def listen():
    try:
        with sr.Microphone() as source:
            print("Listening...")
            r.adjust_for_ambient_noise(source, duration=0.5)
            r.energy_threshold = 3000
            r.dynamic_energy_threshold = False
            r.pause_threshold = 0.5
            r.phrase_threshold = 0.1
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
        text = r.recognize_google(audio)
        return text
    except sr.WaitTimeoutError:
        print("No audio detected. Try again.")
        speak("No audio detected. Try again.")
        return None
    except sr.UnknownValueError:
        print("Could not understand audio")
        speak("Could not understand audio")
        return None
    except sr.RequestError as e:
        print(f"API error: {e}")
        return None
    except Exception as e:
        print(f"Listen error: {e}")
        return None

def get_response(user_text):
    if user_text is None:
        return None
    user_lower = user_text.lower()
    if "hello" in user_lower:
        return "Hello! How can I help you?"
    elif "name" in user_lower:
        return "I am an AI talking agent."
    elif "weather" in user_lower:
        return "I can tell you the weather. Please tell me your city."
    elif "temperature" in user_lower:
        return "The weather is sunny today."
    else:
        return "I am still learning."

while True:
    try:
        text = listen()
        if text:
            print(f"You: {text}")
            if "quit" in text.lower():
                print("Goodbye!")
                speak("Goodbye!")
                break
            reply = get_response(text)
            if reply:
                print(f"Agent: {reply}")
                speak(reply)
        time.sleep(1)
    except KeyboardInterrupt:
        print("Goodbye!")
        speak("Goodbye!")
        break
    except Exception as e:
        print(f"Error: {e}")
        continue