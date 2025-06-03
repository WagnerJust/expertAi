from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    pdf_dir: str = "./pdf_storage"
    db_url: str = "sqlite:///./local_database.sqlite"

settings = Settings()
