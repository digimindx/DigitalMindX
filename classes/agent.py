from openai import OpenAI
import json


# ==========================================
# 🤖 AGENT RUNNER
# ==========================================
class Agent:
    """Orchestrates the LLM, manages tool registration, and handles the conversation loop."""

    def __init__(self, base_url: str, api_key: str, managers: list):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.managers = managers
        
        # Aggregate all schemas and tools from registered managers
        self.tools_schemas = []
        self.available_tools = {}
        
        for manager in self.managers:
            self.tools_schemas.extend(manager.schemas)
            self.available_tools.update(manager.tools)

    def run(self, user_prompt: str) -> str:
        messages = [
            {
                "role": "system", 
                "content": "You are a helpful AI assistant equipped with web search and file management tools. "
                           "All file operations are strictly restricted to the './workspace' directory. "
                           "Always use available tools when precise calculations, external info, or file actions are needed."
            },
            {"role": "user", "content": user_prompt}
        ]

        print(f"User: {user_prompt}\n")

        # Step A: Initial call to local model
        response = self.client.chat.completions.create(
            model="local-model",
            messages=messages,
            tools=self.tools_schemas,
            tool_choice="auto"
        )

        response_message = response.choices[0].message
        messages.append(response_message)

        # Step B: Check if the model requested a tool execution
        if response_message.tool_calls:
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                print(f"[Agent Tool Execution] Calling: {function_name}({function_args})")
                
                if function_name in self.available_tools:
                    tool_output = self.available_tools[function_name](**function_args)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": str(tool_output)
                    })
                else:
                    print(f"[WARNING] Model requested unknown tool: '{function_name}'")
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": "Error: Tool not found."
                    })

            # Step C: Send tool result back to model for final synthesis
            final_response = self.client.chat.completions.create(
                model="local-model",
                messages=messages,
                tools=self.tools_schemas, # Keep tools in context for potential chaining
                tool_choice="auto"
            )
            return final_response.choices[0].message.content
        else:
            return response_message.content

