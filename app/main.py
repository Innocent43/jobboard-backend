from fastapi import FastAPI
from app.routers import users
from app.routers import jobs
from app.routers import applications
from app.routers import auth
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.limiter import limiter
from app.core.logging import setup_logging
from app.routers import message
import time
from fastapi import Request
import logging

logger = logging.getLogger(__name__)
setup_logging()

app: FastAPI = FastAPI(title="JOBBOARD")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded,_rate_limit_exceeded_handler)


app.middleware("http")
async def log_request_timing(request: Request,call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} completed in {duration:.3f}s")
    return response

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_V1_PREFIX = "/api/v1"
app.include_router(users.router,prefix=API_V1_PREFIX)
app.include_router(jobs.router,prefix=API_V1_PREFIX)
app.include_router(applications.router,prefix=API_V1_PREFIX)
app.include_router(auth.router,prefix=API_V1_PREFIX)
app.include_router(message.router,prefix=API_V1_PREFIX)

@app.get("/")
def get_root()-> dict[str,str]:
    return {"message": "DevBoard API is running"}

