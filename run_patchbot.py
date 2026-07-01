# run_patchbot.py
import uuid
from agent_brain.graph import patchbot_app
from mcp_sandbox.mcp_server import sandbox, ACTIVE_SANDBOXES

def main():
    # 1. Generate a unique execution tracking token
    run_token = f"CVE-RUN-{uuid.uuid4().hex[:6].upper()}"
    print(f"🔥 Initiating Live Fire Drill. Trace ID: {run_token}")
    
    # 2. Provision the physical infrastructure BEFORE starting the cognitive graph
    # This ensures the Evaluator and PR Gate have a physical sandbox to access
    print("🐳 Provisioning isolated Docker environment and Git Worktree...")
    container_id, worktree_path = sandbox.initialize_sandbox_env(run_token)
    
    # 3. Define the starting state ledger
    config = {"configurable": {"thread_id": run_token}}
    initial_state = {
        "patch_id": run_token,
        "cve_report": "CRITICAL: Remote Code Execution vulnerability in calculator module via python eval(). Replace with a secure alternative like ast.literal_eval.",
        "target_file": "calculator.py",
        "max_revisions": 3,
        "revision_count": 0
    }

    # 4. Stream the execution graph live to the terminal
    print("🧠 Engaging Agentic Brain. Streaming state transitions...")
    for event in patchbot_app.stream(initial_state, config):
        # LangGraph returns a dictionary where the key is the name of the node that just finished
        for node_name, state_updates in event.items():
            print(f"\n✅ [Transition Complete] Node: {node_name}")
            if "revision_count" in state_updates:
                print(f"   ↳ Revision: {state_updates['revision_count']}")

if __name__ == "__main__":
    main()