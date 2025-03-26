from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.endpoints import router
from app.utils.file_cleanup import cleanup_temp_files, _temp_files

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    yield
    # Cleanup code
    cleanup_temp_files()

app = FastAPI(
    title="Document Generation Service",
    description="An API to generate PDF and DOCX documents from HTML input.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def home():
    return {"message": "Welcome to the Document Generation API!"}