import json
import logging
from typing import List, Dict, Any, Tuple
from embeddings import EmbeddingGenerator
from retrieval import VectorRetrieval
from llm import ClaudeLLM
from storage import VectorStore
import re

logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self, 
                 similarity_threshold: float = 0.75,
                 top_k: int = 3,
                 chunk_size: int = 300):
        self.similarity_threshold = similarity_threshold
        self.top_k = top_k
        self.chunk_size = chunk_size
        
        self.embedding_generator = EmbeddingGenerator()
        self.vector_store = VectorStore()
        self.retrieval = VectorRetrieval(self.vector_store)
        self.llm = ClaudeLLM()
        
        self._initialize_knowledge_base()
        logger.info("RAG Pipeline initialized")
    
    def _initialize_knowledge_base(self):
        try:
            with open("docs.json", "r") as f:
                documents = json.load(f)
            
            logger.info(f"Loaded {len(documents)} documents from docs.json")
            
            total_chunks = 0
            for doc in documents:
                chunks = self._chunk_document(doc)
                total_chunks += len(chunks)
                
                for chunk_id, chunk_text in enumerate(chunks):
                    embedding = self.embedding_generator.generate_embedding(chunk_text)
                    
                    self.vector_store.add(
                        chunk_id=f"{doc['title']}_{chunk_id}",
                        text=chunk_text,
                        embedding=embedding,
                        metadata={
                            "title": doc["title"],
                            "chunk_id": chunk_id,
                            "source": doc["title"]
                        }
                    )
            
            logger.info(f"Indexed {total_chunks} chunks from {len(documents)} documents")
            
        except FileNotFoundError:
            logger.error("docs.json not found")
            raise
        except Exception as e:
            logger.error(f"Error initializing knowledge base: {str(e)}")
            raise
    
    def _chunk_document(self, document: Dict[str, str]) -> List[str]:
        content = document.get("content", "")
        sentences = re.split(r'(?<=[.!?])\s+', content.strip())
        
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for sentence in sentences:
            sentence_tokens = int(len(sentence.split()) * 1.3)
            
            if current_tokens + sentence_tokens > self.chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_tokens = sentence_tokens
            else:
                current_chunk.append(sentence)
                current_tokens += sentence_tokens
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks if chunks else [content]
    
    def _retrieve_context(self, query: str) -> Tuple[List[Dict[str, Any]], float]:
        query_embedding = self.embedding_generator.generate_embedding(query)
        
        results = self.retrieval.search(
            query_embedding=query_embedding,
            top_k=self.top_k
        )
        
        filtered_results = [
            r for r in results 
            if r['similarity'] >= self.similarity_threshold
        ]
        
        max_similarity = max([r['similarity'] for r in results], default=0)
        
        logger.info(f"Retrieved {len(filtered_results)} chunks above threshold {self.similarity_threshold}")
        
        return filtered_results, max_similarity
    
    def _build_prompt(self,
                     query: str,
                     retrieved_chunks: List[Dict[str, Any]],
                     conversation_history: List[Dict[str, str]]) -> str:
        context_text = ""
        if retrieved_chunks:
            context_text = "\n\n".join([
                f"[{chunk['metadata'].get('title', 'Document')}]\n{chunk['text']}"
                for chunk in retrieved_chunks
            ])
        else:
            context_text = "No relevant documents found."
        
        history_text = ""
        if conversation_history:
            history_lines = []
            for msg in conversation_history[-5:]:
                history_lines.append(f"User: {msg['user']}")
                history_lines.append(f"Assistant: {msg['assistant']}")
            history_text = "\n".join(history_lines)
        
        prompt = f"""You are a helpful AI assistant. Your role is to answer questions based ONLY on the provided context.

IMPORTANT RULES:
1. Use ONLY the information provided in the Context section below
2. If the context does not contain information to answer the question, respond: "I don't have enough information in the knowledge base to answer this question. Please ask something related to the provided documents."
3. Be concise and direct
4. Cite the document title when referencing information

Context:
{context_text}

{"Previous Conversation History:" if history_text else ""}
{history_text}

Current Question: {query}

Answer:"""
        
        return prompt
    
    def process_query(self,
                     query: str,
                     conversation_history: List[Dict[str, str]],
                     session_id: str) -> Dict[str, Any]:
        try:
            logger.info(f"Processing query for session {session_id}: {query[:100]}")
            
            retrieved_chunks, max_similarity = self._retrieve_context(query)
            prompt = self._build_prompt(query, retrieved_chunks, conversation_history)
            response = self.llm.generate(prompt)
            
            return {
                "reply": response.get("text", "Error generating response"),
                "tokens_used": response.get("tokens_used"),
                "num_chunks": len(retrieved_chunks),
                "confidence": max_similarity,
                "sources": [
                    chunk['metadata'].get('title', 'Unknown')
                    for chunk in retrieved_chunks
                ]
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            return {
                "reply": f"Error processing your query: {str(e)}",
                "tokens_used": None,
                "num_chunks": 0,
                "confidence": 0.0,
                "sources": []
            }