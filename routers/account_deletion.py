import os
import json
import bcrypt
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter()


@router.delete("/delete_account")
async def delete_account(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    password = data.get("password")

    if not user_id or not password:
        raise HTTPException(status_code=400, detail="user_id and password are required")

    file_path = os.path.join("data", f"{user_id}.json")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="User not found")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            user_data = json.load(f)
    except IOError:
        raise HTTPException(status_code=500, detail="Internal Server Error")

    if not bcrypt.checkpw(
        password.encode("utf-8"), user_data.get("password").encode("utf-8")
    ):
        raise HTTPException(status_code=401, detail="Invalid password")

    try:
        os.remove(file_path)
    except IOError:
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return JSONResponse(
        content={"message": "회원탈퇴가 완료되었습니다."}, status_code=200
    )
