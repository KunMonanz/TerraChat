from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "users" (
    "id" UUID NOT NULL PRIMARY KEY,
    "username" VARCHAR(50) NOT NULL,
    "email" VARCHAR(100) NOT NULL,
    "hashed_password" VARCHAR(255) NOT NULL,
    "location" VARCHAR(100) NOT NULL
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
    "eJzVlm1r2zAQx79K8KsOupKmSVvGGKQZYxlbCt0yBqUYRVJsEVlyLWltCfnu010e7LhxFr"
    "cra94E+393ubufTz5PAyq1Y2GiGZfmqAc3Q8Oz4F1jGiiScH9R5XLYCEialh1AtmQkMdJ5"
    "P1TIyNiMUOvFMZGGe4lxQzORWqGVV5WTEkRNvaNQUS45JW4dD62OuI2xsusbLwvF+D03y9"
    "t0Eo4Fl2ytcMEgN+qhfUhRGw77Hz+hJ6QbhVRLl6jcO32wsVYrd+cEO4IYsEVc8YxYzgpt"
    "QJWLdpfSvGIv2MzxVaksFxgfEycBRvB+7BQFBg3MBD/tD0ENPFQrQCuUBRbT2byrvGdUA0"
    "jV+9y9Ojg5fYNdamOjDI1IJJhhILFkHopcc5DwHPH6Ec5eTLLNOIsxJai+4KfgXAo5z3yW"
    "lkCXoJ5GL0jIfSi5imzsbzvNLTR/dq8QaKeJQLWf7vnMDxaWFpqAa86RJ0TIOhBXAftJ8L"
    "i5C0LvVckQbesQY2JizsKUGHOnsw1HvBrnhtD9BNvqdHYA670qwaJtHazUlGBZNYgWY/YT"
    "5T+bUVhD40nh/QnCiNDJHclY+MiiW7rK97EpaSVlhSgSIR5oEjpYW9NdngkaV6/xhX2HHU"
    "5yz1ezxPvK1tjh/rmXB3GxiJ+3vJ85hRFkeds6bp+1z09O2+feBStZKWdb5rI/+PGXnf3b"
    "f3rVPMyFkP08yy/yWoQDUgPiwn0/Ab7IwvYZLZ+fwXWIX75fDjZDLISUQA6Vb/CaCWoPG1"
    "IYe/M6sW6hCF1D0Ykxt7II7+Bb91eZa+/r5UX5gx3+4OJ/L5zZH9Yej0g="
)
