# agent_brain/graph.py
import os
import sys
import hashlib

# Cross-Platform Path Guard: Forcefully inject the repository root into Python's search paths
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.append(repo_root)

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from agent_brain.state import PatchBotState
from agent_brain.planner import planner_node
from agent_brain.evaluator import evaluator_node
from agent_brain.pr_gate import pr_gate_node

# Stateful in-memory tracker mapping: patch_id -> set of unique error string hashes
SEEN_ERROR_HASHES = {}

def route_evaluation_results(state: PatchBotState) -> str:
    """Conditional routing engine that acts as the state machine's traffic cop.
    Intercepts degradation and loops via cryptographic signature tracking.
    """
    if state.get("is_final"):
        print("🏁 [Router] Test suite passed perfectly. Routing execution state to PR Gate Node.")
        return "deploy"
        
    patch_id = state.get("patch_id")
    current_errors = state.get("test_failures", "")
    
    # SYSTEM GUARD: Error String Fingerprinting (Loop Detection)
    if current_errors:
        error_hash = hashlib.sha256(current_errors.strip().encode("utf-8")).hexdigest()
        
        if patch_id not in SEEN_ERROR_HASHES:
            SEEN_ERROR_HASHES[patch_id] = set()
            
        if error_hash in SEEN_ERROR_HASHES[patch_id]:
            print(f"🚨 [Router] Infinite Loop Detected! Error signature matches a previous run. Triggering Early Rollback on step {state.get('revision_count')}!")
            return "rollback"
            
        SEEN_ERROR_HASHES[patch_id].add(error_hash)

    # Fallback Step-Budget Tracker
    current_cycle = state.get("revision_count", 0)
    max_cycles = state.get("max_revisions", 3)
    
    if current_cycle >= max_cycles:
        print(f"🚨 [Router] Max loop limits reached ({current_cycle}/{max_cycles}). Triggering Deterministic Rollback!")
        return "rollback"
        
    print(f"🔄 [Router] Verification failed. Routing cycle back to Planner (Attempt {current_cycle + 1}).")
    return "continue"


def rollback_node(state: PatchBotState) -> dict:
    """Executes a physical environment wipe and resets volatile parameters 
    when the agent enters an unrecoverable failure loop.
    """
    print("🛡️ [Node: Rollback] Initiating time-travel rollback sequence...")
    patch_id = state["patch_id"]
    
    from mcp_sandbox.mcp_server import ACTIVE_SANDBOXES, sandbox
    if patch_id in ACTIVE_SANDBOXES:
        meta = ACTIVE_SANDBOXES[patch_id]
        print(f"🧹 [Rollback] Evicting corrupted physical directory path: {meta['worktree_path']}")
        
        sandbox.cleanup_sandbox(meta["container_id"])
        sandbox.cleanup_worktree(patch_id, meta["worktree_path"])
        del ACTIVE_SANDBOXES[patch_id]
        
    print("⏳ [Rollback] Synchronizing checkpointer ledger. Rewinding environment properties back to baseline safety.")
    return {
        "current_patch": "",
        "current_code_state": "Wiped via Deterministic Rollback.",
        "test_failures": "CRITICAL: Agent loop degraded. Physical sandbox neutralized and rolled back to baseline.",
        "is_final": False
    }


# Initialize the compilation workflow map linked to our shared state blueprint
workflow = StateGraph(PatchBotState)

# Register our operational nodes
workflow.add_node("planner_node", planner_node)
workflow.add_node("evaluator_node", evaluator_node)
workflow.add_node("rollback_node", rollback_node)
workflow.add_node("pr_gate_node", pr_gate_node)

# Map the structural execution wires
workflow.add_edge(START, "planner_node")
workflow.add_edge("planner_node", "evaluator_node")

# Inject the conditional routing gates to manage the self-healing cycle
workflow.add_conditional_edges(
    "evaluator_node",
    route_evaluation_results,
    {
        "continue": "planner_node",
        "rollback": "rollback_node",
        "deploy": "pr_gate_node"
    }
)

# Connect system output nodes explicitly to final graph termination boundaries
workflow.add_edge("rollback_node", END)
workflow.add_edge("pr_gate_node", END)

# Compile the state machine with memory tracking
memory = MemorySaver()
patchbot_app = workflow.compile(checkpointer=memory)

print("🦅 LangGraph State Machine successfully compiled with Automated GitHub PR Gate Capabilities.")
