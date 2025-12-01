# Article Summarizer + Key Insights

A modern web application that takes any article URL, fetches its content using LangChain, and generates a concise summary with key insights using Groq's LLM.

## 🎯 Features

- **URL-based Article Fetching**: Paste any article URL to extract content
- **AI-Powered Summarization**: Uses Groq's Llama3-70B model via LangChain
- **Key Insights Extraction**: Automatically identifies 3-5 main takeaways
- **Modern UI**: Glassmorphism design with smooth animations
- **Real-time Processing**: Live loading states and error handling

## 🏗️ Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with async support
- **LLM Integration**: LangChain + Groq
- **Content Fetching**: WebBaseLoader for URL scraping
- **Output Parsing**: JsonOutputParser for structured responses

### Frontend (React + Vite)
- **Framework**: React 18 with Vite
- **Styling**: Vanilla CSS with modern design patterns
- **State Management**: React hooks (useState)
- **API Communication**: Fetch API

## 📁 Project Structure

```
dec1_langchain/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main React component
│   │   └── index.css        # Global styles
│   └── package.json         # Node dependencies
└── README.md
```

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- Groq API Key ([Get one here](https://console.groq.com))

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Install Python dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Create `.env` file**:
   ```bash
   cp .env.example .env
   ```

4. **Add your Groq API key** to `.env`:
   ```
   GROQ_API_KEY=your_actual_groq_api_key_here
   ```

5. **Start the backend server**:
   ```bash
   python3 -m uvicorn main:app --reload
   ```
   
   The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies** (if not already done):
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm run dev
   ```
   
   The app will be available at `http://localhost:5173`

## 🎮 Usage

1. Open your browser to `http://localhost:5173`
2. Paste any article URL into the input field
3. Click "Summarize"
4. Wait for the AI to process the article
5. View the summary and key insights

## 🔧 API Endpoints

### `GET /`
Health check endpoint.

**Response**:
```json
{
  "message": "Article Summarizer API is running"
}
```

### `POST /summarize`
Summarizes an article from a given URL.

**Request Body**:
```json
{
  "url": "https://example.com/article"
}
```

**Response**:
```json
{
  "summary": "A concise summary of the article...",
  "key_insights": [
    "First key insight",
    "Second key insight",
    "Third key insight"
  ]
}
```

## 🎨 Design Features

- **Glassmorphism**: Frosted glass effect with backdrop blur
- **Gradient Text**: Purple-blue gradient for headings
- **Dark Theme**: Modern dark background with subtle gradients
- **Smooth Animations**: Fade-in effects and loading spinners
- **Responsive Layout**: Works on all screen sizes

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **LangChain**: LLM orchestration framework
- **Groq**: High-performance LLM inference
- **BeautifulSoup4**: HTML parsing
- **Python-dotenv**: Environment variable management

### Frontend
- **React**: UI library
- **Vite**: Build tool and dev server
- **Vanilla CSS**: Custom styling without frameworks

## 📝 Code Review Notes

### Backend (`main.py`)
- ✅ Clean separation of concerns
- ✅ Proper error handling with HTTPException
- ✅ CORS configured for development
- ✅ Environment variable validation
- ✅ JsonOutputParser ensures structured responses
- ✅ Uses Groq's Llama3-70B-8192 model

### Frontend (`App.jsx`)
- ✅ Proper state management with hooks
- ✅ Loading and error states handled
- ✅ Clean component structure
- ✅ Accessible form with proper validation
- ✅ Responsive error messaging

### Styling (`index.css`)
- ✅ Modern design with glassmorphism
- ✅ Smooth animations and transitions
- ✅ Consistent color scheme
- ✅ Responsive layout
- ✅ Loading spinner animation

## 🔒 Security Notes

- The `.env` file is gitignored (should add `.gitignore`)
- CORS is set to allow all origins (change for production)
- API key is stored securely in environment variables

## 🚧 Future Enhancements

- [ ] Add `.gitignore` file
- [ ] Support for multiple article formats (PDF, etc.)
- [ ] Save/export summaries
- [ ] History of summarized articles
- [ ] Different summary lengths (short/medium/long)
- [ ] Support for other LLM providers
- [ ] Rate limiting on API
- [ ] User authentication
- [ ] Deployment configuration

## 📄 License

This project is open source and available for educational purposes.

## 🤝 Contributing

Feel free to fork, modify, and submit pull requests!

---

**Built with ❤️ using LangChain, Groq, FastAPI, and React**
