from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas, db

# Create FastAPI app
app = FastAPI(title="Service A - Item API")

# Create tables in the database
models.Base.metadata.create_all(bind=db.engine)

@app.post("/items", response_model=schemas.Item, status_code=status.HTTP_201_CREATED)
def create_item(item: schemas.ItemCreate, db_session: Session = Depends(db.get_db)):
    """Create a new item in the database"""
    db_item = models.Item(value=item.value)
    db_session.add(db_item)
    db_session.commit()
    db_session.refresh(db_item)
    return db_item

@app.get("/items", response_model=schemas.ItemList)
def read_items(skip: int = 0, limit: int = 100, db_session: Session = Depends(db.get_db)):
    """Get all items from the database"""
    items = db_session.query(models.Item).offset(skip).limit(limit).all()
    return {"items": items}

@app.get("/items/count", response_model=int)
def count_items(db_session: Session = Depends(db.get_db)):
    """Count all items in the database"""
    count = db_session.query(models.Item).count()
    return count

@app.get("/items/search", response_model=schemas.ItemList)
def search_items(q: str, db_session: Session = Depends(db.get_db)):
    """Search items by value"""
    items = db_session.query(models.Item).filter(models.Item.value.contains(q)).all()
    return {"items": items}

@app.get("/items/{item_id}", response_model=schemas.Item)
def read_item(item_id: int, db_session: Session = Depends(db.get_db)):
    """Get a specific item by ID"""
    item = db_session.query(models.Item).filter(models.Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db_session: Session = Depends(db.get_db)):
    """Delete an item by ID"""
    item = db_session.query(models.Item).filter(models.Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db_session.delete(item)
    db_session.commit()
    return None

@app.put("/items/{item_id}", response_model=schemas.Item)
def update_item(item_id: int, item: schemas.ItemCreate, db_session: Session = Depends(db.get_db)):
    """Update an item by ID"""
    db_item = db_session.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db_item.value = item.value
    db_session.commit()
    db_session.refresh(db_item)
    return db_item


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
