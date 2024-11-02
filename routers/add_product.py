from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
import json
import os

router = APIRouter()


@router.post("/add_product")
async def add_product(request: Request):
    try:
        data = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    required_fields = [
        "user_id",
        "name",
        "description",
        "price",
        "images",
        "mainImage",
        "sellerName",
    ]
    for field in required_fields:
        if field not in data:
            raise HTTPException(status_code=400, detail=f"Missing field: {field}")

    seller_id = data["user_id"]
    timestamp = datetime.now().strftime("%Y%m%d")
    product_key = f"{seller_id}_{timestamp}"

    file_path = f"./data/{seller_id}.json"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Seller data not found")

    try:
        with open(file_path, "r") as f:
            seller_data = json.load(f)
    except Exception:
        raise HTTPException(status_code=500, detail="Error reading seller data")

    new_product = {
        "name": data["name"],
        "key": product_key,
        "description": data["description"],
        "price": int(data["price"]),
        "images": data["images"],
        "mainImage": data["mainImage"],
        "sellerName": data["sellerName"],
        "sellerId": seller_id,
        "dateAdded": datetime.now().strftime("%Y%m%d"),
    }

    seller_data["registered_products"].append(new_product)

    try:
        with open(file_path, "w") as f:
            json.dump(seller_data, f, indent=4)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error saving seller data")

    return JSONResponse(
        content={"message": "Product added successfully!"}, status_code=200
    )
