import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any
from passlib.context import CryptContext

app = FastAPI()

USER_DATA_FILE = "user_data.json"
PRODUCT_DATA_FILE = "product_data.json"

app.mount("/static", StaticFiles(directory="static"), name="static")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(BaseModel):
    username: str
    password: str
    name: str
    balance: int = Field(default=0)

    @field_validator("password")
    def hash_password(cls, v):
        return pwd_context.hash(v)


class UserLogin(BaseModel):
    username: str
    password: str


class Product(BaseModel):
    product_id: str
    name: str
    price: float

    @field_validator("price")
    def check_price(cls, v):
        if v <= 0:
            raise ValueError("Price must be a positive number")
        return v


def load_data(file_path: str) -> Dict[str, Any]:
    """Load JSON data from a file and return it as a dictionary."""
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_data(file_path: str, data: Dict[str, Any]) -> None:
    """Save a dictionary as JSON to a specified file."""
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


def user_exists(users: Dict[str, Any], username: str) -> bool:
    """Check if a user exists in the users dictionary."""
    return username in users


@app.get("/")
async def root():
    """Serve the main HTML page."""
    return FileResponse("./templates/index.html")


@app.get("/favicon.ico")
async def get_favicon():
    """Serve the favicon."""
    return ""


@app.post("/register")
async def register(user: User):
    """Register a new user."""
    users = load_data(USER_DATA_FILE)

    if user_exists(users, user.username):
        raise HTTPException(status_code=400, detail="Username already exists")

    users[user.username] = user.dict()
    save_data(USER_DATA_FILE, users)
    return {"message": "User registered successfully"}


@app.post("/login")
async def login(user: UserLogin):
    """Log in an existing user."""
    users = load_data(USER_DATA_FILE)

    if not user_exists(users, user.username):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    user_data = users[user.username]
    if not pwd_context.verify(user.password, user_data["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {
        "message": "Login successful",
        "userId": user.username,
        "name": user_data["name"],
        "balance": user_data["balance"],
    }


@app.post("/add_product")
async def add_product(product: Product):
    """Add a new product."""
    products = load_data(PRODUCT_DATA_FILE)

    if product.product_id in products:
        raise HTTPException(status_code=400, detail="Product ID already exists")

    products[product.product_id] = product.dict()
    save_data(PRODUCT_DATA_FILE, products)
    return {"message": "Product added successfully"}


@app.get("/products")
async def get_products():
    """Retrieve a list of all products."""
    products = load_data(PRODUCT_DATA_FILE)
    return products


@app.put("/update_product/{product_id}")
async def update_product(product_id: str, product: Product):
    """Update an existing product."""
    products = load_data(PRODUCT_DATA_FILE)

    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")

    products[product_id] = product.model_dump()
    for key, value in product.model_dump().items():
        products[product_id][key] = value
    save_data(PRODUCT_DATA_FILE, products)
    return {"message": "Product updated successfully"}


@app.delete("/delete_product/{product_id}")
async def delete_product(product_id: str):
    """Delete a product."""
    products = load_data(PRODUCT_DATA_FILE)

    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")

    del products[product_id]
    save_data(PRODUCT_DATA_FILE, products)
    return {"message": "Product deleted successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
