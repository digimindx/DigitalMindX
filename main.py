import os
import json
from classes.agent import Agent
from classes.filemanager import FileManager
from classes.searchweb import SearchManager
from classes.Executer import Executer
from classes.webscrapper import WebScraper

# ==========================================
# ⚙️ CONFIGURATION MANAGEMENT
# ==========================================
def load_or_create_config():
    """Loads config from ~/.digitalmindx/config.json or creates it with defaults."""
    # Resolves to C:\Users\{username} on Windows, /Users/{username} on Mac/Linux
    home_dir = os.path.expanduser("~")
    config_dir = os.path.join(home_dir, ".digitalmindx")
    config_file = os.path.join(config_dir, "config.json")
    
    default_config = {
        "URL": "http://localhost:1234/v1",
        "API": "lm-studio"
    }
    
    # 1. Create the .digitalmindx folder if it doesn't exist
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
        print(f"📁 Created configuration directory: {config_dir}")
        
    # 2. Create config.json with default settings if it doesn't exist
    if not os.path.exists(config_file):
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4)
        print(f"🆕 Created default configuration file at: {config_file}")
        return default_config
    else:
        # 3. Load existing config if it does exist
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Ensure required keys exist, fallback to defaults if the user deleted them
            config["URL"] = config.get("URL", default_config["URL"])
            config["API"] = config.get("API", default_config["API"])
            print(f"✅ Loaded configuration from: {config_file}")
            return config
            
        except Exception as e:
            print(f"⚠️ Error reading config file: {e}. Recreating with defaults.")
            # Backup corrupted file logic could go here, but recreating is safest
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4)
            return default_config


def print_intro():
    """Clears the screen and prints a stylish intro box."""
    print("\033[H\033[J", end="")  # Clear screen
    
    # Box dimensions and styling
    width = 42
    print("╔" + "═" * width + "╗")
    print("║" + " " * width + "║")
    print("║" + " DIGITALMINDX AGENT ".center(width) + "║")
    print("║" + "Powered by Local LLM & Tools".center(width) + "║")
    print("║" + "Developed By:".center(width) + "║")
    print("║" + " A.elAzeez Mabrouk".center(width) + "║")
    print("║" + " " * width + "║")
    print("╚" + "═" * width + "╝")
    print() # Empty line for spacing


def showHelp():
    print("/exit, /quit             : Terminate Agent.")
    print("/command <command>       : Execute direct command in the current path.")
    print("/?                       : Show this help.")
    print("/cls                     : Clean screen.")
    print("/clear                   : Clear memory.")
# ==========================================
# 🚀 MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    print_intro()
    
    # 1. Load or Create Configuration
    config = load_or_create_config()
    
    # 2. Initialize Managers
    search_manager = SearchManager()
    file_manager = FileManager(workspace_path="./workspace")
    executer_manager = Executer()
    scraper_manager = WebScraper()
    
    print(f"✅ Agent initialized. Workspace locked to: {file_manager.workspace_path}")
    
    # 3. Initialize Agent with Managers AND Dynamic Config from JSON
    agent = Agent(
        base_url=config["URL"],
        api_key=config["API"],
        managers=[search_manager, file_manager, executer_manager, scraper_manager]
    )
    
    # 4. Run Interactive Loop
    print("Type '/quit' to exit, '/clear' to reset memory, '/cls' to clear screen.")
    print("Type '/command <cmd>' to execute shell commands directly without AI.\n")
    
    while True:
        prompt = input("->> ").strip()
        
        if prompt.lower() == "/quit" or prompt.lower() == "/exit": 
            break
            
        elif prompt.lower() == "/cls":
            print("\033[H\033[J", end="")
            continue
            
        elif prompt.lower() == "/clear":
            print(agent.clear_memory())
            continue

        elif prompt.lower() == "/?":
            print("")
            
        # Direct Command Execution (Bypasses AI)
        elif prompt.lower().startswith("/command "):
            cmd_to_run = prompt[9:].strip() 
            if cmd_to_run:
                print(f"\n[Direct Execution] Running: {cmd_to_run}")
                result = executer_manager.execute_command(cmd_to_run)
                print(f"\nOutput:\n{result}\n")
            else:
                print("⚠️ Please provide a command. Usage: /command <your_command>\n")
            continue
            
        elif not prompt:
            print("I have nothing to do!\n")
            continue
        
        # Run the agent and get response
        result = agent.run(prompt)
        print(f"\nAgent: {result}\n")