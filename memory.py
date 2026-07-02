import chromadb

client = chromadb.PersistentClient(path="memory")
rules = client.get_or_create_collection("design_rules")

def ingest():
    text = open("knowledge/design-rules.md").read()
    chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
    rules.upsert(
        ids=[f"chunk-{i}" for i in range(len(chunks))],
        documents=chunks,
    )
    print(f"Sealed {len(chunks)} memories into the scroll.")

def recall(query, k=3):
    hits = rules.query(query_texts=[query], n_results=k)
    return "\n\n".join(hits["documents"][0])

if __name__ == "__main__":
    ingest()
    print("--- RECALL TEST: 'clean minimal premium site' ---")
    print(recall("clean minimal premium site"))
