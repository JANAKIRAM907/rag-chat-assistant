import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid

logger = logging.getLogger(__name__)

class VectorStore:
    """
    In-memory vector storage for embeddings
    Stores chunks with their embeddings and metadata
    """
    
    def __init__(self):
        """Initialize vector store"""
        self.store: Dict[str, Dict[str, Any]] = {}
        logger.info("Vector Store initialized")
    
    def add(self,
            chunk_id: str,
            text: str,
            embedding: List[float],
            metadata: Optional[Dict[str, Any]] = None):
        """
        Add chunk with embedding to store
        
        Args:
            chunk_id: Unique chunk identifier
            text: Chunk text content
            embedding: Embedding vector
            metadata: Additional metadata (title, source, etc)
        """
        try:
            self.store[chunk_id] = {
                'chunk_id': chunk_id,
                'text': text,
                'embedding': embedding,
                'metadata': metadata or {},
                'added_at': datetime.now().isoformat()
            }
            logger.debug(f"Added chunk to store: {chunk_id}")
        except Exception as e:
            logger.error(f"Error adding to vector store: {str(e)}")
            raise
    
    def get(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Get specific chunk"""
        return self.store.get(chunk_id)
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all chunks"""
        return list(self.store.values())
    
    def delete(self, chunk_id: str) -> bool:
        """Delete specific chunk"""
        if chunk_id in self.store:
            del self.store[chunk_id]
            logger.debug(f"Deleted chunk: {chunk_id}")
            return True
        return False
    
    def clear(self):
        """Clear all chunks"""
        self.store.clear()
        logger.info("Vector store cleared")
    
    def size(self) -> int:
        """Get number of chunks in store"""
        return len(self.store)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get store statistics"""
        return {
            "total_chunks": len(self.store),
            "embedding_dim": len(self.store[list(self.store.keys())[0]]['embedding']) if self.store else 0,
            "sources": list(set(
                c.get('metadata', {}).get('source') 
                for c in self.store.values()
            ))
        }


class SessionStorage:
    """
    Stores conversation sessions and history
    Uses in-memory storage with automatic cleanup
    """
    
    def __init__(self, session_timeout_minutes: int = 120):
        """
        Initialize session storage
        
        Args:
            session_timeout_minutes: Inactive session cleanup time
        """
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        logger.info(f"Session Storage initialized with {session_timeout_minutes}min timeout")
    
    def create_session(self) -> str:
        """
        Create new session
        
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            'session_id': session_id,
            'created_at': datetime.now(),
            'last_activity': datetime.now(),
            'messages': []
        }
        logger.info(f"Created session: {session_id}")
        return session_id
    
    def add_message(self,
                   session_id: str,
                   user_message: str,
                   assistant_message: str):
        """
        Add message pair to session history
        
        Args:
            session_id: Session identifier
            user_message: User's message
            assistant_message: Assistant's response
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'session_id': session_id,
                'created_at': datetime.now(),
                'last_activity': datetime.now(),
                'messages': []
            }
        
        session = self.sessions[session_id]
        session['messages'].append({
            'user': user_message,
            'assistant': assistant_message,
            'timestamp': datetime.now().isoformat()
        })
        session['last_activity'] = datetime.now()
        
        logger.debug(f"Added message to session {session_id}. Total messages: {len(session['messages'])}")
    
    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """
        Get conversation history for session
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of message pairs
        """
        if session_id not in self.sessions:
            return []
        
        return self.sessions[session_id]['messages']
    
    def clear_history(self, session_id: str):
        """Clear session history"""
        if session_id in self.sessions:
            self.sessions[session_id]['messages'] = []
            logger.info(f"Cleared history for session: {session_id}")
    
    def delete_session(self, session_id: str):
        """Delete entire session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
    
    def cleanup_expired_sessions(self):
        """Remove sessions that have timed out"""
        now = datetime.now()
        expired = [
            sid for sid, session in self.sessions.items()
            if now - session['last_activity'] > self.session_timeout
        ]
        
        for sid in expired:
            del self.sessions[sid]
            logger.info(f"Cleaned up expired session: {sid}")
        
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions")
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        return {
            'session_id': session_id,
            'created_at': session['created_at'].isoformat(),
            'last_activity': session['last_activity'].isoformat(),
            'message_count': len(session['messages'])
        }
    
    def get_all_sessions(self) -> List[str]:
        """Get all active session IDs"""
        return list(self.sessions.keys())


# Persistent Storage (Optional - for production)
class PersistentVectorStore(VectorStore):
    """
    Vector store with file persistence
    Saves embeddings to JSON file
    """
    
    def __init__(self, filepath: str = "vector_store.json"):
        """Initialize with file persistence"""
        super().__init__()
        self.filepath = filepath
        self._load()
    
    def _load(self):
        """Load store from file"""
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
                self.store = data
            logger.info(f"Loaded vector store from {self.filepath}")
        except FileNotFoundError:
            logger.info(f"Vector store file not found: {self.filepath}")
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
    
    def add(self, chunk_id: str, text: str, embedding: List[float], metadata: Optional[Dict] = None):
        """Add with persistence"""
        super().add(chunk_id, text, embedding, metadata)
        self._save()
    
    def _save(self):
        """Save store to file"""
        try:
            with open(self.filepath, 'w') as f:
                # Convert numpy arrays to lists for JSON serialization
                data = {}
                for k, v in self.store.items():
                    data[k] = {
                        'chunk_id': v['chunk_id'],
                        'text': v['text'],
                        'embedding': v['embedding'],
                        'metadata': v['metadata'],
                        'added_at': v['added_at']
                    }
                json.dump(data, f, indent=2)
            logger.debug(f"Saved vector store to {self.filepath}")
        except Exception as e:
            logger.error(f"Error saving vector store: {str(e)}")
