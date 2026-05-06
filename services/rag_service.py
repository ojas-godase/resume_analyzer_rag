import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="vector_db/chroma_db")

collection = client.get_collection("recruiter_knowledge")


def retrieve_context(query, top_k=4):

    embedding = model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=embedding,
        n_results=top_k
    )

    return results["documents"][0]