import re
import os
import json
import bcrypt
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/login")
async def login(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    password = data.get("password")

    if not user_id or not password:
        raise HTTPException(status_code=400, detail="user_id and password are required")

    sanitized_user_id = sanitize_user_id(user_id)
    user_data = get_user_data(sanitized_user_id)

    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(password, user_data.get("password")):
        raise HTTPException(status_code=401, detail="Invalid password")

    # 로그인 성공 시 사용자 데이터를 반환 (비밀번호 제외)
    user_data.pop("password", None)
    return JSONResponse(content=user_data, status_code=200)


def sanitize_user_id(user_id):
    """
    Remove any characters that are not alphanumeric, underscore, or hyphen.
    """
    return re.sub(r"[^a-zA-Z0-9_-]", "", user_id)


def get_user_data(user_id):
    """
    Retrieve user data from the file system.
    """
    file_path = os.path.join("data", f"{user_id}.json")
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except IOError:
        return None


def verify_password(input_password, stored_password):
    """
    Verify the input password against the stored password.
    """
    return bcrypt.checkpw(
        input_password.encode("utf-8"), stored_password.encode("utf-8")
    )
