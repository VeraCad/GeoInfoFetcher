from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn
from datetime import datetime

# FastAPI app initialization
app = FastAPI(
    title="GeoInfoFetcher MCP Server",
    description="Model Context Protocol server providing geographical information tools",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Input Models
class LocationInput(BaseModel):
    location: str

# Output Models for get_basic_info
class BasicInfoOutput(BaseModel):
    country: str
    capital: str
    region: str
    language: str
    timezone: str
    currency: str

# Output Models for get_emergency_numbers  
class EmergencyNumbersOutput(BaseModel):
    police: str
    ambulance: str
    fire: str
    notes: str

# Output Models for get_local_tips
class LocalTipsOutput(BaseModel):
    safety: str
    culture: str
    transport: str

# Mock data for Tokyo
TOKYO_DATA = {
    "basic_info": {
        "country": "Japan",
        "capital": "Tokyo",
        "region": "East Asia",
        "language": "Japanese",
        "timezone": "JST (UTC+9)",
        "currency": "Japanese Yen (JPY)"
    },
    "emergency_numbers": {
        "police": "110",
        "ambulance": "119",
        "fire": "119",
        "notes": "Emergency services are free and operators may speak limited English. Use translation apps if needed."
    },
    "local_tips": {
        "safety": "Japan is one of the safest countries in the world. Keep cash handy as many places don't accept cards. Carry a business card of your hotel.",
        "culture": "Bow slightly when greeting. Remove shoes when entering homes. Avoid eating or drinking while walking. Keep voices low on public transport.",
        "transport": "Get a JR Pass for unlimited train travel. Download Google Translate with camera function. Tokyo Metro has excellent English signage."
    }
}

# Default data for unknown locations
DEFAULT_DATA = {
    "basic_info": {
        "country": "Unknown",
        "capital": "Unknown", 
        "region": "Unknown",
        "language": "Unknown",
        "timezone": "Unknown",
        "currency": "Unknown"
    },
    "emergency_numbers": {
        "police": "No data available",
        "ambulance": "No data available", 
        "fire": "No data available",
        "notes": "Contact local authorities or embassy for emergency information."
    },
    "local_tips": {
        "safety": "No data available",
        "culture": "No data available",
        "transport": "No data available"
    }
}

def get_location_data(location: str, data_type: str) -> Dict[str, Any]:
    """Get data for a location, returning Tokyo data or defaults."""
    location_lower = location.lower().strip()
    
    if location_lower in ["tokyo", "japan", "tokyo, japan"]:
        return TOKYO_DATA[data_type]
    else:
        return DEFAULT_DATA[data_type]

# Tool Endpoints

@app.post("/tools/get_basic_info", response_model=BasicInfoOutput)
async def get_basic_info(input_data: LocationInput) -> BasicInfoOutput:
    """
    Get basic geographical and political information about a location.
    
    Returns country, capital, region, language, timezone, and currency information.
    """
    try:
        data = get_location_data(input_data.location, "basic_info")
        return BasicInfoOutput(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving basic info: {str(e)}")

@app.post("/tools/get_emergency_numbers", response_model=EmergencyNumbersOutput)  
async def get_emergency_numbers(input_data: LocationInput) -> EmergencyNumbersOutput:
    """
    Get emergency contact numbers for a location.
    
    Returns police, ambulance, fire department numbers and helpful notes.
    """
    try:
        data = get_location_data(input_data.location, "emergency_numbers")
        return EmergencyNumbersOutput(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving emergency numbers: {str(e)}")

@app.post("/tools/get_local_tips", response_model=LocalTipsOutput)
async def get_local_tips(input_data: LocationInput) -> LocalTipsOutput:
    """
    Get local tips and advice for travelers.
    
    Returns safety, cultural, and transportation tips for the location.
    """
    try:
        data = get_location_data(input_data.location, "local_tips") 
        return LocalTipsOutput(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving local tips: {str(e)}")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint providing server information."""
    return {
        "name": "GeoInfoFetcher MCP Server",
        "version": "1.0.0",
        "description": "Model Context Protocol server for geographical information",
        "tools": [
            {
                "name": "get_basic_info",
                "description": "Get basic geographical and political information",
                "endpoint": "/tools/get_basic_info"
            },
            {
                "name": "get_emergency_numbers", 
                "description": "Get emergency contact numbers",
                "endpoint": "/tools/get_emergency_numbers"
            },
            {
                "name": "get_local_tips",
                "description": "Get local tips and travel advice", 
                "endpoint": "/tools/get_local_tips"
            }
        ],
        "timestamp": datetime.now().isoformat()
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 