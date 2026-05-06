import os
import chromadb
from sentence_transformers import SentenceTransformer

KNOWLEDGE_DIR = "knowledge"

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="vector_db/chroma_db")

collection = client.get_or_create_collection("recruiter_knowledge")

documents = []

for file in os.listdir(KNOWLEDGE_DIR):

    path = os.path.join(KNOWLEDGE_DIR, file)

    with open(path, "r") as f:

        text = f.read()

        chunks = text.split("\n\n")

        for chunk in chunks:
            if chunk.strip():
                documents.append(chunk.strip())

embeddings = model.encode(documents).tolist()

for i, doc in enumerate(documents):

    collection.add(
        documents=[doc],
        embeddings=[embeddings[i]],
        ids=[str(i)]
    )

print("Knowledge index created")