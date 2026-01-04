from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client
from pydantic import BaseModel
import openai
from .config import settings

app = FastAPI()

# CORS - allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://ai-saas-fawn-kappa.vercel.app",  # Your Vercel app
        "https://*.vercel.app",  # All Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Initialize Supabase
supabase = create_client(settings.supabase_url, settings.supabase_key)

# Initialize OpenAI
openai.api_key = settings.openai_api_key

# Security
security = HTTPBearer()

# Verify user from JWT token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        user = supabase.auth.get_user(credentials.credentials)
        return user.user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication")

# Models
class AIRequest(BaseModel):
    prompt: str

class AIResponse(BaseModel):
    result: str

# Routes
@app.get("/")
def read_root():
    return {"message": "AI SaaS API is running"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/generate", response_model=AIResponse)
async def generate_ai_content(
    request: AIRequest,
    current_user = Depends(get_current_user)
):
    try:
        # Call OpenAI
        client = openai.OpenAI(api_key=settings.openai_api_key)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # cheaper for testing
            messages=[
                {"role": "user", "content": request.prompt}
            ],
            max_tokens=500
        )
        
        result = response.choices[0].message.content
        
        # Optional: Log usage to Supabase
        supabase.table('usage_logs').insert({
            'user_id': current_user.id,
            'prompt': request.prompt,
            'tokens_used': response.usage.total_tokens
        }).execute()
        
        return AIResponse(result=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))