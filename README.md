# 🤖 XCER AI Talking Agent

**Hack4Delhi Project by Team XCER - IEEE NSUT**

A voice-interactive AI assistant that handles **real phone calls** using Twilio and **intelligent conversations** using Google Gemini AI.

## 🌟 Features

- 📞 **Real Phone Calls** - Handle inbound/outbound calls via Twilio
- 🤖 **Gemini AI** - Intelligent, context-aware responses
- 🎤 **Speech Recognition** - Google Speech-to-Text API
- 🔊 **Text-to-Speech** - Natural voice responses
- 💬 **Web Chat Interface** - Beautiful UI for testing
- 🔄 **24/7 Availability** - Always ready to answer
- ⚡ **Scalable** - FastAPI handles high volumes

## 👥 Team XCER

1. Ankur Anand
2. Kriti Saini
3. Kushagra Sharma
4. Parv Jain
5. Mudit Kaushik

## 📋 Prerequisites

- Python 3.7+
- Twilio Account (for phone calls)
- Google Gemini API Key
- ngrok (for exposing local server)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install fastapi uvicorn pydantic SpeechRecognition pyttsx3 python-multipart
```

### 2. Run the Backend Server

```bash
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8080
```

### 3. Open Frontend

Open `frontend.html` in your web browser:
- Double-click the file, OR
- Right-click → Open with → Browser

### 4. Start Talking!

1. Click the **🎤 Speak** button
2. Say something to the AI
3. The AI responds with text and voice
4. Continue talking or click **⏹️ Stop** to exit

## 📁 Project Structure

```
ai_talking_agent/
├── agent.py          # Core AI logic with smart responses
├── main.py           # FastAPI backend server
├── ai_agent.py       # Standalone agent (CLI version)
├── frontend.html     # Web UI for interaction
└── README.md         # This file
```

## 🔧 Configuration

### Change Backend Port

Edit `main.py`:
```python
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8080,  # Change this number
        log_level="info"
    )
```

Also update `frontend.html`:
```javascript
const BACKEND_URL = "http://127.0.0.1:8080";  // Change port here
```

### Change Speech Rate

Edit `frontend.html` in the `speakResponse()` function:
```javascript
voiceOutput.rate = 1.0;  // 0.5 (slow) to 2.0 (fast)
```

## 📡 API Endpoints

If you want to use the API directly:

### Chat Endpoint
```bash
POST http://127.0.0.1:8080/chat
Content-Type: application/json

{"text": "hello"}
```

Response:
```json
{
  "status": "success",
  "user_input": "hello",
  "agent_reply": "Hello! How can I help you today?"
}
```

### Available Endpoints
- `GET /` - Health check
- `GET /health` - Server status
- `GET /info` - API documentation
- `POST /chat` - Main chat endpoint
- `POST /listen` - Speech recognition
- `POST /speak` - Text-to-speech
- `GET /docs` - Interactive API docs (Swagger UI)

## 💡 Example Interactions

### Ask Time
- **You:** "What time is it?"
- **AI:** "The current time is 3:45 PM."

### Request Joke
- **You:** "Tell me a joke"
- **AI:** "Why don't scientists trust atoms? Because they make up everything!"

### Ask About Features
- **You:** "What can you do?"
- **AI:** "I can help with many things! You can ask me about the time, date, for jokes or funny stories..."

### Exit
- **You:** "Quit"
- **AI:** "Goodbye! It was nice talking to you. Have a wonderful day!"

## 🐛 Troubleshooting

### "Error: Failed to fetch"
- Make sure backend is running: `python main.py`
- Check if port 8080 is accessible
- Verify backend shows `Application startup complete`

### Microphone not working
- Check browser has microphone permission
- Try refreshing the page
- Make sure microphone is connected and working
- Try a different browser

### No voice output
- Check browser volume
- Check speaker is connected
- Verify text-to-speech is enabled in settings

### Backend crashes
- Check Python version (3.7+)
- Verify all dependencies are installed
- Check for port conflicts on port 8080

## 🔐 Privacy & Security

- Speech recognition uses Google's API (requires internet)
- No data is stored or logged permanently
- Audio is processed and discarded immediately
- For production, consider self-hosted speech recognition

## 📚 Technologies Used

- **Backend:** FastAPI (Python web framework)
- **Frontend:** Vanilla JavaScript, HTML5, CSS3
- **Speech Recognition:** Google Speech Recognition API
- **Text-to-Speech:** pyttsx3 (offline)
- **Server:** Uvicorn (ASGI server)

## 🤝 Contributing

Feel free to fork and improve! Some ideas:
- Add NLP for better responses
- Integrate with weather API
- Add persistent chat history
- Multi-language support
- Mobile app version

## 📝 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

Created by Kushagra Sharma

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review GitHub issues
3. Check browser console for errors (F12)
4. Verify all dependencies are installed

---

**Happy Chatting! 🎉**
