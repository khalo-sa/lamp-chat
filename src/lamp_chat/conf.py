from pydantic_settings import BaseSettings


class Config(BaseSettings):
    use_model: str = "gpt-4o-mini"


conf = Config()
