"""
Test script for sentence-transformers embeddings.
Verifies model loads and generates embeddings locally.
"""

from sentence_transformers import SentenceTransformer
import numpy as np

print("Loading model (first time downloads ~420MB)...")
print("This may take 2-5 minutes on first run.\n")

# Load model (downloads on first use)
model = SentenceTransformer('all-mpnet-base-v2')

print("✅ Model loaded successfully!\n")

# Test text
test_text = "Hello, this is a test of embeddings!"

print(f"Generating embedding for: '{test_text}'")
print("Processing locally (no API call)...\n")

# Generate embedding
embedding = model.encode(test_text)

print(f"✅ Success!")
print(f"Embedding dimensions: {len(embedding)}")
print(f"First 10 values: {embedding[:10]}")
print(f"Data type: {type(embedding)}")
print(f"Numpy dtype: {embedding.dtype}")
print(f"\n🎉 Sentence-Transformers is working perfectly!")