# etl/config/etl_config.py

from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

POSTGRES_CONFIG = {
    "host": os.getenv("POSTGRES_HOST"),
    "port": int(os.getenv("POSTGRES_PORT")),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "database": os.getenv("POSTGRES_DB"),
    "schema" : os.getenv("POSTGRES_SCHEMA")
}

EMBEDDING_CONFIG = {
    "provider": os.getenv("EMBEDDING_PROVIDER", "gemini"),
    "embedding_model": os.getenv("EMBEDDING_MODEL"),
    "api_key": os.getenv("GEMINI_API_KEY"),
    "azure_openai_api_key": os.getenv("AZURE_OPENAI_API_KEY"),
    "azure_openai_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
    "azure_openai_api_version": os.getenv("AZURE_OPENAI_API_VERSION"),
    "azure_openai_embedding_deployment_name": os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")
    
}

CLOUDFLARE_CONFIG = {
    "host": os.getenv("CLOUDFLARE_HOSTNAME")
} 

CHROMA_CONFIG = {
    'host': os.getenv("CHROMA_HOST"),
    'port': os.getenv("CHROMA_PORT"),
    'persist_dir': "../infra/chroma/vector_db"
}

