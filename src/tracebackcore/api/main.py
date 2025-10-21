"""
Traceback API Server

FastAPI server for the Traceback incident triage system.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Add src to path for imports
import sys
from pathlib import Path
# Add the project root (src's parent) to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import our core system components
from tracebackcore.core import traceback_graph, lineage_retriever, vectorstore, initialize_system

# Global variables for the core system
traceback_graph = None
lineage_retriever = None
vectorstore = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the Traceback system on startup."""
    global traceback_graph, lineage_retriever, vectorstore
    
    print("🚀 Initializing Traceback system...")
    
    try:
        # Initialize core components
        initialize_system()
        
        # Update global variables
        from tracebackcore.core import traceback_graph as tg, lineage_retriever as lr, vectorstore as vs
        traceback_graph = tg
        lineage_retriever = lr
        vectorstore = vs
        
        print("✅ Traceback system initialized successfully")
        
    except Exception as e:
        print(f"❌ Failed to initialize Traceback system: {e}")
        raise
    
    yield
    
    print("🛑 Shutting down Traceback system...")

# Create FastAPI app
app = FastAPI(
    title="Traceback API",
    description="AI-powered data pipeline incident triage system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class IncidentRequest(BaseModel):
    question: str
    priority: Optional[str] = "medium"
    context: Optional[Dict[str, Any]] = None

class IncidentResponse(BaseModel):
    incident_brief: str
    blast_radius: List[str]
    impact_assessment: Dict[str, Any]
    processing_time: float
    sources_used: List[str]

class HealthResponse(BaseModel):
    status: str
    timestamp: float
    system_health: Dict[str, Any]

# API Routes
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Traceback API - Data Pipeline Incident Triage",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    system_health = {
        "traceback_graph": traceback_graph is not None,
        "lineage_retriever": lineage_retriever is not None,
        "vectorstore": vectorstore is not None,
        "openai_key": bool(os.getenv("OPENAI_API_KEY")),
        "tavily_key": bool(os.getenv("TAVILY_API_KEY"))
    }
    
    overall_status = "healthy" if all(system_health.values()) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        timestamp=time.time(),
        system_health=system_health
    )

@app.post("/incident/triage", response_model=IncidentResponse)
async def triage_incident(request: IncidentRequest):
    """Main incident triage endpoint."""
    if not traceback_graph:
        raise HTTPException(status_code=503, detail="Traceback system not initialized")
    
    start_time = time.time()
    
    try:
        # Run the incident triage workflow
        from tracebackcore.core import AgentState
        
        initial_state = AgentState(
            question=request.question,
            context=[],
            impact_assessment=None,
            blast_radius=None,
            recommended_actions=None,
            incident_brief=None,
            current_step="supervisor",
            error=None
        )
        
        result = traceback_graph.invoke(initial_state)
        
        processing_time = time.time() - start_time
        
        # Extract sources used
        sources_used = []
        if result.get("impact_assessment"):
            assessment = result["impact_assessment"]
            if isinstance(assessment, dict):
                context_sources = assessment.get("context_sources", [])
                sources_used = [source.get("source", "unknown") for source in context_sources]
        
        return IncidentResponse(
            incident_brief=result.get("incident_brief", "No brief generated"),
            blast_radius=result.get("blast_radius", []),
            impact_assessment=result.get("impact_assessment", {}),
            processing_time=processing_time,
            sources_used=sources_used
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Incident triage failed: {str(e)}")

@app.get("/incident/search")
async def search_documents(query: str, limit: int = 5):
    """Search documents using RAG."""
    if not lineage_retriever:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        results = lineage_retriever.search_with_lineage(query, k=limit)
        
        search_results = []
        for doc in results:
            search_results.append({
                "content": doc.page_content,
                "source": doc.metadata.get("file_name", "unknown"),
                "type": doc.metadata.get("type", "unknown"),
                "metadata": doc.metadata
            })
        
        return {
            "query": query,
            "results": search_results,
            "total": len(search_results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/lineage/{table_name}")
async def get_lineage(table_name: str):
    """Get lineage information for a specific table."""
    if not lineage_retriever:
        raise HTTPException(status_code=503, detail="Lineage system not initialized")
    
    try:
        downstream = lineage_retriever.find_downstream_impact(table_name)
        upstream = lineage_retriever.find_upstream_dependencies(table_name)
        
        return {
            "table": table_name,
            "upstream_dependencies": upstream,
            "downstream_impact": downstream,
            "total_dependencies": len(upstream) + len(downstream)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lineage query failed: {str(e)}")

@app.get("/system/stats")
async def get_system_stats():
    """Get system statistics."""
    # Get document count from Qdrant collection info
    vectorstore_count = 0
    if vectorstore:
        try:
            # Get collection info to determine document count
            collection_info = vectorstore.client.get_collection(vectorstore.collection_name)
            vectorstore_count = collection_info.points_count
        except Exception as e:
            print(f"Warning: Could not get vectorstore count: {e}")
            vectorstore_count = 0
    
    stats = {
        "vectorstore_documents": vectorstore_count,
        "lineage_nodes": len(lineage_retriever.lineage_data.get("nodes", [])) if lineage_retriever else 0,
        "lineage_edges": len(lineage_retriever.lineage_data.get("edges", [])) if lineage_retriever else 0,
        "uptime": time.time(),
        "api_version": "1.0.0"
    }
    
    return stats

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
