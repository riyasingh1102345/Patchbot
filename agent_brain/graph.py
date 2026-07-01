# agent_brain/graph.py
import os
import sys

# Cross-Platform Path Guard: Forcefully inject the repository root into Python's search paths
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.append(repo_root)

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from agent_brain.state import PatchBotState
from agent_brain.planner import planner_node
from agent_brain.evaluator import evaluator_node

def route_evaluation_results(state: PatchBotState) -> str:
    """Conditional routing engine that acts as the state machine's traffic cop.
    Intercepts degradation and routes execution to rollback instead of a raw exit.
    """
    if state.get("is_final"):
        print("🏁 [Router] Test suite passed perfectly. Terminating loop sequence gracefully.")
        return "end"
        
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
    
    # 1. Imperative Systems Clean: Force-evict physical worktree and terminate containers
    from mcp_sandbox.mcp_server import ACTIVE_SANDBOXES, sandbox
    if patch_id in ACTIVE_SANDBOXES:
        meta = ACTIVE_SANDBOXES[patch_id]
        print(f"🧹 [Rollback] Evicting corrupted physical directory path: {meta['worktree_path']}")
        
        # Command our core system client directly to dismantle the sandboxed infrastructure
        sandbox.cleanup_sandbox(meta["container_id"])
        sandbox.cleanup_worktree(patch_id, meta["worktree_path"])
        del ACTIVE_SANDBOXES[patch_id]
        
    # 2. Semantic State Reset
    # We maintain the overall compilation diagnostics list for systemic logging,
    # but wipe out the broken current patch and code state variables to safely exit.
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
        "end": END
    }
)

# Connect the rollback completion directly to graph termination
workflow.add_edge("rollback_node", END)

# Compile the state machine with memory tracking
memory = MemorySaver()
patchbot_app = workflow.compile(checkpointer=memory)

print("🦅 LangGraph State Machine successfully compiled with Time-Travel Rollback capabilities.")
