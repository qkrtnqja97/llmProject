# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel

# app = FastAPI()

# # 🔥 프론트 주소들 (지금 Vite가 5173 / 5174 둘 다 쓸 수도 있어서 다 넣음)
# origins = [
#     "http://localhost:5173",
#     "http://localhost:5174",
#     "http://127.0.0.1:5173",
#     "http://127.0.0.1:5174",
#     "http://192.168.0.243:5173",
#     "http://192.168.0.243:5174",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],      # 개발 중이라면 ["*"] 해도 됨
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# class Prompt(BaseModel):
#     prompt: str

# @app.post("/v1/")
# async def search(req: Prompt):
#     print("프론트에서 받은 값:", req.prompt)
#     # 여기서 나중에 진짜 검색/LLM 로직 넣으면 됨
#     return {"response": f"'{req.prompt}' 에 대한 더미 응답입니다."}

