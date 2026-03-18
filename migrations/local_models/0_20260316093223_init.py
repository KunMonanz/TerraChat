from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


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
    "answer_type" VARCHAR(10) NOT NULL DEFAULT '',
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" CHAR(36) NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "eJztmG1v2jAQx78KyqtOmqqOjb6Ypkkp0BX1ga1Nt6rTFJnYhKiOncWOKKr47vOZhMR5oK"
    "WCtUh9U5H/3eG7n68+hweLcg9RN+SYULF/Bg/XgsTW59aDxVBI1Icml/ctC0VR2QFkiUZU"
    "RybKTytoJGSMPKnEMaKCKAkT4cVBJAPOlMoSSkHknnIMmJ9LCQv+JsSV3CdyojP7/UfJAc"
    "PknojsMbpzxwGh2Eg8wLC21l05i7R2fT3oHWtPWG7kepwmIcu9o5mccLZ0T5IA70MM2HzC"
    "SIwkwYUyIMu03ExaZKwEGSdkmSrOBUzGKKEAw/oyTpgHDFp6Jfjz6au1Bh6PM0AbMAksHu"
    "aLqvKatWrBUt0T+3Lv4+E7XSUX0o+1UROx5joQSbQI1VxzkLCP+nMFZ3eC4nqcxZgSVJXw"
    "dnBmmJ7HzgrRvUsJ8+VEPXYOVrD8aV9qnJ0DjZOr3l50/EVqaWsTUM0pkhAFdB2Ey4Bd5P"
    "fh4CkAlVcjQW0zEU6QmBDsRkiIKY9r/r2bYdaEbgZrJuRc8yNuG2Dbnc4TwCqvRrDaZoKF"
    "I1yntQbRYsxuotxYj8IIGt8Vzk4QRsi7m6IYu4YlZ65qFpC/qEI/SkOPTy8JbYJszOUf6Z"
    "fp+fw62c+zBsrU9AjS9HibN+GrmsJ2WFYQQ77OGtaGlVbQabzcVCA+dsExtvDtkrPTl5xs"
    "L11J7mWVqaPUeqaVwF05DFdwdPo3DiQdCvGXFo+8vXP7RtMNZ6nlbHjxLXMvHJHds+FRac"
    "ggJqYkXptvKez/0bW206NbZQtU1pjhpbDdYFse4k+a4StGePky5MUEqnVRTZv2lEUGIanH"
    "aUaWaOI0dD/78DpPBUvVgIeMzrLxvKKTB+f9K8c+/260c892+mBpG62cqXuHpZ1Yfknr18"
    "A5acFj63Z40S8f4Us/59aCnFAiucv41EW4MHYyNQNjbGwS4WdurBn5trEvurFp8ubvE+56"
    "F6FCyCZvQy86tB+5/FReUkyAVXrHPCaBz07JTDMcqDwQ8+oGRfNPhK8WYOU1RMkxmi5v2M"
    "UOUZWqyohcDFP7qmv3+ta8+R1v8y8083+GSgIT"
)
