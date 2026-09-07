from classes.agent import Agent
from classes.filemanager import FileManager
from classes.searchweb import SearchManager
from classes.Executer import Executer
from classes.webscrapper import WebScraper

# ==========================================
# 🚀 MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    print("\033[H\033[J", end="")
    print("DigitalMindX Agent!\n")
    
    # 1. Initialize Managers
    search_manager = SearchManager()
    file_manager = FileManager(workspace_path="./workspace")
    executer_manager = Executer()
    scraper_manager = WebScraper()
    
    print(f"✅ Agent initialized. Workspace locked to: {file_manager.workspace_path}")
    
    # 2. Initialize Agent with Managers
    agent = Agent(
        base_url="http://localhost:1234/v1",
        api_key="lm-studio",
        managers=[search_manager, file_manager, executer_manager, scraper_manager]
    )
    
    # 3. Run Interactive Loop
    print("Type '/quit' to exit, '/clear' to reset memory, '/cls' to clear screen.\n")
    
    while True:
        prompt = input("::>> ").strip()
        
        if prompt.lower() == "/quit": 
            break
            
        elif prompt.lower() == "/cls":
            print("\033[H\033[J", end="")
            continue
            
        elif prompt.lower() == "/clear":
            print(agent.clear_memory())
            continue
            
        elif not prompt:
            print("I have nothing to do!\n")
            continue
        
        # Run the agent and get response
        result = agent.run(prompt)
        print(f"\nAgent: {result}\n")