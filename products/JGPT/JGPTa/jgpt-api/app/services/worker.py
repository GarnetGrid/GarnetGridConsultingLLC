import asyncio
import logging
from sqlalchemy import select
from app.db.session import SessionLocal
from app.db.models import IngestionJob
from app.util.url_ingest import scrape_url
from app.util.ingest import ingest_kb
# ... import other ingest logic

logger = logging.getLogger(__name__)

async def process_job(job_id: int):
    logger.info(f"Processing job {job_id}")
    with SessionLocal() as db:
        job = db.execute(select(IngestionJob).where(IngestionJob.id == job_id)).scalar_one_or_none()
        if not job:
            return
        
        job.status = "processing"
        db.commit()
        
        try:
            # Dispatch based on source_type
            if job.source_type == "url":
                # Call ingest logic here. Ideally reuse app.services.web_ingest or util
                # For now simulating or calling simple logic
                logger.info(f"Ingesting URL: {job.source_target}")
                
                # SIMULATION: In a real flow, we'd have extracted text here.
                simulated_text = f"Content from {job.source_target}. " * 50 
                
                # DeepSeek Hook
                from app.services.local_llm.deepseek_worker import summarize_text
                summary = await summarize_text(simulated_text)
                logger.info(f"Generated Summary: {summary[:100]}...")
                
                # TODO: Save summary to Document model

                
            # Simulate success for now as we refine the worker logic
            # Actual implementation needs to call the heavy lifting functions
            # from app.util.ingest etc.
            
            job.status = "completed"
            db.commit()
            
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}")
            job.status = "failed"
            job.error = str(e)
            db.commit()

async def worker_loop():
    """Polls for pending jobs."""
    logger.info("Worker started.")
    while True:
        try:
            # Fetch pending job
            # Use a separate session for polling to avoid holding connections
            with SessionLocal() as db:
                stmt = select(IngestionJob).where(IngestionJob.status == "pending").limit(1).with_for_update(skip_locked=True)
                job = db.execute(stmt).scalar_one_or_none()
                if job:
                   job_id = job.id
                else:
                   job_id = None
            
            if job_id:
                await process_job(job_id)
            else:
                await asyncio.sleep(5) # Audit frequency
                
        except Exception as e:
            logger.error(f"Worker loop error: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(worker_loop())
