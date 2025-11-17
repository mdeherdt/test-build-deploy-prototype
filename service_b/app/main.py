from fastapi import FastAPI, HTTPException
from typing import Dict, Any, List

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
        transformed_data = await client.transform_items(items_data)
        
        return transformed_data
    except Exception as e:
        # Handle errors (e.g., Service A is down)
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