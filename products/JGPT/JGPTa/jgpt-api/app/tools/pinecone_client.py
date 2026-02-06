import os
import logging
from pinecone import Pinecone

logger = logging.getLogger(__name__)

def get_pinecone_client():
    """
    Initializes and returns a Pinecone client.
    Returns None if PINECONE_API_KEY is not set.
    """
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        logger.warning("PINECONE_API_KEY is not set. Pinecone features will be disabled.")
        return None

    try:
        pc = Pinecone(api_key=api_key)
        return pc
    except Exception as e:
        logger.error(f"Failed to initialize Pinecone client: {e}")
        return None
