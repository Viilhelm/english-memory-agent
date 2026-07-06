# Model Context Protocol (MCP) Server

This document explains the Model Context Protocol (MCP) server implementation for the **English Memory Agent**.

## What is MCP?

The **Model Context Protocol (MCP)** is an open standard that allows developers to build secure, bidirectional connections between AI models and external data sources or tools. Rather than writing custom API connectors for each model or user interface, a single MCP Server can expose tools, resources, and prompt templates that any compatible MCP Client (like Cursor, Claude Desktop, or custom IDE plugins) can instantly consume.

For the **Kaggle Capstone Project**, the MCP Server demonstrates:
- **Tool Decoupling**: Database logic is separated from the AI core, making the memory database accessible to other external AI agents or chat interfaces.
- **Interoperability**: Any LLM-based agent configured with this MCP Server can query, save, or manage vocabulary cards without needing access to the Streamlit frontend.

---

## MCP Server Implementation

The server is implemented inside [**`mcp_server/memory_mcp_server.py`**](file:///d:/waley/Projects/english-memory-agent/mcp_server/memory_mcp_server.py) using the official `mcp` FastMCP SDK. 

It does not duplicate database queries. Instead, it imports and wraps the existing Python functions from `app/tools/` and `app/database/` directly, keeping the SQLite operations DRY (Don't Repeat Yourself).

---

## Exposed MCP Tools

The server exposes 5 tools to any connecting MCP Client:

1. **`save_memory_card`**:
   - Exposes parameters: `card_type`, `original_input`, `corrected_version`, `natural_version`, `formal_version`, `chinese_explanation`, `key_expression`, `error_type`, `scenario`, `tags`.
   - Saves memory cards to SQLite after running the PII privacy scan check.

2. **`search_memory_cards`**:
   - Parameter: `query` (str).
   - Searches the database for matching cards by keyword.

3. **`list_recent_memory_cards`**:
   - Parameter: `limit` (int).
   - Lists the most recently saved cards.

4. **`delete_memory_card`**:
   - Parameter: `card_id` (int).
   - Deletes a card by database ID.

5. **`generate_review_quiz`**:
   - Parameter: `limit` (int).
   - Fetches recent cards and generates interactive review questions.

---

## Database Connection

The MCP server connects to the database using the same `DATABASE_PATH` environment variable set in the local `.env` file. 

By default, if the environment variable is not defined, it resolves to `app/database/memory.db`.

---

## How to Run the MCP Server Locally

You can launch the MCP server using standard Python or via the `mcp` dev toolchain.

### Option A: Direct Python Execution
```powershell
# Activate venv first
.venv\Scripts\Activate.ps1

# Run the server
python mcp_server/memory_mcp_server.py
```

### Option B: Using the `mcp` CLI tool (inspector)
The MCP Inspector provides an interactive web console to test your tools:
```powershell
mcp dev mcp_server/memory_mcp_server.py
```
This starts a local dev server and provides a link to test tool execution, arguments, and return payloads.
