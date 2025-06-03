from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    pdf_dir: str = "./data/pdfs"  # Updated default for clarity
    db_url: str = "sqlite:///./local_database.sqlite"
    initial_corpus_dir: str = "/Users/justin/LLMS/Contexts/PromptEngineering/"
    default_collection_name: str = "Default Collection"

settings = Settings()
