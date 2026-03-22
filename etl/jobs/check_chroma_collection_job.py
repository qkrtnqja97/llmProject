# llmServer/etl/jobs/check_chroma_collection_job.py
# python -m jobs.check_chroma_collection_job

from loaders.chroma_loader import get_chroma_client


def check_collection(client, name):

    print(f"\n🔎 Collection: {name}")

    try:
        collection = client.get_collection(name=name)

        count = collection.count()
        print(f"📦 document count: {count}")

        if count > 0:
            sample = collection.peek(limit=2)

            print("\n📄 sample documents:")
            for i, doc in enumerate(sample["documents"]):
                print(f"\n--- sample {i+1} ---")
                print(doc[:200])

            print("\n🧾 metadata sample:")
            for meta in sample["metadatas"]:
                print(meta)

        else:
            print("⚠️ collection is empty")

    except Exception as e:
        print(f"❌ collection not found: {e}")


def run():

    print("🔗 Chroma connection test")

    client = get_chroma_client()

    collections = client.list_collections()

    if not collections:
        print("⚠️ No collections found")
        return

    print("\n📚 Collections found:")
    for c in collections:
        print("-", c.name)

    for c in collections:
        check_collection(client, c.name)

    print("\n🎉 Chroma check 완료")


if __name__ == "__main__":
    run()