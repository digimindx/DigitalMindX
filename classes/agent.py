import json
import os
from openai import OpenAI

# ==========================================
# 🤖 AGENT RUNNER
# ==========================================
class Agent:
    """Orchestrates the LLM, manages tool registration, and handles the conversation loop with persistent Markdown memory."""

    def __init__(self, base_url: str, api_key: str, managers: list, workspace_path: str = "./workspace"):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.managers = managers
        
        # Aggregate all schemas and tools from registered managers
        self.tools_schemas = []
        self.available_tools = {}
        
        for manager in self.managers:
            self.tools_schemas.extend(manager.schemas)
            self.available_tools.update(manager.tools)

        # 🌟 Setup Workspace and Memory File Path
        self.workspace_path = os.path.abspath(workspace_path)
        os.makedirs(self.workspace_path, exist_ok=True) # Ensure workspace exists
        self.memory_file = os.path.join(self.workspace_path, "chat_history.md")

        # Initialize conversation memory with the system prompt
        self.messages = [
            {
                "role": "system", 
                "content": "Your name is DigitalMindX and you are a helpful AI Cyber Security Engineer equipped with web search, file management, web scraping, and OS execution tools. "
                           "All file operations are strictly restricted to the './workspace' directory. "
                           "CRITICAL RULE: Before executing ANY OS commands using execute_command, you MUST FIRST use the get_system_info tool to check the current Operating System. "
                           "This ensures you use the correct commands for the specific OS (e.g., use 'dir' for Windows, 'ls' for Linux/macOS). "
                           "Always use available tools when precise calculations, external info, or file actions are needed."
            }
        ]

        # Load previous memory from Markdown file on startup
        self.load_memory()

    def load_memory(self):
        """Loads chat history from the Markdown file inside the workspace folder."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract the JSON data from the markdown code block
                if '```json' in content:
                    json_str = content.split('```json')[1].split('```')[0].strip()
                    loaded_messages = json.loads(json_str)
                    
                    # Validate structure and load
                    if isinstance(loaded_messages, list) and len(loaded_messages) > 0:
                        self.messages = loaded_messages
                        print(f"✅ Loaded {len(self.messages) - 1} previous messages from '{self.memory_file}'")
                    else:
                        print(f"⚠️ '{self.memory_file}' found but invalid format. Starting fresh.")
                else:
                    print(f"⚠️ '{self.memory_file}' found but no JSON block found. Starting fresh.")
            except Exception as e:
                print(f"❌ Error loading memory: {e}. Starting fresh.")
        else:
            print(" No previous memory found. Starting a new chat.")

    def save_memory(self):
        """Saves the current chat history to a human-readable Markdown file inside the workspace."""
        try:
            # Create a beautiful Markdown header
            md_content = f"# DigitalMindX Chat History\n\n"
            md_content += f"> This file stores the conversation history for the DigitalMindX agent.\n"
            md_content += f"> The actual data is stored in the JSON block below to ensure perfect compatibility with the AI model.\n\n"
            
            # Add a human-readable conversation log
            md_content += "## Conversation Log\n\n"
            for msg in self.messages:
                role = msg.get('role', 'unknown').capitalize()
                content = msg.get('content', '')
                if content:
                    # Format content nicely for Markdown
                    clean_content = content.replace('\n', '\n> ')
                    md_content += f"### {role}\n> {clean_content}\n\n"
            
            # Append the raw JSON data inside a code block for perfect reloading
            md_content += "---\n\n## Raw Data (Do Not Edit)\n\n```json\n"
            md_content += json.dumps(self.messages, indent=2, ensure_ascii=False)
            md_content += "\n```\n"
            
            # Write to file inside the workspace
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                f.write(md_content)
                
        except Exception as e:
            print(f"❌ Error saving memory to {self.memory_file}: {e}")

    def clear_memory(self) -> str:
        """Clears the conversation history and resets the memory file."""
        self.messages = [self.messages[0]]
        self.save_memory() # Overwrite the file with just the system prompt
        return "✅ Conversation memory cleared. Starting fresh!"

    def record_direct_command(self, command: str, output: str):
        """Records a direct command execution into the chat history and saves it."""
        # Add the user's command to history
        self.messages.append({"role": "user", "content": f"/command {command}"})
        
        # Add the system's output to history as an assistant response
        self.messages.append({
            "role": "assistant", 
            "content": f"Executed command directly:\n```bash\n{command}\n```\n\n**Output:**\n{output}"
        })

    def search_history(self, query: str) -> str:
        """Searches the chat history (in-memory mirror of the file) for a specific keyword."""
        if not query:
            return "Please provide a search term. Usage: /history <keyword>"
        
        query_lower = query.lower()
        matches = []
        
        # Search through all messages for the keyword (case-insensitive)
        for i, msg in enumerate(self.messages):
            content = msg.get('content', '')
            if content and query_lower in content.lower():
                role = msg.get('role', 'unknown').upper()
                # Truncate very long messages to keep the terminal output clean
                snippet = content[:300] + ("..." if len(content) > 300 else "")
                matches.append(f"Turn {i} [{role}]:\n{snippet}")
                
        if not matches:
            return f"❌ No matches found for '{query}' in the chat history."
        
        # Format and return the results
        separator = "\n\n" + "-"*50 + "\n\n"
        return f" Found {len(matches)} match(es) for '{query}':\n\n" + separator.join(matches)

    def _clean_message(self, message) -> dict:
        """Converts OpenAI API response objects into clean dictionaries for LM Studio."""
        clean_msg = {
            "role": message.role,
            "content": message.content
        }
        
        if hasattr(message, 'tool_calls') and message.tool_calls:
            clean_msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                } for tc in message.tool_calls
            ]
        return clean_msg

    def run(self, user_prompt: str) -> str:
        # Append the new user message to the persistent history
        self.messages.append({"role": "user", "content": user_prompt})
        #print(f"🧑: {user_prompt}\n")

        # Step A: Initial call to local model
        response = self.client.chat.completions.create(
            model="local-model",
            messages=self.messages,
            tools=self.tools_schemas,
            tool_choice="auto"
        )

        response_message = response.choices[0].message
        self.messages.append(self._clean_message(response_message))

        # Step B: Check if the model requested a tool execution
        if response_message.tool_calls:
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                print(f"[Agent Tool Execution] Calling: {function_name}({function_args})")
                
                if function_name in self.available_tools:
                    tool_output = self.available_tools[function_name](**function_args)
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": str(tool_output)
                    })
                else:
                    print(f"[WARNING] Model requested unknown tool: '{function_name}'")
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": "Error: Tool not found."
                    })

            # Step C: Send tool result back to model for final synthesis
            final_response = self.client.chat.completions.create(
                model="local-model",
                messages=self.messages,
                tools=self.tools_schemas,
                tool_choice="auto"
            )
            
            final_message = final_response.choices[0].message
            self.messages.append(self._clean_message(final_message))
            
            # 🌟 Save memory after every successful turn
            self.save_memory()
            return final_message.content
        else:
            # 🌟 Save memory even if no tools were used
            self.save_memory()
            return response_message.content