#!/usr/bin/env python3
"""
GeoInfoFetcher MCP Server
A proper Model Context Protocol server that communicates via stdin/stdout JSON-RPC.
"""

import json
import sys
from typing import Dict, Any

# Mock data for Tokyo (same as FastAPI version)
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