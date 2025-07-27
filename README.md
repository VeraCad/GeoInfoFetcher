# GeoInfoFetcher MCP Server

A FastAPI-based Model Context Protocol (MCP) server that provides geographical information tools for AI applications.

## Overview

GeoInfoFetcher is an MCP-compliant server that exposes three geographical information tools:

1. **`get_basic_info`** - Provides basic geographical and political information
2. **`get_emergency_numbers`** - Returns emergency contact numbers  
3. **`get_local_tips`** - Offers local tips and travel advice

## Features

- ✅ **MCP Compliant**: Follows the Model Context Protocol specification
- ✅ **Pydantic Models**: Strongly typed inputs and outputs
- ✅ **OpenAPI Documentation**: Automatic Swagger UI at `/docs`
- ✅ **Mock Data**: Returns realistic data for Tokyo, defaults for other locations
- ✅ **Error Handling**: Comprehensive error handling and validation
- ✅ **Health Checks**: Built-in health monitoring

## Installation

1. **Clone or create the project directory:**
   ```bash
   mkdir GeoInfoFetcher
   cd GeoInfoFetcher
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server

Start the server using uvicorn:

```bash
python main.py
```

Or directly with uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The server will start on `http://localhost:8000`

## API Documentation

Once the server is running, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Server Info**: http://localhost:8000/
- **Health Check**: http://localhost:8000/health

## API Endpoints

### 1. Get Basic Info
**POST** `/tools/get_basic_info`

Returns basic geographical and political information about a location.

**Request Body:**
```json
{
  "location": "Tokyo"
}
```

**Response:**
```json
{
  "country": "Japan",
  "capital": "Tokyo", 
  "region": "East Asia",
  "language": "Japanese",
  "timezone": "JST (UTC+9)",
  "currency": "Japanese Yen (JPY)"
}
```

### 2. Get Emergency Numbers
**POST** `/tools/get_emergency_numbers`

Returns emergency contact numbers for a location.

**Request Body:**
```json
{
  "location": "Tokyo"
}
```

**Response:**
```json
{
  "police": "110",
  "ambulance": "119", 
  "fire": "119",
  "notes": "Emergency services are free and operators may speak limited English. Use translation apps if needed."
}
```

### 3. Get Local Tips
**POST** `/tools/get_local_tips`

Returns local tips and travel advice for a location.

**Request Body:**
```json
{
  "location": "Tokyo"
}
```

**Response:**
```json
{
  "safety": "Japan is one of the safest countries in the world. Keep cash handy as many places don't accept cards. Carry a business card of your hotel.",
  "culture": "Bow slightly when greeting. Remove shoes when entering homes. Avoid eating or drinking while walking. Keep voices low on public transport.", 
  "transport": "Get a JR Pass for unlimited train travel. Download Google Translate with camera function. Tokyo Metro has excellent English signage."
}
```

## Testing the API

### Using curl

Test the basic info endpoint:
```bash
curl -X POST "http://localhost:8000/tools/get_basic_info" \
     -H "Content-Type: application/json" \
     -d '{"location": "Tokyo"}'
```

Test with an unknown location:
```bash
curl -X POST "http://localhost:8000/tools/get_basic_info" \
     -H "Content-Type: application/json" \
     -d '{"location": "Unknown City"}'
```

### Using Python requests

```python
import requests
import json

# Test get_basic_info
response = requests.post(
    "http://localhost:8000/tools/get_basic_info",
    json={"location": "Tokyo"}
)
print(json.dumps(response.json(), indent=2))

# Test get_emergency_numbers  
response = requests.post(
    "http://localhost:8000/tools/get_emergency_numbers",
    json={"location": "Tokyo"}
)
print(json.dumps(response.json(), indent=2))

# Test get_local_tips
response = requests.post(
    "http://localhost:8000/tools/get_local_tips", 
    json={"location": "Tokyo"}
)
print(json.dumps(response.json(), indent=2))
```

## Data Handling

- **Tokyo Recognition**: The server recognizes "Tokyo", "Japan", and "Tokyo, Japan" (case-insensitive)
- **Mock Data**: Returns realistic mock data for Tokyo
- **Unknown Locations**: Returns "Unknown" or "No data available" for unrecognized locations
- **Error Handling**: Graceful error handling with appropriate HTTP status codes

## MCP Compliance

This server follows the Model Context Protocol specification:

- ✅ Uses structured JSON endpoints 
- ✅ Implements proper tool interfaces
- ✅ Provides clear input/output schemas
- ✅ Supports discovery through root endpoint
- ✅ Includes comprehensive documentation

## Development

### Project Structure
```
GeoInfoFetcher/
├── main.py              # Main FastAPI application
├── requirements.txt     # Python dependencies  
└── README.md           # This file
```

### Adding New Tools

To add a new tool:

1. Create Pydantic models for input/output
2. Add mock/default data structures  
3. Implement the tool function
4. Add POST endpoint at `/tools/{tool_name}`
5. Update the root endpoint tool list

## Requirements

- Python 3.8+
- FastAPI 0.104.1+
- Pydantic 2.5.0+
- Uvicorn 0.24.0+

## License

This project is provided as-is for educational and development purposes. 