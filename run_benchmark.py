# run_benchmark.py
import time
import json
import uuid
from mcp_sandbox.mcp_server import sandbox, ACTIVE_SANDBOXES
from agent_brain.graph import patchbot_app
from dotenv import load_dotenv

load_dotenv()

def execute_system_benchmark(iterations=3):
    print(f"🏋️ Starting Live Empirical FinOps Benchmark ({iterations} iterations)...")
    benchmark_results = []
    
    for i in range(iterations):
        print(f"\n--- 🏃 Test Run {i+1}/{iterations} ---")
        run_token = f"CVE-RUN-{uuid.uuid4().hex[:6].upper()}"
        
        # Setup infrastructure
        container_id, worktree_path = sandbox.initialize_sandbox_env(run_token)
        ACTIVE_SANDBOXES[run_token] = {"container_id": container_id, "worktree_path": worktree_path}
        
        with open("calculator.py", "r") as f:
            vulnerable_code = f.read()
            
        initial_state = {
            "patch_id": run_token,
            "cve_report": "CRITICAL: Remote Code Execution vulnerability via eval(). Replace with ast.literal_eval.",
            "target_file": "calculator.py",
            "current_code_state": vulnerable_code,
            "max_revisions": 3,
            "revision_count": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0
        }
        
        config = {"configurable": {"thread_id": run_token}}
        
        t_start = time.perf_counter()
        
        final_state_snapshot = {}
        try:
            for event in patchbot_app.stream(initial_state, config):
                for node_name, state_updates in event.items():
                    if state_updates:
                        # Keep updating our snapshot with the latest memory
                        final_state_snapshot.update(state_updates)
            resolved = final_state_snapshot.get("is_final", False)
        except Exception as e:
            print(f"❌ Fault: {e}")
            resolved = False
            
        t_end = time.perf_counter()
        
        benchmark_results.append({
            "run_id": run_token,
            "execution_time_sec": t_end - t_start,
            "resolved": resolved,
            "revisions_needed": final_state_snapshot.get("revision_count", 0),
            "input_tokens": final_state_snapshot.get("total_input_tokens", 0),
            "output_tokens": final_state_snapshot.get("total_output_tokens", 0)
        })
        time.sleep(2)
        
    with open("benchmark_metrics.json", "w") as f:
        json.dump(benchmark_results, f, indent=4)
    print("\n🏁 Benchmark suite complete. Data written to benchmark_metrics.json.")

if __name__ == "__main__":
    execute_system_benchmark(iterations=3)
