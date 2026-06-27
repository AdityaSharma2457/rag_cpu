from langchain_community.vectorstores import Chroma



collection = Chroma(
    persist_directory="./chroma_db",
    collection_name="universities")



