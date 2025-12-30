Got it — `PocketFlow` is an external library, not your own. Here's the updated **English README** with `uv` for dependency management and a corrected attribution:

---

# 🎲 TabletopMagnat

**TabletopMagnat** is an asynchronous LLM-powered application designed to help users understand tabletop game rules. It uses multiple expert agents working in parallel to break down, classify, and respond to user queries about board and tabletop games.

---

## 🧠 Architecture

The app is built on an **asynchronous pipeline** using the [PocketFlow](https://github.com/the-pocket/PocketFlow) framework. Key components:

- **Security Node** — validates user input for safety.
- **Task Classifier** — determines the type of request: `explanation`, `clarification`, or `general`.
- **Task Splitter** — splits the task into subtasks for expert agents.
- **Expert Nodes (1–3)** — process subtasks in parallel with access to external tools via MCP.
- **Join Node** — merges expert outputs.
- **Summary Node** — generates the final response.
- **Switch Node** — routes the final message back to the main dialog.

---

## 🧰 Tech Stack

- **Python 3.13+**
- **Pydantic** — for configuration and state validation
- **OpenAI API** — for LLM inference
- **Langfuse** — for observability and tracing
- **FastMCP** — for external tool integration
- **[PocketFlow](https://github.com/the-pocket/PocketFlow)** — lightweight async pipeline framework

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/your-org/tabletopmagnat.git
cd tabletopmagnat
```

### 2. Install dependencies with `uv`

```bash
uv sync
```

> If you don’t have `uv` yet:  
> `curl -LsSf https://astral.sh/uv/install.sh | sh`

### 3. Configure environment

Create a `.env` file:

```env
OPENAI__API_KEY=your_openai_key
OPENAI__BASE_URL=
LANGFUSE__PUBLIC_KEY=your_langfuse_pk
LANGFUSE__SECRET_KEY=your_langfuse_sk
LANGFUSE__HOST=https://cloud.langfuse.com
MCP__URL=http://localhost:8000/mcp
MODELS__SECURITY_MODEL=deepseek/deepseek-v3.2-exp
MODELS__GENERAL_MODEL=deepseek/deepseek-v3.2-exp
MODELS__RAGS_MODEL=deepseek/deepseek-v3.2-exp
```

---

## 📦 Project Structure

| Module                  | Purpose                                      |
|-------------------------|----------------------------------------------|
| `application/`          | Entry point and orchestration                |
| `config/`               | Environment-based configuration              |
| `node/`                 | Pipeline nodes (security, experts, etc.)     |
| `services/`             | LLM services and integrations                |
| `state/`                | Dialog and expert state management           |
| `types/`                | Shared types for messages, tools, dialogs    |
| `subgraphs/`            | Expert subgraph creation via RASG            |
| `structured_output/`    | Pydantic models for structured LLM outputs   |

---

## 🧪 Usage Example

```python
import asyncio
from tabletopmagnat.services.llm_service import Service
from tabletopmagnat.config.config import Config
from tabletopmagnat.types.dialog import Dialog
from tabletopmagnat.types.messages import UserMessage

async def main():
    config = Config()
    service = Service(config)
    dialog = Dialog()
    dialog.add_message(UserMessage(content="Explain the rules of Monopoly"))
    response = await service.run(dialog)
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## ✅ Features

- Parallel expert processing
- MCP tool integration
- Full Langfuse tracing
- Modular node-based architecture
- Async-first design for high concurrency

---

## 📄 License

MIT © 2025