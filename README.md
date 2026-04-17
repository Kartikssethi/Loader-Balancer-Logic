# 🔥 Smart Load Balancer for Tatkal System

A sophisticated load balancer system that distributes booking requests across multiple servers with advanced features like health checks, rate limiting, and intelligent load distribution strategies.

## 🎯 Project Overview

This project implements a real-world load balancer inspired by the high-traffic Tatkal booking system. It demonstrates how to handle traffic spikes, distribute load efficiently, and maintain system stability.

### 📊 Architecture

```
┌─────────────────────────────────────────────────────┐
│                  CLIENT REQUESTS                    │
└────────────────────┬────────────────────────────────┘
                     │
        ┌────────────▼────────────┐
        │   LOAD BALANCER         │
        │   (Port 8000)           │
        │                         │
        │ Features:               │
        │ ✅ Load Balancing       │
        │ ✅ Health Check         │
        │ ✅ Rate Limiting        │
        │ ✅ Request Queuing      │
        └─┬──────────┬──────────┬─┘
          │          │          │
    ┌─────▼──┐  ┌────▼─┐  ┌────▼─┐
    │Server 1│  │Server 2│  │Server 3│
    │ 8001   │  │ 8002   │  │ 8003   │
    └────────┘  └────────┘  └────────┘
```

## 🚀 Features

### 1. **Load Balancing Strategies**

- **Round Robin**: Distributes requests equally to all servers
- **Least Connections** (Default): Sends requests to server with fewest active connections

### 2. **Health Check**

- Automatically monitors server status every 5 seconds
- Removes unhealthy servers from rotation
- Resumes serving when server recovers

### 3. **Rate Limiting**

- Prevents server overload by limiting requests per time window
- Configurable rate limit and time window
- Returns 429 error when limit exceeded

### 4. **Request Queuing**

- Queues excess requests instead of rejecting them
- Processes queued requests as capacity becomes available
- Prevents loss of booking requests during traffic spikes

### 5. **Statistics & Monitoring**

- Tracks request distribution across servers
- Monitors active connections per server
- Provides real-time load balancer status

## 📁 Project Structure

```
miniproject/
├── backend_server.py          # Individual backend server implementation
├── load_balancer.py           # Main load balancer with all features
├── test_load_balancer.py      # Test suite with stress tests
├── gui.html                   # Interactive web GUI for testing
├── run_servers.sh             # Script to start all servers
├── start_backend.sh           # Start individual backend server
├── start_lb.sh                # Start load balancer
├── open_gui.sh                # Open GUI in browser
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🎮 Interactive GUI (NEW!)

A beautiful web-based dashboard for **manual and automated testing**:

### Features:

- ✅ Send requests manually with custom delays
- ✅ Send burst of 10 requests
- ✅ Simulate Tatkal rush with 50+ requests
- ✅ Real-time server status visualization
- ✅ Active connection tracking per server
- ✅ Request history with timestamps
- ✅ Server load visualization with color coding
- ✅ Success/Queued/Failed counters

## 💻 Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start All Servers (Choose One Option)

#### Option A: Using the provided script (easiest - macOS/Linux)

```bash
chmod +x *.sh
bash run_servers.sh
```

#### Option B: Start manually in separate terminals

**Terminal 1 - Backend Server 1:**

```bash
python3 backend_server.py 1 8001
```

**Terminal 2 - Backend Server 2:**

```bash
python3 backend_server.py 2 8002
```

**Terminal 3 - Backend Server 3:**

```bash
python3 backend_server.py 3 8003
```

**Terminal 4 - Load Balancer:**

```bash
python3 load_balancer.py
```

### 3. Open the GUI

Once servers are running, open your browser:

```bash
# Automatic (macOS)
bash open_gui.sh

# Manual - Open this URL in any browser:
http://127.0.0.1:8000
```

### 4. Test with GUI

In the GUI, you can now:

1. **Send Single Request** - Click "➕ Send 1 Request"
2. **Send Burst** - Click "🔥 Burst (10 requests)"
3. **Simulate Tatkal Rush** - Click "⚡ Tatkal Rush (50 reqs)"
4. **Watch Live** - See which server handles each request
5. **Adjust Delays** - Use sliders to control request timing

**What You'll See:**

- 🟢 Green = Server healthy & available
- 🟡 Yellow = Server overloaded
- 🔴 Red = Server down
- ⏳ Queued requests waiting in queue
- 📊 Real-time load distribution

### 5. Run Automated Tests (Optional)

In another terminal:

```bash
python3 test_load_balancer.py
```

## 🧪 Test Suite Features

The test suite (`test_load_balancer.py`) includes:

### **Test 1: Basic Booking Requests**

- Makes 5 sequential booking requests
- Shows which server handled each request
- Displays server distribution

### **Test 2: Concurrent Requests**

- Simulates 20 simultaneous requests
- Measures throughput (requests/second)
- Shows load distribution under concurrent load

### **Test 3: Tatkal Rush Simulation**

- Simulates high-traffic scenario with 60 rapid requests
- Tests rate limiting and queue functionality
- Shows success, queued, and failed request counts

### **Test 4: Strategy Switching**

- Demonstrates switching between load balancing strategies
- Compares distribution with different strategies

## 🔌 API Endpoints

### Load Balancer (Port 8000)

#### Make a Booking

```bash
curl -X POST http://127.0.0.1:8000/book
```

**Response (Success):**

```json
{
  "status": "success",
  "message": "Booked by Server 2",
  "server_id": 2,
  "port": 8002,
  "timestamp": 1234567890.123,
  "request_number": 42,
  "load_balancer_decision": {
    "strategy": "least_connections",
    "selected_server": 2,
    "server_url": "http://127.0.0.1:8002",
    "active_connections": 0
  }
}
```

#### Get Status

```bash
curl http://127.0.0.1:8000/status
```

#### Get Servers Info

```bash
curl http://127.0.0.1:8000/servers
```

#### Change Strategy

```bash
curl -X POST http://127.0.0.1:8000/strategy/round_robin
```

### Backend Servers (Ports 8001-8003)

#### Health Check

```bash
curl http://127.0.0.1:8001/health
```

#### Server Statistics

```bash
curl http://127.0.0.1:8001/stats
```

## 📊 Configuration

You can customize the load balancer by editing `load_balancer.py`:

```python
# In the main() function

# Change rate limit (default: 50 requests per 10 seconds)
rate_limit=50,
rate_limit_window=10,

# Change strategy (ROUND_ROBIN or LEAST_CONNECTIONS)
strategy=LoadBalancingStrategy.LEAST_CONNECTIONS,

# Change load balancer port
lb.run(port=8000)
```

## 🎯 How It Works

### Request Flow

1. **Client Request** → Load Balancer `/book` endpoint
2. **Rate Limit Check** → Is request within rate limit?
   - ✅ Yes → Continue
   - ❌ No → Queue or Reject
3. **Server Selection** → Pick server using strategy
   - Round Robin: Next in rotation
   - Least Connections: Server with fewest active connections
4. **Forward Request** → Send to selected server
5. **Return Response** → Response back to client

### Health Check Flow

1. Every 5 seconds, load balancer pings `/health` on each server
2. If server responds → Mark as healthy
3. If server doesn't respond → Mark as unhealthy
4. Only healthy servers receive new requests
5. Unhealthy servers are automatically recovered when they respond again

### Queue Processing Flow

1. When rate limit is exceeded, request goes to queue
2. Background thread processes queue every 1 second
3. Processes queued requests as capacity becomes available
4. Maintains FIFO order in queue

## 📈 Testing Scenarios

### Scenario 1: Normal Operation

```bash
python test_load_balancer.py
# Tests basic functionality and load distribution
```

### Scenario 2: Kill a Server (Simulate Failure)

```bash
# While tests are running, press Ctrl+C on one of the backend servers
# Load balancer automatically detects failure and stops sending requests to it
```

### Scenario 3: Manual Testing

```bash
# Test with curl commands
for i in {1..10}; do curl -s -X POST http://127.0.0.1:8000/book | python -m json.tool; done
```

## 🔍 Monitoring

Check real-time statistics:

```bash
# In a new terminal, continuously monitor status
while true; do
  curl -s http://127.0.0.1:8000/status | python -m json.tool
  sleep 2
done
```

## 🛠️ Advanced Customizations

### 1. Change Load Balancing Strategy

```python
# Edit load_balancer.py, main() function
lb = SmartLoadBalancer(
    servers=servers_config,
    strategy=LoadBalancingStrategy.ROUND_ROBIN,  # Change this
    ...
)
```

### 2. Adjust Rate Limiting

```python
lb = SmartLoadBalancer(
    servers=servers_config,
    rate_limit=200,        # Increase limit
    rate_limit_window=30,  # Increase window
    ...
)
```

### 3. Add More Servers

```python
servers_config = [
    {"id": 1, "port": 8001},
    {"id": 2, "port": 8002},
    {"id": 3, "port": 8003},
    {"id": 4, "port": 8004},  # Add new server
    {"id": 5, "port": 8005},  # Add new server
]
```

### 4. Simulate Server Failure in Backend

Edit `backend_server.py` to add failure simulation:

```python
# In the /book endpoint
import random
if random.random() < 0.1:  # 10% failure rate
    raise HTTPException(status_code=500)
```

## 📊 Performance Metrics

Expected performance with default settings:

- **Throughput**: ~30-50 requests/second
- **Latency**: ~500-1500ms per request
- **Server Distribution**: Balanced across servers
- **Health Check Overhead**: ~5% CPU

## 🎓 Learning Outcomes

By building and understanding this project, you'll learn:

1. **Load Balancing Algorithms**
   - Round Robin vs. Least Connections
   - Trade-offs between strategies

2. **System Design**
   - Request queuing and buffering
   - Health monitoring
   - Graceful degradation

3. **Distributed Systems Concepts**
   - Request routing
   - Service discovery
   - Fault tolerance

4. **Python & FastAPI**
   - Async request handling
   - Background workers (threading)
   - RESTful API design

5. **Performance Testing**
   - Stress testing
   - Concurrent request handling
   - Monitoring and metrics

## 🐛 Troubleshooting

### Problem: "Connection refused" when running tests

- **Solution**: Make sure all 4 processes are running:
  - 3 backend servers (8001, 8002, 8003)
  - 1 load balancer (8000)

### Problem: Port already in use

- **Solution**: Kill existing processes or use different ports
  ```bash
  lsof -i :8000  # Find process on port 8000
  kill -9 <PID>  # Kill the process
  ```

### Problem: Tests show unbalanced distribution

- **Check**: Whether you're using the right strategy (`least_connections` vs `round_robin`)
- **Note**: Distribution may vary during rush tests due to variable processing times

## 🚀 Future Enhancements

1. **Load Balancing Strategies**
   - Weighted Round Robin
   - IP Hash
   - Consistent Hashing

2. **Advanced Features**
   - SSL/TLS support
   - WebSocket support
   - Request filtering/validation

3. **Monitoring & Analytics**
   - Prometheus metrics export
   - Grafana dashboard
   - Request latency histogram

4. **Scaling**
   - Distributed load balancing (multiple load balancers)
   - Session persistence
   - Database backend for queued requests

## 📝 License

This project is created for educational purposes.

## 👨‍💻 Author Notes

This load balancer is inspired by real-world systems used in high-traffic applications like IRCTC's Tatkal booking system. The design emphasizes:

- **Reliability**: Health checks and automatic failover
- **Fairness**: Intelligent load distribution
- **Resilience**: Request queuing prevents loss
- **Transparency**: Comprehensive monitoring and statistics

Happy coding! 🎉
