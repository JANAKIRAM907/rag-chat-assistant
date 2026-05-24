import os
import logging
import hashlib

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    def __init__(self):
        logger.info("Embedding generator initialized")

    def generate_embedding(self, text: str) -> list:
        try:
            words = text.lower().split()
            embedding = [0.0] * 384
            for i, word in enumerate(words):
                hash_val = int(hashlib.md5(word.encode()).hexdigest(), 16)
                for j in range(min(10, 384)):
                    idx = (hash_val + i * 7 + j * 13) % 384
                    embedding[idx] += 1.0 / (i + 1)
            norm = sum(x**2 for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def generate_embeddings(self, texts: list) -> list:
        return [self.generate_embedding(t) for t in texts]