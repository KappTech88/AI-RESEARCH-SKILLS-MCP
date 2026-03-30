# AI Research Skills MCP

**91 expert-level AI research skills** as a local MCP server for Claude Desktop.

Built from [Orchestra Research's AI Research Skills](https://github.com/Orchestra-Research/AI-Research-SKILLs) (MIT License).

## Setup (Windows — same pattern as gmail-multi MCP)

### 1. Copy this folder

Put the entire `ai-research-skills-mcp` folder somewhere on your machine, e.g.:

```
D:\.claude\ai-research-skills-mcp\
```

### 2. Run setup

```
cd D:\.claude\ai-research-skills-mcp
setup.bat
```

This creates a Python venv and installs dependencies (`mcp`, `pyyaml`).

### 3. Add to Claude Desktop

Press `Win+R`, type `%APPDATA%\Claude`, open `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "gmail-multi": {
      "command": "C:\\claude-gmail-mcp\\venv\\Scripts\\python.exe",
      "args": ["C:\\claude-gmail-mcp\\server.py"]
    },
    "ai-research-skills": {
      "command": "D:\\.claude\\ai-research-skills-mcp\\venv\\Scripts\\python.exe",
      "args": ["D:\\.claude\\ai-research-skills-mcp\\servers\\server.py"]
    }
  }
}
```

> Use double backslashes `\\` in all paths (required in JSON on Windows).

### 4. Restart Claude Desktop

Fully quit (right-click tray icon → Quit) and reopen.

## Tools Available (8)

| Tool | What it does |
|------|-------------|
| `research_list_categories` | Browse all 22 categories |
| `research_list_skills` | List skills with optional category filter |
| `research_search_skills` | Keyword search |
| `research_read_skill` | Load full expert guidance |
| `research_read_reference` | Read supporting docs/examples/scripts |
| `research_get_metadata` | Quick metadata lookup |
| `research_recommend` | Task-based skill recommendations |
| `research_routing_table` | Full research lifecycle routing table |

## Try It Out

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

## 22 Categories

Model Architecture, Tokenization, Fine-Tuning, Mechanistic Interpretability, Data Processing, Post-Training/RLHF, Safety & Alignment, Distributed Training, Infrastructure, Optimization, Evaluation, Inference & Serving, MLOps, Agents, RAG, Prompt Engineering, Observability, Multimodal, Emerging Techniques, ML Paper Writing, Research Ideation, Autonomous Research Orchestration.
