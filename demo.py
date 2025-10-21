"""
Traceback Demo Script

Simple demo script to showcase the Traceback system.
"""

import os
import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

def main():
    """Run a demo of the Traceback system."""
    print("🚨 Traceback Demo - Data Pipeline Incident Triage")
    print("=" * 60)
    
    try:
        # Import core system
        from tracebackcore.core import traceback_graph, AgentState, initialize_system
        
        # Initialize system if not already done
        if not traceback_graph:
            initialize_system()
        
        if not traceback_graph:
            print("❌ Traceback system not initialized")
            return
        
        # Demo questions
        demo_questions = [
            "Job curated.sales_orders failed — who's impacted?",
            "What should I do if raw.sales_orders has quality issues?",
            "Which dashboards depend on curated.revenue_summary?"
        ]
        
        for i, question in enumerate(demo_questions, 1):
            print(f"\n🔍 Demo {i}: {question}")
            print("-" * 50)
            
            start_time = time.time()
            
            # Run triage
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
            
            processing_time = time.time() - start_time
            
            # Display results
            if result.get("incident_brief"):
                print(f"\n📋 Incident Brief:")
                print(result["incident_brief"])
            
            if result.get("blast_radius"):
                print(f"\n💥 Blast Radius:")
                for item in result["blast_radius"][:5]:
                    print(f"  • {item}")
            
            print(f"\n⏱️ Processing time: {processing_time:.2f}s")
            print("=" * 60)
        
        print("\n🎉 Demo completed successfully!")
        print("\nNext steps:")
        print("  • Start API server: python -m tracebackcore.cli.main serve")
        print("  • Use CLI: python -m tracebackcore.cli.main triage 'your question'")
        print("  • View API docs: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        return

if __name__ == "__main__":
    main()
