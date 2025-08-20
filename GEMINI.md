# Gemini Code Assistant Context

## Project Overview

This project is an open-source replication of OpenAI's Deep Research agent. It's a Python-based command-line tool that uses AI agents to conduct web research and answer complex questions. The agent system is built on the `smolagents` library and features a manager-worker architecture with specialized agents for searching and browsing. It supports various search engines, can inspect different file formats (PDF, Office documents, images), and is highly configurable through command-line arguments.

### Key Technologies

*   **Programming Language:** Python
*   **Core Libraries:** `smolagents`, `openai`, `anthropic`, `transformers`, `torch`
*   **Web Scraping & Search:** `beautifulsoup4`, `google-search-results`, `requests`
*   **File Processing:** `pdfminer`, `openpyxl`, `Pillow`
*   **CLI:** `argparse`

### Architecture

The system uses a multi-agent approach:

*   **Manager Agent:** Oversees the research process, plans steps, and delegates tasks.
*   **Search Agent:** Executes web searches using configured search tools.
*   **Browser Agent:** "Visits" web pages, extracts text, and can inspect files.

The agents use a variety of tools to perform their tasks, including:

*   **Search Tools:** Google, DuckDuckGo, Wikipedia, etc.
*   **Web Browser Tools:** Tools for visiting URLs, scrolling, and finding text on pages.
*   **Inspector Tools:** Tools for analyzing the content of text, images, and other files.

## Building and Running

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/pminervini/open-deep-research.git
    cd open-deep-research
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Set up environment variables for API keys (e.g., `SERPAPI_API_KEY`, `OPENAI_API_KEY`).

### Running the Research Agent

The main entry point is `cli/research-agent-cli.py`.

**Basic Usage:**

```bash
python cli/research-agent-cli.py "What are the latest developments in quantum computing?"
```

**Using a specific model:**

```bash
python cli/research-agent-cli.py "Compare Tesla and BYD electric vehicle sales in 2024" --model openai/gpt-oss:20b
```

### Running GAIA Evaluation

The project includes an evaluation script for the GAIA benchmark.

```bash
python cli/gaia-eval-cli.py --model "gpt-4o" --run-name "my-evaluation"
```

## Development Conventions

*   The project follows standard Python conventions.
*   It uses the `dotenv` library for managing environment variables.
*   The code is organized into `src` and `cli` directories.
*   The `smolagents` library provides the core framework for building the agents.
*   The project is designed to be extensible, allowing for the addition of new models, search tools, and agent types.
