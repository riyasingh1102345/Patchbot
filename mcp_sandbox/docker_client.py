# mcp_sandbox/docker_client.py
import os
import shutil
import git
import docker

class SandboxManager:
    def __init__(self, base_repo_path: str = None):
        """Initializes the Git and Docker engines across cross-platform environments."""
        self.base_repo_path = base_repo_path or os.getcwd()
        self.repo = git.Repo(self.base_repo_path)
        self.docker_client = docker.from_env()

    def create_worktree(self, patch_id: str) -> tuple[str, str]:
        """Creates an isolated Git worktree and unique tracking branch for a patch iteration."""
        parent_dir = os.path.dirname(self.base_repo_path)
        worktree_path = os.path.abspath(os.path.join(parent_dir, "ephemeral_patches", f"patch_{patch_id}"))
        
        # Clean any zombie paths left over from interrupted previous runs
        if os.path.exists(worktree_path):
            self.cleanup_worktree(patch_id, worktree_path)

        # Detect active base branch dynamically (master/main)
        base_branch = self.repo.active_branch.name
        branch_name = f"patchbot/run-{patch_id}"
        
        print(f"🎬 Cutting isolated Git Worktree: {worktree_path} on branch [{branch_name}]")
        
        # Execute low-level git worktree add call
        try:
            self.repo.git.worktree("add", "-b", branch_name, worktree_path, base_branch)
        except Exception as e:
            if "already exists" in str(e):
                self.repo.git.worktree("add", worktree_path, branch_name)
            else:
                raise e
                
        return worktree_path, branch_name

    def spawn_container(self, host_worktree_path: str, image: str = "python:3.11-slim") -> str:
        """Spawns a detached headless Docker sandbox container mounting the ephemeral worktree."""
        container_workspace = "/workspace"
        
        # Configure the volume mapping matrix
        volumes = {
            host_worktree_path: {
                "bind": container_workspace,
                "mode": "rw"
            }
        }
        
        # Core Docker arguments configuration
        run_kwargs = {
            "image": image,
            "command": "tail -f /dev/null",  # Headless loop to keep container alive indefinitely
            "detach": True,
            "volumes": volumes,
            "working_dir": container_workspace,
            "network_mode": "bridge"
        }
        
        # Systems Guardrail: Apply User ID mapping on Mac/Linux to prevent root file pollution.
        # Skipped on Windows (Mohammad's HP) where WSL2 backend handles mapping natively.
        if os.name != "nt":
            run_kwargs["user"] = f"{os.getuid()}:{os.getgid()}"
            
        print(f"🐳 Launching secure Docker workspace sandbox using [{image}]")
        container = self.docker_client.containers.run(**run_kwargs)
        return container.id

    def cleanup_sandbox(self, container_id: str):
        """Forcefully terminates and deletes the sandboxed container."""
        try:
            container = self.docker_client.containers.get(container_id)
            print(f"🛑 Force killing container sandbox: {container_id[:12]}")
            container.remove(force=True)
        except Exception as e:
            print(f"⚠️ Sandbox cleanup logging: {e}")

    def cleanup_worktree(self, patch_id: str, worktree_path: str):
        """Prunes the physical workspace directories and untracked git branch layers cleanly."""
        print(f"🧹 Evicting Git Worktree physical path tracking: {worktree_path}")
        try:
            self.repo.git.worktree("remove", "--force", worktree_path)
        except Exception as e:
            print(f"⚠️ Git worktree removal metadata: {e}")
            
        # Hard system wipe if folder locks linger
        if os.path.exists(worktree_path):
            shutil.rmtree(worktree_path, ignore_errors=True)
            
        try:
            branch_name = f"patchbot/run-{patch_id}"
            self.repo.git.branch("-D", branch_name)
        except Exception:
            pass


# Systems Engine Smoke Test Run Execution
if __name__ == "__main__":
    print("🧪 Commencing Hour 3 Systems Isolation Live Fire Test...")
    manager = SandboxManager()
    
    test_id = "01_test"
    w_path, b_name = manager.create_worktree(test_id)
    c_id = manager.spawn_container(w_path)
    
    print(f"🔥 Verification Success! Container Active ID: {c_id[:12]}")
    
    # Tear down test cycle to maintain local environment parity
    manager.cleanup_sandbox(c_id)
    manager.cleanup_worktree(test_id, w_path)
    print("🏁 Sandbox teardown successful. Local machine status: pristine.")
