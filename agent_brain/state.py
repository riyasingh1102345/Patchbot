# agent_brain/state.py
from typing import TypedDict, List, Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

class PatchBotState(TypedDict):
    # The unique identification token for the sandboxed session
    patch_id: str
    
    # Context injected at initialization
    cve_report: str
    target_file: str
    
    # Active structural strings modified across cycles
    current_code_state: str
    current_patch: str
    
    # Systems execution tracking parameters
    compiler_diagnostics: Annotated[List[str], add_messages]
    test_failures: str
    
    # Loop control boundary parameters
    revision_count: int
    max_revisions: int
    is_final: bool
