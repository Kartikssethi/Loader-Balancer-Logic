"""
Smart Load Balancer for Tatkal System
Features:
- Round Robin
- Least Connections
- Health Check
- Rate Limiting
- Queue Integration
"""

import time
import requests
import threading
from queue import Queue
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
from dataclasses import dataclass, field
from enum import Enum
import uvicorn
import os
from collections import defaultdict

class LoadBalancingStrategy(Enum):
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"

@dataclass
class Server:
    """Represents a backend server"""
    id: int
    url: str
    port: int
    active_connections: int = 0
    total_requests: int = 0
    is_healthy: bool = True
    last_health_check: float = field(default_factory=time.time)

class SmartLoadBalancer:
    def __init__(self, 
                 servers: List[Dict],
                 strategy: LoadBalancingStrategy = LoadBalancingStrategy.LEAST_CONNECTIONS,
                 rate_limit: int = 100,
                 rate_limit_window: int = 60):
        """
        Initialize Load Balancer
        
        Args:
            servers: List of server configs [{"id": 1, "port": 8001}, ...]
            strategy: Load balancing strategy (ROUND_ROBIN or LEAST_CONNECTIONS)
            rate_limit: Maximum requests per time window
            rate_limit_window: Time window in seconds
        """
        self.app = FastAPI(title="Smart Load Balancer")
        
        # Add CORS middleware for GUI
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self.servers: List[Server] = [
            Server(
                id=s["id"],
                url=f"http://127.0.0.1:{s['port']}",
                port=s["port"]
            )
            for s in servers
        ]
        self.strategy = strategy
        self.current_index = 0
        
        # Rate limiting
        self.rate_limit = rate_limit
        self.rate_limit_window = rate_limit_window
        self.request_timestamps: List[float] = []
        self.client_requests: Dict[str, List[float]] = defaultdict(list)
        
        # Queue for request queuing
        self.request_queue = Queue()
        self.queue_enabled = True
        self.max_queue_size = 200 
        
        # Statistics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.queued_requests = 0
        
        # Setup routes
        self.setup_routes()
        
        # Start background threads
        self.start_background_tasks()
    
    def setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/")
        async def gui():
            """Serve the GUI HTML"""
            gui_path = os.path.join(os.path.dirname(__file__), "gui.html")
            if os.path.exists(gui_path):
                return FileResponse(gui_path, media_type="text/html")
            else:
                return {
                    "message": "Smart Load Balancer API",
                    "endpoints": {
                        "gui": "GET /",
                        "book": "POST /book",
                        "status": "GET /status",
                        "servers": "GET /servers",
                        "strategy": "POST /strategy/{strategy_name}"
                    }
                }
        
        @self.app.post("/book")
        async def book_request(request: Request):
            """Main booking endpoint with load balancing"""
            client_ip = request.client.host
            
            # Check global rate limit
            current_time = time.time()
            self.request_timestamps = [
                ts for ts in self.request_timestamps 
                if current_time - ts < self.rate_limit_window
            ]
            
            if len(self.request_timestamps) >= self.rate_limit:
                self.queued_requests += 1
                
                if self.queue_enabled and self.request_queue.qsize() < self.max_queue_size:
                    # Queue the request
                    self.request_queue.put({
                        "client_ip": client_ip,
                        "timestamp": current_time
                    })
                    return {
                        "status": "queued",
                        "message": "Server busy. Your request has been queued.",
                        "queue_position": self.request_queue.qsize(),
                        "queue_length": self.request_queue.qsize()
                    }
                else:
                    self.failed_requests += 1
                    raise HTTPException(
                        status_code=429,
                        detail={
                            "message": "Server capacity exceeded. Request rejected.",
                            "queue_full": True
                        }
                    )
            
            self.request_timestamps.append(current_time)
            self.total_requests += 1
            
            # Try servers with retry logic (up to 3 attempts)
            max_retries = 3
            for attempt in range(max_retries):
                # Select server based on strategy
                server = self.select_server()
                
                if not server:
                    self.failed_requests += 1
                    raise HTTPException(
                        status_code=503,
                        detail="No healthy servers available"
                    )
                
                # Forward request to selected server
                try:
                    server.active_connections += 1
                    response = requests.post(
                        f"{server.url}/book",
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        self.successful_requests += 1
                        result = response.json()
                        result["load_balancer_decision"] = {
                            "strategy": self.strategy.value,
                            "selected_server": server.id,
                            "server_url": server.url,
                            "active_connections": server.active_connections,
                            "attempt": attempt + 1
                        }
                        return result
                    elif response.status_code == 503:
                        # Server is overloaded, mark as unhealthy and retry
                        server.is_healthy = False
                        print(f"⚠️  Server {server.id} marked unhealthy (503 error)")
                        # Continue to next attempt with different server
                        continue
                    else:
                        self.failed_requests += 1
                        raise HTTPException(status_code=response.status_code)
                        
                except requests.exceptions.RequestException as e:
                    server.is_healthy = False
                    print(f"⚠️  Server {server.id} connection failed: {str(e)}")
                    # Continue to next attempt with different server
                    continue
                finally:
                    server.active_connections = max(0, server.active_connections - 1)
            
            # All servers failed
            self.failed_requests += 1
            raise HTTPException(
                status_code=503,
                detail="All servers overloaded or unavailable. Request would be queued if queue enabled."
            )
        
        @self.app.get("/status")
        async def load_balancer_status():
            """Get load balancer status"""
            return {
                "status": "operational",
                "strategy": self.strategy.value,
                "servers": [
                    {
                        "id": s.id,
                        "port": s.port,
                        "url": s.url,
                        "active_connections": s.active_connections,
                        "total_requests": s.total_requests,
                        "is_healthy": s.is_healthy
                    }
                    for s in self.servers
                ],
                "statistics": {
                    "total_requests": self.total_requests,
                    "successful_requests": self.successful_requests,
                    "failed_requests": self.failed_requests,
                    "queued_requests": self.queued_requests,
                    "queue_size": self.request_queue.qsize()
                },
                "rate_limit": {
                    "limit": self.rate_limit,
                    "window_seconds": self.rate_limit_window,
                    "current_requests": len(self.request_timestamps)
                }
            }
        
        @self.app.get("/servers")
        async def get_servers():
            """Get all servers info"""
            return {
                "servers": [
                    {
                        "id": s.id,
                        "port": s.port,
                        "connections": s.active_connections,
                        "total_requests": s.total_requests,
                        "healthy": s.is_healthy
                    }
                    for s in self.servers
                ]
            }
        
        @self.app.post("/strategy/{strategy_name}")
        async def change_strategy(strategy_name: str):
            """Change load balancing strategy"""
            try:
                self.strategy = LoadBalancingStrategy[strategy_name.upper()]
                return {
                    "message": f"Strategy changed to {strategy_name}",
                    "current_strategy": self.strategy.value
                }
            except KeyError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unknown strategy. Available: {[s.value for s in LoadBalancingStrategy]}"
                )
    
    def select_server(self) -> Server:
        """Select a server based on the configured strategy"""
        # Filter healthy servers
        healthy_servers = [s for s in self.servers if s.is_healthy]
        
        if not healthy_servers:
            return None
        
        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self.select_round_robin(healthy_servers)
        elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return self.select_least_connections(healthy_servers)
    
    def select_round_robin(self, servers: List[Server]) -> Server:
        """Round Robin: distribute requests equally"""
        server = servers[self.current_index % len(servers)]
        self.current_index += 1
        return server
    
    def select_least_connections(self, servers: List[Server]) -> Server:
        """Least Connections: send to server with least active connections"""
        return min(servers, key=lambda s: s.active_connections)
    
    def health_check_worker(self):
        """Background worker for health checks"""
        while True:
            time.sleep(5)  # Check every 5 seconds
            
            for server in self.servers:
                try:
                    response = requests.get(
                        f"{server.url}/health",
                        timeout=2
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        server.is_healthy = True
                        server.active_connections = data.get("active_connections", 0)
                        server.total_requests = data.get("total_requests", 0)
                    else:
                        server.is_healthy = False
                        
                except requests.exceptions.RequestException:
                    server.is_healthy = False
                
                server.last_health_check = time.time()
    
    def queue_processor_worker(self):
        """Background worker for processing queued requests"""
        while True:
            time.sleep(1)  # Check queue every second
            
            # Process queued requests
            while not self.request_queue.empty():
                try:
                    # Check if rate limit allows
                    current_time = time.time()
                    self.request_timestamps = [
                        ts for ts in self.request_timestamps 
                        if current_time - ts < self.rate_limit_window
                    ]
                    
                    if len(self.request_timestamps) >= self.rate_limit:
                        break  # Still rate limited, try again later
                    
                    # Get server and process queued request
                    server = self.select_server()
                    if server:
                        queued_req = self.request_queue.get()
                        
                        try:
                            response = requests.post(
                                f"{server.url}/book",
                                timeout=5
                            )
                            
                            if response.status_code == 200:
                                self.successful_requests += 1
                        except:
                            self.failed_requests += 1
                    else:
                        break  # No healthy servers
                        
                except Exception as e:
                    print(f"Error processing queue: {e}")
                    break
    
    def start_background_tasks(self):
        """Start background threads for health checks and queue processing"""
        # Health check thread
        health_check_thread = threading.Thread(
            target=self.health_check_worker,
            daemon=True
        )
        health_check_thread.start()
        
        # Queue processor thread
        queue_thread = threading.Thread(
            target=self.queue_processor_worker,
            daemon=True
        )
        queue_thread.start()
    
    def run(self, port: int = 8000):
        """Run the load balancer"""
        print(f"🔄 Load Balancer starting on port {port}...")
        print(f"📊 Strategy: {self.strategy.value}")
        uvicorn.run(
            self.app,
            host="127.0.0.1",
            port=port,
            log_level="warning"
        )

def main():
    """Main entry point"""
    # Configure backend servers
    servers_config = [
        {"id": 1, "port": 8001},
        {"id": 2, "port": 8002},
        {"id": 3, "port": 8003},
    ]
    
    # Create load balancer with LEAST_CONNECTIONS strategy
    # Change to ROUND_ROBIN if preferred
    lb = SmartLoadBalancer(
        servers=servers_config,
        strategy=LoadBalancingStrategy.LEAST_CONNECTIONS,
        rate_limit=50,  # Max 50 requests per window
        rate_limit_window=10  # In 10 seconds
    )
    
    lb.run(port=8000)

if __name__ == "__main__":
    main()
