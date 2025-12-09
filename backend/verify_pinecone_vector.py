"""
Verify that vectors are stored in Pinecone and can be queried.
"""

import os
from dotenv import load_dotenv
from pinecone import Pinecone

# Load environment
load_dotenv()

print("=" * 60)
print("PINECONE VECTOR VERIFICATION")
print("=" * 60)

# Initialize Pinecone
api_key = os.getenv("PINECONE_API_KEY")
index_name = os.getenv("PINECONE_INDEX_NAME", "rag-documents")

pc = Pinecone(api_key=api_key)
index = pc.Index(index_name)

# Get index statistics
print(f"\n📊 Index: {index_name}")
print("-" * 60)

stats = index.describe_index_stats()
print(f"Total vectors: {stats.total_vector_count}")
print(f"Dimension: {stats.dimension}")
print(f"Index fullness: {stats.index_fullness * 100:.2f}%")

# Fetch specific vector (document 6, chunk 0)
print(f"\n🔍 Fetching vector: doc_6_chunk_0")
print("-" * 60)

try:
    fetch_result = index.fetch(ids=["doc_6_chunk_0"])
    
    if fetch_result.vectors:
        vector_data = fetch_result.vectors["doc_6_chunk_0"]
        
        print(f"✅ Vector found!")
        print(f"\nVector ID: {vector_data.id}")
        print(f"Metadata:")
        for key, value in vector_data.metadata.items():
            if key == "chunk_text":
                print(f"  {key}: {value[:100]}..." if len(str(value)) > 100 else f"  {key}: {value}")
            else:
                print(f"  {key}: {value}")
        
        print(f"\nEmbedding vector:")
        print(f"  Dimensions: {len(vector_data.values)}")
        print(f"  First 10 values: {vector_data.values[:10]}")
        print(f"  Last 10 values: {vector_data.values[-10:]}")
        
    else:
        print("❌ Vector not found")
        
except Exception as e:
    print(f"❌ Error fetching vector: {e}")

# Test similarity search (using the stored vector itself)
print(f"\n🔎 Testing similarity search")
print("-" * 60)

try:
    # Fetch the vector first
    fetch_result = index.fetch(ids=["doc_6_chunk_0"])
    
    if fetch_result.vectors:
        # Use the vector itself as query (should return itself as top result)
        query_vector = fetch_result.vectors["doc_6_chunk_0"].values
        
        results = index.query(
            vector=query_vector,
            top_k=3,
            include_metadata=True
        )
        
        print(f"Found {len(results.matches)} matches:")
        for i, match in enumerate(results.matches, 1):
            print(f"\n  Match {i}:")
            print(f"    ID: {match.id}")
            print(f"    Score: {match.score:.4f}")
            print(f"    Document ID: {match.metadata.get('document_id')}")
            print(f"    Filename: {match.metadata.get('filename')}")
            
except Exception as e:
    print(f"❌ Error during similarity search: {e}")

print("\n" + "=" * 60)
print("🎉 VERIFICATION COMPLETE!")
print("=" * 60)