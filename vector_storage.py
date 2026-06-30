# for jsonl

# import os
# import json
# import vectordb

# client = vectordb.PersistentClient(path="./chroma_db")
# collection = client.broucher_db("universities")

# folder_path = "scholarships&refunds"

# for file_name in os.listdir(folder_path):

#     if not file_name.endswith(".jsonl"):
#         continue

#     file_path = os.path.join(folder_path, file_name)

#     ids = []
#     documents = []
#     metadatas = []

#     with open(file_path, "r", encoding="utf-8") as f:

#         for line in f:
#             line = line.strip()

#             if not line:
#                 continue

#             chunk = json.loads(line)

#             ids.append(f"{file_name}_{chunk['id']}")  # unique ids
#             documents.append(chunk["text"])
#             metadatas.append(chunk["metadata"])

#     collection.add(
#         ids=ids,
#         documents=documents,
#         metadatas=metadatas
#     )

#     print(f"Stored {len(ids)} docs from {file_name}")

# print("Done.")






#for json


# import os
# import json
# import chromadb

# client = chromadb.PersistentClient(path="./chroma_db")
# collection = client.get_or_create_collection("universities")

# folder_path = "courses"

# for file_name in os.listdir(folder_path):

#     if not file_name.endswith(".json"):
#         continue

#     file_path = os.path.join(folder_path, file_name)

#     with open(file_path, "r", encoding="utf-8") as f:
#         data = json.load(f)

#     ids = []
#     documents = []
#     metadatas = []

#     for chunk in data:
#         ids.append(f"{file_name}_{chunk['id']}")
#         documents.append(chunk["text"])
#         metadatas.append(chunk["metadata"])

#     collection.add(
#         ids=ids,
#         documents=documents,
#         metadatas=metadatas
#     )

#     print(f"Stored {len(ids)} docs from {file_name}")

# print("Done.")

