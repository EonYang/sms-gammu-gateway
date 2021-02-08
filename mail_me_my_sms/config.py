
from pydantic import BaseModel

import os


class Config(BaseModel):

    REDIS_PORT: int = 6379
    REDIS_HOST: str = 'pi'
    RECEIVER_EMAIL: str = 'yangthere@gmail.com'
    SENDGRID_API_KEY: str
    REDIS_DB: int = 6
    SMS_CHECK_INTERVAL: int = 6


CONF = Config(**os.environ)
