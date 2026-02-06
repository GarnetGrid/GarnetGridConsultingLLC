import asyncio
import logging
from arq import create_pool, cron
from arq.connections import RedisSettings
import os
from app.services.ingest_service import ingestion_service

logger = logging.getLogger(__name__)

async def startup(ctx):
    logger.info("Worker starting up...")
    # Initialize things if needed

async def shutdown(ctx):
    logger.info("Worker shutting down...")

async def run_ingestion_job(ctx):
    logger.info("Starting ingestion job")
    result = await ingestion_service.run_ingestion()
    logger.info(f"Ingestion job complete: {result}")
    return result

class WorkerSettings:
    redis_settings = RedisSettings(
        host=os.getenv("REDIS_HOST", "redis"),
        port=int(os.getenv("REDIS_PORT", 6379))
    )
    functions = [run_ingestion_job]
    on_startup = startup
    on_shutdown = shutdown

if __name__ == "__main__":
    # For local running/testing without arq cli
    import sys
    from arq.worker import run_worker
    sys.exit(run_worker(WorkerSettings))
