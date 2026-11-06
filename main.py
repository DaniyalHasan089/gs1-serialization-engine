#!/usr/bin/env python3
"""FastAPI Application Entry Point.

Run with:
    uvicorn main:app --reload
or:
    python main.py
or CLI mode:
    python main.py --cli
"""

import sys
from gs1.api import app

if __name__ == "__main__":
    if "--cli" in sys.argv:
        from gs1.cli import main as cli_main
        cli_main()
    else:
        try:
            import uvicorn
            print("=" * 60)
            print("  GS1 DataMatrix Serialization Engine - FastAPI Server")
            print("=" * 60)
            print("  Web Dashboard : http://127.0.0.1:8000")
            print("  Swagger Docs  : http://127.0.0.1:8000/docs")
            print("  ReDoc         : http://127.0.0.1:8000/redoc")
            print("=" * 60)
            uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
        except ImportError:
            print("Note: uvicorn is not installed in this environment.")
            print("To start the server, install uvicorn: pip install uvicorn")
            print("To run in interactive CLI mode instead, run: python main.py --cli")
            sys.exit(1)
