#!/usr/bin/env python3
"""
Simple HTTP server to serve the Traceback Web UI
"""

import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

def serve_web_ui(port=3000):
    """Serve the web UI on the specified port."""
    
    # The script is already in the web_ui directory
    web_ui_dir = Path(__file__).parent
    os.chdir(web_ui_dir)
    
    # Create a custom handler to serve index.html for root requests
    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                self.path = '/index.html'
            return super().do_GET()
    
    # Start the server
    with socketserver.TCPServer(("", port), CustomHandler) as httpd:
        print(f"🌐 Traceback Web UI server starting...")
        print(f"📱 Web UI available at: http://localhost:{port}")
        print(f"🔗 Make sure the Traceback API is running at: http://localhost:8000")
        print(f"⏹️  Press Ctrl+C to stop the server")
        
        # Try to open the browser automatically
        try:
            webbrowser.open(f'http://localhost:{port}')
            print(f"🚀 Browser opened automatically")
        except:
            print(f"⚠️  Could not open browser automatically")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n🛑 Server stopped")

if __name__ == "__main__":
    import sys
    
    port = 3000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number. Using default port 3000.")
    
    serve_web_ui(port)
