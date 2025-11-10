#!/usr/bin/env python3
"""
Ethio Bingo - Main Entry Point
Runs both the Telegram Bot and FastAPI server
"""
import sys
import asyncio
import uvicorn
from multiprocessing import Process
import logging

from src.core.config import settings
from src.core.database import init_db

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def run_bot():
    """Run Telegram Bot"""
    from src.bot.telegram_bot import bot
    bot.setup()
    bot.run()


def run_api():
    """Run FastAPI Server"""
    uvicorn.run(
        "src.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )


def main():
    """Main entry point"""
    try:
        logger.info("Initializing Ethio Bingo...")
        
        # Initialize database
        logger.info("Setting up database...")
        init_db()
        
        # Choose mode based on command line arguments
        if len(sys.argv) > 1:
            mode = sys.argv[1]
            if mode == "bot":
                logger.info("Starting in Bot-only mode...")
                run_bot()
            elif mode == "api":
                logger.info("Starting in API-only mode...")
                run_api()
            else:
                logger.error(f"Unknown mode: {mode}")
                print("Usage: python main.py [bot|api]")
                sys.exit(1)
        else:
            # Run both
            logger.info("Starting in full mode (Bot + API)...")
            
            # Start API server in separate process
            api_process = Process(target=run_api)
            api_process.start()
            
            # Run bot in main process
            try:
                run_bot()
            finally:
                api_process.terminate()
                api_process.join()
    
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
