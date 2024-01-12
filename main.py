from fastapi import FastAPI

from src.routes import posts

app = FastAPI()

app.include_router(posts.router, prefix='/api')


@app.get("/")
def read_root():
    return {"message": "Hello World"}
