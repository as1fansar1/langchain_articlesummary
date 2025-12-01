import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from dotenv import load_dotenv

load_dotenv()

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

@app.get("/")
async def root():
    return {"message": "Article Summarizer API is running"}

@app.post("/summarize")
async def summarize_article(request: SummarizeRequest):
    try:
        # 1. Fetch content
        loader = WebBaseLoader(request.url)
        docs = loader.load()
        
        if not docs:
            raise HTTPException(status_code=400, detail="Could not fetch content from URL")
            
        content = docs[0].page_content
        
        # 2. Summarize using Groq
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY not found in environment variables")
            
        llm = ChatGroq(temperature=0, model_name="llama-3.3-70b-versatile", api_key=groq_api_key)
        
        # Prompt template
        template = """
        You are an expert article summarizer.
        Read the following article content and provide:
        1. A concise summary of the main points.
        2. A list of 3-5 key insights or takeaways.
        
        Format the output as a JSON object with keys "summary" (string) and "key_insights" (list of strings).
        Ensure the JSON is valid and does not contain any other text.
        
        Article Content:
        {text}
        """
        
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | llm | JsonOutputParser()
        
        result = chain.invoke({"text": content})
        
        return result
        
    except Exception as e:
        import traceback
        print(f"Error occurred: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

