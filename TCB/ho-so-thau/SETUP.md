# Team Onboarding Guide

Welcome to the Document Processing Workflow project! This guide will help you get set up and ready to work.

## 1. Prerequisites Checklist

Before you begin, ensure you have the following installed:

- [ ] **Cursor IDE** - Download from [cursor.sh](https://cursor.sh)
  - This is the primary interface for all work - we don't use terminal commands directly
- [ ] **Docker Desktop** - Download from [docker.com](https://www.docker.com/products/docker-desktop)
  - Required for LibreOffice rendering service
  - Ensure Docker is running before proceeding
- [ ] **Git** - Usually pre-installed on macOS/Linux
  - Verify with: `git --version`
- [ ] **uv** (Python package manager) - Install via: `curl -LsSf https://astral.sh/uv/install.sh | sh`
  - Verify with: `uv --version`
  - **Important**: We use `uv` instead of `pip` for all Python package management

## 2. Clone and Install

- [ ] **Clone the repository**
  ```bash
  git clone <repository-url>
  cd ho-so-thau
  ```

- [ ] **Create Python virtual environment** (using uv)
  ```bash
  uv venv
  source .venv/bin/activate  # On macOS/Linux
  # or
  .venv\Scripts\activate  # On Windows
  ```

- [ ] **Install Python dependencies** (using uv)
  ```bash
  uv pip install -r pyproject.toml
  ```
  Note: Dependencies are defined in `pyproject.toml`, not `requirements.txt`

- [ ] **Create required directories** (if they don't exist)
  ```bash
  mkdir -p input output review tmp/handoff tmp/handoff/history tmp/renders tmp/images tmp/diagrams chat
  ```

## 3. Configure Personal Author Info

Your personal configuration is git-ignored and won't be committed to the repository.

- [ ] **Copy the example config file**
  ```bash
  cp config.yaml.example config.yaml
  ```

- [ ] **Edit `config.yaml`** with your personal information:
  - Your name
  - Your role
  - Your team
  - Company branding (if different from default)
  - Model preferences (optional - defaults are already set)

**Important**: `config.yaml` is git-ignored. Each team member maintains their own copy.

## 4. Verify MCP Servers in Cursor

MCP (Model Context Protocol) servers extend Cursor's capabilities. You need to configure these in Cursor Settings.

- [ ] **Open Cursor Settings** → **Features** → **MCP**

- [ ] **Verify these MCP servers are configured:**
  - [ ] `document-loader-mcp-server` - Reads PDF, Word, Excel, PowerPoint files
  - [ ] `markitdown` - Converts documents to markdown format
  - [ ] `aws-diagram-mcp-server` - Generates architecture diagrams

- [ ] **If servers are missing**, add them to your Cursor MCP settings:
  ```json
  {
    "mcpServers": {
      "document-loader-mcp-server": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-document-loader"]
      },
      "markitdown": {
        "command": "npx",
        "args": ["-y", "@mendableai/markitdown-mcp"]
      },
      "aws-diagram-mcp-server": {
        "command": "npx",
        "args": ["-y", "@aws-diagram-mcp/server"]
      }
    }
  }
  ```

- [ ] **Restart Cursor** after adding MCP servers

## 5. Verify Cursor Rules are Loaded

Cursor Rules provide AI guidance for document processing workflows. They should auto-load from `.cursor/rules/`.

- [ ] **Check that these rule files exist** in `.cursor/rules/`:
  - [ ] `document-workflow.mdc` - Main workflow instructions
  - [ ] `document-types.mdc` - Document type definitions
  - [ ] `formatting-standards.mdc` - Formatting specifications
  - [ ] `review-checklist.mdc` - Review quality checklist

- [ ] **Verify rules are active**: Open a chat in Cursor and ask: "What document types are supported?"
  - The AI should reference the rules automatically

## 6. Verify System Dependencies (LibreOffice via Docker)

LibreOffice runs in a Docker container for document rendering. This must be running in the background.

- [ ] **Start the Docker container**
  ```bash
  docker-compose up -d
  ```

- [ ] **Verify container is running**
  ```bash
  docker ps | grep ho-so-thau-renderer
  ```
  You should see the container running.

- [ ] **Check container logs** (if needed)
  ```bash
  docker-compose logs renderer
  ```

**Note**: The container runs in the background (`restart: unless-stopped`). You don't need to restart it unless you modify the Dockerfile or docker-compose.yml.

## 7. Test the Workflow

Let's verify everything works with a quick test.

- [ ] **Create a test file** in `input/`:
  - Place a simple Word document (`test.docx`) or PDF (`test.pdf`) in `input/`
  - Or use an existing sample file if available

- [ ] **Open Cursor chat** and ask:
  ```
  Read the document from input/test.docx and summarize its contents.
  ```
  - The AI should use the MCP document-loader to read the file

- [ ] **Test document rendering** (if you have a document):
  ```
  Render the first page of input/test.docx to PNG
  ```
  - This should create a PNG in `tmp/renders/`

- [ ] **Verify output directories**:
  - Check that `output/`, `review/`, `tmp/` directories exist
  - These are git-ignored (personal to each team member)

## 8. You're Ready! 🎉

Everything is set up. Here's what you should know:

### What Gets Committed to Git (Shared)
- `.cursor/rules/` - Cursor Rules for AI guidance
- `scripts/` - Helper scripts for document processing
- `templates/` - Document templates (Word, Excel, PowerPoint)
- `WORKFLOW.md`, `SETUP.md`, `README.md` - Documentation
- `config.yaml.example` - Example configuration (not your personal config)
- `Dockerfile`, `docker-compose.yml` - Docker configuration
- `pyproject.toml` - Python dependencies

### What is Git-Ignored (Personal)
- `config.yaml` - Your personal author configuration
- `input/` - Your source documents
- `output/` - Your generated documents
- `review/` - Your review reports
- `tmp/` - Temporary files (images, diagrams, renders, handoff files)
- `chat/` - Chat history logs
- `.venv/` - Python virtual environment

### Key Workflow Points

- **All interaction through Cursor**: Use Cursor chat for all document processing tasks
- **Docker runs LibreOffice**: The renderer container must be running for document rendering
- **uv for Python packages**: Always use `uv pip install` instead of `pip install`
- **Personal config**: Each team member has their own `config.yaml` (git-ignored)
- **MCP servers**: Configured in Cursor Settings → Features → MCP
- **Cursor Rules**: Auto-loaded from `.cursor/rules/` directory

### Next Steps

- Read `WORKFLOW.md` to understand the document processing phases
- Read `README.md` for project overview
- Review `.cursor/rules/document-workflow.mdc` for detailed workflow instructions
- Start processing documents! Place files in `input/` and ask Cursor to process them

### Getting Help

- Check `WORKFLOW.md` for workflow questions
- Review `.cursor/rules/` for AI behavior and standards
- Ask in team chat if you encounter issues

---

**Last Updated**: 2026-02-09
