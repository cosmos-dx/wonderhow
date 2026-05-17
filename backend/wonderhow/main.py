import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from wonderhow.api.routes import router as api_router
from wonderhow.api.websocket import router as ws_router
from wonderhow.config import settings
from wonderhow.db.database import engine, Base
from wonderhow.orchestrator.lifecycle import Orchestrator


orchestrator = Orchestrator()


@asynccontextmanager
async def lifespan(app: FastAPI):
    from wonderhow.db import tables  # noqa: F401 - ensure models are registered
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    task = asyncio.create_task(orchestrator.run())
    yield
    orchestrator.stop()
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    await engine.dispose()


app = FastAPI(
    title="WonderHow",
    description="Autonomous multi-agent social simulation",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
app.include_router(ws_router, prefix="/ws")
