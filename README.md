# English Memory Agent

**Kaggle Capstone Project Submission**  
**Track:** Concierge Agents  

The **English Memory Agent** is an AI-powered personal English learning concierge designed to help Chinese-native English learners correct writing mistakes, study useful collocations, extract key expressions, generate context-aware rewrites or example sentences (natural conversational and formal professional register), scan inputs for privacy risks, and save cards to a local database after human approval.

Inputs are not limited to full sentences — the pipeline classifies each input as a **sentence**, **phrase / idiom / collocation**, or **single word / abbreviation** and adapts the analysis accordingly (grammar checking for sentences, meaning + POS + definition + example sentences for words/phrases).

This project is fully compliant with the official **Agents CLI / ADK 2.0 Starter Scaffold Conventions** using graph-based workflows and includes an **MCP (Model Context Protocol)** server.

---

## Live Demo

Try the deployed Streamlit app here:

https://viilhelm-english-memory-agent-app-yszhgg.streamlit.app/

If the live demo is temporarily unavailable, the project can be run locally using the setup instructions below.

---

## Problem Statement

Many Chinese-native English learners face three practical problems.

First, they can understand English expressions temporarily but fail to reuse them later. Useful expressions are often saved in random notebooks, chat logs, or screenshots, making them hard to retrieve.

Second, learners often do not know the difference between a grammatically correct expression and a natural expression. For example, a sentence may be understandable but still sound unnatural, too direct, or too informal.

Third, existing learning tools often separate correction, explanation, vocabulary management, and review. This creates extra friction. Learners need to copy content between tools instead of having one assistant that can analyze, explain, save, and review expressions in one workflow.

English Memory Agent solves this by acting as a personal learning concierge. It guides the user from input analysis to correction, explanation, memory creation, privacy checking, human approval, and long-term review.

---

## Solution

The system provides a complete learning-memory loop:

1. The user enters an English word, phrase, sentence, or paragraph.
2. A router agent identifies the user’s intent.
3. Specialized agents correct the input, rewrite it into natural and formal versions, and explain the expression in Chinese.
4. The organizer creates a structured memory card.
5. A privacy scan checks whether the content contains sensitive information.
6. The user reviews the generated card and decides whether to save it.
7. Approved cards are stored in a local SQLite database.
8. The user can search, list, delete, or generate review quizzes from saved cards.

This design makes agents central to the project. The system is not just a prompt wrapper. It uses a graph workflow, multiple specialized agents, custom tools, local persistence, privacy controls, and human-in-the-loop decision making.

---

## Capstone Concepts Demonstrated

1. **Google ADK (Agent Development Kit) 2.0**:
   - Uses the new `google-adk>=2.0.0` Graph Workflow API.
   - Leverages `Gemini` models with explicit attempt retries.
2. **Multi-Agent Graph Workflow**:
   - The coordinator `root_agent` is implemented as an ADK `Workflow` defining explicit graph execution edges.
   - Routes control flow dynamically to 5 specialized sub-agents (`router_agent`, `correction_agent`, `rewrite_agent`, `explanation_agent`, and `organizer_agent`).
3. **Human-in-the-Loop (HITL) Integration**:
   - The ADK workflow implements a validation step using `RequestInput` which pauses the graph and asks the user for save confirmation. In the ADK Web / Agents CLI playground this is a native pause-and-resume. The Streamlit dashboard shows the same confirmation UI but persists the card via a direct save (see the note in `app.py`) because ADK's cross-loop resume does not survive Streamlit's per-click rerun model.
4. **Agent Tools / Skills**:
   - Custom python functions (`save_card`, `search_cards`, `list_recent_cards`, `delete_card`, `privacy_scan`, and `generate_review_quiz_from_cards`) registered as workflow nodes.
5. **Model Context Protocol (MCP) Server**:
   - Exposes database operations as MCP tools to decouple the SQLite storage layer, allowing external AI clients (like Cursor or Claude Desktop) to query, save, and review cards.
6. **Local SQLite Storage**:
   - Saves learning history securely in a local database file. New columns are added via idempotent migrations so old databases keep working.

---

## Memory Card Types

The organizer agent classifies each analyzed input into one of four card types, which the DB persists and the UI renders differently:

| Card Type          | When                                                                | Signature fields                                          |
|--------------------|---------------------------------------------------------------------|-----------------------------------------------------------|
| `error_card`       | Input is a full sentence with grammar/spelling errors               | `corrected_version`, `error_type`                         |
| `rewrite_card`     | Input is a correct sentence that can be improved in style/tone      | `natural_version`, `formal_version`                       |
| `expression_card`  | Input is a phrase, collocation, or idiom                            | `key_expression`, natural/formal example sentences        |
| `word_card`        | Input is a single word, abbreviation, or technical term             | `key_expression`, `part_of_speech`, `definition`, natural/formal example sentences |

The `natural_version` / `formal_version` fields carry either sentence rewrites (for sentences) or example sentences using the headword (for words/phrases). A legacy `ielts_version` column remains in the DB schema for backward compatibility with rows written before it was retired; it is no longer produced or displayed.

---

## Restructured Project Layout

Consistent with `agents-cli` conventions, all python code resides inside the `english_memory_agent/` directory. Duplicate folders have been cleaned up:
```
english-memory-agent/
├── README.md                   # Submission introduction & setup
├── pyproject.toml              # Dependencies & wheel targets
├── agents-cli-manifest.yaml    # Agents CLI configuration
├── Dockerfile                  # Container definition
├── app.py                      # Streamlit frontend dashboard
├── .gitignore                  # Ignores caches, .env, and local DBs
├── .env.example                # Environment configuration template
├── GEMINI.md                   # Agent guidance file
├── deployment_metadata.json    # Deployment metadata config
├── uv.lock                     # Python package lockfile
├── english_memory_agent/
│   ├── __init__.py             # Exports the App object
│   ├── agent.py                # Defines ADK 2.0 Workflow graph
│   ├── fast_api_app.py         # Exposes FastAPI endpoints
│   ├── agent_runtime_app.py    # AgentEngineApp entrypoint for Vertex deployment
│   ├── agents/                 # Pydantic schemas, prompts, and agents
│   │   ├── __init__.py
│   │   ├── prompts.py
│   │   ├── schemas.py
│   │   └── root_agent.py
│   ├── tools/                  # Privacy scan, SQLite tools, and quiz tools
│   │   ├── __init__.py
│   │   ├── memory_tools.py
│   │   ├── privacy_tools.py
│   │   └── review_tools.py
│   ├── database/               # SQLite connection and card table schemas
│   │   ├── __init__.py
│   │   ├── db.py
│   │   └── schema.sql
│   └── app_utils/              # Telemetry hooks and helper types
│       ├── __init__.py
│       ├── telemetry.py
│       └── typing.py
├── mcp_server/
│   └── memory_mcp_server.py    # Exposes SQLite database as MCP tools
├── deployment/
│   └── terraform/              # IaC directory
├── docs/                       # Project documentation
│   ├── architecture.md         # Workflow diagram & coordination specs
│   ├── security.md             # PII checks & safety controls
│   └── mcp_server.md           # Model Context Protocol details
├── examples/                   # Input and output example references
│   ├── demo_inputs.md
│   └── demo_outputs.md
└── tests/                      # Python unit and integration tests
    ├── unit/
    │   ├── test_memory_tools.py
    │   └── test_privacy_tools.py
    ├── integration/
    │   ├── test_agent.py
    │   └── test_agent_runtime_app.py
    └── eval/
        ├── eval_config.yaml
        └── datasets/
```

---

## Agent Graph and Data Flow

```
User Input 
    │
    ▼
Streamlit UI (Runner)
    │
    ▼
[START]
    │
    ▼
Router Node ──(Routes by Intent)──► [search_memory] ────────► Search DB Node
    │                             ► [generate_review] ──────► Quiz Generation Node
    │                             ► [delete_card] ──────────► Delete DB Node
    │                             ► [list_recent_cards] ────► List DB Node
    │
    └─► [analyze_new_english_input]
              │
              ▼
      Analysis Flow Node (Correction ──► Rewrite ──► Explanation ──► Organizer)
              │
              ▼
      Request Approval Node (Pre-save local Privacy Scan)
              │
         (Yields RequestInput: Pauses session)
              │
              ├─► UI User Approves ("yes") ──► Save Card Node ──► SQLite DB
              └─► UI User Rejects ("no")  ──► Skip Save Node
```

For more details, see [docs/architecture.md](file:///d:/waley/Projects/english-memory-agent/docs/architecture.md).

---

## Model Context Protocol (MCP) Tools

The MCP server exposes the database layer via these standard tools:
- `save_memory_card`: Saves vocabulary/error cards after a PII safety scan.
- `search_memory_cards`: Performs keyword search across saved cards.
- `list_recent_memory_cards`: Lists recently saved cards.
- `delete_memory_card`: Permanently deletes a card entry by ID.
- `generate_review_quiz`: Returns structured question drills (correction, translation, rewrite choices).

For implementation details, see [docs/mcp_server.md](file:///d:/waley/Projects/english-memory-agent/docs/mcp_server.md).

---

## Setup Instructions

### Option A: Windows (PowerShell)

1. **Navigate to the project folder**:
   ```powershell
   cd english-memory-agent
   ```

2. **Create the Python virtual environment**:
   ```powershell
   python -m venv .venv
   ```

3. **Activate the virtual environment**:
   ```powershell
   .venv\Scripts\Activate.ps1
   ```
   *Note: If PowerShell blocks the script execution, run:*
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
   *Then attempt activation again.*

4. **Install dependencies**:
   ```powershell
   pip install -e .
   ```

5. **Create the environment file**:
   ```powershell
   Copy-Item .env.example .env
   ```

---

### Option B: macOS / Linux (Terminal)

1. **Navigate to the project folder**:
   ```bash
   cd english-memory-agent
   ```

2. **Create the Python virtual environment**:
   ```bash
   python3 -m venv .venv
   ```

3. **Activate the virtual environment**:
   ```bash
   source .venv/bin/activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -e .
   ```

5. **Create the environment file**:
   ```bash
   cp .env.example .env
   ```

---

## Environment Variables Configuration

Open the newly created `.env` file in your text editor and configure it using the Google Cloud Vertex AI / Enterprise settings:

```env
GOOGLE_GENAI_USE_ENTERPRISE=True
GOOGLE_CLOUD_PROJECT=your-google-cloud-project-id
GOOGLE_CLOUD_LOCATION=us-east1
DATABASE_PATH=english_memory_agent/database/memory.db
```

If you prefer to use a personal Gemini API key instead of Vertex AI, set GOOGLE_GENAI_USE_ENTERPRISE=False and add GOOGLE_API_KEY=... to .env.

### Google Cloud Authentication (Application Default Credentials)
Before launching the application or running tests, you must authenticate with Google Cloud using Application Default Credentials (ADC) and enable the Vertex AI APIs. Run these commands in your shell:

```powershell
# 1. Authenticate locally with Google Cloud Application Default Credentials
gcloud auth application-default login

# 2. Configure your active project ID
gcloud config set project YOUR_PROJECT_ID

# 3. Set the quota billing project for your ADC credentials
gcloud auth application-default set-quota-project YOUR_PROJECT_ID

# 4. Enable the Vertex AI API service
gcloud services enable aiplatform.googleapis.com --project=YOUR_PROJECT_ID
```


---

## Running the Application

### 1. Primary Local UI: Streamlit Dashboard
The Streamlit dashboard is the recommended local interface. It provides tabbed access to input analysis, memory search, quiz review, and card management, with a bento-card layout and inline HITL confirmation.
```powershell
python -m streamlit run app.py
```
The dashboard structurally separates concerns by tab: the **Analyze English** tab drives the ADK workflow, while **Search Memory** and **Recent Cards** talk directly to the SQLite layer for immediate feedback.

### 2. ADK Web Dev UI (Conversational Debug)
The ADK Web Dev Server is useful for exercising the router-driven workflow as a single conversational stream (all intents — analyze, search, list, delete, review — flow through `router_node`):
```powershell
adk web . --host 127.0.0.1 --port 8080
```
Open your browser and navigate to:
[http://127.0.0.1:8080/dev-ui/?app=english_memory_agent](http://127.0.0.1:8080/dev-ui/?app=english_memory_agent)

Note: because the router uses an LLM classifier, bare English inputs default to the analyze intent. To trigger search from the ADK Web UI, use an explicit command verb (e.g. "search for apple", "list my cards").

### 3. Local Agents CLI Playground
To start the local command line playground:
```powershell
agents-cli playground
```

### 4. Running the MCP Server
To launch the database MCP server (useful for connecting Cursor, Claude Desktop, or other MCP clients):
```powershell
python mcp_server/memory_mcp_server.py
```
Or debug using the interactive inspector:
```powershell
mcp dev mcp_server/memory_mcp_server.py
```

### 5. Production Deployment: Google Agent Runtime
To deploy your agent to Google Cloud Agent Runtime in production:
```powershell
# 1. Login to Google Cloud
gcloud auth login

# 2. Deploy using Agents CLI
agents-cli deploy --project YOUR_PROJECT_ID --region us-east1
```

---

## Running Tests

To execute the unit and integration test suite:
```powershell
.venv\Scripts\python.exe -m pytest
```

---

## Final Submission Checklist

- [x] ADK Web local playground runs successfully
- [x] Production deployment configuration is verified
- [x] Unit and integration tests pass
- [x] README is complete
- [x] No real API key is committed
- [x] Walkthrough video/screenshots demonstrate the main workflow
