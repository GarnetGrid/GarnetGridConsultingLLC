"""
Vision model client for image understanding using LLaVA via Ollama.
"""
from __future__ import annotations

import os
import json
import base64
from pathlib import Path
from typing import Optional

import httpx


def _base_url() -> str:
    """Get Ollama base URL from environment"""
    return os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


def _vision_model() -> str:
    """Get vision model name from environment"""
    return os.getenv("VISION_MODEL", "llava:7b")


async def describe_image(
    image_path: Path,
    prompt: str = "Describe this image in detail, focusing on key information, data, charts, diagrams, and visual elements that would be useful for answering questions.",
    model: Optional[str] = None,
    timeout: float = 120.0
) -> str:
    """
    Generate a detailed description of an image using a vision model.
    
    Args:
        image_path: Path to the image file
        prompt: Custom prompt for description generation
        model: Vision model to use (defaults to VISION_MODEL env var)
        timeout: Request timeout in seconds
        
    Returns:
        AI-generated image description
    """
    model = model or _vision_model()
    
    # Read and encode image
    image_bytes = image_path.read_bytes()
    image_b64 = base64.b64encode(image_bytes).decode('utf-8')
    
    payload = {
        "model": model,
        "prompt": prompt,
        "images": [image_b64],
        "stream": False
    }
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            f"{_base_url()}/api/generate",
            json=payload
        )
        response.raise_for_status()
        result = response.json()
        return result.get("response", "")


async def answer_image_question(
    image_path: Path,
    question: str,
    model: Optional[str] = None,
    timeout: float = 120.0
) -> str:
    """
    Answer a specific question about an image.
    
    Args:
        image_path: Path to the image file
        question: Question to answer about the image
        model: Vision model to use
        timeout: Request timeout in seconds
        
    Returns:
        Answer to the question
    """
    model = model or _vision_model()
    
    # Read and encode image
    image_bytes = image_path.read_bytes()
    image_b64 = base64.b64encode(image_bytes).decode('utf-8')
    
    payload = {
        "model": model,
        "prompt": question,
        "images": [image_b64],
        "stream": False
    }
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            f"{_base_url()}/api/generate",
            json=payload
        )
        response.raise_for_status()
        result = response.json()
        return result.get("response", "")


async def extract_text_from_image(
    image_path: Path,
    model: Optional[str] = None,
    timeout: float = 120.0
) -> str:
    """
    Extract text from an image using OCR capabilities of vision model.
    
    Args:
        image_path: Path to the image file
        model: Vision model to use
        timeout: Request timeout in seconds
        
    Returns:
        Extracted text
    """
    prompt = "Extract all text from this image. Provide only the text content, maintaining the original structure and formatting as much as possible."
    return await describe_image(image_path, prompt, model, timeout)


async def analyze_chart(
    image_path: Path,
    model: Optional[str] = None,
    timeout: float = 120.0
) -> dict:
    """
    Analyze a chart or graph image and extract key insights.
    
    Args:
        image_path: Path to the chart image
        model: Vision model to use
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary with chart analysis
    """
    prompt = """Analyze this chart or graph and provide:
1. Chart type (bar, line, pie, etc.)
2. Title and axis labels
3. Key data points and trends
4. Main insights or conclusions

Format your response as JSON with keys: chart_type, title, axes, data_points, insights"""
    
    description = await describe_image(image_path, prompt, model, timeout)
    
    # Try to parse as JSON, fallback to plain text
    try:
        return json.loads(description)
    except json.JSONDecodeError:
        return {
            "chart_type": "unknown",
            "description": description,
            "insights": description
        }


async def check_vision_model_available(model: Optional[str] = None) -> bool:
    """
    Check if the vision model is available in Ollama.
    
    Args:
        model: Model name to check
        
    Returns:
        True if model is available
    """
    model = model or _vision_model()
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{_base_url()}/api/tags")
            response.raise_for_status()
            models = response.json().get("models", [])
            return any(m.get("name") == model for m in models)
    except Exception:
        return False
