import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL ya SUPABASE_KEY missing hai!")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="Auth API - Supabase Practice")
security = HTTPBearer()

class AuthCredentials(BaseModel):
    email: EmailStr
    password: str

# Helper Dependency to Verify Token
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        # Supabase token ke zariye user ki profile fetch karta hai
        user_response = supabase.auth.get_user(token)
        if not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        return user_response.user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

@app.get("/")
def root():
    return {"message": "Server running and connected to Supabase"}

@app.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def signup(credentials: AuthCredentials):
    try:
        response = supabase.auth.sign_up({
            "email": credentials.email,
            "password": credentials.password
        })
        if not response.user:
            raise HTTPException(status_code=400, detail="Signup failed")
        return {"message": "User registered successfully", "user": response.user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login", status_code=status.HTTP_200_OK)
def login(credentials: AuthCredentials):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })
        if not response.session:
            raise HTTPException(status_code=401, detail="Invalid login credentials")
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer"
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid login credentials")

# --- STAGE 2 & 3: PROTECTED ENDPOINT ---
@app.get("/auth/me", status_code=status.HTTP_200_OK)
def get_current_user_profile(current_user = Depends(verify_token)):
    return {
        "message": "Access granted to protected route",
        "user_id": current_user.id,
        "email": current_user.email
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)