import sys
import os
import json
import ollama
import requests
from bs4 import BeautifulSoup

# Configuration

OLLAMA_HOST = "http://localhost:11434"
MODEL_NAME = "" # Global variable, starts empty
LIBRARY_URL = "https://ollama.com/search?o=newest"

def print_separator():
    print("=" * 80)

def print_header():
    print("------------------------------------------------------------------------------")
    print("                       OLLAMA PYTHON INTERACTIVE CLI")
    print("------------------------------------------------------------------------------")

def pre_validation():
    """Checks if the Ollama service is reachable."""
    try:
        ollama.list()
        return True
    except Exception:
        return False

def confirm_action(action_name):
    confirm = input(f"⚠️  Are you sure you want to {action_name}? (y/N): ")
    return confirm.lower() == 'y'
    
def fetch_all_remote_data():
    """Helper to scrape all model entries from the current page."""
    try:
        response = requests.get(LIBRARY_URL, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ollama search result items are typically in <li> tags with class 'py-6'
        return soup.find_all('li', class_='py-6') or soup.select('ul > li')
    except Exception as e:
        print(f"❌ Error reaching Ollama website: {e}")
        return []

def list_remote_models():
    """Fetches ALL models from the newest search page and displays them with separators."""
    print(f"\n🌐 Querying live library at: {LIBRARY_URL}")
    print("Please wait, parsing newest models...\n")
    
    try:
        response = requests.get(LIBRARY_URL, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Select the list items that contain model information
        # Ollama typically uses <li> tags with specific classes for search results
        model_items = soup.find_all('li', class_='py-6')
        
        if not model_items:
            # Fallback for different site versions
            model_items = soup.select('ul > li')

        print(f"{'MODEL NAME':<30} | {'FULL DESCRIPTION'}")
        print_separator()

        found_any = False
        for item in model_items:
            # Extract Name
            name_tag = item.find('h2') or item.find('span', class_='text-lg')
            # Extract Description
            desc_tag = item.find('p') or item.find('span', class_='max-w-md')
            
            if name_tag:
                name = name_tag.get_text(strip=True)
                description = desc_tag.get_text(strip=True) if desc_tag else "No description provided."
                
                # Print with a clear line separator after each
                print(f"{name:<30} | {description}")
                print("-" * 80) # Line separator for each model
                found_any = True
        
        if not found_any:
            print("❌ Could not parse any models. The website structure may have changed.")
            
    except Exception as e:
        print(f"❌ Error fetching remote data: {e}")
        
def search_remote_models():
    """Asks user for a string and finds matching models in the remote library."""
    search_query = input("\n🔎 Enter a model name or keyword to search for (e.g., 'mistral' or 'vision'): ").lower()
    
    if not search_query:
        print("Search cancelled (empty query).")
        return

    print(f"📡 Searching library for: '{search_query}'...")
    items = fetch_all_remote_data()
    
    matches = []
    for item in items:
        name_tag = item.find('h2') or item.find('span', class_='text-lg')
        desc_tag = item.find('p') or item.find('span', class_='max-w-md')
        
        if name_tag:
            name = name_tag.get_text(strip=True)
            desc = desc_tag.get_text(strip=True) if desc_tag else ""
            
            # Check if query is in name or description
            if search_query in name.lower() or search_query in desc.lower():
                matches.append((name, desc))

    if matches:
        print(f"\n✅ Found {len(matches)} matching model(s):")
        print(f"{'MODEL NAME':<30} | {'DESCRIPTION'}")
        print_separator()
        for name, desc in matches:
            print(f"{name:<30} | {desc}")
            print_separator()
    else:
        print(f"❌ No models found matching '{search_query}'.")

def list_installed_models():
    """Retrieves and displays local models. Returns a list of names."""
    print("\n📦 Installed Local Models:")
    try:
        response = ollama.list()
        # In the official library, models is a list of objects or dicts
        models_info = response.get('models', [])
        
        if not models_info:
            return []
        
        names = []
        print(f"{'NAME':<30} | {'SIZE (GB)':<10} | {'ID'}")
        print("-" * 65)
        
        for m in models_info:
            # Safely get the name from various possible key formats
            name = m.get('name', m.get('model', 'Unknown'))
            size_gb = m.get('size', 0) / (1024**3)
            mid = m.get('digest', 'N/A')[:12]
            
            names.append(name)
            print(f"{name:<30} | {size_gb:<10.2f} | {mid}")
            
        return names
    except Exception as e:
        print(f"❌ Error listing models: {e}")
        return []

def pull_model():
    model_name = input("Enter the model name to pull (e.g., llama3): ")
    if confirm_action(f"pull '{model_name}'"):
        print(f"📥 Pulling {model_name}...")
        try:
            for progress in ollama.pull(model=model_name, stream=True):
                status = progress.get('status', '')
                print(f"\rStatus: {status: <50}", end="", flush=True)
            print(f"\n✅ {model_name} ready.")
        except Exception as e:
            print(f"\n❌ Pull failed: {e}")

def remove_model():
    model_name = input("Enter the model name to delete: ")
    if confirm_action(f"DELETE '{model_name}'"):
        try:
            ollama.delete(model=model_name)
            print(f"🗑️  Successfully deleted '{model_name}'.")
        except Exception as e:
            print(f"❌ Error: {e}")
            
def ensure_model_exists(model_name):
    """
    Checks if the model exists locally; if not, pulls it from Ollama.
    Returns True if the model is ready.
    """
    print(f"🔍 Checking if '{model_name}' is ready...")
    try:
        response = ollama.list()
        models = [getattr(m, 'model', m.get('model', m.get('name', ''))) for m in response.get('models', [])]
        
        if model_name not in models and f"{model_name}:latest" not in models:
            print(f"📥 Model '{model_name}' not found. Downloading now...")
            for progress in ollama.pull(model=model_name, stream=True):
                status = progress.get('status', '')
                print(f"\rStatus: {status: <50}", end="", flush=True)
            print(f"\n✅ {model_name} downloaded successfully!")
        else:
            print(f"✅ {model_name} is ready to go.")
        return True
    except Exception as e:
        print(f"\n❌ Error validating/pulling model: {e}")
        return False

def select_and_run_model():
    """Function to select an installed model and start a chat session."""
    global MODEL_NAME
    
    # 1. Get the actual list of installed models
    installed_names = list_installed_models()
    
    # FIX: Check if the list actually has content
    if not installed_names:
        print("\n⚠️ No models available to chat with. Please pull a model first.")
        return

    # 2. Ask user for input
    user_choice = input("\nEnter the NAME of the model to chat with (e.g., llama3): ").strip()
    
    if not user_choice:
        return

    # 3. Matching Logic:
    # We check if the input matches exactly OR if the input + ':latest' matches
    matched_model = ""
    if user_choice in installed_names:
        matched_model = user_choice
    elif f"{user_choice}:latest" in installed_names:
        matched_model = f"{user_choice}:latest"

    if matched_model:
        # 4. Set global variable and run
        MODEL_NAME = matched_model
        print(f"✅ Selected: {MODEL_NAME}")
        run_llama()
    else:
        print(f"❌ Error: '{user_choice}' is not in the installed list.")

def run_llama():
    """Starts the chat loop with the selected MODEL_NAME and includes a sub-menu."""
    # Ensure model is ready before starting
    if not ensure_model_exists(MODEL_NAME):
        return

    print(f"\n--- CHAT STARTED WITH {MODEL_NAME} (Type 'exit' to quit) ---")
    
    while True:
        # 1. Get the user's prompt
        prompt = input("\nYou: ").strip()
        
        # Allow exiting directly from the prompt
        if prompt.lower() in ["exit", "quit", "q"]:
            print("Returning to Main Menu...")
            break

        try:
            # 2. Generate and stream the response
            stream = ollama.chat(
                model=MODEL_NAME,
                messages=[{'role': 'user', 'content': prompt}],
                stream=True
            )

            print(f"Llama ({MODEL_NAME}): ", end="", flush=True)
            for chunk in stream:
                content = chunk.get('message', {}).get('content', '')
                print(content, end="", flush=True)
            print() # New line after model finishes
            
            # 3. SUB-MENU PROMPT: Pause and ask for the next action
            while True:
                choice = input("\n[c] Continue chatting | [q] Quit to main menu: ").lower().strip()
                if choice == 'c':
                    break # Breaks the sub-menu loop to stay in the chat loop
                elif choice == 'q':
                    print("Returning to Main Menu...")
                    return # Exits the entire function back to the main menu
                else:
                    print("Invalid input. Please enter 'c' or 'q'.")
            
        except Exception as e:
            print(f"\n⚠️ Error during chat: {e}")
            break

def show_ps():
    print("\n🚀 Currently Loaded in RAM:")
    try:
        running = ollama.ps().get('models', [])
        if not running:
            print("Memory is clear. No models currently running.")
            return
        for m in running:
            name = getattr(m, 'model', m.get('model', m.get('name', 'Unknown')))
            print(f"- {name} (Size: {m['size']/(1024**3):.2f} GB)")
    except Exception as e:
        print(f"❌ Error checking ps: {e}")

def stop_model():
    model_name = input("Enter model name to stop (unload): ")
    if confirm_action(f"STOP '{model_name}'"):
        try:
            # Ollama unloads models when keep_alive is 0
            ollama.generate(model=model_name, keep_alive=0)
            print(f"🛑 Unload signal sent for '{model_name}'.")
        except Exception as e:
            print(f"❌ Error: {e}")
            
def list_ollama_paths():
    """Display default Linux paths for Ollama files."""
    print("\n📂 Ollama Linux Paths:")
    paths = {
        "Binary": "/usr/bin/ollama",
        "Service Config": "/etc/systemd/system/ollama.service",
        "Models (Service)": "/usr/share/ollama/.ollama/models",
        "Models (Manual)": "~/.ollama/models",
        "Public Keys": "/usr/share/ollama/.ollama/id_ed25519.pub",
        "Logs": "/var/log/syslog (via journalctl -u ollama)"
    }
    print(f"{'TYPE':<20} | {'PATH'}")
    print("-" * 60)
    for k, v in paths.items():
        print(f"{k:<20} | {v}")

def show_public_keys():
    """Retrieves the Ollama public key and displays its full system path."""
    # Define potential paths based on Linux installation type
    service_path = "/usr/share/ollama/.ollama/id_ed25519.pub"
    manual_path = os.path.expanduser("~/.ollama/id_ed25519.pub")
    
    # Check which one exists
    active_path = service_path if os.path.exists(service_path) else manual_path

    print(f"\n🔑 Ollama Public Key")
    print(f"📍 Full Path: {active_path}")
    print("-" * 60)

    try:
        with open(active_path, 'r') as f:
            print(f.read().strip())
    except FileNotFoundError:
        print("❌ Public key not found. Ensure Ollama has been initialized.")
    except PermissionError:
        print(f"🔒 Permission denied. To read {active_path}, try running with sudo.")

def list_model_manifests():
    """Lists local manifests, their sizes, and the full paths to their descriptor files."""
    print("\n📄 Model Manifests & Internal Paths:")
    
    # Determine the root manifest directory
    service_root = "/usr/share/ollama/.ollama/models/manifests/registry.ollama.ai/library"
    manual_root = os.path.expanduser("~/.ollama/models/manifests/registry.ollama.ai/library")
    manifest_root = service_root if os.path.exists(service_root) else manual_root

    if not os.path.exists(manifest_root):
        print("❌ Manifest directory not found.")
        return

    print(f"{'MODEL:TAG':<30} | {'SIZE':<10} | {'FULL MANIFEST PATH'}")
    print("-" * 100)
    
    for model_dir in os.listdir(manifest_root):
        model_path = os.path.join(manifest_root, model_dir)
        if os.path.isdir(model_path):
            for tag in os.listdir(model_path):
                file_path = os.path.join(model_path, tag)
                file_size = os.path.getsize(file_path) / 1024 # KB
                
                # Print the model info and the absolute path to the manifest file
                print(f"{model_dir + ':' + tag:<30} | {file_size:.2f} KB | {file_path}")
                
                # Optional: Read the manifest to show the config SHA256 (the actual model ID)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        config_sha = data.get('config', {}).get('digest', 'Unknown')
                        print(f"   ↳ SHA256 Model ID: {config_sha}")
                except:
                    pass

def main():
    while True:
        print_header()
        is_alive = pre_validation()
        
        if not is_alive:
            print("🔴 STATUS: Ollama Service Offline")
            print("   (Ensure 'ollama serve' is running)")
            print("\n1. Retry Connection")
            print("0. Exit")
        else:
            print("\n🟢 STATUS: Ollama Service Online")
            print("\n1. 💬 Run/CHAT with a specific model")
            print("2. 🌐 List ALL Remote Library Models (Live)")
            print("3. 🔎 Search Remote Library Models")
            print("4. 🖥️ List Installed Local Models")
            print("5. 🚀 Show Running Models (ps)")
            print("6. 📥 Pull a New Model")
            print("7. 🗑️  Remove a Model")
            print("8. 🛑 Stop/Unload a Model")
            print("9. 🔑 Show Ollama Public Keys")
            print("10. 📄 List Manifests & Sizes")
            print("11. 📂 Show Linux File Paths")
            print("0. Exit")

        choice = input("\nSelect [0-6]: ")

        if choice == "0": break
        elif choice == "1": select_and_run_model()
        elif choice == "2": list_remote_models()
        elif choice == "3": search_remote_models()
        elif choice == "4": list_installed_models()
        elif choice == "5": show_ps()
        elif choice == "6": pull_model()
        elif choice == "7": remove_model()
        elif choice == "8": stop_model()
        elif choice == "9": show_public_keys()
        elif choice == "10": list_model_manifests()
        elif choice == "11": list_ollama_paths()
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
