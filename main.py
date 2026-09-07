from classes.agent import Agent
from classes.filemanager import FileManager
from classes.searchweb import SearchManager

# ==========================================
# 🚀 MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    print("\033[H\033[J", end="")
    # 1. Initialize Managers
    search_manager = SearchManager()
    file_manager = FileManager(workspace_path="./workspace")
    
    print(f"✅ Agent initialized. Workspace locked to: {file_manager.workspace_path}")
    
    # 2. Initialize Agent with Managers
    agent = Agent(
        base_url="http://localhost:1234/v1",
        api_key="lm-studio",
        managers=[search_manager, file_manager]
    )
    
    # 3. Run Interactive Loop
    print("Type '/quit' to exit.\n")
    while True:
        prompt = input("::>> ").strip()
        if prompt.lower() == "/quit": 
            break
        if not prompt:
            continue
            
        result = agent.run(prompt)
        print(f"\nAgent: {result}\n")