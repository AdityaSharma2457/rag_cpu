from vector_db import history_db
import uuid
import chromadb


client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("history_db")


def add_to_history_db(question, response):
    convo = f"""
    user : {question}
    assistant : {response}"""

    collection.add(
        ids=[str(uuid.uuid4())],
        documents = [convo]
    )

def search_historydb(question, k = 3):
    return history_db.similarity_search_with_score(query=question, k=k)
