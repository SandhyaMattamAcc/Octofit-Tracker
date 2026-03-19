"""AMS Dashboard - FastAPI Application Entry Point."""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.api.routes import router

app = FastAPI(
    title="Agentic AMS Dashboard",
    description=(
        "AI-powered Application Management Services dashboard with CrewAI agents "
        "for autonomous incident detection, root cause analysis, remediation, and prevention."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# Serve React frontend in production
frontend_build = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(frontend_build):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_build, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        return FileResponse(os.path.join(frontend_build, "index.html"))


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AMS Dashboard API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
