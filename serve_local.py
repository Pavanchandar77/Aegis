#!/usr/bin/env python3
"""
AEGIS — Local Dev Server
Serves the FastAPI API at /api/* and the static dashboard at /*.
Single-process, single-port — mirrors production (Vercel) routing.

Usage:
    python serve_local.py
    Then open http://localhost:8000
"""

import os
import sys

# Ensure project root is on sys.path so 'api.index' can be imported
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

from api.index import app   # noqa: E402

from fastapi.staticfiles import StaticFiles  # noqa: E402
from fastapi.responses import FileResponse    # noqa: E402

# ── Serve index.html for the root path ──
public_dir = os.path.join(project_dir, "public")


@app.get("/", include_in_schema=False)
def serve_index():
    return FileResponse(os.path.join(public_dir, "index.html"))


# ── Mount remaining static assets (style.css, app.js, etc.) ──
app.mount("/", StaticFiles(directory=public_dir), name="static")


if __name__ == "__main__":
    import uvicorn
    print("AEGIS Local Server -> http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
