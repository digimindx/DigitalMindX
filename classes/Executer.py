import subprocess
import platform
import os

# ==========================================
# ⚙️ EXECUTER MANAGER
# ==========================================
class Executer:
    """
    Handles execution of OS shell commands and system information retrieval.
    """

    def get_system_info(self) -> str:
        """Retrieves current OS and environment details."""
        try:
            info = {
                "OS": platform.system(),
                "Platform": platform.platform(),
                "Architecture": platform.machine(),
                "Current Directory": os.getcwd()
            }
            return "System Information:\n" + "\n".join([f"- {k}: {v}" for k, v in info.items()])
        except Exception as e:
            return f"Error getting system info: {str(e)}"

    def execute_command(self, command: str, timeout: int = 10) -> str:
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8'
            )
            
            output = result.stdout.strip()
            error = result.stderr.strip()
            
            if result.returncode == 0:
                if not output:
                    return "Command executed successfully. (No output)"
                return f"Command executed successfully.\nOutput:\n{output}"
            else:
                return f"Command failed with return code {result.returncode}.\nError:\n{error}"
                
        except subprocess.TimeoutExpired:
            return f"Error: Command timed out after {timeout} seconds. The process was killed."
        except Exception as e:
            return f"Error executing command: {str(e)}"

    @property
    def schemas(self) -> list:
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_system_info",
                    "description": "Retrieves the current Operating System, architecture, and environment details. MUST be called before executing any OS commands.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "execute_command",
                    "description": "Executes a shell command on the operating system. WARNING: Use only for safe, necessary system operations.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string", 
                                "description": "The exact shell command to execute (e.g., 'ls -la', 'ping -c 3 google.com', 'python --version')."
                            },
                            "timeout": {
                                "type": "integer",
                                "description": "Maximum time in seconds to wait for the command to finish before killing it.",
                                "default": 10
                            }
                        },
                        "required": ["command"]
                    }
                }
            }
        ]

    @property
    def tools(self) -> dict:
        return {
            "get_system_info": self.get_system_info,
            "execute_command": self.execute_command
        }