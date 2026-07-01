# mcp_sandbox/mcp_server.py
import os
import sys
import json

# Cross-Platform Path Guard: Forcefully inject the repository root into Python's search paths
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.append(repo_root)

# Systems Guardrail: Force standard I/O streams to use UTF-8 encoding on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from mcp.server.fastmcp import FastMCP
from mcp_sandbox.docker_client import SandboxManager

# Initialize the FastMCP protocol engine
mcp = FastMCP("PatchBot-Sandbox")

# Long-lived systems orchestrator instance
sandbox = SandboxManager()

# Stateful runtime engine map: tracks patch_id -> {"worktree_path": str, "container_id": str}
ACTIVE_SANDBOXES = {}

@mcp.tool()
def initialize_sandbox_env(patch_id: str) -> str:
    """Spawns an isolated Git worktree and a secure Docker container for a given patching run.
    
    Args:
        patch_id (str): A unique token identifying this specific vulnerability run.
    """
    if patch_id in ACTIVE_SANDBOXES:
        return f"Sandbox environment for run [{patch_id}] already active."
        
    try:
        w_path, b_name = sandbox.create_worktree(patch_id)
        c_id = sandbox.spawn_container(w_path)
        
        ACTIVE_SANDBOXES[patch_id] = {
            "worktree_path": w_path,
            "container_id": c_id,
            "branch_name": b_name
        }
        return f"🚀 Sandbox initialization successful.\nWorkspace Path: {w_path}\nContainer Identifier: {c_id[:12]}"
    except Exception as e:
        return f"❌ Sandbox initialization failure: {str(e)}"

@mcp.tool()
def read_source_file(patch_id: str, relative_path: str) -> str:
    """Reads a localized code file from the active sandboxed workspace safely.
    
    Args:
        patch_id (str): The active tracking identifier of the vulnerability run.
        relative_path (str): The relative path to the file from the workspace root.
    """
    if patch_id not in ACTIVE_SANDBOXES:
        return f"Error: No active sandbox found for patch runtime identifier: {patch_id}"
        
    workspace_path = ACTIVE_SANDBOXES[patch_id]["worktree_path"]
    resolved_path = os.path.abspath(os.path.join(workspace_path, relative_path))

    # Path-Traversal Guardrail check inside the active worktree directory bounds
    if not resolved_path.startswith(workspace_path):
        return "Security Violation: Operation blocked. Attempted to read outside the isolated sandbox bounds."

    if not os.path.exists(resolved_path):
        return f"Error: File not found at layout location: {relative_path}"

    with open(resolved_path, "r", encoding="utf-8") as f:
        return f.read()

@mcp.tool()
def write_patch_to_file(patch_id: str, relative_path: str, code_content: str) -> str:
    """Safely writes written code alterations directly to a file inside the isolated sandbox workspace.
    
    Args:
        patch_id (str): The active tracking identifier of the vulnerability run.
        relative_path (str): File destination path relative to the workspace root.
        code_content (str): The raw string contents of the updated source file.
    """
    if patch_id not in ACTIVE_SANDBOXES:
        return f"Error: No active sandbox found for patch runtime identifier: {patch_id}"
        
    workspace_path = ACTIVE_SANDBOXES[patch_id]["worktree_path"]
    target_file_path = os.path.abspath(os.path.join(workspace_path, relative_path))
    
    # Path-Traversal Guardrail check inside the active worktree directory bounds
    if not target_file_path.startswith(workspace_path):
        return "Security Violation: Operation blocked. Attempted to write outside the isolated sandbox bounds."
        
    try:
        # Guarantee sub-directories exist
        os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
        with open(target_file_path, "w", encoding="utf-8") as f:
            f.write(code_content)
        return f"Successfully wrote {len(code_content)} bytes to physical layer path: {relative_path}"
    except Exception as e:
        return f"Error writing patch payload: {str(e)}"


@mcp.tool()
def execute_sandboxed_tests(patch_id: str, test_command: str) -> str:
    """Executes build instructions or test runners inside the container with strict 15-second limits.
    
    Args:
        patch_id (str): The active tracking identifier of the vulnerability run.
        test_command (str): The exact terminal command string to execute (e.g., 'pytest' or 'python -m unittest').
    """
    if patch_id not in ACTIVE_SANDBOXES:
        return f"Error: Execution context missing for runtime identifier: {patch_id}"
        
    container_id = ACTIVE_SANDBOXES[patch_id]["container_id"]
    docker_engine = sandbox.docker_client
    
    try:
        container = docker_engine.containers.get(container_id)
        
        # Systems Guardrail: Prepend linux timeout command to capture infinite runaway loops
        secured_shell_command = f"timeout 15 {test_command}"
        
        print(f"⚡ Executing sandboxed instruction context: [{secured_shell_command}]")
        
        # Run terminal command inside the container system engine
        exit_code, stream_output = container.exec_run(
            cmd=["bash", "-c", secured_shell_command],
            demux=False
        )
        
        # Parse return metadata payload
        decoded_output = stream_output.decode("utf-8", errors="replace")
        
        # Explicit check for the Linux timeout exit status code (124)
        if exit_code == 124:
            return json.dumps({
                "status": "TIMEOUT_FAILURE",
                "exit_code": 124,
                "logs": "❌ Critical Exception: Test execution cycle exceeded the maximum 15.0s processing limit. Processing forcefully halted."
            })
            
        return json.dumps({
            "status": "SUCCESS" if exit_code == 0 else "EXECUTION_FAILURE",
            "exit_code": exit_code,
            "logs": decoded_output
        }, indent=2)
        
    except Exception as e:
        return f"Internal container communication exception: {str(e)}"


@mcp.tool()
def teardown_sandbox_env(patch_id: str) -> str:
    """Tears down, prunes, and terminates the physical sandboxed resources for a completed runtime session.
    
    Args:
        patch_id (str): The identifier of the tracking session to destroy.
    """
    if patch_id not in ACTIVE_SANDBOXES:
        return f"No sandbox active tracking logs found for id: {patch_id}"
        
    meta = ACTIVE_SANDBOXES[patch_id]
    sandbox.cleanup_sandbox(meta["container_id"])
    sandbox.cleanup_worktree(patch_id, meta["worktree_path"])
    
    del ACTIVE_SANDBOXES[patch_id]
    return f"🧹 Sandbox environment sequence [{patch_id}] successfully discarded."

if __name__ == "__main__":
    mcp.run()