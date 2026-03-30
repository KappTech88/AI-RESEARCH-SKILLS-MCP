# AI Research Skills MCP

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-91-green.svg)]()
[![Categories](https://img.shields.io/badge/categories-22-orange.svg)]()

Local MCP server providing 91 expert-level AI research skills for Claude Desktop.

Built from [Orchestra Research's AI Research Skills](https://github.com/Orchestra-Research/AI-Research-SKILLs) library.

## Installation

### Prerequisites

- Python 3.9+
- Claude Desktop

### Setup

> **Run PowerShell as Administrator** (right-click → "Run as administrator")

```powershell
# Create the directory structure (skip if it already exists)
New-Item -ItemType Directory -Force -Path "D:\claude-desktop-connectors\ai-research-skills-mcp"

# Navigate into the project folder
cd D:\claude-desktop-connectors\ai-research-skills-mcp

# Create virtual environment and install dependencies
python -m venv venv
venv\Scripts\activate
pip install mcp pyyaml
```

### Connect to Claude Desktop

Press `Win+R`, type `%APPDATA%\Claude`, open `claude_desktop_config.json` and add to the `mcpServers` section:

```json
"ai-research-skills": {
  "command": "D:\\claude-desktop-connectors\\ai-research-skills-mcp\\venv\\Scripts\\python.exe",
  "args": [
    "D:\\claude-desktop-connectors\\ai-research-skills-mcp\\servers\\server.py"
  ]
}
```

Fully quit Claude Desktop (tray icon → Quit) and reopen.

## Tools (8)

| Tool | Description |
|------|-------------|
| `research_list_categories` | Browse all 22 categories with skill counts |
| `research_list_skills` | List skills, optionally filtered by category |
| `research_search_skills` | Keyword search across names, descriptions, tags |
| `research_read_skill` | Load full expert guidance for any skill |
| `research_read_reference` | Read supporting docs, examples, scripts |
| `research_get_metadata` | Quick metadata without loading full content |
| `research_recommend` | Task-based skill recommendations |
| `research_routing_table` | Full research lifecycle routing table |

## Usage

```
List my AI research skill categories
```

```
What skills should I use to fine-tune a 7B model with RLHF?
```

```
Load the vllm skill
```

```
Search for quantization skills
```

## 22 Categories (91 Skills)

Model Architecture, Tokenization, Fine-Tuning, Mechanistic Interpretability, Data Processing, Post-Training/RLHF, Safety & Alignment, Distributed Training, Infrastructure, Optimization, Evaluation, Inference & Serving, MLOps, Agents, RAG, Prompt Engineering, Observability, Multimodal, Emerging Techniques, ML Paper Writing, Research Ideation, and Autonomous Research Orchestration.

## Project Structure

```
D:\claude-desktop-connectors\ai-research-skills-mcp\
├── servers\
│   └── server.py           ← MCP server (stdio transport)
├── skills\                  ← 91 skill directories
│   ├── autoresearch\
│   ├── vllm\
│   ├── deepspeed\
│   ├── peft\
│   └── ...
├── venv\                    ← Python virtual environment
├── setup.bat                ← Windows setup script
└── README.md
```

## Troubleshooting

### Claude says it can't find the research tools

Fully quit and relaunch Claude Desktop after editing `claude_desktop_config.json`. Verify the paths use double backslashes `\\` and point to the correct location on D: drive.

### Server fails to start

Confirm dependencies are installed in the venv:

```powershell
D:\claude-desktop-connectors\ai-research-skills-mcp\venv\Scripts\python.exe -c "import mcp, yaml; print('OK')"
```

### Skills not loading

The server scans `skills/` relative to its own location. Confirm the `skills` folder is present alongside the `servers` folder.

## License

Skills content: MIT (Orchestra Research). Plugin packaging: MIT.
