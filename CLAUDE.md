# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
- `python cli/research_agent.py --model-id "gpt-4o-mini" "Your question here"` - Run the main research agent with a question
- `python app.py` - Launch the Gradio web interface for interactive use
- `python cli/evaluate_gaia.py` - Run evaluation on the GAIA benchmark dataset

### Setup Commands
- `pip install -r requirements.txt` - Install project-specific dependencies
- `pip install -e ../../.[dev]` - Install smolagents in development mode from the parent directory

### Testing and Quality (from smolagents root)
- `make test` - Run all tests with pytest
- `make quality` - Check code formatting and linting with ruff
- `make style` - Auto-format code with ruff
- `pytest ./tests/test_specific.py` - Run specific test files
- `ruff check examples src tests` - Manual linting check
- `ruff format examples src tests` - Manual formatting

## Architecture Overview

This is the **Open Deep Research** example - an open replication of OpenAI's Deep Research that achieves 55% pass@1 on the GAIA validation set. The system uses a multi-agent architecture with specialized roles.

### Core Components

**Main Agent Structure** (`cli/research_agent.py`):
- `Manager Agent` - A `CodeAgent` that orchestrates the research process and handles complex reasoning
- `Search Agent` - A `ToolCallingAgent` specialized for web browsing and information gathering
- Uses LiteLLM for model abstraction, defaulting to OpenAI's o1 model

**Key Agent Configuration**:
- Manager uses `CodeAgent` with `max_steps=12` and custom Python execution environment
- Search agent uses `ToolCallingAgent` with `max_steps=20` and planning every 4 steps
- Both agents have `verbosity_level=2` for detailed logging

**Web Browsing Tools** (`scripts/text_web_browser.py`):
- `SimpleTextBrowser` - Text-based web browser with configurable viewport
- Navigation tools: `VisitTool`, `PageUpTool`, `PageDownTool`, `FinderTool`
- `ArchiveSearchTool` for accessing archived web content
- Custom request configuration with user-agent spoofing and 5-minute timeouts

**Document Processing Tools**:
- `TextInspectorTool` - Processes documents and extracts relevant information using LLM
- `visualizer` - Visual QA tool for image analysis
- File handling supports: PDF, Excel, Word, images, audio, zip archives
- Automatic conversion to PNG screenshots for visual documents when available

### Multi-Agent Communication

**Manager-Search Agent Interaction**:
- Manager delegates web research tasks to the search agent
- Search agent provides detailed summaries using `provide_run_summary=True`
- Manager handles final reasoning and answer synthesis
- Search agent can request clarification through `final_answer` calls

**Planning and Memory**:
- Both agents use planning intervals (every 4 steps) for strategic decision-making
- Manager has access to additional authorized imports (`"*"`) for flexible code execution
- Custom role conversions map tool interactions to assistant/user roles for model compatibility

### Environment Configuration

**Required Environment Variables**:
- `OPENAI_API_KEY` - For o1 model access (requires tier-3 access)
- `SERPAPI_API_KEY` or `SERPER_API_KEY` - For Google Search functionality
- `HF_TOKEN` - HuggingFace authentication for model access

**Browser Configuration**:
- Large viewport size (5120px) for comprehensive page content
- Dedicated downloads folder for file handling
- 5-minute request timeout for slow-loading pages
- Custom user agent for web compatibility

### File Processing Strategy

The system automatically handles various file formats:
- Images (PNG, JPG) are processed directly through visual QA
- Documents (PDF, Excel, Word) prefer PNG screenshots when available
- Zip files are extracted and each contained file is processed individually
- Audio files are noted but not processed (requires additional tools)

### Performance Considerations

- Uses threading locks for concurrent file operations
- Text processing limited to 100,000 characters per document
- Automatic file type detection and appropriate tool selection
- Caches browser sessions for efficient web navigation