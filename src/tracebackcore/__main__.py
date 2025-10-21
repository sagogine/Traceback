"""
Traceback Package Entry Point

Main entry point for the Traceback package.
"""

import sys
from pathlib import Path

# Add notebooks to path for core system
sys.path.append(str(Path(__file__).parent / "notebooks"))

def main():
    """Main entry point for Traceback."""
    print("🚨 Traceback - Data Pipeline Incident Triage System")
    print("Version: 1.0.0")
    print()
    print("Available commands:")
    print("  • demo: Run a demo of the system")
    print("  • api: Start the API server")
    print("  • cli: Use the command-line interface")
    print()
    print("Examples:")
    print("  python demo.py")
    print("  python -m tracebackcore.cli.main triage 'Job failed'")
    print("  python -m tracebackcore.api.main")

if __name__ == "__main__":
    main()
