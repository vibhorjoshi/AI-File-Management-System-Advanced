"""
ML Service for Advanced Similarity Detection
"""
import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import MLSettings
from app.services.similarity import SimilarityService

# Initialize settings
settings = MLSettings()

# Global similarity service
similarity_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager"""
    global similarity_service
    
    # Startup
    print(f"Starting ML Service v{settings.APP_VERSION}")
    print("Loading ML models...")
    
    try:
        similarity_service = SimilarityService()
        await similarity_service.initialize()
        print("ML models loaded successfully")
    except Exception as e:
        print(f"Failed to load ML models: {e}")
        raise
    
    yield
    
    # Shutdown
    if similarity_service:
        await similarity_service.cleanup()
    print("ML Service shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="AI File Cleanup - ML Service",
    version=settings.APP_VERSION,
    description="Machine Learning service for file similarity detection",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI File Cleanup - ML Service",
        "version": settings.APP_VERSION,
        "status": "active",
        "docs_url": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global similarity_service
    
    status = "healthy" if similarity_service and similarity_service.is_ready() else "unhealthy"
    
    return {
        "status": status,
        "timestamp": "2025-01-11T00:00:00Z",
        "version": settings.APP_VERSION,
        "models_loaded": similarity_service.is_ready() if similarity_service else False,
        "available_models": similarity_service.get_available_models() if similarity_service else []
    }

@app.post("/analyze/similarity")
async def analyze_similarity(request: dict):
    """Analyze file similarity using ML models"""
    global similarity_service
    
    if not similarity_service or not similarity_service.is_ready():
        raise HTTPException(status_code=503, detail="ML service not ready")
    
    try:
        files = request.get("files", [])
        similarity_threshold = request.get("similarity_threshold", 0.85)
        
        if len(files) < 2:
            return {"groups": []}
        
        # Analyze files for similarity
        groups = await similarity_service.analyze_batch_similarity(
            files, similarity_threshold
        )
        
        return {"groups": groups}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Similarity analysis failed: {str(e)}")

@app.post("/analyze/content")
async def analyze_content(request: dict):
    """Analyze file content for advanced features"""
    global similarity_service
    
    if not similarity_service or not similarity_service.is_ready():
        raise HTTPException(status_code=503, detail="ML service not ready")
    
    try:
        file_path = request.get("file_path")
        analysis_types = request.get("analysis_types", ["embedding", "features"])
        
        result = await similarity_service.analyze_file_content(
            file_path, analysis_types
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content analysis failed: {str(e)}")

@app.get("/models/status")
async def get_models_status():
    """Get status of loaded ML models"""
    global similarity_service
    
    if not similarity_service:
        return {"models": [], "status": "not_initialized"}
    
    return {
        "models": similarity_service.get_model_status(),
        "status": "ready" if similarity_service.is_ready() else "loading"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )
