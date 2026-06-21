from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import chromadb


client = chromadb.PersistentClient(path="./chroma_db")

embeddings = HuggingFaceEmbeddings()
loader = TextLoader("data.txt")
docs = loader.load()



db = Chroma.from_documents(
    documents=docs,
    embedding=embeddings,
    persist_directory="./chroma_db"
)


retriever = db.as_retriever()