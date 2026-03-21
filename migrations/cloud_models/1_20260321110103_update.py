from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" ALTER COLUMN "hashed_password" TYPE VARCHAR(255) USING "hashed_password"::VARCHAR(255);
        ALTER TABLE "users" ALTER COLUMN "location" TYPE VARCHAR(100) USING "location"::VARCHAR(100);
        ALTER TABLE "users" ALTER COLUMN "username" TYPE VARCHAR(50) USING "username"::VARCHAR(50);
        ALTER TABLE "users" ALTER COLUMN "email" TYPE VARCHAR(100) USING "email"::VARCHAR(100);
        ALTER TABLE "questions" ALTER COLUMN "question_text" TYPE TEXT USING "question_text"::TEXT;
        ALTER TABLE "questions" ALTER COLUMN "created_at" TYPE TIMESTAMPTZ USING "created_at"::TIMESTAMPTZ;
        ALTER TABLE "questions" ALTER COLUMN "user_id" TYPE UUID USING "user_id"::UUID;
        ALTER TABLE "questions" ALTER COLUMN "updated_at" TYPE TIMESTAMPTZ USING "updated_at"::TIMESTAMPTZ;
        ALTER TABLE "questions" ALTER COLUMN "answer_type" TYPE VARCHAR(10) USING "answer_type"::VARCHAR(10);
        ALTER TABLE "questions" ALTER COLUMN "answer_text" TYPE TEXT USING "answer_text"::TEXT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" ALTER COLUMN "hashed_password" TYPE VARCHAR(255) USING "hashed_password"::VARCHAR(255);
        ALTER TABLE "users" ALTER COLUMN "location" TYPE VARCHAR(100) USING "location"::VARCHAR(100);
        ALTER TABLE "users" ALTER COLUMN "username" TYPE VARCHAR(50) USING "username"::VARCHAR(50);
        ALTER TABLE "users" ALTER COLUMN "email" TYPE VARCHAR(100) USING "email"::VARCHAR(100);
        ALTER TABLE "questions" ALTER COLUMN "question_text" TYPE TEXT USING "question_text"::TEXT;
        ALTER TABLE "questions" ALTER COLUMN "created_at" TYPE TIMESTAMPTZ USING "created_at"::TIMESTAMPTZ;
        ALTER TABLE "questions" ALTER COLUMN "user_id" TYPE UUID USING "user_id"::UUID;
        ALTER TABLE "questions" ALTER COLUMN "updated_at" TYPE TIMESTAMPTZ USING "updated_at"::TIMESTAMPTZ;
        ALTER TABLE "questions" ALTER COLUMN "answer_type" TYPE VARCHAR(10) USING "answer_type"::VARCHAR(10);
        ALTER TABLE "questions" ALTER COLUMN "answer_text" TYPE TEXT USING "answer_text"::TEXT;"""
