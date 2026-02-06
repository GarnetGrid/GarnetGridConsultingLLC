import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore

# Setup logging
logger = logging.getLogger(__name__)

# Initialize Scheduler
# Using MemoryJobStore for now. For persistence across restarts, we'd use SQLAlchemyJobStore.
jobstores = {
    'default': MemoryJobStore()
}
executors = {
    'default': {'type': 'threadpool', 'max_workers': 20}
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}

scheduler = AsyncIOScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone="UTC")

def start_scheduler():
    """Start the global scheduler."""
    if not scheduler.running:
        scheduler.start()
        logger.info("APScheduler started.")

def stop_scheduler():
    """Shutdown the scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler stopped.")
