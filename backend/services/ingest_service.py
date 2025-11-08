import os, json
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
import pinecone

def ingest_docs():
    OPENAI_API_KEY_2 = os.getenv("OPENAI_API_KEY_2")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
    PINECONE_INDEX = os.getenv("PINECONE_INDEX_NAME", "travel-guides")

    pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY_2, base_url=OPENAI_BASE_URL)
    index = Pinecone.from_existing_index(PINECONE_INDEX, embeddings)

    with open("data/travel_tips.json", "r") as f:
        docs = json.load(f)
    for doc in docs:
        index.add_texts([doc["content"]], metadatas=[{"source": doc["source"]}])

    print("✅ Ingested", len(docs), "documents.")
