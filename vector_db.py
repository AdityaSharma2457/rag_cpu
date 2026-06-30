from langchain_community.vectorstores import Chroma


broucher_db = Chroma(
    persist_directory="./chroma_db",
    collection_name="universities")


history_db = Chroma(
    persist_directory="./chroma_db",
    collection_name="history")