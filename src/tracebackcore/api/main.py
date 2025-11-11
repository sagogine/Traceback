"""
Traceback API Server

FastAPI server for the Traceback incident triage system.
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Add the project root (src's parent) to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import our core system components
# Global variables for the core system
traceback_graph = None
lineage_retriever = None
vectorstore = None
llm = None

# Advanced retriever functions
def generate_hybrid_response(question: str) -> Dict[str, Any]:
    """Generate response using hybrid search (vector + BM25)."""
    try:
        # Simple hybrid implementation for evaluation
        import re
        
        # Get vector search results
        docs = vectorstore.similarity_search(question, k=10)
        
        # Simple BM25-style scoring
        query_words = set(re.findall(r'\b\w+\b', question.lower()))
        
        scored_docs = []
        for doc in docs:
            content_words = set(re.findall(r'\b\w+\b', doc.page_content.lower()))
            overlap = len(query_words.intersection(content_words))
            score = overlap / len(query_words) if query_words else 0
            scored_docs.append((doc, score))
        
        # Sort by combined score and take top 5
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        top_docs = [doc for doc, score in scored_docs[:5]]
        
        context_docs = [doc.page_content for doc in top_docs]
        context_text = "\n\n".join(context_docs)
        
        # Generate answer
        prompt = f"""Based on the following context, answer the question: {question}

Context:
{context_text}

Answer:"""
        
        response = llm.invoke(prompt)
        answer = response.content if hasattr(response, 'content') else str(response)
        
        return {
            'question': question,
            'answer': answer,
            'context': context_docs,
            'method': 'Hybrid Search'
        }
        
    except Exception as e:
        return {
            'question': question,
            'answer': f"Error generating response: {str(e)}",
            'context': [],
            'method': 'Hybrid Search (Error)'
        }

def generate_lineage_aware_response(question: str) -> Dict[str, Any]:
    """Generate response using lineage-aware retrieval."""
    try:
        # Extract table names from question
        import re
        table_patterns = [
            r'(curated\.\w+)',
            r'(raw\.\w+)',
            r'(analytics\.\w+)',
            r'(bi\.\w+)',
            r'(ops\.\w+)'
        ]
        
        table_names = []
        for pattern in table_patterns:
            matches = re.findall(pattern, question.lower())
            table_names.extend(matches)
        
        # Enhance query with lineage context
        enhanced_query = question
        if table_names:
            enhanced_query = f"{question} Related tables: {', '.join(table_names[:3])}"
        
        # Search with enhanced query using lineage-aware retriever when available
        search_docs = []
        if lineage_retriever:
            search_docs = lineage_retriever.search_with_lineage(enhanced_query, k=5)
        else:
            search_docs = vectorstore.similarity_search(enhanced_query, k=5)
        
        docs = search_docs[:5]
        context_docs = [doc.page_content for doc in docs]
        context_sources = [
            doc.metadata.get("file_name", doc.metadata.get("table", "unknown"))
            for doc in docs
        ]
        
        # Generate answer
        context_text = "\n\n".join(context_docs)
        
        # Determine blast radius using lineage information
        all_table_names = set(table_names)
        table_regex_matches = re.findall(r'\b(?:raw|curated|analytics|bi|ops)\.[a-z0-9_]+\b', context_text, flags=re.IGNORECASE)
        for table in table_regex_matches:
            all_table_names.add(table.lower())
        
        blast_radius = []
        if lineage_retriever and all_table_names:
            downstream = []
            for table_name in all_table_names:
                downstream.extend(lineage_retriever.find_downstream_impact(table_name))
            blast_radius = sorted(set(downstream))
        
        # Generate comprehensive incident brief
        brief_prompt = f"""
You are the Incident Writer for the Traceback data pipeline triage system.

Question: {question}

Context:
{context_text}

Known downstream impact: {', '.join(blast_radius) if blast_radius else 'None identified'}

Compose a single, structured incident brief that blends business and technical insights using these sections:
1. **Incident Summary**
2. **Business Impact**
3. **Blast Radius**
4. **Root Cause Analysis**
5. **Recommended Actions**
6. **Recovery Plan**
7. **Prevention / Next Steps**

Use concise paragraphs or bullet points under each heading.
"""
        brief_response = llm.invoke(brief_prompt)
        incident_brief = brief_response.content if hasattr(brief_response, 'content') else str(brief_response)
        
        return {
            'question': question,
            'incident_brief': incident_brief,
            'blast_radius': blast_radius,
            'context': context_docs,
            'sources': context_sources,
            'method': 'Lineage-Aware Retrieval'
        }
        
    except Exception as e:
        return {
            'question': question,
            'answer': f"Error generating response: {str(e)}",
            'context': [],
            'blast_radius': [],
            'method': 'Lineage-Aware Retrieval (Error)'
        }

def generate_cohere_reranking_response(question: str) -> Dict[str, Any]:
    """Generate response using Cohere reranking."""
    try:
        # Get documents from vectorstore
        docs = vectorstore.similarity_search(question, k=10)  # Get more candidates for reranking
        context_docs = [doc.page_content for doc in docs]
        
        if not context_docs:
            return {
                'question': question,
                'answer': 'No relevant context found.',
                'context': [],
                'method': 'Cohere Reranking'
            }
        
        # Use Cohere reranking if available
        try:
            import cohere
            cohere_client = cohere.Client(os.getenv("COHERE_API_KEY"))
            
            # Rerank the documents
            rerank_response = cohere_client.rerank(
                model="rerank-english-v2.0",
                query=question,
                documents=context_docs,
                top_n=5  # Fixed parameter name
            )
            
            # Get top reranked documents
            reranked_docs = [doc.document.text for doc in rerank_response.results]
            context_text = "\n\n".join(reranked_docs)
            
        except Exception as e:
            print(f"Cohere reranking failed: {e}, using top 5 documents")
            context_text = "\n\n".join(context_docs[:5])
            reranked_docs = context_docs[:5]
        
        # Generate answer
        prompt = f"""Based on the following context, answer the question: {question}

Context:
{context_text}

Answer:"""
        
        response = llm.invoke(prompt)
        answer = response.content if hasattr(response, 'content') else str(response)
        
        return {
            'question': question,
            'answer': answer,
            'context': reranked_docs,
            'method': 'Cohere Reranking'
        }
        
    except Exception as e:
        return {
            'question': question,
            'answer': f"Error generating response: {str(e)}",
            'context': [],
            'method': 'Cohere Reranking (Error)'
        }

def generate_query_expansion_response(question: str) -> Dict[str, Any]:
    """Generate response using query expansion."""
    try:
        # Expand the query
        expansion_prompt = f"""Given this question: "{question}"

Generate 3 alternative phrasings that might help find relevant information:
1. Technical/implementation focused version
2. Business/impact focused version  
3. Troubleshooting/operational version

Return only the 3 alternative questions, one per line."""

        expansion_response = llm.invoke(expansion_prompt)
        expansion_text = expansion_response.content if hasattr(expansion_response, 'content') else str(expansion_response)
        
        # Parse expanded queries
        expanded_queries = [line.strip() for line in expansion_text.split('\n') if line.strip()]
        expanded_queries = [q for q in expanded_queries if not q.startswith(('1.', '2.', '3.'))]
        
        # Add original query
        all_queries = [question] + expanded_queries[:3]
        
        # Search for each query and combine results
        all_docs = []
        for query in all_queries:
            docs = vectorstore.similarity_search(query, k=3)
            all_docs.extend(docs)
        
        # Remove duplicates and get top 5
        seen_content = set()
        unique_docs = []
        for doc in all_docs:
            if doc.page_content not in seen_content:
                seen_content.add(doc.page_content)
                unique_docs.append(doc)
                if len(unique_docs) >= 5:
                    break
        
        context_docs = [doc.page_content for doc in unique_docs]
        context_text = "\n\n".join(context_docs)
        
        # Generate answer
        prompt = f"""Based on the following context, answer the question: {question}

Context:
{context_text}

Answer:"""
        
        response = llm.invoke(prompt)
        answer = response.content if hasattr(response, 'content') else str(response)
        
        return {
            'question': question,
            'answer': answer,
            'context': context_docs,
            'method': 'Query Expansion'
        }
        
    except Exception as e:
        return {
            'question': question,
            'answer': f"Error generating response: {str(e)}",
            'context': [],
            'method': 'Query Expansion (Error)'
        }

# Available retriever methods
RETRIEVER_METHODS = {
    'Original RAG': None,  # Use default traceback_graph
    'Hybrid Search': generate_hybrid_response,
    'Lineage-Aware Retrieval': generate_lineage_aware_response,
    'Cohere Reranking': generate_cohere_reranking_response,
    'Query Expansion': generate_query_expansion_response
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the Traceback system on startup."""
    global traceback_graph, lineage_retriever, vectorstore, llm
    
    print("🚀 Initializing Traceback system...")
    
    try:
        # Initialize core components
        from tracebackcore.core import initialize_system
        initialize_system()
        
        # Update global variables
        from tracebackcore.core import traceback_graph as tg, lineage_retriever as lr, vectorstore as vs, llm as llm_obj
        traceback_graph = tg
        lineage_retriever = lr
        vectorstore = vs
        llm = llm_obj
        
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
    retriever: Optional[str] = "Original RAG"

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
        "tavily_key": bool(os.getenv("TAVILY_API_KEY")),
        "cohere_key": bool(os.getenv("COHERE_API_KEY"))
    }
    
    overall_status = "healthy" if all(system_health.values()) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        timestamp=time.time(),
        system_health=system_health
    )

@app.get("/retrievers")
async def get_available_retrievers():
    """Get available retriever methods."""
    return {
        "available_retrievers": list(RETRIEVER_METHODS.keys()),
        "descriptions": {
            "Original RAG": "Standard RAG with full incident triage workflow",
            "Hybrid Search": "Vector search combined with BM25 scoring",
            "Lineage-Aware Retrieval": "Context-aware search with data lineage",
            "Cohere Reranking": "Advanced reranking with Cohere API",
            "Query Expansion": "Semantic query enhancement with multiple search strategies"
        }
    }

@app.post("/incident/triage", response_model=IncidentResponse)
async def triage_incident(request: IncidentRequest):
    """Main incident triage endpoint."""
    if not traceback_graph:
        raise HTTPException(status_code=503, detail="Traceback system not initialized")
    
    start_time = time.time()
    
    try:
        # Check if using advanced retriever
        retriever_method = request.retriever or "Original RAG"
        
        if retriever_method != "Original RAG" and retriever_method in RETRIEVER_METHODS:
            # Use advanced retriever
            retriever_func = RETRIEVER_METHODS[retriever_method]
            if retriever_func:
                result = retriever_func(request.question)
                
                processing_time = time.time() - start_time
                
                # Convert advanced retriever result to IncidentResponse format
                incident_brief = result.get("incident_brief") or result.get("answer", "No response generated")
                blast_radius = result.get("blast_radius", [])
                context_sources = result.get("sources", [])
                impact_assessment_value = result.get("impact_assessment") or "See incident brief for combined analysis."

                impact_assessment = {
                    "assessment": impact_assessment_value,
                    "context_sources": [{"source": src} for src in context_sources] or [{"source": f"Advanced Retriever: {retriever_method}"}],
                    "method": result.get("method", retriever_method)
                }
                
                return IncidentResponse(
                    incident_brief=incident_brief,
                    blast_radius=blast_radius,
                    impact_assessment=impact_assessment,
                    processing_time=processing_time,
                    sources_used=context_sources if context_sources else [f"Advanced Retriever: {retriever_method}"]
                )
        
        # Use original RAG workflow
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
