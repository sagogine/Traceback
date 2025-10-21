"""
Traceback CLI

Command-line interface for the Traceback incident triage system.
"""

import os
import json
import time
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add src to path for imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import our core system components
from tracebackcore.core import traceback_graph, lineage_retriever, vectorstore, AgentState, initialize_system

console = Console()

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Traceback CLI - Data Pipeline Incident Triage System."""
    pass

@cli.command()
@click.argument("question")
@click.option("--priority", "-p", default="medium", help="Incident priority")
@click.option("--output", "-o", type=click.Choice(["text", "json"]), default="text", help="Output format")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def triage(question: str, priority: str, output: str, verbose: bool):
    """Triage a data pipeline incident."""
    
    console.print(f"🚨 [bold red]Traceback Incident Triage[/bold red]")
    console.print(f"📋 Question: {question}")
    console.print(f"⚡ Priority: {priority}")
    console.print()
    
    try:
        # Import core system
        from tracebackcore.core import traceback_graph, AgentState, initialize_system
        
        # Initialize system if not already done
        if not traceback_graph:
            initialize_system()
        
        if not traceback_graph:
            console.print("❌ [red]Traceback system not initialized[/red]")
            sys.exit(1)
        
        # Run triage
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Analyzing incident...", total=None)
            
            initial_state = AgentState(
                question=question,
                context=[],
                impact_assessment=None,
                blast_radius=None,
                recommended_actions=None,
                incident_brief=None,
                current_step="supervisor",
                error=None
            )
            
            result = traceback_graph.invoke(initial_state)
        
        # Display results
        if output == "json":
            console.print(json.dumps({
                "question": question,
                "incident_brief": result.get("incident_brief", ""),
                "blast_radius": result.get("blast_radius", []),
                "impact_assessment": result.get("impact_assessment", {}),
                "error": result.get("error")
            }, indent=2))
        else:
            # Text output
            if result.get("incident_brief"):
                console.print(Panel(
                    result["incident_brief"],
                    title="📋 Incident Brief",
                    border_style="blue"
                ))
            
            if result.get("blast_radius"):
                console.print("\n💥 [bold]Blast Radius:[/bold]")
                for item in result["blast_radius"][:10]:  # Show top 10
                    console.print(f"  • {item}")
            
            if verbose and result.get("impact_assessment"):
                console.print("\n📊 [bold]Impact Assessment:[/bold]")
                assessment = result["impact_assessment"]
                if isinstance(assessment, dict):
                    console.print(json.dumps(assessment, indent=2))
        
        if result.get("error"):
            console.print(f"\n⚠️ [yellow]Warning: {result['error']}[/yellow]")
            
    except Exception as e:
        console.print(f"❌ [red]Error: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
@click.argument("query")
@click.option("--limit", "-l", default=5, help="Number of results")
@click.option("--type", "-t", help="Filter by document type")
def search(query: str, limit: int, type: Optional[str]):
    """Search documents and code."""
    
    console.print(f"🔍 [bold]Searching for:[/bold] {query}")
    console.print()
    
    try:
        from tracebackcore.core import lineage_retriever, initialize_system
        
        # Initialize system if not already done
        if not lineage_retriever:
            initialize_system()
        
        if not lineage_retriever:
            console.print("❌ [red]RAG system not initialized[/red]")
            sys.exit(1)
        
        results = lineage_retriever.search_with_lineage(query, k=limit)
        
        if not results:
            console.print("🔍 [yellow]No results found[/yellow]")
            return
        
        # Create results table
        table = Table(title=f"Search Results ({len(results)} found)")
        table.add_column("Source", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Content", style="white")
        
        for doc in results:
            doc_type = doc.metadata.get("type", "unknown")
            if type and doc_type != type:
                continue
                
            table.add_row(
                doc.metadata.get("file_name", "unknown"),
                doc_type,
                doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ [red]Error: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
@click.argument("table_name")
def lineage(table_name: str):
    """Get lineage information for a table."""
    
    console.print(f"🧬 [bold]Lineage Analysis for:[/bold] {table_name}")
    console.print()
    
    try:
        from tracebackcore.core import lineage_retriever, initialize_system
        
        # Initialize system if not already done
        if not lineage_retriever:
            initialize_system()
        
        if not lineage_retriever:
            console.print("❌ [red]Lineage system not initialized[/red]")
            sys.exit(1)
        
        downstream = lineage_retriever.find_downstream_impact(table_name)
        upstream = lineage_retriever.find_upstream_dependencies(table_name)
        
        # Upstream dependencies
        if upstream:
            console.print("📉 [bold]Upstream Dependencies:[/bold]")
            for dep in upstream:
                console.print(f"  • {dep}")
        else:
            console.print("📉 [yellow]No upstream dependencies found[/yellow]")
        
        console.print()
        
        # Downstream impact
        if downstream:
            console.print("📈 [bold]Downstream Impact:[/bold]")
            for impact in downstream:
                console.print(f"  • {impact}")
        else:
            console.print("📈 [yellow]No downstream impact found[/yellow]")
        
        console.print(f"\n📊 [bold]Total Dependencies:[/bold] {len(upstream) + len(downstream)}")
        
    except Exception as e:
        console.print(f"❌ [red]Error: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
def status():
    """Check system status."""
    
    console.print("🔍 [bold]Traceback System Status[/bold]")
    console.print()
    
    try:
        from tracebackcore.core import traceback_graph, lineage_retriever, vectorstore, initialize_system
        
        # Initialize system if not already done
        if not traceback_graph:
            initialize_system()
        
        # System components
        table = Table(title="System Components")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        
        table.add_row("Traceback Graph", "✅ Ready" if traceback_graph else "❌ Not initialized")
        table.add_row("Lineage Retriever", "✅ Ready" if lineage_retriever else "❌ Not initialized")
        table.add_row("Vector Store", "✅ Ready" if vectorstore else "❌ Not initialized")
        
        console.print(table)
        
        # API Keys
        console.print("\n🔑 [bold]API Keys:[/bold]")
        console.print(f"  OpenAI: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Not set'}")
        console.print(f"  Tavily: {'✅ Set' if os.getenv('TAVILY_API_KEY') else '❌ Not set'}")
        console.print(f"  Cohere: {'✅ Set' if os.getenv('COHERE_API_KEY') else '❌ Not set'}")
        
        # System stats
        if lineage_retriever:
            console.print(f"\n📊 [bold]System Stats:[/bold]")
            console.print(f"  Lineage Nodes: {len(lineage_retriever.lineage_data.get('nodes', []))}")
            console.print(f"  Lineage Edges: {len(lineage_retriever.lineage_data.get('edges', []))}")
        
        if vectorstore:
            console.print(f"  Documents Indexed: {len(vectorstore.documents) if hasattr(vectorstore, 'documents') else 'Unknown'}")
        
    except Exception as e:
        console.print(f"❌ [red]Error checking status: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--port", default=8000, help="Port to bind to")
@click.option("--reload", is_flag=True, help="Enable auto-reload")
def serve(host: str, port: int, reload: bool):
    """Start the Traceback API server."""
    
    console.print(f"🚀 [bold]Starting Traceback API Server[/bold]")
    console.print(f"🌐 Host: {host}")
    console.print(f"🔌 Port: {port}")
    console.print(f"🔄 Reload: {'Enabled' if reload else 'Disabled'}")
    console.print()
    
    try:
        import uvicorn
        uvicorn.run(
            "tracebackcore.api.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except Exception as e:
        console.print(f"❌ [red]Error starting server: {str(e)}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    cli()
