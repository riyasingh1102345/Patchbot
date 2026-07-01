# mcp_sandbox/docker_client.py
import os
import shutil
import git
import docker


class SandboxManager:
    def __init__(self, base_repo_path: str = None):
        self.base_repo_path = base_repo_path or os.getcwd()
        self.repo = git.Repo(self.base_repo_path)
        self.docker_client = docker.from_env()

    def initialize_sandbox_env(self, patch_id: str) -> tuple[str, str]:
        """Provisions a Git worktree and boots an isolated Docker container."""
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        worktree_path = os.path.abspath(
            os.path.join(repo_root, "..", f"patchbot_env_{patch_id}")
        )

        branch_name = f"sandbox-{patch_id}"

        if os.path.exists(worktree_path):
            shutil.rmtree(worktree_path, ignore_errors=True)

        try:
            subprocess_result = self.repo.git.worktree(
                "add",
                "-b",
                branch_name,
                worktree_path,
                self.repo.active_branch.name,
            )
            print(subprocess_result)
        except Exception as e:
            if "already exists" in str(e):
                self.repo.git.worktree("add", worktree_path, branch_name)
            else:
                raise e

        container_id = self.spawn_container(worktree_path)
        return container_id, worktree_path

    def create_worktree(self, patch_id: str) -> tuple[str, str]:
        parent_dir = os.path.dirname(self.base_repo_path)
        worktree_path = os.path.abspath(
            os.path.join(parent_dir, "ephemeral_patches", f"patch_{patch_id}")
        )

        if os.path.exists(worktree_path):
            self.cleanup_worktree(patch_id, worktree_path)

        base_branch = self.repo.active_branch.name
        branch_name = f"patchbot/run-{patch_id}"

        print(f"🎬 Cutting isolated Git Worktree: {worktree_path} on branch [{branch_name}]")

        try:
            self.repo.git.worktree("add", "-b", branch_name, worktree_path, base_branch)
        except Exception as e:
            if "already exists" in str(e):
                self.repo.git.worktree("add", worktree_path, branch_name)
            else:
                raise e

        return worktree_path, branch_name

    def spawn_container(self, host_worktree_path: str, image: str = "python:3.11-slim") -> str:
        container_workspace = "/workspace"

        run_kwargs = {
            "image": image,
            "command": "tail -f /dev/null",
            "detach": True,
            "volumes": {
                host_worktree_path: {
                    "bind": container_workspace,
                    "mode": "rw",
                }
            },
            "working_dir": container_workspace,
            "network_mode": "bridge",
        }

        if os.name != "nt":
            run_kwargs["user"] = f"{os.getuid()}:{os.getgid()}"

        print(f"🐳 Launching secure Docker workspace sandbox using [{image}]")
        container = self.docker_client.containers.run(**run_kwargs)
        return container.id

    def cleanup_sandbox(self, container_id: str):
        try:
            container = self.docker_client.containers.get(container_id)
            print(f"🛑 Force killing container sandbox: {container_id[:12]}")
            container.remove(force=True)
        except Exception as e:
            print(f"⚠️ Sandbox cleanup logging: {e}")

    def cleanup_worktree(self, patch_id: str, worktree_path: str):
        print(f"🧹 Evicting Git Worktree physical path tracking: {worktree_path}")

        try:
            self.repo.git.worktree("remove", "--force", worktree_path)
        except Exception as e:
            print(f"⚠️ Git worktree removal metadata: {e}")

        if os.path.exists(worktree_path):
            shutil.rmtree(worktree_path, ignore_errors=True)

        for branch_name in (f"patchbot/run-{patch_id}", f"sandbox-{patch_id}"):
            try:
                self.repo.git.branch("-D", branch_name)
            except Exception:
                pass


if __name__ == "__main__":
    print("🧪 Commencing Hour 3 Systems Isolation Live Fire Test...")
    manager = SandboxManager()

    test_id = "01_test"
    w_path, b_name = manager.create_worktree(test_id)
    c_id = manager.spawn_container(w_path)

    print(f"🔥 Verification Success! Container Active ID: {c_id[:12]}")

    manager.cleanup_sandbox(c_id)
    manager.cleanup_worktree(test_id, w_path)
    print("🏁 Sandbox teardown successful. Local machine status: pristine.")