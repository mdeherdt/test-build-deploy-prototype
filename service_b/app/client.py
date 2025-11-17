import os
import httpx
from typing import Dict, Any, List

# Get Service A base URL from environment variable or use default
SERVICE_A_BASE_URL = os.getenv("SERVICE_A_BASE_URL", "http://localhost:8000")

async def get_items() -> Dict[str, List[Dict[str, Any]]]:
    """
    Get all items from Service A
    
    Returns:
        Dict containing a list of items
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SERVICE_A_BASE_URL}/items")
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        return response.json()

async def transform_items(items_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Transform items data from Service A
    
    This is a simple transformation that adds a "source" field to each item.
    In a real application, you might do more complex transformations.
    
    Args:
        items_data: Data from Service A
        
    Returns:
        Transformed data
    """
    transformed_items = []
    
    for item in items_data.get("items", []):
        # Add a source field to each item
        transformed_item = {
            **item,
            "source": "service_a"
        }
        transformed_items.append(transformed_item)
    
    return {"items": transformed_items}