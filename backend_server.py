"""
Backend Server Module
Each server handles /book requests and simulates processing time
"""
import time
import json
from fastapi import FastAPI, HTTPException
from typing import Dict
import uvicorn

class BackendServer:
    def __init__(self, server_id: int, port: int):
        self.server_id = server_id
        self.port = port
        self.app = FastAPI()
        self.request_count = 0
        self.active_connections = 0
        self.is_overloaded = False
        self.max_requests_before_failure = 50  # Fail after 50 requests
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.post("/book")
        async def book_ticket():
            """Simulates booking a ticket on this server"""
            self.active_connections += 1
            self.request_count += 1
            
            # Check if server has exceeded request limit (simulate failure after 50 requests)
            if self.request_count > self.max_requests_before_failure:
                self.is_overloaded = True
                self.active_connections -= 1
                raise HTTPException(
                    status_code=503,
                    detail={
                        "message": f"Server {self.server_id} is overloaded! Handled {self.request_count} requests.",
                        "server_id": self.server_id,
                        "requests_handled": self.request_count
                    }
                )
            
            try:
                # Simulate processing time (0.5-1.5 seconds)
                processing_time = 0.5
                time.sleep(processing_time)
                
                return {
                    "status": "success",
                    "message": f"Booked by Server {self.server_id}",
                    "server_id": self.server_id,
                    "port": self.port,
                    "timestamp": time.time(),
                    "request_number": self.request_count,
                    "requests_until_failure": self.max_requests_before_failure - self.request_count
                }
            finally:
                self.active_connections -= 1
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            status = "unhealthy" if self.is_overloaded else "healthy"
            return {
                "status": status,
                "server_id": self.server_id,
                "port": self.port,
                "active_connections": self.active_connections,
                "total_requests": self.request_count,
                "is_overloaded": self.is_overloaded,
                "requests_until_failure": self.max_requests_before_failure - self.request_count if not self.is_overloaded else 0
            }
        
        @self.app.get("/stats")
        async def get_stats():
            """Get server statistics"""
            return {
                "server_id": self.server_id,
                "port": self.port,
                "active_connections": self.active_connections,
                "total_requests": self.request_count,
                "status": "overloaded" if self.is_overloaded else "operational",
                "is_overloaded": self.is_overloaded,
                "requests_until_failure": self.max_requests_before_failure - self.request_count if not self.is_overloaded else 0
            }
        
        @self.app.post("/reset")
        async def reset_server():
            """Reset server statistics (for testing)"""
            self.request_count = 0
            self.active_connections = 0
            self.is_overloaded = False
            return {
                "message": f"Server {self.server_id} has been reset",
                "server_id": self.server_id
            }
    
    def run(self):
        """Run the server"""
        uvicorn.run(
            self.app,
            host="127.0.0.1",
            port=self.port,
            log_level="warning"
        )

def create_and_run_server(server_id: int, port: int):
    """Factory function to create and run a server"""
    server = BackendServer(server_id, port)
    print(f" Starting Backend Server {server_id} on port {port}...")
    server.run()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python backend_server.py <server_id> <port>")
        print("Example: python backend_server.py 1 8001")
        sys.exit(1)
    
    server_id = int(sys.argv[1])
    port = int(sys.argv[2])
    create_and_run_server(server_id, port)
