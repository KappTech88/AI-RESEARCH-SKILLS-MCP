"""
AI Research Skills MCP Server
91 expert-level AI research skills for Claude Desktop.
Uses stdio transport — same pattern as gmail-multi MCP.
"""

import json, re, yaml, asyncio
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

# ---------------------------------------------------------------------------
# Paths & Index
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent.parent
SKILLS_DIR = BASE_DIR / "skills"

CATEGORY_MAP = {
    "autoresearch": "Autonomous Research Orchestration",
    "litgpt": "Model Architecture", "mamba": "Model Architecture",
    "nanogpt": "Model Architecture", "rwkv": "Model Architecture",
    "torchtitan": "Model Architecture",
    "huggingface-tokenizers": "Tokenization", "sentencepiece": "Tokenization",
    "axolotl": "Fine-Tuning", "llama-factory": "Fine-Tuning",
    "peft": "Fine-Tuning", "unsloth": "Fine-Tuning",
    "nnsight": "Mechanistic Interpretability", "pyvene": "Mechanistic Interpretability",
    "saelens": "Mechanistic Interpretability", "transformer-lens": "Mechanistic Interpretability",
    "nemo-curator": "Data Processing", "ray-data": "Data Processing",
    "grpo-rl-training": "Post-Training / RLHF", "miles": "Post-Training / RLHF",
    "openrlhf": "Post-Training / RLHF", "simpo": "Post-Training / RLHF",
    "slime": "Post-Training / RLHF", "torchforge": "Post-Training / RLHF",
    "trl-fine-tuning": "Post-Training / RLHF", "verl": "Post-Training / RLHF",
    "constitutional-ai": "Safety & Alignment", "llamaguard": "Safety & Alignment",
    "nemo-guardrails": "Safety & Alignment", "prompt-guard": "Safety & Alignment",
    "accelerate": "Distributed Training", "deepspeed": "Distributed Training",
    "megatron-core": "Distributed Training", "pytorch-fsdp2": "Distributed Training",
    "pytorch-lightning": "Distributed Training", "ray-train": "Distributed Training",
    "lambda-labs": "Infrastructure", "modal": "Infrastructure", "skypilot": "Infrastructure",
    "awq": "Optimization", "bitsandbytes": "Optimization",
    "flash-attention": "Optimization", "gguf": "Optimization",
    "gptq": "Optimization", "hqq": "Optimization",
    "bigcode-evaluation-harness": "Evaluation",
    "lm-evaluation-harness": "Evaluation", "nemo-evaluator": "Evaluation",
    "llama-cpp": "Inference & Serving", "sglang": "Inference & Serving",
    "tensorrt-llm": "Inference & Serving", "vllm": "Inference & Serving",
    "mlflow": "MLOps", "swanlab": "MLOps", "tensorboard": "MLOps",
    "weights-and-biases": "MLOps",
    "autogpt": "Agents", "crewai": "Agents",
    "langchain": "Agents", "llamaindex": "Agents",
    "chroma": "RAG", "faiss": "RAG", "pinecone": "RAG",
    "qdrant": "RAG", "sentence-transformers": "RAG",
    "dspy": "Prompt Engineering", "guidance": "Prompt Engineering",
    "instructor": "Prompt Engineering", "outlines": "Prompt Engineering",
    "langsmith": "Observability", "phoenix": "Observability",
    "audiocraft": "Multimodal", "blip-2": "Multimodal", "clip": "Multimodal",
    "cosmos-policy": "Multimodal", "llava": "Multimodal",
    "openpi": "Multimodal", "openvla-oft": "Multimodal",
    "segment-anything": "Multimodal", "stable-diffusion": "Multimodal",
    "whisper": "Multimodal",
    "knowledge-distillation": "Emerging Techniques",
    "long-context": "Emerging Techniques", "model-merging": "Emerging Techniques",
    "model-pruning": "Emerging Techniques", "moe-training": "Emerging Techniques",
    "speculative-decoding": "Emerging Techniques",
    "academic-plotting": "ML Paper Writing", "ml-paper-writing": "ML Paper Writing",
    "brainstorming-research-ideas": "Research Ideation",
    "creative-thinking-for-research": "Research Ideation",
}

def parse_frontmatter(text):
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    try:
        return yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return {}

def get_body(text):
    if not text.startswith("---"):
        return text
    parts = text.split("---", 2)
    return parts[2].strip() if len(parts) >= 3 else text

def build_index():
    index = {}
    if not SKILLS_DIR.exists():
        return index
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue
        text = skill_md.read_text(encoding="utf-8", errors="replace")
        meta = parse_frontmatter(text)
        refs = sorted(f.name for f in (skill_dir / "references").iterdir() if f.is_file()) if (skill_dir / "references").is_dir() else []
        examples = sorted(f.name for f in (skill_dir / "examples").iterdir() if f.is_file()) if (skill_dir / "examples").is_dir() else []
        scripts = sorted(f.name for f in (skill_dir / "scripts").iterdir() if f.is_file()) if (skill_dir / "scripts").is_dir() else []
        templates = sorted(f.name for f in (skill_dir / "templates").iterdir() if f.is_file()) if (skill_dir / "templates").is_dir() else []
        index[skill_dir.name] = {
            "name": meta.get("name", skill_dir.name),
            "description": meta.get("description", ""),
            "tags": meta.get("tags", []),
            "version": meta.get("version", ""),
            "dependencies": meta.get("dependencies", []),
            "references": refs, "examples": examples,
            "scripts": scripts, "templates": templates,
            "lines": len(text.splitlines()),
        }
    return index

SKILL_INDEX = build_index()

# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------
server = Server("ai-research-skills")

@server.list_tools()
async def list_tools():
    return [
        types.Tool(
            name="research_list_categories",
            description="List all 22 AI research skill categories with skill counts. Start here to explore.",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="research_list_skills",
            description=f"List skills ({len(SKILL_INDEX)} total), optionally filtered by category.",
            inputSchema={"type": "object", "properties": {
                "category": {"type": "string", "description": "Category filter (e.g. 'Fine-Tuning', 'RAG', 'Optimization'). Leave empty for all."}
            }}
        ),
        types.Tool(
            name="research_search_skills",
            description="Search skills by keyword across names, descriptions, and tags.",
            inputSchema={"type": "object", "properties": {
                "query": {"type": "string", "description": "Search term (e.g. 'quantization', 'RLHF', 'vllm')"}
            }, "required": ["query"]}
        ),
        types.Tool(
            name="research_read_skill",
            description="Load the full expert guidance (SKILL.md) for a specific skill.",
            inputSchema={"type": "object", "properties": {
                "skill_slug": {"type": "string", "description": "Skill directory name (e.g. 'vllm', 'deepspeed', 'autoresearch')"}
            }, "required": ["skill_slug"]}
        ),
        types.Tool(
            name="research_read_reference",
            description="Read a reference, example, script, or template file from a skill.",
            inputSchema={"type": "object", "properties": {
                "skill_slug": {"type": "string", "description": "Skill directory name"},
                "filename": {"type": "string", "description": "File to read from references/, examples/, scripts/, or templates/"}
            }, "required": ["skill_slug", "filename"]}
        ),
        types.Tool(
            name="research_get_metadata",
            description="Get quick metadata for a skill (tags, deps, file listings) without loading full content.",
            inputSchema={"type": "object", "properties": {
                "skill_slug": {"type": "string", "description": "Skill directory name"}
            }, "required": ["skill_slug"]}
        ),
        types.Tool(
            name="research_recommend",
            description="Recommend the best skills for a research task description.",
            inputSchema={"type": "object", "properties": {
                "task": {"type": "string", "description": "Describe your research task (e.g. 'fine-tune 7B model with RLHF')"}
            }, "required": ["task"]}
        ),
        types.Tool(
            name="research_routing_table",
            description="Show the complete routing table mapping research activities to skills.",
            inputSchema={"type": "object", "properties": {}}
        ),
    ]

@server.call_tool()
async def call_tool(name, arguments):
    # --- list_categories ---
    if name == "research_list_categories":
        cats = {}
        for slug, info in SKILL_INDEX.items():
            cat = CATEGORY_MAP.get(slug, "Uncategorized")
            cats.setdefault(cat, []).append(info["name"])
        lines = [f"AI Research Skills — {len(SKILL_INDEX)} skills across {len(cats)} categories\n"]
        for cat in sorted(cats):
            skills = sorted(cats[cat])
            lines.append(f"## {cat} ({len(skills)})")
            for s in skills:
                lines.append(f"  - {s}")
            lines.append("")
        return [types.TextContent(type="text", text="\n".join(lines))]

    # --- list_skills ---
    elif name == "research_list_skills":
        category = arguments.get("category", "")
        results = []
        for slug, info in sorted(SKILL_INDEX.items()):
            cat = CATEGORY_MAP.get(slug, "Uncategorized")
            if category and category.lower() not in cat.lower():
                continue
            results.append({
                "slug": slug, "name": info["name"], "category": cat,
                "description": info["description"][:200],
                "tags": info["tags"], "version": info["version"],
            })
        if not results:
            return [types.TextContent(type="text", text=f"No skills for category '{category}'. Use research_list_categories to see options.")]
        return [types.TextContent(type="text", text=json.dumps(results, indent=2))]

    # --- search_skills ---
    elif name == "research_search_skills":
        query = arguments["query"].lower()
        matches = []
        for slug, info in SKILL_INDEX.items():
            searchable = f"{info['name']} {info['description']} {' '.join(info['tags'])} {slug}".lower()
            if query in searchable:
                score = 100 if query == slug else 80 if query in slug else 60 if query in info["name"].lower() else 40
                matches.append((score, slug, info))
        matches.sort(key=lambda x: -x[0])
        if not matches:
            return [types.TextContent(type="text", text=f"No skills matching '{query}'.")]
        lines = [f"Search results for '{query}' — {len(matches)} matches\n"]
        for score, slug, info in matches[:15]:
            cat = CATEGORY_MAP.get(slug, "Uncategorized")
            lines.append(f"**{info['name']}** (`{slug}`) — {cat}")
            lines.append(f"  {info['description'][:150]}\n")
        return [types.TextContent(type="text", text="\n".join(lines))]

    # --- read_skill ---
    elif name == "research_read_skill":
        slug = arguments["skill_slug"]
        skill_md = SKILLS_DIR / slug / "SKILL.md"
        if not skill_md.is_file():
            candidates = [s for s in SKILL_INDEX if slug.lower() in s.lower()]
            if candidates:
                return [types.TextContent(type="text", text=f"Skill '{slug}' not found. Did you mean: {', '.join(candidates)}?")]
            return [types.TextContent(type="text", text=f"Skill '{slug}' not found.")]
        text = skill_md.read_text(encoding="utf-8", errors="replace")
        info = SKILL_INDEX.get(slug, {})
        header = f"Skill: {info.get('name', slug)} | Category: {CATEGORY_MAP.get(slug, '?')}\n"
        if info.get("references"):
            header += f"References: {', '.join(info['references'])}\n"
        if info.get("examples"):
            header += f"Examples: {', '.join(info['examples'])}\n"
        if info.get("scripts"):
            header += f"Scripts: {', '.join(info['scripts'])}\n"
        if info.get("templates"):
            header += f"Templates: {', '.join(info['templates'])}\n"
        header += "---\n\n"
        return [types.TextContent(type="text", text=header + get_body(text))]

    # --- read_reference ---
    elif name == "research_read_reference":
        slug = arguments["skill_slug"]
        fname = arguments["filename"]
        skill_dir = SKILLS_DIR / slug
        if not skill_dir.is_dir():
            return [types.TextContent(type="text", text=f"Skill '{slug}' not found.")]
        for subdir in ["references", "examples", "scripts", "templates"]:
            fpath = skill_dir / subdir / fname
            if fpath.is_file():
                return [types.TextContent(type="text", text=f"# {slug}/{subdir}/{fname}\n\n" + fpath.read_text(encoding="utf-8", errors="replace"))]
        fpath = skill_dir / fname
        if fpath.is_file():
            return [types.TextContent(type="text", text=f"# {slug}/{fname}\n\n" + fpath.read_text(encoding="utf-8", errors="replace"))]
        available = []
        for subdir in ["references", "examples", "scripts", "templates"]:
            d = skill_dir / subdir
            if d.is_dir():
                available.extend(f"{subdir}/{f.name}" for f in d.iterdir() if f.is_file())
        if available:
            return [types.TextContent(type="text", text=f"'{fname}' not found. Available:\n" + "\n".join(f"  - {a}" for a in available))]
        return [types.TextContent(type="text", text=f"'{fname}' not found and no supporting files exist for '{slug}'.")]

    # --- get_metadata ---
    elif name == "research_get_metadata":
        slug = arguments["skill_slug"]
        info = SKILL_INDEX.get(slug)
        if not info:
            candidates = [s for s in SKILL_INDEX if slug.lower() in s.lower()]
            return [types.TextContent(type="text", text=f"Not found. Did you mean: {', '.join(candidates)}?" if candidates else f"'{slug}' not found.")]
        meta = {
            "slug": slug, "name": info["name"],
            "category": CATEGORY_MAP.get(slug, "Uncategorized"),
            "description": info["description"], "version": info["version"],
            "tags": info["tags"], "dependencies": info["dependencies"],
            "lines": info["lines"],
            "files": {"references": info["references"], "examples": info["examples"],
                      "scripts": info["scripts"], "templates": info["templates"]},
        }
        return [types.TextContent(type="text", text=json.dumps(meta, indent=2))]

    # --- recommend ---
    elif name == "research_recommend":
        task = arguments["task"].lower()
        keywords = set(re.findall(r'\b[a-z]{3,}\b', task))
        patterns = {
            "fine-tun": ["axolotl", "llama-factory", "peft", "unsloth", "trl-fine-tuning"],
            "rlhf": ["trl-fine-tuning", "grpo-rl-training", "openrlhf", "simpo", "verl"],
            "train": ["accelerate", "deepspeed", "pytorch-fsdp2", "pytorch-lightning", "ray-train", "megatron-core"],
            "quantiz": ["awq", "bitsandbytes", "gptq", "gguf", "hqq"],
            "infer": ["vllm", "tensorrt-llm", "llama-cpp", "sglang"],
            "serv": ["vllm", "tensorrt-llm", "sglang"],
            "deploy": ["vllm", "modal", "skypilot", "lambda-labs"],
            "eval": ["lm-evaluation-harness", "bigcode-evaluation-harness", "nemo-evaluator"],
            "interpret": ["transformer-lens", "saelens", "nnsight", "pyvene"],
            "rag": ["chroma", "faiss", "pinecone", "qdrant", "sentence-transformers"],
            "agent": ["langchain", "llamaindex", "crewai", "autogpt"],
            "paper": ["ml-paper-writing", "academic-plotting"],
            "safety": ["constitutional-ai", "llamaguard", "nemo-guardrails", "prompt-guard"],
            "track": ["weights-and-biases", "mlflow", "tensorboard"],
            "data": ["ray-data", "nemo-curator"],
            "multimodal": ["clip", "whisper", "llava", "stable-diffusion", "segment-anything", "blip-2", "audiocraft"],
            "image": ["clip", "stable-diffusion", "segment-anything", "blip-2", "llava"],
            "audio": ["whisper", "audiocraft"],
            "optim": ["flash-attention", "bitsandbytes", "awq", "gptq", "gguf", "hqq"],
            "prompt": ["dspy", "instructor", "guidance", "outlines"],
            "token": ["huggingface-tokenizers", "sentencepiece"],
            "research": ["autoresearch", "brainstorming-research-ideas"],
            "idea": ["brainstorming-research-ideas", "creative-thinking-for-research"],
        }
        scored = []
        for slug, info in SKILL_INDEX.items():
            score = 0
            searchable = f"{info['name']} {info['description']} {' '.join(info['tags'])} {slug}".lower()
            for kw in keywords:
                if kw in searchable: score += 5
                if kw in slug: score += 10
            for pat, boost_slugs in patterns.items():
                if pat in task and slug in boost_slugs: score += 30
            if score > 0:
                scored.append((score, slug, info))
        scored.sort(key=lambda x: -x[0])
        if not scored:
            return [types.TextContent(type="text", text="No matches. Try research_list_categories or research_search_skills.")]
        lines = [f"Recommended skills for: {arguments['task']}\n"]
        for i, (_, slug, info) in enumerate(scored[:10], 1):
            cat = CATEGORY_MAP.get(slug, "?")
            lines.append(f"{i}. **{info['name']}** (`{slug}`) — {cat}")
            lines.append(f"   {info['description'][:180]}\n")
        lines.append("Use research_read_skill(slug) to load full guidance.")
        return [types.TextContent(type="text", text="\n".join(lines))]

    # --- routing_table ---
    elif name == "research_routing_table":
        routing = {
            "Literature & Ideation": ["brainstorming-research-ideas", "creative-thinking-for-research"],
            "Data Preparation": ["ray-data", "nemo-curator", "huggingface-tokenizers", "sentencepiece"],
            "Model Architecture": ["litgpt", "nanogpt", "mamba", "rwkv", "torchtitan"],
            "Fine-Tuning": ["axolotl", "llama-factory", "peft", "unsloth"],
            "Post-Training / RLHF": ["trl-fine-tuning", "grpo-rl-training", "openrlhf", "simpo", "verl", "slime", "miles", "torchforge"],
            "Distributed Training": ["deepspeed", "pytorch-fsdp2", "megatron-core", "accelerate", "pytorch-lightning", "ray-train"],
            "Optimization": ["flash-attention", "bitsandbytes", "gptq", "awq", "hqq", "gguf"],
            "Evaluation": ["lm-evaluation-harness", "bigcode-evaluation-harness", "nemo-evaluator"],
            "Inference & Serving": ["vllm", "tensorrt-llm", "llama-cpp", "sglang"],
            "Safety": ["constitutional-ai", "llamaguard", "nemo-guardrails", "prompt-guard"],
            "Interpretability": ["transformer-lens", "saelens", "nnsight", "pyvene"],
            "RAG": ["chroma", "faiss", "pinecone", "qdrant", "sentence-transformers"],
            "Agents": ["langchain", "llamaindex", "crewai", "autogpt"],
            "Prompt Engineering": ["dspy", "instructor", "guidance", "outlines"],
            "MLOps": ["weights-and-biases", "mlflow", "tensorboard", "swanlab"],
            "Observability": ["langsmith", "phoenix"],
            "Multimodal": ["clip", "whisper", "llava", "stable-diffusion", "segment-anything", "blip-2", "audiocraft", "cosmos-policy", "openpi", "openvla-oft"],
            "Emerging Techniques": ["moe-training", "model-merging", "long-context", "speculative-decoding", "knowledge-distillation", "model-pruning"],
            "Infrastructure": ["modal", "skypilot", "lambda-labs"],
            "Paper Writing": ["ml-paper-writing", "academic-plotting"],
            "Full Lifecycle": ["autoresearch"],
        }
        lines = ["AI Research Skills — Complete Routing Table\n"]
        for activity, slugs in routing.items():
            lines.append(f"## {activity}")
            for s in slugs:
                info = SKILL_INDEX.get(s, {})
                lines.append(f"  - `{s}` — {info.get('name', s)}")
            lines.append("")
        return [types.TextContent(type="text", text="\n".join(lines))]

    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

# ---------------------------------------------------------------------------
# Entry point (stdio — same as gmail-multi MCP)
# ---------------------------------------------------------------------------
async def main():
    async with stdio_server() as (r, w):
        await server.run(r, w, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
