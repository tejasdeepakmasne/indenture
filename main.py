from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

@app.post("/items/")
async def create_item(item: Item):
    """
    Endpoint to receive JSON data and return it.
    """
    return item.dict()

@app.post("/receive-json/")
async def receive_json(data: Dict):
    """
    A more generic endpoint to receive any JSON data.
    """
    print("Received JSON:", data)
    return {"message": "JSON data received successfully", "received_data": data}

@app.post("/process-json/")
async def process_json(payload: dict):
    """
    Another way to receive and process arbitrary JSON.
    """
    print("Processing payload:", payload)
    result = {"status": "success", "received": payload}
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
