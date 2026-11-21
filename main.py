
from fastapi import FastAPI
from datetime import datetime

app = FastAPI(
    title="Asfandyar AI Studio",
    description="Free AI Digital Marketing Manager",
    version="1.0.0"
)

@app.get("/")
def home():
    return {
        "project": "Asfandyar AI Studio",
        "status": "Running",
        "message": "Welcome to Asfandyar AI Studio"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "time": datetime.now().isoformat()
    }

@app.get("/features")
def features():
    return {
        "features": [
            "AI Content Creation",
            "Blogger Automation",
            "Facebook Management",
            "X (Twitter) Management",
            "Adsterra Integration",
            "Monetag Integration",
            "Traffic Analytics"
        ]
    }
