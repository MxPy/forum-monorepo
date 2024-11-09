from pydantic import AmqpDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    AMQP_URL: AmqpDsn = "amqp://rabbitmq?connection_attempts=5&retry_delay=5"
    PREFECTH_COUNT = 100

settings = Settings()  # pyright: ignore