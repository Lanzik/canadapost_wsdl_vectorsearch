import ollama
from qdrant_client import QdrantClient

client = QdrantClient("") 
collection_name = "canada_post_gemma_schema"

def get_embedding(text):
    response = ollama.embeddings(model='embeddinggemma:latest', prompt=text)
    return response['embedding']

def search_in_wsdl(query, limit=3):
    query_vector = get_embedding(query)
    results = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=limit,
        with_payload=True
    )
    
    print(f"\n🔍 result: '{query}'")
    print("="*50)
    
    if not results.points:
        print("didn't find anything")
        return

    for i, hit in enumerate(results.points, 1):
        payload = hit.payload
        print(f"{i}. name: {payload.get('name')}")
        print(f"   category: {payload.get('category')}")
        print(f"   fields: {', '.join(payload.get('fields', []))}")
        print(f"   similarity percent: {hit.score:.4f}")
        print("-" * 30)

if __name__ == "__main__":
    #examples
    search_in_wsdl("How can I calculate shipping rates or prices?")
    search_in_wsdl("tracking package and delivery status")

    search_in_wsdl("قیمت کشتی هارو چطور محاسبه کنم؟")

    # user_query = input("قیمت کشتی هارو چطور محاسبه کنم؟")
    # search_in_wsdl(user_query)