import argparse
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_SOURCE = BASE_DIR / "brochure_sentences.txt"
DEFAULT_DB_PATH = BASE_DIR / "chroma_db"
COLLECTION_NAME = "universities"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def load_points(source_path: Path) -> list[tuple[int, str]]:
    text = source_path.read_text(encoding="utf-8-sig")
    matches = list(re.finditer(r"(?m)^\s*(\d+)\.\s+", text))
    if not matches:
        raise ValueError(f"No numbered points found in {source_path}")

    points = []
    seen_numbers = set()
    for index, match in enumerate(matches):
        point_number = int(match.group(1))
        point_end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        point_text = text[match.end():point_end].strip()

        if point_number in seen_numbers:
            raise ValueError(f"Duplicate point number {point_number} in {source_path}")
        if not point_text:
            raise ValueError(f"Point {point_number} is empty in {source_path}")

        seen_numbers.add(point_number)
        points.append((point_number, point_text))

    return points


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import numbered brochure points into the project's Chroma collection."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help=f"Text file to import (default: {DEFAULT_SOURCE})",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=DEFAULT_DB_PATH,
        help=f"Chroma persistence directory (default: {DEFAULT_DB_PATH})",
    )
    args = parser.parse_args()

    source_path = args.source.resolve()
    if not source_path.is_file():
        raise FileNotFoundError(f"Source file does not exist: {source_path}")

    points = load_points(source_path)
    documents = [text for _, text in points]
    source_id = re.sub(r"[^a-zA-Z0-9_-]+", "_", source_path.stem).strip("_")
    ids = [f"{source_id}_{number:06d}" for number, _ in points]
    metadatas = [
        {"source": source_path.name, "point_number": number}
        for number, _ in points
    ]

    import chromadb
    from langchain_community.embeddings import HuggingFaceEmbeddings

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    vectors = embeddings.embed_documents(documents)

    client = chromadb.PersistentClient(path=str(args.db_path.resolve()))
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=vectors,
    )

    print(
        f"Imported or updated {len(points)} points from {source_path.name} "
        f"in collection '{COLLECTION_NAME}' at {args.db_path.resolve()}."
    )


if __name__ == "__main__":
    main()
