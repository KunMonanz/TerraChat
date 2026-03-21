import uuid

from tortoise import fields, models

from models.base.black_listed_token_base import BlackListedTokenBase


class BlackListedTokenCloud(BlackListedTokenBase):

    class Meta:
        app = "cloud_models"
        table = "blacklisted_tokens"
