import numpy as np
import json
import os
from typing import List, Dict, Tuple
import pickle

class SimpleVectorIndex:
    """
    Simple in-memory vector index using cosine similarity
    For production, consider using FAISS, Pinecone, or similar
    """
    
    def __init__(self):
        self.embeddings = []
        self.metadata = []
        self.dimension = None
    
    def add_embeddings(self, embeddings: List[List[float]], chunks_metadata: List[Dict]):
        """
        Add embeddings and their metadata to the index
        
        Args:
            embeddings (List[List[float]]): List of vector embeddings
            chunks_metadata (List[Dict]): Corresponding chunk metadata
        """
        if len(embeddings) != len(chunks_metadata):
            raise ValueError("Embeddings and metadata lists must have same length")
        
        if not embeddings:
            return
        
        # Convert to numpy arrays for efficient computation
        embedding_arrays = [np.array(emb, dtype=np.float32) for emb in embeddings]
        
        # Set dimension from first embedding
        if self.dimension is None:
            self.dimension = len(embedding_arrays[0])
        
        # Validate all embeddings have same dimension
        for emb in embedding_arrays:
            if len(emb) != self.dimension:
                raise ValueError(f"All embeddings must have dimension {self.dimension}")
        
        self.embeddings.extend(embedding_arrays)
        self.metadata.extend(chunks_metadata)
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """
        Search for most similar chunks using cosine similarity
        
        Args:
            query_embedding (List[float]): Query vector
            top_k (int): Number of results to return
            
        Returns:
            List[Dict]: Top-k most similar chunks with scores
        """
        if not self.embeddings:
            return []
        
        query_vec = np.array(query_embedding, dtype=np.float32)
        if len(query_vec) != self.dimension:
            raise ValueError(f"Query embedding must have dimension {self.dimension}")
        
        # Normalize query vector
        query_norm = np.linalg.norm(query_vec)
        if query_norm == 0:
            raise ValueError("Query embedding cannot be zero vector")
        query_vec = query_vec / query_norm
        
        # Calculate cosine similarities
        similarities = []
        for emb in self.embeddings:
            emb_norm = np.linalg.norm(emb)
            if emb_norm == 0:
                similarity = 0.0
            else:
                similarity = np.dot(query_vec, emb / emb_norm)
            similarities.append(similarity)
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Build results with similarity scores
        results = []
        for rank, idx in enumerate(top_indices):
            chunk_data = self.metadata[idx].copy()
            chunk_data['similarity_score'] = float(similarities[idx])
            chunk_data['rank'] = rank + 1
            results.append(chunk_data)
        
        return results
    
    def save(self, index_path: str):
        """
        Save index to disk
        
        Args:
            index_path (str): Path to save the index
        """
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        
        # Save as pickle file for simplicity
        index_data = {
            'embeddings': [emb.tolist() for emb in self.embeddings],
            'metadata': self.metadata,
            'dimension': self.dimension
        }
        
        with open(index_path, 'wb') as f:
            pickle.dump(index_data, f)
    
    @classmethod
    def load(cls, index_path: str) -> 'SimpleVectorIndex':
        """
        Load index from disk
        
        Args:
            index_path (str): Path to the saved index
            
        Returns:
            SimpleVectorIndex: Loaded index
        """
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"Index file not found: {index_path}")
        
        with open(index_path, 'rb') as f:
            index_data = pickle.load(f)
        
        index = cls()
        index.embeddings = [np.array(emb, dtype=np.float32) for emb in index_data['embeddings']]
        index.metadata = index_data['metadata']
        index.dimension = index_data['dimension']
        
        return index

def create_vector_index(embeddings: List[List[float]], chunks_metadata: List[Dict]) -> SimpleVectorIndex:
    """
    Create a vector index from embeddings and metadata
    
    Args:
        embeddings (List[List[float]]): List of vector embeddings
        chunks_metadata (List[Dict]): Corresponding chunk metadata
        
    Returns:
        SimpleVectorIndex: Created vector index
    """
    index = SimpleVectorIndex()
    index.add_embeddings(embeddings, chunks_metadata)
    return index

def load_vector_index(index_path: str) -> Tuple[SimpleVectorIndex, List[Dict]]:
    """
    Load vector index from persistent storage
    
    Args:
        index_path (str): Path to the saved index
        
    Returns:
        Tuple[SimpleVectorIndex, List[Dict]]: Loaded index and metadata
    """
    index = SimpleVectorIndex.load(index_path)
    return index, index.metadata

def search_vector_index(query_embedding: List[float], index: SimpleVectorIndex, top_k: int = 5) -> List[Dict]:
    """
    Search vector index for similar chunks
    
    Args:
        query_embedding (List[float]): Query vector
        index (SimpleVectorIndex): Vector index to search
        top_k (int): Number of results to return
        
    Returns:
        List[Dict]: Top-k most similar chunks with scores
    """
    return index.search(query_embedding, top_k)

if __name__ == "__main__":
    # Test the vector index
    from get_embedding import get_embedding, batch_get_embeddings
    
    # Test data
    test_chunks = [
        {"text": "Startups are about growth", "title": "Essay 1"},
        {"text": "Do things that don't scale", "title": "Essay 2"},
        {"text": "The best way to get startup ideas", "title": "Essay 3"}
    ]
    
    print("Testing vector index...")
    
    # Get embeddings (this would normally be done in the embedding node)
    texts = [chunk["text"] for chunk in test_chunks]
    try:
        embeddings = batch_get_embeddings(texts)
        
        # Create index
        index = create_vector_index(embeddings, test_chunks)
        
        # Test search
        query = "How to grow a startup"
        query_embedding = get_embedding(query)
        results = search_vector_index(query_embedding, index, top_k=2)
        
        print(f"Query: {query}")
        print("Results:")
        for result in results:
            print(f"  Score: {result['similarity_score']:.3f} - {result['text']}")
            
    except Exception as e:
        print(f"Error testing vector index: {e}")
        print("Note: This test requires valid Google Cloud credentials")
