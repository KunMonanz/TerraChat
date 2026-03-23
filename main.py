from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from db.tortoise_config import TORTOISE_ORM
from users.users_routers import router as user_router
from questions.questions_routers import router as question_router

app = FastAPI(
    doc_urls="/docs",
    swagger_ui_parameters={"syntaxHighligtht": False}
)

register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True,
)

app.include_router(user_router)
app.include_router(question_router)
