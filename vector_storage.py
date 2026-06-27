#for json

import os
import json
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("universities")

folder_path = "n"

for file_name in os.listdir(folder_path):

    if not file_name.endswith(".json"):
        continue

    file_path = os.path.join(folder_path, file_name)

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    ids = []
    documents = []

    for chunk in data:
        ids.append(f"{file_name}_{chunk['id']}")
        documents.append(chunk["text"])

    collection.add(
        ids=ids,
        documents=documents,
    )

    print(f"Stored {len(ids)} docs from {file_name}")

print("Done.")