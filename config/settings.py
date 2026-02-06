from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    mongo_user: str
    mongo_password: str
    mongo_host: str

    @property
    def mongo_uri(self) -> str:
        return f"mongodb+srv://{self.mongo_user}:{self.mongo_password}@{self.mongo_host}/?retryWrites=true&w=majority"

settings = Settings()