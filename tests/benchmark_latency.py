import time
import requests
import statistics

URL = "http://localhost:8000/v1/decision"

def run_benchmark(num_requests=50):
    payload = {
        "applicant_features": {"age": 35, "income": 55000, "education": "Bachelors", "sex": "Female"},
        "model_output": {"decision": "denied", "confidence": 0.73},
        "protected_attributes": ["sex"]
    }
    
    latencies = []
    
    print(f"Running {num_requests} requests to benchmark latency...")
    
    for _ in range(num_requests):
        start_time = time.time()
        try:
            response = requests.post(URL, json=payload, timeout=2.0)
            if response.status_code == 200:
                latencies.append((time.time() - start_time) * 1000) # in ms
        except Exception as e:
            print("Request failed:", e)
            
    if not latencies:
        print("No successful requests. Is the backend running?")
        return
        
    latencies.sort()
    
    p50 = statistics.median(latencies)
    
    # Calculate p95 loosely
    p95_idx = int(len(latencies) * 0.95)
    p95 = latencies[p95_idx] if p95_idx < len(latencies) else latencies[-1]
    
    print(f"Results over {len(latencies)} successful requests:")
    print(f"Average Latency: {sum(latencies)/len(latencies):.2f} ms")
    print(f"P50 Latency:     {p50:.2f} ms")
    print(f"P95 Latency:     {p95:.2f} ms")
    
    if p95 < 300:
        print("✅ SUCCESS: P95 latency is under the 300ms SLA.")
    else:
        print("❌ FAILED: P95 latency exceeds 300ms threshold.")

if __name__ == "__main__":
    run_benchmark(50)
