import os

# ==========================================
# 📁 FILE MANAGER
# ==========================================
class FileManager:
    """Handles all file system operations within a secure sandbox."""

    def __init__(self, workspace_path: str = "./workspace"):
        self.workspace_path = os.path.abspath(workspace_path)
        os.makedirs(self.workspace_path, exist_ok=True)

    def _ensure_safe_path(self, file_path: str) -> str:
        """Ensures the requested path is strictly inside the safe workspace."""
        abs_path = os.path.abspath(os.path.join(self.workspace_path, file_path))
        # commonpath prevents directory traversal attacks (e.g., "../../../")
        if os.path.commonpath([abs_path, self.workspace_path]) != self.workspace_path:
            raise ValueError(f"Access denied: Path '{file_path}' is outside the safe workspace.")
        return abs_path

    def create_file(self, file_path: str, content: str) -> str:
        try:
            safe_path = self._ensure_safe_path(file_path)
            if os.path.exists(safe_path):
                return f"Error: File '{file_path}' already exists. Use edit_file to modify it."
            
            dir_name = os.path.dirname(safe_path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            
            with open(safe_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully created file: {file_path}"
        except Exception as e:
            return f"Error creating file: {str(e)}"

    def read_file(self, file_path: str) -> str:
        try:
            safe_path = self._ensure_safe_path(file_path)
            if not os.path.exists(safe_path):
                return f"Error: File '{file_path}' does not exist."
            with open(safe_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def edit_file(self, file_path: str, content: str) -> str:
        try:
            safe_path = self._ensure_safe_path(file_path)
            if not os.path.exists(safe_path):
                return f"Error: File '{file_path}' does not exist. Use create_file first."
            with open(safe_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully overwrote/edited file: {file_path}"
        except Exception as e:
            return f"Error editing file: {str(e)}"

    def delete_file(self, file_path: str) -> str:
        try:
            safe_path = self._ensure_safe_path(file_path)
            if not os.path.exists(safe_path):
                return f"Error: File '{file_path}' does not exist."
            os.remove(safe_path)
            return f"Successfully deleted file: {file_path}"
        except Exception as e:
            return f"Error deleting file: {str(e)}"

    def list_files(self, directory_path: str) -> str:
        try:
            safe_path = self._ensure_safe_path(directory_path)
            if not os.path.isdir(safe_path):
                return f"Error: Directory '{directory_path}' does not exist."
            
            items = os.listdir(safe_path)
            if not items:
                return f"Directory '{directory_path}' is empty."
            
            result = []
            for item in items:
                item_path = os.path.join(safe_path, item)
                if os.path.isdir(item_path):
                    result.append(f"📁 [DIR]  {item}")
                else:
                    result.append(f"📄 [FILE] {item}")
            
            return f"Contents of '{directory_path}':\n" + "\n".join(result)
        except Exception as e:
            return f"Error listing files: {str(e)}"

    @property
    def schemas(self) -> list:
        return [
            {
                "type": "function",
                "function": {
                    "name": "create_file",
                    "description": "Creates a new file with the specified content. Fails if the file already exists.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "The relative path and name of the file (e.g., 'notes.txt' or 'data/info.json')."},
                            "content": {"type": "string", "description": "The text content to write into the new file."}
                        },
                        "required": ["file_path", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Reads and returns the full text content of an existing file.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "The relative path and name of the file to read."}
                        },
                        "required": ["file_path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "edit_file",
                    "description": "Overwrites an existing file with new content. (Tip: Use read_file first to know the current content).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "The relative path and name of the file to edit."},
                            "content": {"type": "string", "description": "The complete new text content to write into the file."}
                        },
                        "required": ["file_path", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_file",
                    "description": "Permanently deletes a file.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "The relative path and name of the file to delete."}
                        },
                        "required": ["file_path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_files",
                    "description": "Lists all files and directories in a given path to help find files.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory_path": {"type": "string", "description": "The relative path of the directory to list (use '.' for the root workspace)."}
                        },
                        "required": ["directory_path"]
                    }
                }
            }
        ]

    @property
    def tools(self) -> dict:
        return {
            "create_file": self.create_file,
            "read_file": self.read_file,
            "edit_file": self.edit_file,
            "delete_file": self.delete_file,
            "list_files": self.list_files
        }

