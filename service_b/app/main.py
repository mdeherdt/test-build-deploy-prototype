from fastapi import FastAPI, HTTPException
from typing import Dict, Any, List
import httpx

from . import client

# Create FastAPI app
app = FastAPI(title="Service B - Proxy API")

@app.get("/proxy-items")
async def proxy_items():
    """
    Proxy endpoint that gets items from Service A and transforms them

    Returns:
        Dict containing a list of transformed items
    """
    try:
        # Get items from Service A
        items_data = await client.get_items()

        # Transform the items
        transformed_data = client.transform_items(items_data)

        return transformed_data
    except Exception as e:
        # Handle errors (e.g., Service A is down)
        raise HTTPException(
            status_code=503,
            detail=f"Error communicating with Service A: {str(e)}"
        )

@app.get("/proxy-items/search")
async def proxy_search_items(q: str):
    """
    Proxy endpoint that searches items from Service A and transforms them

    Args:
        q: Search query

    Returns:
        Dict containing a list of transformed items
    """
    try:
        # Search items from Service A
        items_data = await client.search_items(q)

        # Transform the items
        transformed_data = client.transform_items(items_data)

        return transformed_data
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Error communicating with Service A: {str(e)}"
        )

@app.get("/proxy-items/count")
async def proxy_count_items():
    """
    Proxy endpoint that counts items from Service A

    Returns:
        Number of items
    """
    try:
        # Count items from Service A
        count = await client.count_items()
        return count
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Error communicating with Service A: {str(e)}"
        )

@app.get("/proxy-items/{item_id}")
async def proxy_item(item_id: int):
    """
    Proxy endpoint that gets a specific item from Service A and transforms it

    Args:
        item_id: ID of the item to get

    Returns:
        Dict containing the transformed item
    """
    try:
        # Get the item from Service A
        item_data = await client.get_item(item_id)

        # Add the source field
        transformed_item = {
            **item_data,
            "source": "service_a"
        }

        return transformed_item
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Item not found")
        raise HTTPException(
            status_code=503,
            detail=f"Error communicating with Service A: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Error communicating with Service A: {str(e)}"
        )

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
