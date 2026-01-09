# Program developed by Gustavo Wydler Azuaga - 2026-01-09

# OLLAMA PYTHON INTERACTIVE CLI

A powerful, all-in-one terminal manager for **Ollama**. This tool provides a streamlined interface to manage local LLMs, explore the remote library, and conduct streaming chat sessions directly from your Linux console.

## 🚀 Features

### 💬 Interactive Chat & Run
* **Model Selector:** Choose from your installed models to start a session.
* **Auto-Pull:** Automatically downloads the model if it is missing.
* **Streamed Responses:** Real-time token generation for a natural chat experience.
* **Session Control:** Sub-menu during chat allows you to continue [c] or return to menu [q].

### 🔍 Remote Library Discovery
* **Live Scraper:** Queries `ollama.com` directly to fetch the newest models.
* **Search Function:** Filter the remote library by name or keyword (e.g., "mistral", "vision", "coding").
* **Full Descriptions:** View the complete model details without truncation.

### 💾 Local Management
* **List Models:** View installed models, their sizes, and IDs.
* **Process Monitor (ps):** See which models are currently loaded in your system's RAM/VRAM.
* **Storage Control:** Pull new models or safely delete existing ones with confirmation prompts.
* **Unload/Stop:** Force a model to exit memory (RAM) using the `keep_alive: 0` signal.

### 🔑 System & Admin Tools
* **Public Keys:** View your Ollama public key and its full system path for cloud linking.
* **Manifest Inspector:** View model metadata files, sizes, and their exact SHA256 file paths.
* **Path Navigator:** Quick reference for all default Ollama Linux directory paths.

## 🛠️ Requirements

- **Python:** 3.x
- **Ollama:** Service must be running (`ollama serve`)
- **Libraries:**
  - `ollama` (Official Python library)
  - `requests` (For web queries)
  - `beautifulsoup4` (For library scraping)

## 🚀 Getting Started

To run the program, navigate to your cloned repository and execute the script using Python 3.13:

```bash
# Navigate to the cloned project directory
cd ollama_python_linux_management_cli

# Run the interactive CLI
python3.13 ollama_cli.py
```

## 📂 Linux File Paths Supported
The tool is optimized for Linux environments, tracking files in:
* **Service path:** `/usr/share/ollama/.ollama/`
* **User path:** `~/.ollama/`

## 🕹️ Menu Interface

| Option | Icon | Action |
| :--- | :--- | :--- |
| **1** | 💬 | Select and Chat with a model |
| **2** | 🌐 | List all newest models from Ollama Library |
| **3** | 🔍 | Search for a specific model online |
| **4** | 💾 | List installed local models |
| **5** | 🚀 | Show models currently running in memory |
| **6** | 📥 | Pull a new model |
| **7** | 🗑️ | Remove/Delete a model |
| **8** | 🛑 | Stop/Unload a model from RAM |
| **9** | 🔑 | Show Public Keys and File Paths |
| **10** | 📄 | List Manifests, Sizes, and SHA256 Paths |
| **11** | 📂 | Show all Ollama Linux File Paths |

## ⚠️ Pre-Validation
The tool includes a safety gate that pings the Ollama API before every operation. If the service is offline, the menu will shift to "Offline Mode" and prompt you to start `ollama serve`.
