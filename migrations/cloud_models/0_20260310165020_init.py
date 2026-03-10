from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "users" (
    "id" UUID NOT NULL PRIMARY KEY,
    "username" VARCHAR(50) NOT NULL UNIQUE,
    "email" VARCHAR(100) NOT NULL UNIQUE,
    "hashed_password" VARCHAR(255) NOT NULL,
    "location" VARCHAR(100) NOT NULL
);
CREATE TABLE IF NOT EXISTS "questions" (
    "id" UUID NOT NULL PRIMARY KEY,
    "question_text" TEXT NOT NULL,
    "answer_text" TEXT NOT NULL,
    "answer_type" VARCHAR(10) NOT NULL DEFAULT '',
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" UUID NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "eJztmG1P2zAQgP9KlU9MYghKy9A0TQptGR3QbpBuCIQiN3bTiMQOsbNSof732W7SvKcEtd"
    "BKfKmae4nvHju+s58VwyY+1B0CkU33WuJhQJGnfK09Kxg4iP8pMtmtKcB10wZCzMDQlp4+"
    "t5MSMKTMAwbjwhGwKeIiiKjhWS6zCOZS7Nu2EBKDG1rYjEQ+th59pDNiIjaWkd3dc7GFIX"
    "pCNHx0H/SRhWyYCNyCYmwp19nUlbLBoNs+lZZiuKFuENt3cGTtTtmY4IW571twT/gInYkw"
    "8gBDMJaGiDJINxTNI+YC5vloESqMBBCNgG8LGMq3kY8NwaAmRxI/je9KBTwGwQKthZlg8T"
    "ybZxXlLKWKGKp1pl7tHB59klkSykxPKiURZSYdAQNzV8k1AinmUf7P4GyNgZePM+6TgsoD"
    "Xg/OENPr2CkOeNJthE025o/N/RKWf9QribO5L3ESvrbnK74XaOpSJahGFJEDLLsKwoXDNv"
    "I72H8JQG5VSFDqkgjHgI4R1F1A6YR4OZ93Mcwc19VgDQUR12iLWwfYerP5ArDcqhCs1CXB"
    "2sQAMqwKROM+24lyZWtUlKDRQ2zvFIIhMB4mwIN6QhMx5zlTET/NQj8JXE/Pr5BdBDlRl3"
    "8HL5P1eTPZz8IFFEqDLUjSI3VShC+rcupOWgIwMGXUYmwxUgmdwuYmA3FZg5OYwo8mZ6ub"
    "nHAudYaeWJapxqX5TDOO27IZlnDUOjeaCNqh9NGOb3k7l+qNpOtMA81Fv/cjNI9tka2L/k"
    "mqyABMJ8irzDfl9nZ0lfWs0bWyFVQq1PCU23awTRfxF9XwkhKeboYMD4lsdZCzTNtcwywH"
    "5eNMeqZowsB1L/yzmbuCwnOAfWxPw/JcspK7l51rTb38lVjObVXrCE09sZRD6c5RaiYWL6"
    "n97WpnNfFYu+33OuktfGGn3SoiJuAzomMy0QGMlZ1QGoJJTKzvwldObNLzY2LfdWKD4JP3"
    "E3q1Rijmsspu6F2L9pLmJ3NISQLM0jslHrJMfI6mkmGXxwGwkVcoiq8INxZg5hjCxR6YLD"
    "rs+ArhmfLMEJsXU/W6pbY7yqz4jLf+A42KPMsYK4UnmUC/u/wIAyLLjTm/dHFBK5j7wYop"
    "TK20YD7f9TbMFKN8rh80vjSOD48ax9xERrKQfCn5lLs9bclx5R/yaMULm5jLthxR3uDqS3"
    "wgVTrmufl2AlzLpSwfkSGc01L9vO73CvrkyCUFcoB5gnfQMthuzbYou99MrCUURdblx7v0"
    "SS5VrsULTqpdKq6+4Mz+A886EJE="
)
