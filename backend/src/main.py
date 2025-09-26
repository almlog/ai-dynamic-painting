from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import API routers
from src.api.routes import videos, display, m5stack, system, admin, ai_generation, ai_dashboard

app = FastAPI(
    title="AI Dynamic Painting API",
    description="Phase 4 Phase B: AI画像品質向上システム（バックエンド完成版）",
    version="2.4.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development (default)
        "http://localhost:5173",  # Vite development (current frontend)
        "http://127.0.0.1:5173",  # Alternative localhost format
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(videos.router, prefix="/api", tags=["videos"])
app.include_router(display.router, prefix="/api", tags=["display"])
app.include_router(m5stack.router, prefix="/api", tags=["m5stack"])
app.include_router(system.router, prefix="/api", tags=["system"])
app.include_router(ai_generation.router, prefix="/ai", tags=["ai"])
app.include_router(admin.router, tags=["admin"])  # Admin routes have their own prefix
app.include_router(ai_dashboard.router, tags=["dashboard"])  # Dashboard routes have their own prefix

# Application lifecycle events
@app.on_event("startup")
async def startup_event():
    """Initialize AI services on application startup."""
    await ai_generation.initialize_ai_services()

@app.on_event("shutdown") 
async def shutdown_event():
    """Cleanup AI services on application shutdown."""
    await ai_generation.cleanup_ai_services()

@app.get("/")
async def root():
    return {"message": "AI Dynamic Painting System - Phase 4 Phase B", "version": "2.4.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "phase": "Phase 4 Phase B", "version": "2.4.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)