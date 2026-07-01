# agent_brain/graph.py
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from agent_brain.state import PatchBotState
from agent_brain.planner import planner_node
from agent_brain.evaluator import evaluator_node

def route_evaluation_results(state: PatchBotState) -> str:
    """Conditional routing engine that acts as the state machine's traffic cop.
    Decides whether to keep looping or terminate the runtime session.
    """
    # Force termination if the Evaluator confirms the fix is perfectly green
    if state.get("is_final"):
        print("🏁 [Router] Test suite passed perfectly. Terminating loop sequence gracefully.")
        return "end"
        
    # Circuit Breaker: Halt execution if the AI hits its max loop threshold
    current_cycle = state.get("revision_count", 0)
    max_cycles = state.get("max_revisions", 3)
    
    if current_cycle >= max_cycles:
        print(f"🛑 [Router] Max loop limits reached ({current_cycle}/{max_cycles}). Halting code generation.")
        return "end"
        
    # Otherwise, pass the compiler errors back to the planner for another attempt
    print(f"🔄 [Router] Verification failed. Routing cycle back to Planner (Attempt {current_cycle + 1}).")
    return "continue"


# Initialize the compilation workflow map linked to our shared state blueprint
workflow = StateGraph(PatchBotState)

# 1. Register our operational nodes
workflow.add_node("planner_node", planner_node)
workflow.add_node("evaluator_node", evaluator_node)

# 2. Map the structural execution wires
workflow.add_edge(START, "planner_node")
workflow.add_edge("planner_node", "evaluator_node")

# 3. Inject the conditional routing gates to manage the self-healing cycle
workflow.add_conditional_edges(
    "evaluator_node",
    route_evaluation_results,
    {
        "continue": "planner_node",
        "end": END
    }
)

# 4. Compile the state machine with memory tracking
# Ties back to the MemorySaver checkpointer verified in your Hour 1 smoke test
memory = MemorySaver()
patchbot_app = workflow.compile(checkpointer=memory)

print("🦅 LangGraph State Machine successfully compiled. Self-healing engine is armed and online.")