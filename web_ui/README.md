# Traceback Web UI

A modern, interactive web interface for the Traceback Data Pipeline Incident Triage API.

## Features

### 🚨 Incident Triage
- **AI-Powered Analysis**: Submit incident descriptions and get comprehensive analysis
- **Priority Levels**: Set incident priority (Low, Medium, High, Critical)
- **Detailed Reports**: Get incident briefs, blast radius analysis, and impact assessments
- **Processing Metrics**: View response times and source usage

### 🔍 Document Search
- **RAG-Powered Search**: Search through all documents using vector similarity
- **Configurable Results**: Choose how many results to return (3, 5, or 10)
- **Rich Metadata**: View document sources, types, and metadata
- **Content Preview**: See relevant content snippets

### 📊 Data Lineage
- **Dependency Mapping**: View upstream dependencies and downstream impact
- **Table Analysis**: Get comprehensive lineage information for any table
- **Visual Representation**: Clear visualization of data relationships
- **Impact Assessment**: Understand the scope of changes

### 📈 System Statistics
- **Real-time Metrics**: View system health and statistics
- **Document Count**: Number of documents in the vector store
- **Lineage Graph**: Nodes and edges in the lineage graph
- **API Version**: Current API version information

## Quick Start

### 1. Start the Traceback API
```bash
# From the project root
cd src/tracebackcore/api
python main.py
```
The API will be available at `http://localhost:8000`

### 2. Start the Web UI Server
```bash
# From the project root
cd web_ui
python server.py
```
The Web UI will be available at `http://localhost:3000`

### 3. Open the Web Interface
The browser should open automatically, or navigate to `http://localhost:3000`

## Usage

### Incident Triage
1. Navigate to the "Incident Triage" tab
2. Enter a detailed description of the data pipeline incident
3. Select the appropriate priority level
4. Click "Analyze Incident" to get AI-powered analysis
5. Review the incident brief, blast radius, and impact assessment

### Document Search
1. Navigate to the "Document Search" tab
2. Enter your search query
3. Select the number of results you want
4. Click "Search Documents" to find relevant information
5. Review the search results with content previews

### Data Lineage
1. Navigate to the "Data Lineage" tab
2. Enter the name of a table or data asset
3. Click "Get Lineage" to view dependencies
4. Review upstream dependencies and downstream impact

### System Statistics
1. Navigate to the "System Stats" tab
2. View real-time system metrics
3. Click "Refresh Stats" to update the information

## Configuration

### API Base URL
- Default: `http://localhost:8000`
- Change the API Base URL in the configuration section if your API is running on a different host/port
- Click "Test Connection" to verify the connection

### Custom Ports
```bash
# Serve on a different port
python server.py 8080
```

## API Endpoints Used

The Web UI interacts with the following Traceback API endpoints:

- `GET /health` - System health check
- `POST /incident/triage` - Incident triage analysis
- `GET /incident/search` - Document search
- `GET /lineage/{table_name}` - Data lineage information
- `GET /system/stats` - System statistics

## Features

### Modern Design
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Tailwind CSS**: Modern, clean styling
- **Font Awesome Icons**: Intuitive iconography
- **Smooth Animations**: Fade-in effects and hover states

### User Experience
- **Tabbed Interface**: Easy navigation between different features
- **Loading States**: Visual feedback during API calls
- **Error Handling**: Clear error messages and status indicators
- **Auto-refresh**: System stats update automatically

### Accessibility
- **Keyboard Navigation**: Full keyboard support
- **Screen Reader Friendly**: Proper ARIA labels and semantic HTML
- **High Contrast**: Clear visual hierarchy and contrast

## Troubleshooting

### Connection Issues
- Ensure the Traceback API is running on `http://localhost:8000`
- Check the API Base URL configuration
- Verify network connectivity
- Check browser console for error messages

### Performance Issues
- Large documents may take longer to process
- Reduce the search limit for faster results
- Check system resources and API server logs

### Browser Compatibility
- Modern browsers (Chrome, Firefox, Safari, Edge)
- JavaScript must be enabled
- Local storage may be used for preferences

## Development

### File Structure
```
web_ui/
├── index.html          # Main web interface
├── server.py           # Simple HTTP server
└── README.md           # This file
```

### Customization
- Modify `index.html` to customize the interface
- Update CSS classes for styling changes
- Add new API endpoints in the JavaScript section
- Extend the server functionality in `server.py`

## Security Notes

- This is a development interface
- No authentication is implemented
- API keys are not exposed to the frontend
- Use HTTPS in production environments
- Implement proper authentication for production use

