# run_benchmark.py
import time
import json
from run_patchbot import main as run_single_patch

def execute_system_benchmark(iterations=3):
    print(f"🏋️ Starting Live Empirical Benchmark Suite ({iterations} iterations)...")
    benchmark_results = []
    
    for i in range(iterations):
        print(f"\n--- 🏃 Test Run {i+1}/{iterations} ---")
        
        # Capture raw high-resolution system time before graph boot
        t_start = time.perf_counter()
        
        try:
            # Execute your live state machine graph
            run_single_patch()
            resolved = True
        except Exception as e:
            print(f"❌ Run failed due to runtime fault: {e}")
            resolved = False
            
        t_end = time.perf_counter()
        execution_delta = t_end - t_start
        
        # Log the real, raw systems data
        benchmark_results.append({
            "run_id": f"BENCH-RUN-{i+1}",
            "execution_time_sec": execution_delta,
            "resolved": resolved
        })
        
        # Avoid rate-limiting or API thermal throttling between test cycles
        time.sleep(2)
        
    # Save raw empirical dataset to disk for auditability
    with open("benchmark_metrics.json", "w") as f:
        json.dump(benchmark_results, f, indent=4)
        
    print("\n🏁 Benchmark suite complete. Raw data written to benchmark_metrics.json.")

if __name__ == "__main__":
    # We will do 3 runs for the live benchmark test
    execute_system_benchmark(iterations=3)