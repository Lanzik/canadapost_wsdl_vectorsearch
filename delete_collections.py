from qdrant_client import QdrantClient

client = QdrantClient(host='localhost', port=6333)

collections_to_delete = ["star_charts2", "star_charts", "post canada", "learning_collection2", "canada_post_schema_v8_4", "canada_post_manifest_v8_3", "canada_post_manifest_v8_2", "canada_post_manifest_v8", "canada_post_gemma_schema"]
for collection in collections_to_delete:
    client.delete_collection(collection)