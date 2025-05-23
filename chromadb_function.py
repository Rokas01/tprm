import chromadb
import numpy as np
import uuid



def create_collection(collection_name,client):
    # Lets create the chromaDB collection
    try:
        collection = client.get_or_create_collection(name=collection_name, metadata={"hnsw:space": "cosine"})
        return collection
    except Exception as e:
        print(f"Having following issue in create_db_collection file  - {e}")


def add_to_collection(text_chunks,collection):
    try:
        documents = []
        ids = []

        for idx,text in enumerate(text_chunks):
            random_id = str(uuid.uuid4())
            # This is most important step which includes unique ids every 
            ids.append(f"chunk_id_{idx}_unique_id_{random_id}")
            documents.append(text.page_content)

        collection.add(
            documents = documents,
            ids = ids
        )
    except Exception as e:
        print(f"Having following issue in add_to_collection method - {e}")