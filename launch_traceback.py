#!/usr/bin/env python3
"""
Traceback System Launcher

This script launches both the Traceback API server and the Web UI.
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def start_api_server():
    """Start the Traceback API server."""
    print("🚀 Starting Traceback API server...")
    
    # Use the project root directory
    project_root = Path(__file__).parent
    
    try:
        # Start the API server using uvicorn directly
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "src.tracebackcore.api.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ], cwd=project_root)
        
        print("✅ API server started (PID: {})".format(process.pid))
        print("📡 API available at: http://localhost:8000")
        
        return process
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        return None

def start_web_ui():
    """Start the Web UI server."""
    print("🌐 Starting Web UI server...")
    
    # Change to the web_ui directory
    web_ui_dir = Path(__file__).parent / "web_ui"
    
    try:
        # Start the Web UI server
        process = subprocess.Popen([
            sys.executable, "server.py"
        ], cwd=web_ui_dir)
        
        print("✅ Web UI server started (PID: {})".format(process.pid))
        print("📱 Web UI available at: http://localhost:3000")
        
        return process
    except Exception as e:
        print(f"❌ Failed to start Web UI server: {e}")
        return None

def main():
    """Main launcher function."""
    print("=" * 60)
    print("🎯 Traceback Data Pipeline Incident Triage System")
    print("=" * 60)
    
    # Start API server
    api_process = start_api_server()
    if not api_process:
        print("❌ Cannot start Web UI without API server")
        return 1
    
    # Wait a moment for API to initialize
    print("⏳ Waiting for API server to initialize...")
    time.sleep(3)
    
    # Start Web UI server
    web_process = start_web_ui()
    if not web_process:
        print("❌ Failed to start Web UI server")
        api_process.terminate()
        return 1
    
    print("\n" + "=" * 60)
    print("🎉 Traceback System Started Successfully!")
    print("=" * 60)
    print("📡 API Server: http://localhost:8000")
    print("📱 Web UI: http://localhost:3000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("=" * 60)
    print("⏹️  Press Ctrl+C to stop both servers")
    print("=" * 60)
    
    try:
        # Wait for both processes
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if api_process.poll() is not None:
                print("❌ API server stopped unexpectedly")
                break
            if web_process.poll() is not None:
                print("❌ Web UI server stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Traceback system...")
        
        # Terminate both processes
        if api_process:
            api_process.terminate()
            print("✅ API server stopped")
        
        if web_process:
            web_process.terminate()
            print("✅ Web UI server stopped")
        
        print("👋 Traceback system shutdown complete")
        return 0

if __name__ == "__main__":
    sys.exit(main())
