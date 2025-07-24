#!/usr/bin/env python3
"""
Urban Harvest Vending Machine API Server

This script starts the FastAPI server for the Urban Harvest Vending Machine system.
It provides a backend API for customer ordering and admin management.

Usage:
    python run_server.py [options]

Options:
    --host HOST     Host to bind to (default: from .env or 0.0.0.0)
    --port PORT     Port to bind to (default: from .env or 8000)
    --reload        Enable auto-reload for development
    --debug         Enable debug mode
    --workers N     Number of worker processes (production)

Examples:
    # Development mode with auto-reload
    python run_server.py --reload --debug

    # Production mode
    python run_server.py --workers 4

    # Custom host and port
    python run_server.py --host 127.0.0.1 --port 9000
"""

import argparse
import os
import sys
import uvicorn
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

from app.config.settings import settings


def main():
    parser = argparse.ArgumentParser(
        description="Urban Harvest Vending Machine API Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "--host",
        default=settings.host,
        help=f"Host to bind to (default: {settings.host})"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=settings.port,
        help=f"Port to bind to (default: {settings.port})"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        default=settings.reload,
        help="Enable auto-reload for development"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        default=settings.debug,
        help="Enable debug mode"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (production mode)"
    )
    
    parser.add_argument(
        "--log-level",
        default=settings.log_level.lower(),
        choices=["critical", "error", "warning", "info", "debug"],
        help=f"Log level (default: {settings.log_level.lower()})"
    )
    
    args = parser.parse_args()
    
    # Validate environment
    if not os.path.exists(".env") and not os.environ.get("DATABASE_URL"):
        print("Warning: No .env file found and DATABASE_URL not set!")
        print("Please copy .env.example to .env and configure your settings.")
        sys.exit(1)
    
    # Production vs Development configuration
    if args.workers > 1:
        # Production mode with multiple workers
        print(f"Starting Urban Harvest API in PRODUCTION mode")
        print(f"Workers: {args.workers}")
        print(f"Host: {args.host}:{args.port}")
        
        uvicorn.run(
            "app.main:app",
            host=args.host,
            port=args.port,
            workers=args.workers,
            log_level=args.log_level,
            access_log=True
        )
    else:
        # Development mode
        print(f"Starting Urban Harvest API in DEVELOPMENT mode")
        print(f"Host: {args.host}:{args.port}")
        print(f"Reload: {args.reload}")
        print(f"Debug: {args.debug}")
        print(f"API Documentation: http://{args.host}:{args.port}/docs")
        
        uvicorn.run(
            "app.main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level,
            access_log=True
        )


if __name__ == "__main__":
    main()
