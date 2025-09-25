import vertexai
from vertexai.language_models import TextEmbeddingModel
import os

def get_embedding(text: str) -> list:
    """
    Generate text embedding using Google's text-embedding-005 model
    
    Args:
        text (str): Input text to embed
        
    Returns:
        list[float]: Vector embedding
    """
    # Initialize Vertex AI
    vertexai.init(project=os.environ.get("GOOGLE_CLOUD_PROJECT"), location="us-central1")
    
    # Use Google's text-embedding-005 model
    model = TextEmbeddingModel.from_pretrained("text-embedding-005")
    
    # Generate embedding
    embeddings = model.get_embeddings([text])
    return embeddings[0].values

def batch_get_embeddings(texts: list) -> list:
    """
    Generate embeddings for multiple texts in batch for efficiency
    
    Args:
        texts (list[str]): List of texts to embed
        
    Returns:
        list[list[float]]: List of vector embeddings
    """
    # Initialize Vertex AI
    vertexai.init(project=os.environ.get("GOOGLE_CLOUD_PROJECT"), location="us-central1")
    
    # Use Google's text-embedding-005 model
    model = TextEmbeddingModel.from_pretrained("text-embedding-005")
    
    # Generate embeddings in batch
    embeddings = model.get_embeddings(texts)
    return [embedding.values for embedding in embeddings]

if __name__ == "__main__":
    # Test the embedding function
    test_text = "Paul Graham is a programmer, writer, and investor."
    embedding = get_embedding(test_text)
    print(f"Embedding dimension: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")
    
    # Test batch embeddings
    test_texts = [
        "Startups are about growth.",
        "The best way to get startup ideas is to notice problems.",
        "Do things that don't scale."
    ]
    batch_embeddings = batch_get_embeddings(test_texts)
    print(f"Batch embeddings count: {len(batch_embeddings)}")
