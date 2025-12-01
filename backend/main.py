import os
import uuid
from typing import Dict, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from dotenv import load_dotenv

load_dotenv()

# In-memory storage for sessions (in production, use Redis/database)
sessions: Dict[str, Dict] = {}
message_histories: Dict[str, ChatMessageHistory] = {}

class SummarizeRequest(BaseModel):
    url: str
    style: str = "executive"  # Default to executive summary

class QARequest(BaseModel):
    session_id: str
    question: str

app = FastAPI(title="Article Summarizer API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SummarizeRequest(BaseModel):
    url: str
    style: str = "executive"  # Default to executive summary

@app.get("/")
async def root():
    return {"message": "Article Summarizer API is running"}

@app.post("/summarize")
async def summarize_article(request: SummarizeRequest):
    try:
        url = request.url
        
        # Detect if URL is a YouTube link
        is_youtube = 'youtube.com' in url or 'youtu.be' in url
        
        # 1. Fetch content based on URL type
        if is_youtube:
            # Use YoutubeLoader for YouTube videos
            from langchain_community.document_loaders import YoutubeLoader
            
            loader = YoutubeLoader.from_youtube_url(
                url,
                add_video_info=False,
                language=["en", "en-US"]
            )
            docs = loader.load()
            
            if not docs:
                raise HTTPException(status_code=400, detail="Could not fetch transcript from YouTube video")
            
            content = docs[0].page_content
            content_type = "video transcript"
        else:
            # Use WebBaseLoader for regular articles
            loader = WebBaseLoader(url)
            docs = loader.load()
            
            if not docs:
                raise HTTPException(status_code=400, detail="Could not fetch content from URL")
                
            content = docs[0].page_content
            content_type = "article"
        
        # 2. Summarize using Groq
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY not found in environment variables")
            
        llm = ChatGroq(temperature=0, model_name="llama-3.3-70b-versatile", api_key=groq_api_key)

        # Define prompt templates for different styles
        style_templates = {
            "executive": """
            You are an executive assistant providing a brief summary for busy professionals.
            Read the following {content_type} and provide:
            1. A very brief summary (2-3 sentences maximum).
            2. 2-3 key takeaways or action items.

            Format the output as a JSON object with keys "summary" (string) and "key_insights" (list of strings).
            Keep everything extremely concise and actionable.

            Content:
            {text}
            """,

            "detailed": """
            You are an analyst providing comprehensive analysis.
            Read the following {content_type} and provide:
            1. A detailed summary covering all main points, context, and implications.
            2. 5-7 key insights, including supporting details and implications.

            Format the output as a JSON object with keys "summary" (string) and "key_insights" (list of strings).
            Be thorough but organized.

            Content:
            {text}
            """,

            "bullet_points": """
            You are a structured note-taker focused on clarity and organization.
            Read the following {content_type} and provide:
            1. A brief introductory summary (1-2 sentences).
            2. Key points organized as clear, concise bullet points (each as a separate string in the array).

            Format the output as a JSON object with keys "summary" (string) and "key_insights" (array of strings, each string being a bullet point).
            Keep each bullet point as a single, complete thought. Do not use nested structures.

            Content:
            {text}
            """,

            "academic": """
            You are an academic researcher providing scholarly analysis.
            Read the following {content_type} and provide:
            1. An objective summary of the main arguments and findings.
            2. Critical insights, methodological considerations, and broader implications.

            Format the output as a JSON object with keys "summary" (string) and "key_insights" (list of strings).
            Use formal academic language and cite conceptual frameworks where relevant.

            Content:
            {text}
            """
        }

        # Get the appropriate template based on style
        style = request.style.lower()
        if style not in style_templates:
            style = "executive"  # Default fallback

        template = style_templates[style]

        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | llm | JsonOutputParser()
        
        result = chain.invoke({"text": content, "content_type": content_type})

        # Add content type to response
        result["content_type"] = "youtube" if is_youtube else "article"

        # Create session and store content for Q&A
        session_id = str(uuid.uuid4())
        message_histories[session_id] = ChatMessageHistory()
        sessions[session_id] = {
            "content": content,
            "content_type": content_type,
            "summary": result,
            "conversation": []
        }

        result["session_id"] = session_id

        return result
        
    except Exception as e:
        import traceback
        print(f"Error occurred: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask_question(request: QARequest):
    try:
        if request.session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found. Please summarize content first.")

        session = sessions[request.session_id]
        content = session["content"]
        content_type = session["content_type"]

        # Initialize Groq LLM
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY not found in environment variables")

        llm = ChatGroq(temperature=0.3, model_name="llama-3.3-70b-versatile", api_key=groq_api_key)

        # Create Q&A prompt with context
        qa_template = f"""
        You are a helpful assistant answering questions about this {content_type}.

        Content Summary:
        {session["summary"]["summary"]}

        Key Insights:
        {"".join(f"- {insight}\n" for insight in session["summary"]["key_insights"])}

        Full Content:
        {content}

        Answer the user's question based on the content above. Be concise but comprehensive.
        If the question cannot be answered from the content, say so clearly.

        Previous conversation context:
        {{history}}
        """

        prompt = ChatPromptTemplate.from_template(qa_template)

        # Create chain with message history
        chain = prompt | llm | StrOutputParser()
        chain_with_history = RunnableWithMessageHistory(
            chain,
            lambda session_id: message_histories[session_id],
            input_messages_key="question",
            history_messages_key="history"
        )

        # Get response
        response = chain_with_history.invoke(
            {"question": request.question},
            config={"configurable": {"session_id": request.session_id}}
        )

        # Store conversation
        session["conversation"].append({
            "question": request.question,
            "answer": response,
            "timestamp": str(uuid.uuid4())  # Simple timestamp
        })

        return {
            "answer": response,
            "conversation_history": session["conversation"]
        }

    except Exception as e:
        import traceback
        print(f"Error occurred in Q&A: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


