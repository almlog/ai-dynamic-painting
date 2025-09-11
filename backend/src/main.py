from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import API routers
from src.api.routes import videos, display, m5stack

app = FastAPI(
    title="AI Dynamic Painting API",
    description="Phase 1: 手動動画管理システム",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(videos.router, prefix="/api", tags=["videos"])
app.include_router(display.router, prefix="/api", tags=["display"])
app.include_router(m5stack.router, prefix="/api", tags=["m5stack"])

@app.get("/")
async def root():
    return {"message": "AI Dynamic Painting System - Phase 1"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "phase": "Phase 1"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)