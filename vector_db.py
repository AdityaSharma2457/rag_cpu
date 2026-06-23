from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import chromadb


client = chromadb.PersistentClient(path="./vector_db")

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5"
)



db = Chroma(
    embedding_function =embeddings,
    persist_directory="./vector_db"
)


retriever = db.as_retriever()