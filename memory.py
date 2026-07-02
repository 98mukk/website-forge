import chromadb
import glob
import os

client = chromadb.PersistentClient(path="memory")
rules = client.get_or_create_collection("design_rules")

def ingest():
    total = 0
    for path in glob.glob("knowledge/*.md"):
        name = os.path.basename(path).replace(".md", "")
        text = open(path).read()
        chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
        rules.upsert(
            ids=[f"{name}-{i}" for i in range(len(chunks))],
            documents=chunks,
        )
        total += len(chunks)
        print(f"Sealed {len(chunks)} memories from {name}")
    print(f"Deck total this run: {total} cards.")

def recall(query, k=3):
    hits = rules.query(query_texts=[query], n_results=k)
    return "\n\n".join(hits["documents"][0])

if __name__ == "__main__":
    ingest()
    print("--- RECALL TEST: 'clean minimal premium site' ---")
    print(recall("clean minimal premium site"))
