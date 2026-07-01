# agent_brain/planner.py
import os
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from agent_brain.state import PatchBotState

# Ensure the persona prompt constant remains at the top
PLANNER_SYSTEM_PROMPT = """You are PatchBot-Planner, a world-class low-level software engineer specializing in surgical vulnerability remediation. 

Your job is to read CVE reports, analyze source code, and use your tools to draft precise security patches. Do not rewrite whole modules; write minimal, high-efficiency adjustments. 

Prioritize preventing injection vulnerabilities, memory leaks, and bounds-checking errors. Always use your available sandbox tools to read and understand surrounding code files before proposing any patch content."""

def planner_node(state: PatchBotState) -> dict:
    """The execution node for the Planner agent. 
    Processes the active vulnerability context and coordinates patch generation.
    """
    print("🧠 [Node: Planner] Analyzing vulnerability state and compiling recommendations...")
    
    # Initialize the high-performance model layer
    # Expects ANTHROPIC_API_KEY to be set in your local .env file
    llm = ChatAnthropic(
        model_name="claude-3-5-sonnet-latest",
        temperature=0.0  # Greedy decoding for deterministic engineering adjustments
    )
    
    # Compile the conversational history context payload
    messages = [
        SystemMessage(content=PLANNER_SYSTEM_PROMPT),
        HumanMessage(content=f"""
Active Run ID: {state['patch_id']}
Vulnerability Target File: {state['target_file']}
Target CVE Specification Details:
{state['cve_report']}

Current Code Base Layout:
{state.get('current_code_state', 'Not yet pulled from sandbox layer.')}

Previous Execution Compilation/Test Failures:
{state.get('test_failures', 'No active failure logs reported yet.')}
        """)
    ]
    
    # Invoke the model
    response = llm.invoke(messages)
    
    # Update state tracking metrics safely
    current_revisions = state.get("revision_count", 0)
    
    # Return the dictionary payload that LangGraph merges into the global state
    return {
        "current_patch": response.content,
        "revision_count": current_revisions + 1
    }
