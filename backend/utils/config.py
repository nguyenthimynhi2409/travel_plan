import os
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY_1 = os.getenv("OPENAI_API_KEY_1")
OPENAI_API_KEY_2 = os.getenv("OPENAI_API_KEY_2")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "travel-guides")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")
