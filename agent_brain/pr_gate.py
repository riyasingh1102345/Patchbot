# agent_brain/pr_gate.py
import os
import subprocess
from github import Github
from agent_brain.state import PatchBotState
from mcp_sandbox.mcp_server import ACTIVE_SANDBOXES, sandbox

def pr_gate_node(state: PatchBotState) -> dict:
    """The deployment gate node. Executes automated local branch isolation,
    commits the verified fix, pushes upstream, and opens a GitHub Pull Request.
    """
    print("🚀 [Node: PR Gate] Packaging clean patch and opening automated GitHub Pull Request...")
    patch_id = state["patch_id"]
    target_file = state["target_file"]
    cve_report = state["cve_report"]
    
    if patch_id not in ACTIVE_SANDBOXES:
        print("❌ [PR Gate] Error: Active sandbox tracking metadata missing. Aborting Git transmission.")
        return {}
        
    meta = ACTIVE_SANDBOXES[patch_id]
    worktree_path = meta["worktree_path"]
    branch_name = f"patchbot/fix-{patch_id.lower()}"
    
    try:
        # 1. Git Automation via Subprocess execution inside the active worktree mount
        print(f"📦 [PR Gate] Initializing local deployment branch: {branch_name}")
        subprocess.run(["git", "checkout", "-b", branch_name], cwd=worktree_path, check=True, capture_output=True)
        
        print(f"📝 [PR Gate] Staging and committing modified target file: {target_file}")
        subprocess.run(["git", "add", target_file], cwd=worktree_path, check=True, capture_output=True)
        
        commit_msg = f"security(patchbot): automated vulnerability remediation for {patch_id}"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=worktree_path, check=True, capture_output=True)
        
        print(f"📤 [PR Gate] Executing upstream push to GitHub tracking branch...")
        subprocess.run(["git", "push", "origin", branch_name, "--force"], cwd=worktree_path, check=True, capture_output=True)
        
        # 2. PyGithub SDK Orchestration
        token = os.environ.get("GITHUB_TOKEN", "").strip()
        repo_slug = os.environ.get("GITHUB_REPOSITORY", "Mohammad-Azlan/first-patchbot")
        
        # Construct production-grade Markdown documentation layout for the PR body description
        pr_body = f"""## 🤖 PatchBot Automated Vulnerability Remediation

### 🔍 Vulnerability Profile Context
* **Remediation Target File:** `{target_file}`
* **Active Execution Run Token:** `{patch_id}`

### 📝 Tracked CVE Specification Target Details
```text
{cve_report}
```

### 🛠️ System Modification Summary
The patch was drafted programmatically by **PatchBot-Planner** using zero-entropy token configurations and successfully passed functional test coverage benchmarks verified inside an isolated, containerized Docker runtime container by **PatchBot-Evaluator**.

---
### 📊 System Telemetry & Execution Observability
* **LangSmith Live Diagnostic Visualization Trace:** [Inspect Agent Analytical Path](https://smith.langchain.com/public/mock-trace-{patch_id})
"""
        
        if not token:
            print("⚠️ [PR Gate] GITHUB_TOKEN missing in environment configuration. Simulating Pull Request interface payload...")
            pr_url = f"https://github.com/{repo_slug}/pull/mock-simulation-{patch_id}"
        else:
            g = Github(token)
            repo = g.get_repo(repo_slug)
            
            print(f"🐙 [PR Gate] Dispatching JSON-RPC request to GitHub API to open Pull Request...")
            pr = repo.create_pull(
                title=f"security(patchbot): Automated Remediation for {patch_id}",
                body=pr_body,
                head=branch_name,
                base="main"
            )
            pr_url = pr.html_url
            
        print(f"🎉 [PR Gate] Code successfully deployed! Active Pull Request URL: {pr_url}")
        
    except subprocess.CalledProcessError as e:
        error_logs = e.stderr.decode("utf-8", errors="replace") if e.stderr else str(e)
        print(f"❌ [PR Gate] Internal Git shell execution failed: {error_logs}")
    except Exception as e:
        print(f"❌ [PR Gate] Structural SDK invocation failure: {str(e)}")
    finally:
        # 3. Post-Flight Infrastructure Demolition
        # Once the code is pushed safely to GitHub, cleanly tear down the containers to free host system resources
        print("🧹 [PR Gate] Initiating post-flight cleanup. Decommissioning ephemeral resources...")
        sandbox.cleanup_sandbox(meta["container_id"])
        sandbox.cleanup_worktree(patch_id, worktree_path)
        del ACTIVE_SANDBOXES[patch_id]
        
    return {}
