from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "users" (
    "id" CHAR(36) NOT NULL PRIMARY KEY,
    "username" VARCHAR(50) NOT NULL UNIQUE,
    "email" VARCHAR(100) NOT NULL UNIQUE,
    "hashed_password" VARCHAR(255) NOT NULL,
    "location" VARCHAR(100) NOT NULL
);
CREATE TABLE IF NOT EXISTS "questions" (
    "id" CHAR(36) NOT NULL PRIMARY KEY,
    "question_text" TEXT NOT NULL,
    "answer_text" TEXT NOT NULL,
    "answer_type" VARCHAR(10) NOT NULL,
    "created_at" TIMESTAMP NOT NULL,
    "updated_at" TIMESTAMP NOT NULL,
    "user_id" CHAR(36) NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "changes" (
    "id" CHAR(36) NOT NULL PRIMARY KEY,
    "change_type" VARCHAR(6) NOT NULL,
    "payload" JSON NOT NULL,
    "model" VARCHAR(100) NOT NULL,
    "used" INT NOT NULL,
    "created_at" TIMESTAMP NOT NULL,
    "user_id" CHAR(36) NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
