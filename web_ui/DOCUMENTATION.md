# Traceback Web UI Documentation

## Overview

The Traceback Web UI is a modern, interactive web interface for the Traceback Data Pipeline Incident Triage API. It provides an intuitive way to interact with all the API endpoints through a beautiful, responsive web interface.

## Architecture

```
┌─────────────────┐    HTTP/HTTPS    ┌─────────────────┐
│   Web Browser   │ ◄──────────────► │   Web UI Server │
│                 │                  │   (Port 3000)   │
└─────────────────┘                  └─────────────────┘
                                              │
                                              │ HTTP/HTTPS
                                              ▼
                                     ┌─────────────────┐
                                     │ Traceback API   │
                                     │ (Port 8000)     │
                                     └─────────────────┘
```

## Features

### 🚨 Incident Triage Tab
- **Purpose**: Submit data pipeline incidents for AI-powered analysis
- **Input**: Incident description (text area) and priority level (dropdown)
- **Output**: 
  - Incident Brief (AI-generated summary)
  - Blast Radius (affected systems/components)
  - Impact Assessment (detailed analysis)
  - Processing metrics (time, sources used)

### 🔍 Document Search Tab
- **Purpose**: Search through documents using RAG (Retrieval-Augmented Generation)
- **Input**: Search query (text input) and result limit (dropdown: 3, 5, 10)
- **Output**: 
  - Search results with content previews
  - Document metadata (source, type)
  - Relevance scores and snippets

### 📊 Data Lineage Tab
- **Purpose**: Analyze data dependencies and lineage
- **Input**: Table name (text input)
- **Output**: 
  - Upstream dependencies
  - Downstream impact
  - Total dependency count

### 📈 System Stats Tab
- **Purpose**: Monitor system health and statistics
- **Features**: 
  - Real-time metrics display
  - Auto-refresh every 30 seconds
  - Manual refresh button
  - System health indicators

## User Interface Components

### Header
- **Logo**: Traceback branding with search icon
- **Status Indicator**: Real-time system health (green/yellow/red dot)
- **Version Info**: System version and description

### Configuration Section
- **API Base URL**: Configurable endpoint (default: localhost:8000)
- **Connection Test**: Verify API connectivity
- **Status Feedback**: Visual connection status

### Tab Navigation
- **Active Tab**: Blue border and text
- **Inactive Tabs**: Gray text with hover effects
- **Icons**: Font Awesome icons for each tab

### Content Areas
- **Input Forms**: Clean, responsive forms with validation
- **Results Display**: Card-based layout with color coding
- **Loading States**: Overlay with spinner animation
- **Error Handling**: User-friendly error messages

## API Integration

### Endpoints Used
```javascript
// Health Check
GET /health

// Incident Triage
POST /incident/triage
{
  "question": "string",
  "priority": "low|medium|high|critical"
}

// Document Search
GET /incident/search?query={query}&limit={limit}

// Data Lineage
GET /lineage/{table_name}

// System Statistics
GET /system/stats
```

### Error Handling
- **Network Errors**: Connection timeout, server unavailable
- **API Errors**: HTTP status codes with detailed messages
- **Validation Errors**: Input validation with user feedback
- **Loading States**: Visual feedback during API calls

## Styling and Design

### CSS Framework
- **Tailwind CSS**: Utility-first CSS framework
- **Custom Styles**: Additional CSS for animations and effects
- **Responsive Design**: Mobile-first approach

### Color Scheme
- **Primary**: Blue (#3B82F6)
- **Success**: Green (#10B981)
- **Warning**: Yellow (#F59E0B)
- **Error**: Red (#EF4444)
- **Info**: Gray (#6B7280)

### Typography
- **Font**: System font stack
- **Sizes**: Responsive text sizing
- **Weights**: Regular, medium, semibold, bold

### Animations
- **Fade In**: Content appears with fade effect
- **Hover Effects**: Card lifting and shadow changes
- **Loading Spinner**: Rotating animation
- **Transitions**: Smooth state changes

## Browser Compatibility

### Supported Browsers
- **Chrome**: 80+
- **Firefox**: 75+
- **Safari**: 13+
- **Edge**: 80+

### Required Features
- **JavaScript**: ES6+ support
- **CSS Grid**: Layout support
- **Fetch API**: HTTP requests
- **Local Storage**: Optional preferences

## Security Considerations

### Development Environment
- **No Authentication**: Open access for development
- **CORS Enabled**: Cross-origin requests allowed
- **HTTP Only**: No HTTPS in development

### Production Recommendations
- **HTTPS**: Secure connections required
- **Authentication**: User login and session management
- **API Keys**: Secure key management
- **Rate Limiting**: Prevent abuse
- **Input Validation**: Server-side validation

## Performance Optimization

### Frontend Optimizations
- **Minimal Dependencies**: Only essential libraries
- **Efficient DOM**: Minimal DOM manipulation
- **Caching**: Browser caching for static assets
- **Lazy Loading**: Load content as needed

### API Optimizations
- **Connection Pooling**: Reuse HTTP connections
- **Request Batching**: Combine multiple requests
- **Error Retry**: Automatic retry on failures
- **Timeout Handling**: Prevent hanging requests

## Development Setup

### Prerequisites
- **Python 3.8+**: For the web server
- **Modern Browser**: For the web interface
- **Traceback API**: Running on port 8000

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd Traceback

# Install dependencies (if needed)
pip install -r requirements.txt

# Start the API server
cd src/tracebackcore/api
python main.py

# Start the Web UI server (in another terminal)
cd web_ui
python server.py
```

### Development Workflow
1. **API Development**: Modify API endpoints
2. **UI Development**: Update HTML/CSS/JavaScript
3. **Testing**: Test both API and UI functionality
4. **Integration**: Verify end-to-end functionality

## Troubleshooting

### Common Issues

#### Connection Failed
- **Check API Server**: Ensure API is running on port 8000
- **Check URL**: Verify API Base URL configuration
- **Check Network**: Ensure no firewall blocking
- **Check Logs**: Review API server logs

#### Slow Performance
- **Check Resources**: Monitor CPU and memory usage
- **Reduce Limits**: Lower search result limits
- **Check Network**: Verify network connectivity
- **Optimize Queries**: Simplify search queries

#### UI Not Loading
- **Check Server**: Ensure Web UI server is running
- **Check Port**: Verify port 3000 is available
- **Check Browser**: Try different browser
- **Check Console**: Review browser console errors

### Debug Mode
```javascript
// Enable debug logging
localStorage.setItem('debug', 'true');

// Check API connectivity
fetch('http://localhost:8000/health')
  .then(response => response.json())
  .then(data => console.log('API Status:', data));
```

## Future Enhancements

### Planned Features
- **User Authentication**: Login and session management
- **Dashboard**: Customizable dashboard with widgets
- **Notifications**: Real-time incident notifications
- **Export**: Export reports and data
- **Themes**: Dark/light mode toggle
- **Mobile App**: Native mobile application

### Technical Improvements
- **PWA Support**: Progressive Web App features
- **Offline Mode**: Work without internet connection
- **Real-time Updates**: WebSocket integration
- **Advanced Search**: Faceted search and filters
- **Data Visualization**: Charts and graphs
- **API Versioning**: Support multiple API versions

## Contributing

### Code Style
- **HTML**: Semantic markup with proper accessibility
- **CSS**: Tailwind utility classes with custom styles
- **JavaScript**: ES6+ with async/await patterns
- **Comments**: Clear, descriptive comments

### Testing
- **Manual Testing**: Test all features manually
- **Cross-browser**: Test on multiple browsers
- **Responsive**: Test on different screen sizes
- **Accessibility**: Test with screen readers

### Pull Requests
1. **Fork Repository**: Create your own fork
2. **Create Branch**: Feature branch for changes
3. **Make Changes**: Implement your changes
4. **Test Thoroughly**: Test all functionality
5. **Submit PR**: Create pull request with description

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- **Issues**: Create GitHub issues
- **Documentation**: Check this README
- **API Docs**: Visit http://localhost:8000/docs
- **Community**: Join our community discussions

