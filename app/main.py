from fastapi import FastAPI

from app.routes.analyze import router as analyze_router



app = FastAPI(

    title="Resume Analysis Python Service",

    version="1.0.0"

)



app.include_router(analyze_router)





@app.get("/")

def health_check():

    return {"status": "Python service running"}







