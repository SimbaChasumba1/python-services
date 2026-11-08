from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

from fastapi import FastAPI
from app.routes.analyze import router as analyze_router


app = FastAPI(

    title="Resume Analysis Python Service",

    version="1.0.0"

)



app.include_router(analyze_router)




@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "resume-analysis-python"
    }







