# mcp_sandbox/mcp_server.py
import os
from mcp.server.fastmcp import FastMCP

# Initialize the FastMCP server for our vulnerability sandbox
mcp = FastMCP("PatchBot-Sandbox")

@mcp.tool()
def read_source_file(relative_path: str) -> str:
    """Reads a localized code file from the current workspace path safely.
    
    Args:
        relative_path (str): The relative path to the file from the project root.
    """
    # Low-level Guardrail: Absolute path resolution to block path-traversal attacks
    resolved_path = os.path.abspath(relative_path)
    current_workspace = os.getcwd()

    if not resolved_path.startswith(current_workspace):
        raise PermissionError(
            f"Security Guardrail Triggered: Attempted path traversal to {resolved_path}"
        )

    if not os.path.exists(resolved_path):
        return f"Error: File not found at layout location: {relative_path}"

    with open(resolved_path, "r", encoding="utf-8") as f:
        return f.read()

# This allows running the server directly via 'uv run' if needed
if __name__ == "__main__":
    mcp.run()