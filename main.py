
from pathlib import Path

from src.conf import messages

import redis.asyncio as redis

from typing import Callable

from pydantic import ConfigDict

from ipaddress import ip_address
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.database.db import get_db
from src.routes import auth, users, posts, tags, photo_url_qr, comments
from src.conf.config import settings
from src.schemas import user

app = FastAPI()
BASE_DIR = Path(__file__).parent
directory = BASE_DIR / "src" / "static"
app.mount("/src/static", StaticFiles(directory=directory), name="static")

banned_ips = [ip_address("192.168.255.1"), ip_address("192.168.255.1")]

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix='/api')
app.include_router(posts.router, prefix='/api')
app.include_router(users.router, prefix='/api')
app.include_router(tags.router, prefix="/api")
app.include_router(photo_url_qr.router, prefix='/api')
app.include_router(comments.router, prefix='/api')

templates = Jinja2Templates(directory=BASE_DIR / "src" / "templates")


@app.middleware("http")
async def ban_ips(request: Request, call_next: Callable):
    """
    The ban_ips function is a middleware function that checks if the client's IP address
    is in the banned_ips list. If it is, then we return a JSON response with status code 403
    and an error message. Otherwise, we call the next middleware function and return its response.

    :param request: Request: Get the client's ip address
    :param call_next: Callable: Pass the next function in the middleware chain to ban_ips
    :return: A jsonresponse with a status code of 403 and a message
    :doc-author: Trelent
    """
    if settings.APP_ENV == "production":
        ip = ip_address(request.client.host)
        if ip in banned_ips:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN, content={"detail": messages.MAIN_IP_BANNED}
            )
    response = await call_next(request)
    return response


@app.on_event("startup")
async def startup():
    """
    The startup function is called when the application starts up.
    It's a good place to initialize things that are needed by your app,
    like connecting to databases or initializing caches.

    :return: A list of functions that are executed when the application starts
    :doc-author: Trelent
    """
    r = await redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=0,
        password=settings.REDIS_PASSWORD,
    )
    await FastAPILimiter.init(r)


@app.get("/", response_class=HTMLResponse, description="Main Page")
async def read_root(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "title": "Killer Instagram App"}
    )


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    The healthchecker function is a simple function that checks the health of the database.
    It does this by executing a SQL query to check if it can connect to the database and retrieve data.
    If it cannot, then an HTTPException is raised with status code 500 (Internal Server Error) and detail message &quot;Error connection to database&quot;.
    Otherwise, if everything works as expected, then we return {&quot;message&quot;: &quot;Welcome to FastAPI!&quot;}.

    :param db: AsyncSession: Get the database session
    :return: A dictionary with a message
    :doc-author: Trelent
    """
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(
                status_code=500, detail=messages.MAIN_DB_NOT_CONFIGURED
            )
        return {"message": messages.WELCOME_MESSAGE}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=messages.MAIN_DB_ERROR_CONNECTION)
