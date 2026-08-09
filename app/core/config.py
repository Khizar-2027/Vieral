from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./vieral_dev.db"
    storage_dir: str = "./storage"

    class Config:
        env_file = ".env"


settings = Settings()