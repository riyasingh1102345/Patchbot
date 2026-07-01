# run_patchbot.py
import os
from dotenv import load_dotenv

# Automatically load keys from the .env file before anything else runs
load_dotenv()

import uuid
from agent_brain.graph import patchbot_app
from mcp_sandbox.mcp_server import sandbox, ACTIVE_SANDBOXES

def main():
    # 1. Generate a unique execution tracking token
    run_token = f"CVE-RUN-{uuid.uuid4().hex[:6].upper()}"
    print(f"🔥 Initiating Live Fire Drill. Trace ID: {run_token}")
    
    # 2. Provision the physical infrastructure
    print("🐳 Provisioning isolated Docker environment and Git Worktree...")
    container_id, worktree_path = sandbox.initialize_sandbox_env(run_token)
    
    # Register the infrastructure so the agent nodes can find it
    ACTIVE_SANDBOXES[run_token] = {
        "container_id": container_id,
        "worktree_path": worktree_path
    }
    
    # 🚨 THE FIX: Read the vulnerable file so the Planner can actually see the code!
    with open("calculator.py", "r") as f:
        vulnerable_code = f.read()
    
    # 3. Define the starting state ledger
    config = {"configurable": {"thread_id": run_token}}
    initial_state = {
        "patch_id": run_token,
        "cve_report": "CRITICAL: Remote Code Execution vulnerability in calculator module via python eval(). Replace with a secure alternative like ast.literal_eval.",
        "target_file": "calculator.py",
        "current_code_state": vulnerable_code, # <-- Injected the real code here!
        "max_revisions": 3,
        "revision_count": 0
    }

    # 4. Stream the execution graph live to the terminal
    print("🧠 Engaging Agentic Brain. Streaming state transitions...")
    for event in patchbot_app.stream(initial_state, config):
        for node_name, state_updates in event.items():
            print(f"\n✅ [Transition Complete] Node: {node_name}")
            # 🛡️ THE FIX: Check if state_updates actually exists before searching it
            if state_updates and "revision_count" in state_updates:
                print(f"   ↳ Revision: {state_updates['revision_count']}")


if __name__ == "__main__":
    main()
