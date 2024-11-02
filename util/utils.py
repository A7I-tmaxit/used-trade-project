import json
import bcrypt
import os
import re
from datetime import datetime

def validate_user_id(user_id: str) -> bool:
    """
    Validate the user_id format.
    """
    return bool(re.match(r"^[a-zA-Z0-9_-]+$", user_id))

def sanitize_user_id(user_id: str) -> str:
    """
    Remove any characters that are not alphanumeric, underscore, or hyphen.
    """
    return re.sub(r"[^a-zA-Z0-9_-]", "", user_id)

def get_user_file_path(user_id: str) -> str:
    """
    Generate the file path for the user data.
    """
    base_dir = "data"
    return os.path.join(base_dir, f"{user_id}.json")

def user_exists(file_path: str) -> bool:
    """
    Check if the user already exists.
    """
    return os.path.exists(file_path)

def create_user_directory() -> None:
    """
    Create the user data directory if it does not exist.
    """
    base_dir = "data"
    os.makedirs(base_dir, exist_ok=True)

def hash_password(password: str) -> str:
    """
    Hash the password using bcrypt.
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def create_user_data(user_id: str, hashed_password: str, balance: int, created_at: str = None) -> dict:
    """
    Create the user data dictionary.
    """
    return {
        "user_id": user_id,
        "password": hashed_password,
        "point": balance,
        "created_at": created_at or datetime.now().strftime("%Y/%m/%d"),
        "registered_products": [],
        "purchased_products": [],
        "liked_products": [],
    }

def save_user_data(file_path: str, user_data: dict) -> None:
    """
    Save the user data to a file.
    """
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(user_data, f)