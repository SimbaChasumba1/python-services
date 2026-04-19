from fastapi import APIRouter

from pydantic import BaseModel

from datetime import datetime



from app.services.text_cleaner import clean_text

from app.services.ai_processor import analyze_with_ai



router = APIRouter(prefix="/analyze")





class ResumeRequest(BaseModel):

    text: str





@router.post("/text")

async def analyze_resume(request: ResumeRequest):



    cleaned_text = clean_text(request.text)

    ai_result = analyze_with_ai(cleaned_text)



    return {

        "resumeFileName": "uploaded_resume.pdf",

        "atsScore": ai_result.get("score", 0),

        "summary": ai_result["summary"],

        "createdAt": datetime.utcnow().isoformat(),

        "strengths": ai_result["strengths"],

        "weaknesses": ai_result["weaknesses"],

        "improvements": ai_result["improvements"]

    }





