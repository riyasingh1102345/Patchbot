# agent_brain/evaluator.py
import os
import json
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from agent_brain.state import PatchBotState
from mcp_sandbox.mcp_server import ACTIVE_SANDBOXES, sandbox

# Ensure the persona prompt constant remains at the top
EVALUATOR_SYSTEM_PROMPT = """You are PatchBot-Evaluator, a cynical, hostile QA and automation testing engineer. 

Your job is to verify if the Planner's fixes are genuinely production-grade. You do not trust the Planner. You must command the sandbox tools to compile the code and execute the test suites. 

Inspect standard error (stderr) streams ruthlessly. Only mark 'is_final' as True inside the state graph if the terminal exit code is exactly 0 and all security test verification suites pass perfectly. If any test or build execution fails, you must propagate the exact error stream back into the system state context."""

def evaluator_node(state: PatchBotState) -> dict:
    """The execution node for the Evaluator agent.
    Pipes the patch into the container, runs tests, and judges the output stability.
    """
    print("🦺 [Node: Evaluator] Catching patch payload and executing sandboxed validation...")
    
    patch_id = state["patch_id"]
    relative_path = state["target_file"]
    patch_code = state["current_patch"]
    
    if patch_id not in ACTIVE_SANDBOXES:
        return {
            "test_failures": "System Error: Active sandbox environment missing.",
            "is_final": False
        }
        
    workspace_path = ACTIVE_SANDBOXES[patch_id]["worktree_path"]
    container_id = ACTIVE_SANDBOXES[patch_id]["container_id"]
    target_file_path = os.path.abspath(os.path.join(workspace_path, relative_path))
    
    # 1. Write the proposed patch to the physical worktree folder
    try:
        os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
        with open(target_file_path, "w", encoding="utf-8") as f:
            f.write(patch_code)
    except Exception as e:
        return {"test_failures": f"File I/O Error writing patch: {str(e)}", "is_final": False}

    # 2. Execute the test runner inside the isolated Docker container
    # For this framework engine, we default to running python's built-in unittest
    test_command = f"timeout 15 python -m unittest discover -s tests"
    container = sandbox.docker_client.containers.get(container_id)
    
    exit_code, stream_output = container.exec_run(
        cmd=["bash", "-c", test_command],
        demux=False
    )
    decoded_logs = stream_output.decode("utf-8", errors="replace")

    # 3. Pass the raw terminal outputs to Claude to verify compliance
    llm = ChatAnthropic(
        model_name="claude-3-5-sonnet-latest",
        temperature=0.0
    )
    
    verification_prompt = f"""
    Review the following test execution results for Patch ID [{patch_id}].
    
    Terminal Exit Code: {exit_code}
    Terminal Log Output:
    {decoded_logs}
    
    Analyze if the software compiled perfectly and passed all functional tests.
    Respond strictly in JSON format with two keys:
    {{
        "is_final": true/false,
        "rationale": "Your short analysis here"
    }}
    """
    
    response = llm.invoke([
        SystemMessage(content=EVALUATOR_SYSTEM_PROMPT),
        HumanMessage(content=verification_prompt)
    ])
    
    # 4. Parse the structural judgment safely
    try:
        # Strip potential markdown wrapping blocks if the LLM includes them
        clean_content = response.content.strip().removeprefix("```json").removesuffix("```").strip()
        decision = json.loads(clean_content)
        is_final = decision.get("is_final", False)
        rationale = decision.get("rationale", "")
    except Exception:
        # Fallback safety default if JSON parsing fails
        is_final = True if exit_code == 0 else "TIMEOUT" not in decoded_logs and False
        rationale = "Fallback parsing executed based on raw exit code."

    print(f"📋 [Evaluator Decision] Is Final: {is_final} | Rationale: {rationale}")

    return {
        "compiler_diagnostics": [f"Run {state.get('revision_count', 1)}: {rationale}"],
        "test_failures": decoded_logs if not is_final else "",
        "is_final": is_final
    }
