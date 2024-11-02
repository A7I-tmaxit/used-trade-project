from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from util.utils import (
    validate_user_id,
    sanitize_user_id,
    get_user_file_path,
    user_exists,
    create_user_directory,
    hash_password,
    create_user_data,
    save_user_data,
)

router = APIRouter()

@router.post("/signup")
async def signup(request: Request):
    data = await request.json()

    user_id = data.get("registerUsername")
    password = data.get("registerPassword")
    balance = data.get("registerBalance", 0)

    if not user_id or not password:
        raise HTTPException(status_code=400, detail="user_id and password are required")

    if not validate_user_id(user_id):
        raise HTTPException(status_code=400, detail="Invalid user_id format")

    sanitized_user_id = sanitize_user_id(user_id)
    file_path = get_user_file_path(sanitized_user_id)

    if user_exists(file_path):
        return JSONResponse(
            content={"message": "이미 존재하는 아이디입니다."}, status_code=400
        )

    create_user_directory()

    hashed_password = hash_password(password)
    user_data = create_user_data(
        sanitized_user_id, hashed_password, balance, data.get("created_at")
    )

    save_user_data(file_path, user_data)

    return JSONResponse(content={"message": "회원가입 성공"}, status_code=201)