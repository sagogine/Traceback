# Traceback API and CLI Usage

## 🚀 Quick Start

### 1. Run Demo
```bash
python demo.py
```

### 2. Start API Server
```bash
python -m tracebackcore.api.main
# Or with uvicorn directly:
uvicorn src.tracebackcore.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Use CLI
```bash
# Triage an incident
python -m tracebackcore.cli.main triage "Job curated.sales_orders failed — who's impacted?"

# Search documents
python -m tracebackcore.cli.main search "sales orders pipeline"

# Check lineage
python -m tracebackcore.cli.main lineage "curated.sales_orders"

# Check system status
python -m tracebackcore.cli.main status

# Start API server via CLI
python -m tracebackcore.cli.main serve --host 0.0.0.0 --port 8000
```

## 🌐 API Endpoints

Once the server is running (http://localhost:8000):

### Core Endpoints
- `GET /` - API information
- `GET /health` - Health check
- `POST /incident/triage` - Main incident triage
- `GET /incident/search` - Search documents
- `GET /lineage/{table_name}` - Get lineage info
- `GET /system/stats` - System statistics

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Example API Usage
```bash
# Triage incident
curl -X POST "http://localhost:8000/incident/triage" \
  -H "Content-Type: application/json" \
  -d '{"question": "Job curated.sales_orders failed — who'\''s impacted?"}'

# Search documents
curl "http://localhost:8000/incident/search?query=sales%20orders&limit=3"

# Get lineage
curl "http://localhost:8000/lineage/curated.sales_orders"

# Health check
curl "http://localhost:8000/health"
```

## 🎯 Features

### API Server
- ✅ FastAPI with automatic OpenAPI docs
- ✅ CORS enabled for web integration
- ✅ Health checks and system monitoring
- ✅ Structured error handling
- ✅ Background task support
- ✅ Production-ready with uvicorn

### CLI Interface
- ✅ Rich terminal output with colors and tables
- ✅ Multiple commands (triage, search, lineage, status)
- ✅ JSON output option
- ✅ Verbose mode for debugging
- ✅ Progress indicators
- ✅ Error handling and status codes

### Demo Script
- ✅ Simple showcase of core functionality
- ✅ Multiple test scenarios
- ✅ Performance timing
- ✅ Usage instructions

## 🔧 Configuration

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your_openai_key

# Optional
TAVILY_API_KEY=your_tavily_key
COHERE_API_KEY=your_cohere_key
```

### API Configuration
- Host: 0.0.0.0 (configurable)
- Port: 8000 (configurable)
- Auto-reload: Enabled in development
- Logging: Info level

## 📊 System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   CLI Interface  │    │   Demo Script   │
│   Server        │    │   (Rich)         │    │   (Simple)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Core System   │
                    │   (Notebook)    │
                    │                 │
                    │ • LangGraph     │
                    │ • RAG System    │
                    │ • Lineage       │
                    │ • Agents        │
                    └─────────────────┘
```

## 🚀 Production Deployment

### Docker (Optional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -e .
EXPOSE 8000
CMD ["uvicorn", "tracebackcore.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Setup
```bash
# Install dependencies
uv sync

# Set environment variables
export OPENAI_API_KEY="your_key"

# Start server
uvicorn src.tracebackcore.api.main:app --host 0.0.0.0 --port 8000
```

## 🧪 Testing

### API Testing
```bash
# Health check
curl http://localhost:8000/health

# Triage test
curl -X POST http://localhost:8000/incident/triage \
  -H "Content-Type: application/json" \
  -d '{"question": "Test incident"}'
```

### CLI Testing
```bash
# Status check
python -m tracebackcore.cli.main status

# Quick triage
python -m tracebackcore.cli.main triage "Test question"
```

## 📝 Next Steps

1. **Run the demo** to see the system in action
2. **Start the API server** for web integration
3. **Use the CLI** for command-line operations
4. **Integrate with your tools** via the API
5. **Deploy to production** with proper configuration
