"""
Test script to demonstrate the load balancer in action
Tests all features: Round Robin, Least Connections, Health Check, Rate Limiting, and Queue
"""

import requests
import time
import threading
from typing import List
import json

class LoadBalancerTester:
    def __init__(self, lb_url: str = "http://127.0.0.1:8000"):
        self.lb_url = lb_url
        self.results = []
        self.lock = threading.Lock()
    
    def single_request(self, request_id: int) -> dict:
        """Make a single booking request"""
        try:
            response = requests.post(
                f"{self.lb_url}/book",
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                with self.lock:
                    self.results.append({
                        "request_id": request_id,
                        "status": "success",
                        "server_id": result.get("server_id"),
                        "response": result
                    })
                return result
            else:
                with self.lock:
                    self.results.append({
                        "request_id": request_id,
                        "status": "error",
                        "error_code": response.status_code
                    })
                return None
                
        except requests.exceptions.RequestException as e:
            with self.lock:
                self.results.append({
                    "request_id": request_id,
                    "status": "exception",
                    "error": str(e)
                })
            return None
    
    def test_basic_booking(self, num_requests: int = 5):
        """Test basic booking requests"""
        print("\n" + "="*60)
        print("TEST 1: Basic Booking Requests")
        print("="*60)
        
        self.results = []
        
        for i in range(num_requests):
            result = self.single_request(i)
            if result:
                print(f"Request {i}: ✅ Booked by Server {result['server_id']}")
            else:
                print(f"Request {i}: ❌ Failed")
            time.sleep(0.5)
        
        self.print_distribution()
    
    def test_concurrent_requests(self, num_requests: int = 20):
        """Test concurrent requests (stress test)"""
        print("\n" + "="*60)
        print(f"TEST 2: Concurrent Requests ({num_requests} simultaneous)")
        print("="*60)
        
        self.results = []
        threads = []
        
        start_time = time.time()
        
        for i in range(num_requests):
            t = threading.Thread(
                target=self.single_request,
                args=(i,)
            )
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        elapsed = time.time() - start_time
        
        print(f"⏱️  Completed {num_requests} requests in {elapsed:.2f} seconds")
        print(f"📊 Throughput: {num_requests/elapsed:.2f} requests/second")
        
        self.print_distribution()
    
    def test_tatkal_rush(self, num_requests: int = 60, delay: float = 0.1):
        """Simulate Tatkal rush with rapid requests"""
        print("\n" + "="*60)
        print(f"TEST 3: Tatkal Rush Simulation ({num_requests} requests)")
        print("="*60)
        
        self.results = []
        threads = []
        
        start_time = time.time()
        
        # Simulate rush - rapid burst of requests
        for i in range(num_requests):
            t = threading.Thread(
                target=self.single_request,
                args=(i,)
            )
            threads.append(t)
            t.start()
            
            if delay > 0:
                time.sleep(delay)
        
        for t in threads:
            t.join()
        
        elapsed = time.time() - start_time
        
        print(f"⏱️  Simulated rush completed in {elapsed:.2f} seconds")
        
        # Count different statuses
        success = sum(1 for r in self.results if r["status"] == "success")
        queued = sum(1 for r in self.results if r["status"] == "queued")
        failed = sum(1 for r in self.results if r["status"] not in ["success", "queued"])
        
        print(f"✅ Successful: {success}")
        print(f"⏳ Queued: {queued}")
        print(f"❌ Failed/Rejected: {failed}")
        
        self.print_distribution()
    
    def print_distribution(self):
        """Print server distribution statistics"""
        server_distribution = {}
        
        for result in self.results:
            if result["status"] == "success":
                server_id = result["server_id"]
                server_distribution[server_id] = server_distribution.get(server_id, 0) + 1
        
        print("\n📊 Server Distribution (Load Balancing):")
        for server_id in sorted(server_distribution.keys()):
            count = server_distribution[server_id]
            percentage = (count / len([r for r in self.results if r["status"] == "success"])) * 100
            bar = "█" * int(percentage / 5)
            print(f"  Server {server_id}: {count:2d} requests ({percentage:5.1f}%) {bar}")
    
    def check_load_balancer_status(self):
        """Check load balancer status and statistics"""
        print("\n" + "="*60)
        print("Load Balancer Status")
        print("="*60)
        
        try:
            response = requests.get(f"{self.lb_url}/status")
            if response.status_code == 200:
                status = response.json()
                
                print(f"Strategy: {status['strategy']}")
                print(f"\nServers:")
                for server in status['servers']:
                    health = "🟢 Healthy" if server['is_healthy'] else "🔴 Down"
                    print(f"  Server {server['id']} (Port {server['port']}): {health}")
                    print(f"    - Active connections: {server['active_connections']}")
                    print(f"    - Total requests: {server['total_requests']}")
                
                stats = status['statistics']
                print(f"\nStatistics:")
                print(f"  Total requests: {stats['total_requests']}")
                print(f"  Successful: {stats['successful_requests']}")
                print(f"  Failed: {stats['failed_requests']}")
                print(f"  Queued: {stats['queued_requests']}")
                print(f"  Current queue size: {stats['queue_size']}")
                
                rl = status['rate_limit']
                print(f"\nRate Limiting:")
                print(f"  Limit: {rl['limit']} requests per {rl['window_seconds']}s")
                print(f"  Current window requests: {rl['current_requests']}")
            else:
                print("❌ Failed to get status")
        except requests.exceptions.RequestException as e:
            print(f"❌ Error connecting to load balancer: {e}")
    
    def test_strategy_switching(self):
        """Test switching between strategies"""
        print("\n" + "="*60)
        print("TEST 4: Strategy Switching")
        print("="*60)
        
        strategies = ["round_robin", "least_connections"]
        
        for strategy in strategies:
            try:
                response = requests.post(
                    f"{self.lb_url}/strategy/{strategy}",
                )
                if response.status_code == 200:
                    print(f"✅ Switched to: {strategy}")
                    
                    # Test with this strategy
                    self.results = []
                    for i in range(10):
                        self.single_request(i)
                    
                    self.print_distribution()
                    time.sleep(1)
            except requests.exceptions.RequestException as e:
                print(f"❌ Error switching strategy: {e}")

def print_welcome():
    """Print welcome message"""
    print("\n" + "="*60)
    print("🚀 Smart Load Balancer for Tatkal System - Tester")
    print("="*60)
    print("""
This test suite demonstrates:
✅ Basic booking requests
✅ Concurrent requests (stress test)
✅ Tatkal rush simulation
✅ Server distribution (Load Balancing)
✅ Health check & monitoring
✅ Rate limiting & queuing
✅ Strategy switching
    """)

def run_all_tests():
    """Run all tests"""
    print_welcome()
    
    tester = LoadBalancerTester()
    
    try:
        # Check initial status
        print("Checking load balancer status...")
        tester.check_load_balancer_status()
        
        # Run tests
        tester.test_basic_booking(num_requests=5)
        time.sleep(2)
        
        tester.test_concurrent_requests(num_requests=15)
        time.sleep(2)
        
        tester.test_tatkal_rush(num_requests=40, delay=0.05)
        time.sleep(2)
        
        tester.test_strategy_switching()
        time.sleep(2)
        
        # Final status
        tester.check_load_balancer_status()
        
        print("\n" + "="*60)
        print("✅ All tests completed!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")

if __name__ == "__main__":
    run_all_tests()
