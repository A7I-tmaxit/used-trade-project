from fastapi import FastAPI
from fastapi.responses import FileResponse
import uvicorn
import importlib
import os

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI()


# 라우터 포함
def include_router():
    routers_dir = "./routers"
    for filename in os.listdir(routers_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"routers.{filename[:-3]}"
            module = importlib.import_module(module_name)
            app.include_router(module.router)


include_router()


# 파비콘 요청 처리
@app.get("/favicon.ico")
async def get_favicon():
    return ""


# 루트 경로 요청 처리
@app.get("/")
async def root():
    # index.html 파일을 응답으로 반환
    return FileResponse("./templates/index.html")


# 애플리케이션 실행
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
