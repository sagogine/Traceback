"""
Traceback Core System

Extracted core components from the Jupyter notebook for API/CLI usage.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Verify API keys
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY is not set. Create a .env file or export it in your shell.")

# Import required libraries
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_qdrant import Qdrant
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langgraph.graph import StateGraph, END
from langchain.tools import Tool
from langchain_community.tools import TavilySearchResults
from typing import TypedDict

# Define the agent state
class AgentState(TypedDict):
    question: str
    context: List[Dict[str, Any]]
    impact_assessment: Optional[Dict[str, Any]]
    blast_radius: Optional[List[str]]
    recommended_actions: Optional[List[str]]
    incident_brief: Optional[str]
    current_step: str
    error: Optional[str]

# Global variables for the system
qdrant_client = None
embeddings = None
llm = None
vectorstore = None
lineage_retriever = None
traceback_graph = None

def create_fallback_lineage_data():
    """Create fallback lineage data if comprehensive data is not available."""
    return {
        "nodes": [
            {"id": "raw.sales_orders", "type": "table", "schema": "raw"},
            {"id": "curated.sales_orders", "type": "table", "schema": "curated"},
            {"id": "curated.revenue_summary", "type": "table", "schema": "curated"},
            {"id": "analytics.customer_behavior", "type": "table", "schema": "analytics"}
        ],
        "edges": [
            {"from": "raw.sales_orders", "to": "curated.sales_orders", "operation": "clean+enrich"},
            {"from": "curated.sales_orders", "to": "curated.revenue_summary", "operation": "aggregate"},
            {"from": "curated.sales_orders", "to": "analytics.customer_behavior", "operation": "aggregate"}
        ],
        "dashboards": [
            {"id": "bi.daily_sales", "tables": ["curated.sales_orders", "curated.revenue_summary"]},
            {"id": "bi.customer_analytics", "tables": ["analytics.customer_behavior"]}
        ]
    }

def initialize_system():
    """Initialize the Traceback system."""
    global qdrant_client, embeddings, llm, vectorstore, lineage_retriever, traceback_graph
    
    print("🚀 Initializing Traceback system...")
    
    # Initialize Qdrant client (in-memory for demo)
    qdrant_client = QdrantClient(":memory:")
    
    # Initialize embeddings
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Initialize LLM
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.1
    )
    
    # Create collection
    collection_name = "traceback_documents"
    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=1536,  # text-embedding-3-small dimension
            distance=Distance.COSINE
        )
    )
    
    # Initialize vector store
    vectorstore = Qdrant(
        client=qdrant_client,
        collection_name=collection_name,
        embeddings=embeddings
    )
    
    # Load all documents from data directories
    print("📚 Loading all specifications and SQL pipelines...")
    
    # Get project root
    project_root = Path(__file__).parent.parent.parent
    docs_dir = project_root / "data" / "docs"
    repo_dir = project_root / "data" / "repo"
    
    all_docs = []
    doc_id = 0
    
    # Load all markdown files from docs directory
    if docs_dir.exists():
        for md_file in docs_dir.glob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                all_docs.append(Document(
                    page_content=content,
                    metadata={"type": "markdown", "file_name": md_file.name, "doc_id": doc_id}
                ))
                doc_id += 1
            except Exception as e:
                print(f"⚠️ Error loading {md_file}: {e}")
    
    # Load all SQL files from repo directory
    if repo_dir.exists():
        for sql_file in repo_dir.glob("*.sql"):
            try:
                with open(sql_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                all_docs.append(Document(
                    page_content=content,
                    metadata={"type": "sql", "file_name": sql_file.name, "doc_id": doc_id}
                ))
                doc_id += 1
            except Exception as e:
                print(f"⚠️ Error loading {sql_file}: {e}")
    
    print(f"✅ Loaded {len(all_docs)} documents ({len([d for d in all_docs if d.metadata['type'] == 'markdown'])} specs, {len([d for d in all_docs if d.metadata['type'] == 'sql'])} SQL files)")
    
    # Add documents to vector store
    if all_docs:
        vectorstore.add_documents(all_docs)
    else:
        print("⚠️ No documents found, using fallback sample data")
        # Fallback to sample data if no files found
        sample_docs = [
            Document(
                page_content="Sales orders pipeline processes raw order data into curated datasets for analytics and reporting.",
                metadata={"type": "markdown", "file_name": "sales_orders_spec.md", "doc_id": 0}
            ),
            Document(
                page_content="SELECT * FROM curated.sales_orders WHERE order_date >= CURRENT_DATE - 1",
                metadata={"type": "sql", "file_name": "sales_orders_pipeline.sql", "doc_id": 1}
            ),
            Document(
                page_content="Data pipeline incident response procedures: 1. Acknowledge incident 2. Assess impact 3. Determine blast radius 4. Notify stakeholders",
                metadata={"type": "markdown", "file_name": "incident_playbook.md", "doc_id": 2}
            )
        ]
        vectorstore.add_documents(sample_docs)
    
    # Load comprehensive lineage data
    lineage_file = project_root / "data" / "lineage.json"
    if lineage_file.exists():
        try:
            with open(lineage_file, 'r', encoding='utf-8') as f:
                lineage_data = json.load(f)
            print(f"✅ Loaded comprehensive lineage data: {len(lineage_data.get('nodes', []))} nodes, {len(lineage_data.get('edges', []))} edges")
        except Exception as e:
            print(f"⚠️ Error loading lineage.json: {e}")
            lineage_data = create_fallback_lineage_data()
    else:
        print("⚠️ lineage.json not found, using fallback data")
        lineage_data = create_fallback_lineage_data()
    
    # Initialize lineage retriever
    lineage_retriever = LineageAwareRetriever(vectorstore, lineage_data)
    
    # Create agent system
    traceback_graph = create_agent_workflow()
    
    print("✅ Traceback system initialized successfully")

class LineageAwareRetriever:
    """Enhanced retriever that combines vector search with lineage queries."""
    
    def __init__(self, vectorstore, lineage_data):
        self.vectorstore = vectorstore
        self.lineage_data = lineage_data
    
    def find_downstream_impact(self, node_id: str) -> List[str]:
        """Find all downstream dependencies of a node."""
        downstream = []
        visited = set()
        
        def dfs(current_node):
            if current_node in visited:
                return
            visited.add(current_node)
            
            for edge in self.lineage_data.get("edges", []):
                if edge["from"] == current_node:
                    downstream.append(edge["to"])
                    dfs(edge["to"])
        
        dfs(node_id)
        return downstream
    
    def find_upstream_dependencies(self, node_id: str) -> List[str]:
        """Find all upstream dependencies of a node."""
        upstream = []
        visited = set()
        
        def dfs(current_node):
            if current_node in visited:
                return
            visited.add(current_node)
            
            for edge in self.lineage_data.get("edges", []):
                if edge["to"] == current_node:
                    upstream.append(edge["from"])
                    dfs(edge["from"])
        
        dfs(node_id)
        return upstream
    
    def search_with_lineage(self, query: str, k: int = 5) -> List[Document]:
        """Search with both vector similarity and lineage context."""
        # Regular vector search
        vector_results = self.vectorstore.similarity_search(query, k=k)
        
        # Extract table names from query
        table_names = []
        for word in query.split():
            if '.' in word and any(schema in word for schema in ['raw.', 'curated.', 'analytics.']):
                table_names.append(word)
        
        # Add lineage context if tables found
        lineage_context = []
        for table_name in table_names:
            downstream = self.find_downstream_impact(table_name)
            upstream = self.find_upstream_dependencies(table_name)
            
            if downstream or upstream:
                context_text = f"Table {table_name}: "
                if upstream:
                    context_text += f"Depends on {', '.join(upstream[:3])}. "
                if downstream:
                    context_text += f"Impacts {', '.join(downstream[:3])}."
                
                lineage_context.append(Document(
                    page_content=context_text,
                    metadata={"type": "lineage", "table": table_name}
                ))
        
        # Combine results
        all_results = vector_results + lineage_context
        return all_results[:k]

def create_agent_workflow():
    """Create the LangGraph agent workflow."""
    
    def supervisor_agent(state: AgentState) -> AgentState:
        """Supervisor agent that orchestrates the incident triage workflow."""
        question = state["question"]
        
        # Simple routing logic
        if "curated.sales_orders" in question or "sales_orders" in question:
            state["current_step"] = "impact_assessor"
        else:
            state["current_step"] = "writer"
        
        return state
    
    def impact_assessor_agent(state: AgentState) -> AgentState:
        """Impact Assessor agent that analyzes business impact and blast radius."""
        question = state["question"]
        
        # Use RAG search to gather context
        results = lineage_retriever.search_with_lineage(question, k=3)
        context = "\n".join([doc.page_content for doc in results])
        
        # Extract table names for lineage analysis
        table_names = []
        for word in question.split():
            if '.' in word and any(schema in word for schema in ['raw.', 'curated.', 'analytics.']):
                table_names.append(word)
        
        # Generate impact assessment
        impact_prompt = f"""
        You are the Impact Assessor Agent for Traceback.
        
        Question: {question}
        
        Context: {context}
        
        Provide a structured impact assessment:
        1. Business Impact Level (Critical/High/Medium/Low)
        2. Affected Systems/Tables
        3. Blast Radius (downstream impact)
        4. SLA Impact
        5. Estimated Recovery Time
        """
        
        try:
            response = llm.invoke([{"role": "user", "content": impact_prompt}])
            
            state["impact_assessment"] = {
                "assessment": response.content,
                "context_sources": [{"content": doc.page_content, "source": doc.metadata.get("file_name", "unknown")} for doc in results]
            }
            
            # Extract blast radius
            blast_radius = []
            for table_name in table_names:
                blast_radius.extend(lineage_retriever.find_downstream_impact(table_name))
            
            state["blast_radius"] = list(set(blast_radius))
            state["current_step"] = "writer"
            
        except Exception as e:
            state["error"] = f"Impact assessor error: {str(e)}"
            state["current_step"] = "writer"
        
        return state
    
    def writer_agent(state: AgentState) -> AgentState:
        """Writer agent that generates the final incident brief."""
        question = state["question"]
        impact_assessment = state.get("impact_assessment", {})
        blast_radius = state.get("blast_radius", [])
        
        # Generate incident brief
        writer_prompt = f"""
        You are the Writer Agent for Traceback incident triage.
        
        Question: {question}
        
        Impact Assessment: {json.dumps(impact_assessment, indent=2)}
        
        Blast Radius: {blast_radius}
        
        Generate a comprehensive incident brief with:
        1. **Incident Summary**: Brief description
        2. **Business Impact**: Level and details
        3. **Blast Radius**: Affected systems/tables
        4. **Root Cause Analysis**: Likely causes
        5. **Recommended Actions**: Immediate steps
        6. **Recovery Plan**: Step-by-step recovery
        7. **Prevention**: Future mitigation
        
        Format as a professional incident brief.
        """
        
        try:
            response = llm.invoke([{"role": "user", "content": writer_prompt}])
            
            state["incident_brief"] = response.content
            state["current_step"] = "complete"
            
        except Exception as e:
            state["error"] = f"Writer error: {str(e)}"
            state["incident_brief"] = f"Error generating incident brief: {str(e)}"
            state["current_step"] = "complete"
        
        return state
    
    # Create the LangGraph workflow
    workflow = StateGraph(AgentState)
    
    # Add nodes for each agent
    workflow.add_node("supervisor", supervisor_agent)
    workflow.add_node("impact_assessor", impact_assessor_agent)
    workflow.add_node("writer", writer_agent)
    
    # Define the workflow edges
    workflow.add_edge("supervisor", "impact_assessor")
    workflow.add_edge("impact_assessor", "writer")
    workflow.add_edge("writer", END)
    
    # Set entry point
    workflow.set_entry_point("supervisor")
    
    # Compile the graph
    return workflow.compile()

# Initialize the system when imported
if __name__ != "__main__":
    initialize_system()
