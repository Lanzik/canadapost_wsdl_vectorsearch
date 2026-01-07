import lxml.etree as ET
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from sentence_transformers import SentenceTransformer
import uuid
import requests
import ollama

# model = SentenceTransformer('all-MiniLM-L6-v2')
client = QdrantClient("") 
collection_name = "canada_post_gemma_schema"

def get_embedding(text):
    response = ollama.embeddings(model='embeddinggemma:latest', prompt=text)
    return response['embedding']


print("Checking model dimensions...")
sample_vec = get_embedding("test")
vector_size = len(sample_vec)
print(f"Model: embeddinggemma | Dimension Size: {vector_size}")

if not client.collection_exists(collection_name):
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

def save_schema_to_qdrant(xml_content):
    root = ET.fromstring(xml_content.encode('utf-8'))
    namespaces = {'xsd': 'http://www.w3.org/2001/XMLSchema'}
    
    points = []
    
    all_types = root.xpath('//xsd:simpleType | //xsd:complexType', namespaces=namespaces)
    
    print(f"Starting embedding process for {len(all_types)} items...")
    for t in all_types:
        name = t.get('name')
        if not name: continue
        
        category = "SimpleType" if "simpleType" in t.tag else "ComplexType"
        elements = t.xpath('.//xsd:element/@name', namespaces=namespaces)
        fields_str = f" containing fields: {', '.join(elements)}" if elements else ""
        
        content_to_embed = f"{category}: {name}. {fields_str}"
        
        vector = get_embedding(content_to_embed)
        
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={
                "name": name,
                "category": category,
                "fields": elements,
                "full_description": content_to_embed
            }
        ))
    
    client.upsert(collection_name=collection_name, points=points)
    print(f"number of {len(points)} data type (Schema Type) saved in Qdrant successfully")
files_url = []
url1 = "https://www.canadapost-postescanada.ca/cpc/doc/en/business/developers/wsdl/manifest.wsdl"
url2 = "https://www.canadapost-postescanada.ca/cpc/doc/en/business/developers/wsdl/artifact.wsdl"
url3 = "https://www.canadapost-postescanada.ca/cpc/doc/en/business/developers/wsdl/rating.wsdl"
url4 = "https://www.canadapost-postescanada.ca/cpc/doc/en/business/developers/wsdl/shipment.wsdl"
url5 = "https://www.canadapost-postescanada.ca/cpc/doc/en/business/developers/wsdl/ncshipment.wsdl"
url6 = "https://www.canadapost-postescanada.ca/cpc/doc/en/business/developers/wsdl/track.wsdl"
url7 = "https://www.canadapost-postescanada.ca/cpc/doc/en/business/developers/wsdl/pickup.wsdl"
url8 = "https://www.canadapost-postescanada.ca/cpc/doc/en/business/developers/wsdl/pickuprequest.wsdl"
url9 = "https://www.canadapost-postescanada.ca/cpc/doc/en/business/developers/wsdl/postoffice.wsdl"
url10 = "https://www.canadapost-postescanada.ca/cpc/doc/en/business/developers/wsdl/customerinfo.wsdl"
url11 = "https://www.canadapost-postescanada.ca/cpc/doc/en/business/developers/wsdl/authreturn.wsdl"
url12 = "https://www.canadapost-postescanada.ca/cpc/doc/en/business/developers/wsdl/openreturn.wsdl"
url13 = "https://www.canadapost-postescanada.ca/cpc/doc/en/business/developers/wsdl/merchantregistration.wsdl"
url14 = "https://www.canadapost-postescanada.ca/cpc/doc/en/business/developers/wsdl/serviceinfo.wsdl"

files_url += [url1, url2, url3, url4, url5, url6, url7, url8
            , url9, url10, url11, url12, url13, url14]

for url in files_url:           
    response = requests.get(url)
    wsdl_text = response.text
    save_schema_to_qdrant(wsdl_text)
    print(f"saved {url} in Qdrant.\n")

