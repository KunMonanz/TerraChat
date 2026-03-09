from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE UNIQUE INDEX IF NOT EXISTS "uid_users_usernam_266d85" ON "users" ("username");
        CREATE UNIQUE INDEX IF NOT EXISTS "uid_users_email_133a6f" ON "users" ("email");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" DROP CONSTRAINT IF EXISTS "users_email_key";
        DROP INDEX IF EXISTS "uid_users_email_133a6f";
        ALTER TABLE "users" DROP CONSTRAINT IF EXISTS "users_username_key";
        DROP INDEX IF EXISTS "uid_users_usernam_266d85";"""


MODELS_STATE = (
    "eJzVlm1r2zAQx79K8KsOupKmSVvGGKQZYxlbCt0yBqUYRVJsEVlyLXltCfnu1V0e/JA4i0"
    "dDmzfB+t9d7u5nSeepR6VOmR9pxqU56cFiaHjifWhMPUUi7h6qXI4bHonjsgPIlowkRqbO"
    "DxUyMjYh1DpxTKThTmLc0ETEVmjlVJVKCaKmzlGoIJNSJe5T7lsdcBtiZbd3ThaK8Uduls"
    "t44o8Fl6xQuGCQG3XfPsWoDYf9z1/QE9KNfKplGqnMO36yoVYr9zQV7ARiwBZwxRNiOcu1"
    "AVUu2l1K84qdYJOUr0plmcD4mKQSYHgfx6miwKCBmeCn/cmrgYdqBWiFssBiOpt3lfWMqg"
    "epel+7N0dn5++wS21skKARiXgzDCSWzEORawYS3iM+r+HshSTZjDMfU4LqCt4PziWm/2Pn"
    "ReTRl1wFNnTLTnMLy9/dG8TZaSJO7fb2fMcPFpYWmoBqRpFHRMg6CFcBh8jvtLkLQOdVSR"
    "BtRYQhMSFnfkyMedDJhuNdDXND6MtgXQoZ1+yK2wfYVqezA1jnVQkWbUWwUlOCZdUgmo85"
    "TJQvtkdhBI0nubsThBGhkweSMH/Nolu6ynfdFLWiskIUCRAPNAkdFEZ0lyeChtUjfGHfYX"
    "6TzPPNDPC+sjXmt3vv5Y24uPVe9aYMIMv71mn7on15dt6+dC5YyUq52LIv+4Nf/5jXf91n"
    "V83DnAs5zLO8l2sRDkgNiAv3wwS4l4HtMlo+P4NFiN9+Xg82Q8yFlEAOlWvwlglqjxtSGH"
    "v3NrFuoQhdQ9GRMfcyD+/oR/dPmWvv+/VV+WMd/uDqtQfO7Bm9c44c"
)
