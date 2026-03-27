from contextlib import asynccontextmanager

from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from background_worker import SyncWorker
from db.tortoise_config import TORTOISE_ORM
from users.users_routers import router as user_router
from questions.questions_routers import router as question_router

worker = SyncWorker(interval=5)

# --------------------------
# Lifespan context
# --------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    await worker.start()
    try:
        yield
    finally:
        await worker.stop()


# --------------------------
# FastAPI app
# --------------------------
app = FastAPI(
    doc_urls="/docs",
    swagger_ui_parameters={"syntaxHighlight": False},  # fix typo
    lifespan=lifespan
)

# Register Tortoise ORM
register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True,
)

# Include routers
app.include_router(user_router)
app.include_router(question_router)
