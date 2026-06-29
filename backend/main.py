from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import init_db
from backend.seed.seed_hops import seed
from backend.routes import parse, search, hops

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed()
    yield

app = FastAPI(
    title="HackerFlights India API",
    description="USA->India LCC hop-chain optimizer with Mistral Nemo NLP",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(parse.router)
app.include_router(search.router)
app.include_router(hops.router)

@app.get("/health")
def health():
    return {"status": "ok", "service": "HackerFlights India API"}
