from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5"
)

db = Chroma(
    persist_directory="./chroma_db",
    collection_name="universities",
    embedding_function=embeddings
)

retriever = db.as_retriever(search_kwargs={"k": 5})


print(db._collection.count())
