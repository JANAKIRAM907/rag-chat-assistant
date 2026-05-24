from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import json
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

# Import custom modules
from rag import RAGPipeline
from storage import SessionStorage

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="GenAI Chat Assistant with RAG",
    description="Production-grade RAG-based chat system using Claude",
    version="1.0.0"
)

# Initialize RAG Pipeline and Session Storage
try:
    rag_pipeline = RAGPipeline()
    session_storage = SessionStorage()
    logger.info("RAG Pipeline initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize RAG Pipeline: {str(e)}")
    raise

# ============= REQUEST/RESPONSE MODELS =============

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    sessionId: str = Field(..., description="Unique session identifier")
    message: str = Field(..., min_length=1, max_length=1000, description="User message")

class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    reply: str
    sessionId: str
    tokensUsed: Optional[int] = None
    retrievedChunks: int
    confidence: float
    timestamp: str

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    message: str

class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    timestamp: str
    details: Optional[str] = None

# ============= API ENDPOINTS =============

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "RAG Assistant is running"
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - processes user message with RAG
    
    Args:
        request: ChatRequest containing sessionId and message
        
    Returns:
        ChatResponse with reply, tokens used, and retrieval metrics
    """
    try:
        # Validate input
        if not request.sessionId or not request.sessionId.strip():
            raise HTTPException(status_code=400, detail="sessionId is required")
        
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message field is required")
        
        logger.info(f"Processing message for session: {request.sessionId}")
        
        # Get conversation history
        history = session_storage.get_history(request.sessionId)
        
        # Process query through RAG pipeline
        result = rag_pipeline.process_query(
            query=request.message.strip(),
            conversation_history=history,
            session_id=request.sessionId
        )
        
        # Store message and response in session
        session_storage.add_message(
            session_id=request.sessionId,
            user_message=request.message.strip(),
            assistant_message=result['reply']
        )
        
        logger.info(f"Chat completed. Retrieved {result['num_chunks']} chunks, Confidence: {result['confidence']}")
        
        return ChatResponse(
            reply=result['reply'],
            sessionId=request.sessionId,
            tokensUsed=result.get('tokens_used'),
            retrievedChunks=result['num_chunks'],
            confidence=round(result['confidence'], 4),
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException as he:
        logger.warning(f"HTTP Exception: {he.detail}")
        raise
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Please try again."
        )

@app.get("/api/sessions/{sessionId}")
async def get_session(sessionId: str):
    """Get conversation history for a session"""
    try:
        history = session_storage.get_history(sessionId)
        return {
            "sessionId": sessionId,
            "history": history,
            "messageCount": len(history)
        }
    except Exception as e:
        logger.error(f"Error retrieving session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve session")

@app.delete("/api/sessions/{sessionId}")
async def clear_session(sessionId: str):
    """Clear session history"""
    try:
        session_storage.clear_history(sessionId)
        return {
            "status": "success",
            "message": f"Session {sessionId} cleared"
        }
    except Exception as e:
        logger.error(f"Error clearing session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clear session")

# ============= STATIC FILES =============

@app.get("/")
async def serve_index():
    """Serve index.html"""
    return FileResponse("frontend/index.html")

# Mount static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# ============= ERROR HANDLERS =============

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return {
        "error": exc.detail,
        "timestamp": datetime.now().isoformat(),
        "status_code": exc.status_code
    }

# ============= STARTUP/SHUTDOWN =============

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("=" * 50)
    logger.info("GenAI Chat Assistant with RAG")
    logger.info("=" * 50)
    logger.info("Application started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Application shutting down")

# ============= RUN =============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
