from fastapi import FastAPI

from src.routes import photo_url_qr

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello World"}


app.include_router(photo_url_qr.router, prefix='/api')

