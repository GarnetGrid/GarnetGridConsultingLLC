import logging
import asyncio
from app.services.digest import generate_daily_digest

logger = logging.getLogger(__name__)

async def digest_job():
    """
    Job to be scheduled. Generates the daily digest.
    """
    logger.info("Starting Daily Digest job...")
    try:
        summary = await generate_daily_digest(hours=24)
        logger.info(f"Daily Digest completed.")
    except Exception as e:
        logger.error(f"Exception in Digest job: {e}")
