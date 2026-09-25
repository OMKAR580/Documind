from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routes import health

app = FastAPI(
    title="DocuMind API",
    description="AI-powered multimodal document intelligence platform",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS — Allow frontend (localhost:3000) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(
    health.router,
    prefix="/api/v1",
    tags=["health"],
)


@app.get("/")
async def root():
    return {"message": "DocuMind API is running. Visit /api/docs for documentation."}
