import chromadb

client = chromadb.PersistentClient(path="./memory_db")
collection = client.get_or_create_collection("research_agent")

def save_memory(text, metadata=None):
    collection.add(documents=[text], ids=[str(hash(text))], metadatas=[metadata or {}])

def recall(query, n=3):
    return collection.query(query_texts=[query], n_results=n)
