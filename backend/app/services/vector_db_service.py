from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

# --- 1. Initialize the Embedding Model ---
print("--- VECTOR DB: Loading embedding model... ---")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
print("--- VECTOR DB: Embedding model loaded. ---")

# --- 2. Initialize the Qdrant Client ---
qdrant_client = QdrantClient("http://localhost", port=6333)
COLLECTION_NAME = "ai_knowledge_worker"

qdrant_client.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=models.VectorParams(
        size=embedding_model.get_sentence_embedding_dimension(),
        distance=models.Distance.COSINE
    ),
)
print(f"--- VECTOR DB: Collection '{COLLECTION_NAME}' ensured to exist. ---")

def add_document_to_vector_db(document_id: int, text: str, metadata: dict):
    """
    Converts a document's text to a vector and stores it in Qdrant.
    """
    try:
        vector = embedding_model.encode(text).tolist()
        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                models.PointStruct(
                    id=document_id,
                    vector=vector,
                    payload=metadata
                )
            ]
        )
        print(f"--- VECTOR DB: Successfully added document ID {document_id} to collection. ---")
    except Exception as e:
        print(f"--- VECTOR DB ERROR: Failed to add document to vector DB: {e} ---")

def search_similar_documents(query_text: str):
    """
    Searches for similar documents in Qdrant based on a text query.
    """
    try:
        # Convert the query text to a vector
        query_vector = embedding_model.encode(query_text).tolist()

        # Search the collection for the most similar vectors
        search_result = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=5 # Return the top 5 most similar results
        )
        print(f"--- VECTOR DB: Found {len(search_result)} similar documents. ---")
        return search_result
    except Exception as e:
        print(f"--- VECTOR DB ERROR: Failed to search documents: {e} ---")
        return []