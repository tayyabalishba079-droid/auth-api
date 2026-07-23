import os
from dotenv import load_dotenv
from fastapi import FastAPI
from supabase import create_client, Client

# .env file load karein
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL ya SUPABASE_KEY .env file mein missing hai!")

# Supabase client initialize karein
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="Auth API - Supabase Practice")

@app.get("/")
def root():
    return {"message": "Server running and connected to Supabase"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)