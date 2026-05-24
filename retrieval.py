import logging
from typing import List, Dict, Any
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class VectorRetrieval:
    """
    Performs similarity search on stored vectors
    Uses cosine similarity to find most relevant chunks
    """
    
    def __init__(self, vector_store):
        """
        Initialize retrieval engine
        
        Args:
            vector_store: VectorStore instance for accessing stored vectors
        """
        self.vector_store = vector_store
        logger.info("Vector Retrieval initialized")
    
    def search(self,
               query_embedding: List[float],
               top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using cosine similarity
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of results with text, similarity, and metadata
        """
        try:
            if not query_embedding:
                logger.warning("Empty query embedding")
                return []
            
            # Get all stored chunks
            chunks = self.vector_store.get_all()
            
            if not chunks:
                logger.warning("No chunks in vector store")
                return []
            
            # Calculate similarities
            similarities = []
            query_array = np.array(query_embedding).reshape(1, -1)
            
            for chunk in chunks:
                try:
                    chunk_array = np.array(chunk['embedding']).reshape(1, -1)
                    
                    # Cosine similarity
                    similarity = cosine_similarity(query_array, chunk_array)[0][0]
                    
                    similarities.append({
                        'chunk_id': chunk['chunk_id'],
                        'text': chunk['text'],
                        'embedding': chunk['embedding'],
                        'metadata': chunk['metadata'],
                        'similarity': float(similarity)
                    })
                
                except Exception as e:
                    logger.warning(f"Error calculating similarity for chunk {chunk.get('chunk_id')}: {str(e)}")
                    continue
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            # Return top-k
            results = similarities[:top_k]
            
            logger.info(f"Search returned {len(results)} results")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}", exc_info=True)
            return []
    
    def search_with_threshold(self,
                             query_embedding: List[float],
                             threshold: float = 0.75,
                             top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search with similarity threshold
        
        Args:
            query_embedding: Query embedding vector
            threshold: Minimum similarity score (0-1)
            top_k: Maximum number of results
            
        Returns:
            List of results above threshold
        """
        results = self.search(query_embedding, top_k)
        
        # Filter by threshold
        filtered = [r for r in results if r['similarity'] >= threshold]
        
        logger.info(f"After filtering by threshold {threshold}: {len(filtered)} results")
        
        return filtered


class DotProductRetrieval:
    """
    Alternative retrieval using dot product similarity
    Useful for normalized vectors
    """
    
    def __init__(self, vector_store):
        """Initialize dot product retrieval"""
        self.vector_store = vector_store
    
    def search(self,
               query_embedding: List[float],
               top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search using dot product similarity
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of results sorted by dot product score
        """
        try:
            chunks = self.vector_store.get_all()
            
            if not chunks:
                return []
            
            similarities = []
            query_array = np.array(query_embedding)
            
            for chunk in chunks:
                try:
                    chunk_array = np.array(chunk['embedding'])
                    
                    # Dot product (assumes normalized vectors)
                    similarity = np.dot(query_array, chunk_array)
                    
                    similarities.append({
                        'chunk_id': chunk['chunk_id'],
                        'text': chunk['text'],
                        'embedding': chunk['embedding'],
                        'metadata': chunk['metadata'],
                        'similarity': float(similarity)
                    })
                
                except Exception as e:
                    logger.warning(f"Error calculating dot product: {str(e)}")
                    continue
            
            # Sort by similarity
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Error in dot product search: {str(e)}")
            return []
