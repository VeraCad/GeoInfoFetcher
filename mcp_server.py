#!/usr/bin/env python3
"""
GeoInfoFetcher MCP Server
A proper Model Context Protocol server that communicates via stdin/stdout JSON-RPC.
"""

import json
import sys
import requests
import time
from typing import Dict, Any, Optional

# Emergency numbers database for common countries/regions
EMERGENCY_NUMBERS = {
    # Major countries with known emergency numbers
    "united states": {"police": "911", "ambulance": "911", "fire": "911", "notes": "Single emergency number for all services. Available 24/7."},
    "canada": {"police": "911", "ambulance": "911", "fire": "911", "notes": "Single emergency number for all services. Available 24/7."},
    "united kingdom": {"police": "999", "ambulance": "999", "fire": "999", "notes": "999 or 112 both work. Available 24/7."},
    "germany": {"police": "110", "ambulance": "112", "fire": "112", "notes": "110 for police, 112 for medical/fire emergencies."},
    "france": {"police": "17", "ambulance": "15", "fire": "18", "notes": "Different numbers for each service. 112 also works."},
    "italy": {"police": "113", "ambulance": "118", "fire": "115", "notes": "Different numbers for each service. 112 also works."},
    "spain": {"police": "091", "ambulance": "112", "fire": "112", "notes": "091 for police, 112 for medical/fire emergencies."},
    "japan": {"police": "110", "ambulance": "119", "fire": "119", "notes": "110 for police, 119 for medical/fire emergencies."},
    "australia": {"police": "000", "ambulance": "000", "fire": "000", "notes": "Single emergency number for all services. Available 24/7."},
    "new zealand": {"police": "111", "ambulance": "111", "fire": "111", "notes": "Single emergency number for all services. Available 24/7."},
    "china": {"police": "110", "ambulance": "120", "fire": "119", "notes": "Different numbers for each service."},
    "india": {"police": "100", "ambulance": "108", "fire": "101", "notes": "Different numbers for each service. 112 also works."},
    "brazil": {"police": "190", "ambulance": "192", "fire": "193", "notes": "Different numbers for each service."},
    "mexico": {"police": "911", "ambulance": "911", "fire": "911", "notes": "Single emergency number for all services."},
    "south korea": {"police": "112", "ambulance": "119", "fire": "119", "notes": "112 for police, 119 for medical/fire emergencies."},
    "russia": {"police": "102", "ambulance": "103", "fire": "101", "notes": "Different numbers for each service. 112 also works."},
    "netherlands": {"police": "112", "ambulance": "112", "fire": "112", "notes": "Single emergency number for all services."},
    "sweden": {"police": "112", "ambulance": "112", "fire": "112", "notes": "Single emergency number for all services."},
    "norway": {"police": "112", "ambulance": "112", "fire": "112", "notes": "Single emergency number for all services."},
    "denmark": {"police": "112", "ambulance": "112", "fire": "112", "notes": "Single emergency number for all services."},
}

def get_country_info_api(location: str) -> Optional[Dict[str, Any]]:
    """Get country information from REST Countries API."""
    try:
        # Clean up location name
        location = location.strip()
        
        # Try different search methods
        search_urls = [
            f"https://restcountries.com/v3.1/name/{location}?fullText=true",  # Exact match
            f"https://restcountries.com/v3.1/name/{location}",  # Partial match
            f"https://restcountries.com/v3.1/capital/{location}",  # Search by capital
        ]
        
        for url in search_urls:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        country = data[0]  # Take first result
                        
                        # Extract information
                        name = country.get('name', {}).get('common', 'Unknown')
                        capital = country.get('capital', ['Unknown'])[0] if country.get('capital') else 'Unknown'
                        region = country.get('region', 'Unknown')
                        subregion = country.get('subregion', '')
                        full_region = f"{region}" + (f", {subregion}" if subregion and subregion != region else "")
                        
                        # Languages
                        languages = country.get('languages', {})
                        if languages:
                            language = ', '.join(languages.values())
                        else:
                            language = 'Unknown'
                        
                        # Timezones
                        timezones = country.get('timezones', ['Unknown'])
                        timezone = ', '.join(timezones[:3])  # Limit to 3 timezones
                        
                        # Currencies
                        currencies = country.get('currencies', {})
                        if currencies:
                            currency_list = []
                            for code, details in currencies.items():
                                name = details.get('name', code)
                                symbol = details.get('symbol', '')
                                if symbol:
                                    currency_list.append(f"{name} ({code}, {symbol})")
                                else:
                                    currency_list.append(f"{name} ({code})")
                            currency = ', '.join(currency_list[:2])  # Limit to 2 currencies
                        else:
                            currency = 'Unknown'
                        
                        return {
                            'country': name,
                            'capital': capital,
                            'region': full_region,
                            'language': language,
                            'timezone': timezone,
                            'currency': currency
                        }
            except requests.RequestException:
                continue
                
        return None
    except Exception as e:
        print(f"Error in get_country_info_api: {e}", file=sys.stderr)
        return None

def get_emergency_numbers(location: str, country_name: str = None) -> Dict[str, str]:
    """Get emergency numbers for a location."""
    # Try to find emergency numbers by location name or country name
    search_terms = [location.lower().strip()]
    if country_name:
        search_terms.append(country_name.lower().strip())
    
    for term in search_terms:
        if term in EMERGENCY_NUMBERS:
            return EMERGENCY_NUMBERS[term]
    
    # Fallback: try partial matches
    for term in search_terms:
        for country_key in EMERGENCY_NUMBERS:
            if term in country_key or country_key in term:
                return EMERGENCY_NUMBERS[country_key]
    
    # Default if not found
    return {
        "police": "Contact local authorities",
        "ambulance": "Contact local authorities", 
        "fire": "Contact local authorities",
        "notes": "Emergency numbers vary by location. Contact local authorities, your embassy, or hotel for assistance."
    }

def generate_local_tips(country_info: Dict[str, Any], location: str) -> Dict[str, str]:
    """Generate local tips based on country information."""
    country = country_info.get('country', location)
    region = country_info.get('region', 'Unknown')
    currency = country_info.get('currency', 'local currency')
    
    # Generate basic tips based on region and country info
    safety_tip = f"Check current travel advisories for {country}. Keep copies of important documents. Stay aware of local customs and laws."
    
    culture_tip = f"Research local customs and etiquette for {country}. Learn basic phrases in the local language. Respect religious and cultural sites."
    
    transport_tip = f"Research transportation options in {country}. Consider getting local currency ({currency.split('(')[0].strip()}) for transportation. Download offline maps and translation apps."
    
    # Add region-specific tips
    if 'europe' in region.lower():
        culture_tip += " Tipping practices vary across Europe - research local expectations."
        transport_tip += " Many European countries are part of the Schengen area for easy travel."
    elif 'asia' in region.lower():
        culture_tip += " Respect for hierarchy and elders is important in many Asian cultures."
        safety_tip += " Carry business cards from your hotel. Many places prefer cash payments."
    elif 'africa' in region.lower():
        safety_tip += " Take precautions against malaria if applicable. Drink bottled water."
        transport_tip += " Road conditions vary widely. Consider guided tours for remote areas."
    elif 'america' in region.lower():
        transport_tip += " Public transportation varies by country. Car rental may be convenient."
        
    return {
        'safety': safety_tip,
        'culture': culture_tip,
        'transport': transport_tip
    }

def get_location_data(location: str, data_type: str) -> Dict[str, Any]:
    """Get data for a location using real APIs."""
    
    if data_type == "basic_info":
        # Try to get real country information
        api_data = get_country_info_api(location)
        if api_data:
            return api_data
        else:
            # Fallback to default
            return {
                "country": "Information not available",
                "capital": "Information not available", 
                "region": "Information not available",
                "language": "Information not available",
                "timezone": "Information not available",
                "currency": "Information not available"
            }
    
    elif data_type == "emergency_numbers":
        # Get country info first to help with emergency number lookup
        country_info = get_country_info_api(location)
        country_name = country_info.get('country') if country_info else None
        return get_emergency_numbers(location, country_name)
    
    elif data_type == "local_tips":
        # Get country info to generate relevant tips
        country_info = get_country_info_api(location)
        if country_info:
            return generate_local_tips(country_info, location)
        else:
            return {
                "safety": "Research current travel advisories and local safety conditions.",
                "culture": "Learn about local customs, traditions, and etiquette before traveling.",
                "transport": "Research transportation options and download offline maps and translation apps."
            }

class MCPServer:
    def __init__(self):
        self.tools = [
            {
                "name": "get_basic_info",
                "description": "Get basic geographical and political information about a location",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The location to get information about"
                        }
                    },
                    "required": ["location"]
                }
            },
            {
                "name": "get_emergency_numbers", 
                "description": "Get emergency contact numbers for a location",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The location to get emergency numbers for"
                        }
                    },
                    "required": ["location"]
                }
            },
            {
                "name": "get_local_tips",
                "description": "Get local tips and travel advice for a location", 
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string", 
                            "description": "The location to get travel tips for"
                        }
                    },
                    "required": ["location"]
                }
            }
        ]

    def send_response(self, response: Dict[str, Any]):
        """Send a JSON-RPC response to stdout."""
        print(json.dumps(response), flush=True)

    def handle_initialize(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request."""
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "protocolVersion": "2025-06-18",
                "capabilities": {
                    "tools": {
                        "listChanged": True
                    }
                },
                "serverInfo": {
                    "name": "geo-info-fetcher",
                    "version": "1.0.0"
                }
            }
        }

    def handle_list_tools(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP tools/list request."""
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "tools": self.tools
            }
        }

    def handle_call_tool(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP tools/call request."""
        try:
            params = request.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name not in [tool["name"] for tool in self.tools]:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                }
            
            location = arguments.get("location", "")
            
            if tool_name == "get_basic_info":
                data = get_location_data(location, "basic_info")
                content = f"**Basic Information for {location}:**\n"
                content += f"• Country: {data['country']}\n"
                content += f"• Capital: {data['capital']}\n"
                content += f"• Region: {data['region']}\n"
                content += f"• Language: {data['language']}\n"
                content += f"• Timezone: {data['timezone']}\n"
                content += f"• Currency: {data['currency']}"
                
            elif tool_name == "get_emergency_numbers":
                data = get_location_data(location, "emergency_numbers")
                content = f"**Emergency Numbers for {location}:**\n"
                content += f"• Police: {data['police']}\n"
                content += f"• Ambulance: {data['ambulance']}\n"
                content += f"• Fire: {data['fire']}\n"
                content += f"• Notes: {data['notes']}"
                
            elif tool_name == "get_local_tips":
                data = get_location_data(location, "local_tips")
                content = f"**Local Tips for {location}:**\n\n"
                content += f"**Safety:** {data['safety']}\n\n"
                content += f"**Culture:** {data['culture']}\n\n"
                content += f"**Transport:** {data['transport']}"
            
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": content
                        }
                    ]
                }
            }
            
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Route MCP request to appropriate handler."""
        method = request.get("method")
        
        if method == "initialize":
            return self.handle_initialize(request)
        elif method == "tools/list":
            return self.handle_list_tools(request)
        elif method == "tools/call":
            return self.handle_call_tool(request)
        elif method == "notifications/initialized":
            # No response needed for notifications
            return None
        else:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }

    def run(self):
        """Main server loop - read from stdin, process, write to stdout."""
        try:
            for line in sys.stdin:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    request = json.loads(line)
                    response = self.handle_request(request)
                    
                    # Only send response if not None (for notifications)
                    if response is not None:
                        self.send_response(response)
                        
                except json.JSONDecodeError:
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": "Parse error"
                        }
                    }
                    self.send_response(error_response)
                except Exception as e:
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32603,
                            "message": f"Internal error: {str(e)}"
                        }
                    }
                    self.send_response(error_response)
        except KeyboardInterrupt:
            pass
        except Exception:
            pass

def main():
    """Entry point for the MCP server."""
    server = MCPServer()
    server.run()

if __name__ == "__main__":
    main() 