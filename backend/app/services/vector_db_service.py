# app/services/vector_db_service.py

# We've commented this out to save memory
# from sentence_transformers import SentenceTransformer
#from qdrant_client import QdrantClient, models


# --- MODIFICATION: Lazy Loading for the Embedding Model ---

#embedding_model = None # Don't load the model on startup
#EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'
# We know the dimension for this model is 384, which is needed for the collection.
#EMBEDDING_DIMENSION = 384

#def get_embedding_model():
    """
    Loads the model if it hasn't been loaded yet.
    This ensures it's only loaded into memory once, when first needed.
    """
    #global embedding_model
    #if embedding_model is None:
     #   print("--- VECTOR DB: Loading embedding model for the first time... ---")
      #  embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
       # print("--- VECTOR DB: Embedding model loaded successfully. ---")
    #return embedding_model

# --- End of Modification ---

# Use in-memory storage for deployment simplicity
#qdrant_client = QdrantClient(":memory:") 
#COLLECTION_NAME = "ai_knowledge_worker"

# Recreate the collection on startup using the known dimension
#qdrant_client.recreate_collection(
 #   collection_name=COLLECTION_NAME,
  ##  vectors_config=models.VectorParams(
    #    size=EMBEDDING_DIMENSION, 
     #   distance=models.Distance.COSINE
    #),
#)
#print(f"--- VECTOR DB: Collection '{COLLECTION_NAME}' ensured to exist. ---")

#def add_document_to_vector_db(document_id: int, text: str, metadata: dict):
 #   """Converts a document's text to a vector and stores it in Qdrant."""
  #  try:
   #     model = get_embedding_model() # Get the model using our lazy-loader
    #    vector = model.encode(text).tolist()
        
     #   qdrant_client.upsert(
      #      collection_name=COLLECTION_NAME,
       #     points=[
        #        models.PointStruct(id=document_id, vector=vector, payload=metadata)
         #   ],
          #  wait=True
        #)
        #print(f"--- VECTOR DB: Successfully added document ID {document_id} to collection. ---")
    #except Exception as e:
     #   print(f"--- VECTOR DB ERROR: Failed to add document: {e} ---")

#def search_similar_documents(query_text: str):
    """Searches for similar documents in Qdrant based on a text query."""
 #   try:
  #      model = get_embedding_model() # Get the model using our lazy-loader
   #     query_vector = model.encode(query_text).tolist()

    #    search_result = qdrant_client.search(
     #       collection_name=COLLECTION_NAME,
      #      query_vector=query_vector,
       #     limit=5
        #)
        #print(f"--- VECTOR DB: Found {len(search_result)} similar documents. ---")
        #return search_result
    #except Exception as e:
     #   print(f"--- VECTOR DB ERROR: Failed to search documents: {e} ---")
      #  return []