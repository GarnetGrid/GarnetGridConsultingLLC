import logging
import asyncio
from app.services.web_ingest import run_ingest

logger = logging.getLogger(__name__)

async def scrap_news_job():
    """
    Job to be scheduled. Runs the web ingestion process for news sites.
    """
    logger.info("Starting scheduled News Scraper job...")
    try:
        # We can define a specific 'news' domain or tag in sources.yaml
        # For now, we run the generic ingest which reads sources.yaml.
        # Ideally, we'd pass a filter to run_ingest to only target "news" items,
        # but run_ingest iterates everything in sources.yaml.
        
        # Force=False ensures we don't re-ingest unchanged pages (relies on hash check in save_to_kb/ingest pipeline)
        report = await run_ingest(force=False, max_pages=5) 
        
        if report.get("ok"):
            details = report.get("details", {})
            logger.info(f"News Scraper job finished. Summary: {details}")
        else:
            logger.error(f"News Scraper job failed: {report.get('error')}")

    except Exception as e:
        logger.error(f"Exception in News Scraper job: {e}")
