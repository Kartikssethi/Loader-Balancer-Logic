#!/bin/bash

# Script to start all servers and load balancer
# Usage: bash run_servers.sh

echo "🚀 Starting Smart Load Balancer System..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to start a server
start_server() {
    local server_id=$1
    local port=$2
    echo -e "${GREEN}Starting Backend Server ${server_id} on port ${port}...${NC}"
    python3 backend_server.py $server_id $port &
    sleep 1
}

# Function to start load balancer
start_load_balancer() {
    echo -e "${GREEN}Starting Load Balancer on port 8000...${NC}"
    python3 load_balancer.py &
    sleep 2
}

# Start backend servers
start_server 1 8001
start_server 2 8002
start_server 3 8003

# Start load balancer
start_load_balancer

# Print instructions
echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ All servers are running!${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "📊 Load Balancer endpoints:"
echo "  - POST http://127.0.0.1:8000/book          (Main booking endpoint)"
echo "  - GET  http://127.0.0.1:8000/status        (View status)"
echo "  - GET  http://127.0.0.1:8000/servers       (List servers)"
echo "  - POST http://127.0.0.1:8000/strategy/STRATEGY_NAME  (Change strategy)"
echo ""
echo "🖥️  Backend servers:"
echo "  - Server 1: http://127.0.0.1:8001"
echo "  - Server 2: http://127.0.0.1:8002"
echo "  - Server 3: http://127.0.0.1:8003"
echo ""
echo "🧪 To run tests in another terminal:"
echo "  python test_load_balancer.py"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all processes${NC}"
echo ""

# Keep script running
wait
