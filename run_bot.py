#!/usr/bin/env python
"""
Telegram Bot Runner for PythonAnywhere
This script runs the Telegram bot using polling
"""

import os
import sys
import django
import asyncio
import logging

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Now import bot after Django setup
from tg_bot.bot import main

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting Telegram Bot on PythonAnywhere...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}", exc_info=True)
