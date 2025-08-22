# Open Deep Research (ODR) Integration Guide

## Overview

Open Deep Research is an open replication of OpenAI's Deep Research that achieves 55% pass@1 on the GAIA validation set. This comprehensive guide provides AI assistants and developers with everything needed to understand, integrate, and utilize the ODR system effectively.

The system implements a sophisticated multi-agent architecture using specialized roles:
- **Manager Agent**: Orchestrates research process and handles complex reasoning
- **Search Agent**: Specialized for web browsing and information gathering
- **Web Browser**: Advanced text-based browser with navigation tools
- **Document Processor**: Handles PDFs, Excel, images, and other file formats
- **Visual QA Tool**: Image analysis and visual document processing

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Components](#core-components)
3. [Agent System](#agent-system)
4. [Web Browsing System](#web-browsing-system)
5. [Document Processing](#document-processing)
6. [Environment Setup](#environment-setup)
7. [Integration Examples](#integration-examples)
8. [API Reference](#api-reference)
9. [Configuration Options](#configuration-options)
10. [Troubleshooting](#troubleshooting)

## Architecture Overview

### Project Structure
```
open-deep-research/
├── cli/                          # Command-line interfaces
│   ├── research-agent-cli.py    # Main research agent CLI
│   ├── gaia-eval-cli.py         # GAIA benchmark evaluation
│   └── search-cli.py            # Standalone search tool CLI
├── src/open_deep_research/       # Core package
│   ├── __init__.py              # Package initialization
│   ├── text_web_browser.py      # Web browsing tools and browser
│   ├── text_inspector_tool.py   # Document analysis tool
│   ├── visual_qa.py             # Visual question answering
│   ├── mdconvert.py             # Document conversion utilities
│   ├── cookies.py               # Web session cookies
│   ├── reformulator.py          # Response reformulation
│   └── run_agents.py            # Agent execution helpers
├── handbooks/                    # Documentation
├── downloads/                    # File download directory
├── downloads_folder/            # Alternative download location
└── tests/                       # Test suite
```

### Dependencies and Installation

**Core Requirements:**
- Python 3.8+
- smolagents 0.4.0+
- OpenAI API access (tier-3 for o1 models)
- SerpAPI or Serper API key for Google Search
- HuggingFace token for model access

**Install via pip:**
```bash
pip install -r requirements.txt
pip install -e .  # Development installation
```

**Environment Variables:**
```bash
export OPENAI_API_KEY="your_openai_key"
export SERPAPI_API_KEY="your_serpapi_key"  # or SERPER_API_KEY
export HF_TOKEN="your_huggingface_token"
export BRAVE_API_KEY="your_brave_key"  # Optional for Brave search
```

## Core Components

### 1. LiteLLMModel Integration

The system uses LiteLLM for model abstraction, supporting multiple providers:

```python
from smolagents import LiteLLMModel

# OpenAI o1 configuration (default)
model = LiteLLMModel(
    model_id="o1",
    reasoning_effort="high",
    max_completion_tokens=8192,
    custom_role_conversions={"tool-call": "assistant", "tool-response": "user"}
)

# Alternative models
model = LiteLLMModel(
    model_id="gpt-4o-mini",
    max_tokens=4096,
    api_base="http://localhost:1234/v1",  # Local server
    api_key="your_key"
)
```

### 2. SimpleTextBrowser

Advanced text-based web browser with comprehensive navigation:

```python
from src.open_deep_research.text_web_browser import SimpleTextBrowser

# Browser configuration
BROWSER_CONFIG = {
    "viewport_size": 1024 * 5,  # Large viewport for comprehensive content
    "downloads_folder": "downloads_folder",
    "request_kwargs": {
        "headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"},
        "timeout": 300  # 5-minute timeout for slow pages
    },
    "serpapi_key": os.getenv("SERPAPI_API_KEY")
}

browser = SimpleTextBrowser(**BROWSER_CONFIG)

# Navigation examples
browser.visit_page("https://example.com")
content = browser.viewport  # Current page content
browser.page_down()  # Navigate down
browser.find_on_page("search term")  # Find text on page
```

### 3. TextInspectorTool

Document analysis and processing tool:

```python
from src.open_deep_research.text_inspector_tool import TextInspectorTool

# Initialize with model and text limit
inspector = TextInspectorTool(model=model, text_limit=100000)

# Document processing
result = inspector.forward(
    file_path="/path/to/document.pdf",
    question="What are the key findings in this research paper?"
)

# Supported formats: PDF, DOCX, XLSX, PPTX, HTML, TXT, WAV, MP3, M4A
```

### 4. Visual QA Tool

Image analysis using GPT-4V:

```python
from src.open_deep_research.visual_qa import visualizer

# Analyze images
result = visualizer(
    image_path="/path/to/image.png",
    question="What does this chart show?"
)

# Automatic captioning (no question)
caption = visualizer(image_path="/path/to/image.png")
```

## Agent System

### Agent Architecture

The system implements a hierarchical multi-agent architecture:

1. **Manager Agent** (CodeAgent/ToolCallingAgent)
   - Orchestrates overall research process
   - Handles complex reasoning and synthesis
   - Manages communication with search agent
   - Has access to visual QA and document inspection tools

2. **Search Agent** (ToolCallingAgent/CodeAgent)
   - Specialized for web research
   - Uses multiple search engines and web tools
   - Provides detailed summaries of findings
   - Can request clarification through `final_answer`

### Creating Agent Teams

```python
from smolagents import CodeAgent, ToolCallingAgent, LiteLLMModel
from src.open_deep_research.text_web_browser import *
from src.open_deep_research.text_inspector_tool import TextInspectorTool
from src.open_deep_research.visual_qa import visualizer

def create_research_agent(
    model_id="o1",
    manager_type="CodeAgent",
    search_type="ToolCallingAgent"
):
    # Model setup
    model = LiteLLMModel(
        model_id=model_id,
        custom_role_conversions={"tool-call": "assistant", "tool-response": "user"}
    )
    
    # Browser and tools
    browser = SimpleTextBrowser(**BROWSER_CONFIG)
    text_inspector = TextInspectorTool(model, text_limit=100000)
    
    # Web tools for search agent
    web_tools = [
        GoogleSearchTool(provider="serper"),
        VisitTool(browser),
        PageUpTool(browser),
        PageDownTool(browser),
        FinderTool(browser),
        FindNextTool(browser),
        ArchiveSearchTool(browser),
        text_inspector
    ]
    
    # Search agent configuration
    search_config = {
        "model": model,
        "max_steps": 20,
        "verbosity_level": 2,
        "planning_interval": 4,
        "name": "search_agent",
        "description": """A team member that will search the internet to answer your question.
        Ask him for all your questions that require browsing the web.
        Provide him as much context as possible, in particular if you need to search on a specific timeframe!
        And don't hesitate to provide him with a complex search task, like finding a difference between two webpages.
        Your request must be a real sentence, not a google search! Like "Find me this information (...)" rather than a few keywords.""",
        "provide_run_summary": True,
        "tools": web_tools
    }
    
    # Create search agent
    if search_type == "ToolCallingAgent":
        search_agent = ToolCallingAgent(**search_config)
    else:
        search_config["additional_authorized_imports"] = ["*"]
        search_agent = CodeAgent(**search_config)
    
    # Enhance search agent prompt
    search_agent.prompt_templates["managed_agent"]["task"] += """You can navigate to .txt online files.
    If a non-html page is in another format, especially .pdf or a Youtube video, use tool 'inspect_file_as_text' to inspect it.
    Additionally, if after some searching you find out that you need more information to answer the question, you can use `final_answer` with your request for clarification as argument to request for more information."""
    
    # Manager agent configuration
    manager_config = {
        "model": model,
        "tools": [visualizer, text_inspector],
        "max_steps": 12,
        "verbosity_level": 2,
        "planning_interval": 4,
        "managed_agents": [search_agent]
    }
    
    # Create manager agent
    if manager_type == "CodeAgent":
        manager_config["additional_authorized_imports"] = ["*"]
        manager_agent = CodeAgent(**manager_config)
    else:
        manager_agent = ToolCallingAgent(**manager_config)
    
    return manager_agent
```

### Agent Communication Patterns

**Manager → Search Agent:**
```python
# The manager delegates research tasks to the search agent
task = "Find the latest information about quantum computing developments in 2024, focusing on IBM and Google's announcements"
result = search_agent.run(task)
```

**Search Agent → Manager:**
```python
# Search agent provides detailed summaries with provide_run_summary=True
# Can request clarification through final_answer calls
```

**Planning and Memory:**
- Both agents use planning intervals (every 4 steps)
- Manager has access to flexible code execution (`additional_authorized_imports=["*"]`)
- Custom role conversions map tool interactions for model compatibility

## Web Browsing System

### Browser Tools

#### VisitTool
Navigates to URLs and returns content:

```python
visit_tool = VisitTool(browser)
content = visit_tool.forward("https://example.com")
```

#### Navigation Tools
```python
page_up_tool = PageUpTool(browser)
page_down_tool = PageDownTool(browser)
finder_tool = FinderTool(browser)
find_next_tool = FindNextTool(browser)

# Usage
page_down_tool.forward()  # Scroll down one page
finder_tool.forward("search term")  # Find text on page
find_next_tool.forward()  # Find next occurrence
```

#### ArchiveSearchTool
Access Wayback Machine archives:

```python
archive_tool = ArchiveSearchTool(browser)
archived_content = archive_tool.forward(
    url="https://example.com",
    date="20200301"  # YYYYMMDD format
)
```

### Search Engine Integration

#### Google Search
```python
from smolagents import GoogleSearchTool

# Using Serper (faster, cheaper)
google_tool = GoogleSearchTool(provider="serper")
results = google_tool.forward("machine learning trends 2024")

# Using SerpAPI (more features)
google_tool = GoogleSearchTool(provider="serpapi")
results = google_tool.forward("AI research papers", filter_year=2024)
```

#### Multiple Search Engines
```python
def create_search_tools(search_types=["google", "duckduckgo", "wikipedia"]):
    tools = []
    
    for search_type in search_types:
        if search_type == "google":
            tools.append(GoogleSearchTool(provider="serper"))
        elif search_type == "duckduckgo":
            tools.append(DuckDuckGoSearchTool())
        elif search_type == "wikipedia":
            tools.append(WikipediaSearchTool(user_agent="OpenDeepResearch/1.0"))
        elif search_type == "brave":
            tools.append(ApiWebSearchTool())  # Requires BRAVE_API_KEY
        elif search_type == "websearch":
            tools.append(WebSearchTool())  # Simple scrapers, no API key needed
    
    return tools
```

### Browser Configuration

```python
# Comprehensive browser setup
BROWSER_CONFIG = {
    "viewport_size": 1024 * 5,  # Large viewport for comprehensive content
    "downloads_folder": "downloads_folder",
    "request_kwargs": {
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"
        },
        "timeout": 300,  # 5-minute timeout
        "cookies": COOKIES  # Pre-configured cookies for site access
    },
    "serpapi_key": os.getenv("SERPAPI_API_KEY")
}
```

## Document Processing

### MarkdownConverter System

The document processing system uses a sophisticated converter architecture:

```python
from src.open_deep_research.mdconvert import MarkdownConverter

converter = MarkdownConverter()

# Supported formats and their converters:
# - PDF: pdfminer-based extraction
# - DOCX: mammoth HTML conversion
# - XLSX/XLS: pandas-based table extraction
# - PPTX: slide content and notes extraction
# - HTML: BeautifulSoup with custom markdown conversion
# - Images (PNG/JPG): metadata extraction + OCR
# - Audio (WAV/MP3/M4A): metadata + speech transcription
# - ZIP: automatic extraction and file listing
```

### File Processing Strategy

```python
def process_document(file_path, question=None):
    """
    Comprehensive document processing with format detection
    """
    # Automatic format detection using:
    # 1. File extension
    # 2. MIME type
    # 3. puremagic (binary signature detection)
    
    result = converter.convert(file_path)
    
    if question:
        # Use TextInspectorTool for Q&A
        inspector = TextInspectorTool(model, text_limit=100000)
        return inspector.forward(file_path, question)
    
    return result.text_content
```

### Specialized Converters

#### PDF Processing
```python
# Handles both text extraction and image conversion
class PdfConverter(DocumentConverter):
    def convert(self, local_path, **kwargs):
        # Uses pdfminer for robust text extraction
        return DocumentConverterResult(
            title=None, 
            text_content=pdfminer_extract_text(local_path)
        )
```

#### Office Documents
```python
# DOCX: Preserves formatting and tables
# XLSX: Converts each sheet to markdown tables
# PPTX: Extracts slides, notes, and image alt text
```

#### Media Files
```python
# Images: Metadata + visual description via GPT-4V
# Audio: Metadata + speech transcription via Google Speech Recognition
# ZIP: Extracts all files and processes individually
```

### YouTube Integration

Special handling for YouTube videos:

```python
class YouTubeConverter(DocumentConverter):
    def convert(self, local_path, **kwargs):
        # Extracts:
        # - Video title and metadata
        # - Description
        # - Full transcript using youtube_transcript_api
        # - Video statistics
        
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        formatted_transcript = SRTFormatter().format_transcript(transcript)
```

## Environment Setup

### Development Environment

```bash
# Clone and setup
git clone https://github.com/pminervini/open-deep-research.git
cd open-deep-research

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Setup environment variables
cp .env.example .env  # Edit with your API keys

# Optional: Install smolagents in development mode
cd ../smolagents  # Assuming smolagents is in parent directory
pip install -e .[dev]
```

### API Keys and Configuration

```bash
# Required
export OPENAI_API_KEY="sk-..."  # OpenAI API (tier-3 for o1)
export HF_TOKEN="hf_..."        # HuggingFace token

# Search APIs (at least one required)
export SERPAPI_API_KEY="..."    # Google Search via SerpAPI
export SERPER_API_KEY="..."     # Google Search via Serper (faster)
export BRAVE_API_KEY="..."      # Brave Search API

# Optional
export ANTHROPIC_API_KEY="..."  # For Claude models
```

### Testing Configuration

The project follows specific testing guidelines:

```python
# Test configuration (as per CLAUDE.md)
TEST_CONFIG = {
    "endpoint": "http://127.0.0.1:11434/v1",
    "model": "openai/gpt-oss:20b",
    "use_real_apis": True  # Never use mocks
}

# Running tests
pytest tests/test_agent.py  # Individual test file
make test                   # Full test suite (from smolagents root)
make quality               # Code quality checks
```

## Integration Examples

### 1. Basic Research Agent

```python
from src.open_deep_research.text_web_browser import SimpleTextBrowser
from src.open_deep_research.text_inspector_tool import TextInspectorTool
from smolagents import CodeAgent, LiteLLMModel

def create_basic_research_agent():
    model = LiteLLMModel(model_id="gpt-4o-mini")
    browser = SimpleTextBrowser(viewport_size=1024*5)
    
    tools = [
        GoogleSearchTool(provider="serper"),
        VisitTool(browser),
        TextInspectorTool(model, 100000)
    ]
    
    agent = CodeAgent(
        model=model,
        tools=tools,
        max_steps=10,
        verbosity_level=2
    )
    
    return agent

# Usage
agent = create_basic_research_agent()
result = agent.run("What are the latest developments in renewable energy technology?")
```

### 2. Document Analysis Pipeline

```python
def analyze_documents(file_paths, question):
    """
    Analyze multiple documents in relation to a research question
    """
    model = LiteLLMModel(model_id="o1")
    inspector = TextInspectorTool(model, text_limit=100000)
    
    results = []
    for file_path in file_paths:
        try:
            if file_path.endswith('.zip'):
                # Handle ZIP files specially
                result = get_zip_description(file_path, question, visualizer, inspector)
            else:
                # Regular file processing
                result = inspector.forward(file_path, question)
            
            results.append({
                'file': file_path,
                'analysis': result,
                'status': 'success'
            })
        except Exception as e:
            results.append({
                'file': file_path,
                'error': str(e),
                'status': 'error'
            })
    
    return results

# Usage
documents = ['report1.pdf', 'data.xlsx', 'presentation.pptx']
analysis = analyze_documents(documents, "What are the key performance metrics?")
```

### 3. Custom Web Research Pipeline

```python
def custom_web_research(query, search_engines=["google", "duckduckgo"], max_pages=5):
    """
    Custom research pipeline with multiple search engines
    """
    browser = SimpleTextBrowser(viewport_size=1024*5)
    model = LiteLLMModel(model_id="gpt-4o")
    
    # Create search tools
    tools = create_search_tools(search_engines)
    tools.extend([
        VisitTool(browser),
        TextInspectorTool(model, 100000)
    ])
    
    agent = ToolCallingAgent(
        model=model,
        tools=tools,
        max_steps=20,
        planning_interval=5
    )
    
    enhanced_query = f"""
    Research the following topic comprehensively using multiple search engines:
    {query}
    
    Please:
    1. Search using different search engines for diverse perspectives
    2. Visit and analyze the most relevant pages
    3. Synthesize findings from multiple sources
    4. Provide a comprehensive summary with sources
    
    Focus on recent information and authoritative sources.
    """
    
    return agent.run(enhanced_query)

# Usage
result = custom_web_research(
    "Impact of AI on healthcare in 2024",
    search_engines=["google", "duckduckgo", "wikipedia"]
)
```

### 4. GAIA Benchmark Evaluation

```python
def run_gaia_evaluation(model_name="o1", concurrency=8):
    """
    Run evaluation on GAIA benchmark dataset
    """
    from cli.gaia_eval_cli import create_agent_team, load_gaia_dataset
    
    # Load dataset
    eval_ds = load_gaia_dataset(use_raw_dataset=False, set_to_run="validation")
    
    # Create model and agent
    model = create_model(model_name)
    agent = create_agent_team(model)
    
    # Process questions
    results = []
    for example in eval_ds:
        if example["file_name"]:  # Only process questions with files
            try:
                result = agent.run(example["question"])
                results.append({
                    'question_id': example['task_id'],
                    'prediction': result,
                    'true_answer': example['true_answer'],
                    'task_level': example['task']
                })
            except Exception as e:
                print(f"Error processing {example['task_id']}: {e}")
    
    return results
```

### 5. Multi-Modal Document Processing

```python
def process_multimodal_document(file_path, query):
    """
    Process documents that may contain both text and images
    """
    import os
    from pathlib import Path
    
    model = LiteLLMModel(model_id="gpt-4o")
    inspector = TextInspectorTool(model, 100000)
    
    # Check for image version of document
    base_path = Path(file_path).with_suffix('')
    image_path = f"{base_path}.png"
    
    results = {}
    
    # Process text content
    try:
        results['text_analysis'] = inspector.forward(file_path, query)
    except Exception as e:
        results['text_error'] = str(e)
    
    # Process image version if available
    if os.path.exists(image_path):
        try:
            results['visual_analysis'] = visualizer(image_path, query)
        except Exception as e:
            results['visual_error'] = str(e)
    
    # Combine analyses
    if 'text_analysis' in results and 'visual_analysis' in results:
        combined_prompt = f"""
        Based on both text and visual analysis of the same document:
        
        Text Analysis: {results['text_analysis']}
        
        Visual Analysis: {results['visual_analysis']}
        
        Question: {query}
        
        Please provide a comprehensive answer that leverages both text and visual information.
        """
        
        results['combined_analysis'] = model([{
            "role": "user",
            "content": combined_prompt
        }]).content
    
    return results
```

## API Reference

### Core Classes

#### SimpleTextBrowser
```python
class SimpleTextBrowser:
    def __init__(
        self, 
        start_page: str = None,
        viewport_size: int = 1024 * 8,
        downloads_folder: str = None,
        serpapi_key: str = None,
        request_kwargs: dict = None
    )
    
    # Navigation methods
    def visit_page(self, path_or_uri: str, filter_year: int = None) -> str
    def page_down(self) -> None
    def page_up(self) -> None
    def find_on_page(self, query: str) -> str | None
    def find_next(self) -> str | None
    
    # Properties
    @property
    def viewport(self) -> str  # Current page content
    @property
    def page_content(self) -> str  # Full page content
    @property
    def address(self) -> str  # Current URL
```

#### TextInspectorTool
```python
class TextInspectorTool(Tool):
    def __init__(self, model: Model, text_limit: int = 100000)
    
    def forward(self, file_path: str, question: str = None) -> str
    def forward_initial_exam_mode(self, file_path: str, question: str) -> str
    
    # Supported formats: 
    # Documents: .pdf, .docx, .xlsx, .pptx, .html, .htm
    # Audio: .wav, .mp3, .m4a, .flac
    # Archives: .zip
    # Text: all text formats
```

#### Browser Tools
```python
class VisitTool(Tool):
    def forward(self, url: str) -> str

class ArchiveSearchTool(Tool):
    def forward(self, url: str, date: str) -> str  # date in YYYYMMDD format

class PageUpTool(Tool):
    def forward(self) -> str

class PageDownTool(Tool):
    def forward(self) -> str

class FinderTool(Tool):
    def forward(self, search_string: str) -> str

class FindNextTool(Tool):
    def forward(self) -> str
```

### Visual QA
```python
@tool
def visualizer(image_path: str, question: str = None) -> str:
    """
    Analyze images using GPT-4V
    
    Args:
        image_path: Local path to image file
        question: Optional question about the image
    
    Returns:
        Analysis or description of the image
    """
```

### Document Converter Classes
```python
class MarkdownConverter:
    def convert(self, source: str | requests.Response, **kwargs) -> DocumentConverterResult
    def convert_local(self, path: str, **kwargs) -> DocumentConverterResult
    def convert_url(self, url: str, **kwargs) -> DocumentConverterResult
    
    # Specialized converters available:
    # - PlainTextConverter
    # - HtmlConverter  
    # - WikipediaConverter
    # - YouTubeConverter
    # - PdfConverter
    # - DocxConverter
    # - XlsxConverter
    # - PptxConverter
    # - ImageConverter
    # - WavConverter
    # - Mp3Converter
    # - ZipConverter
```

## Configuration Options

### Model Configuration
```python
# OpenAI o1 (default, requires tier-3 access)
model_config = {
    "model_id": "o1",
    "reasoning_effort": "high",
    "max_completion_tokens": 8192
}

# GPT-4 variants
model_config = {
    "model_id": "gpt-4o",
    "max_tokens": 4096
}

# Local/alternative models
model_config = {
    "model_id": "openai/gpt-oss:20b",
    "api_base": "http://127.0.0.1:11434/v1",
    "api_key": "api-key"
}

# Claude models
model_config = {
    "model_id": "claude-3-sonnet-20240229",
    "max_tokens": 4096
}
```

### Agent Configuration
```python
# Manager Agent (CodeAgent recommended)
manager_config = {
    "model": model,
    "tools": [visualizer, text_inspector],
    "max_steps": 12,
    "verbosity_level": 2,
    "planning_interval": 4,
    "additional_authorized_imports": ["*"]  # For CodeAgent
}

# Search Agent (ToolCallingAgent recommended)
search_config = {
    "model": model,
    "tools": web_tools,
    "max_steps": 20,
    "verbosity_level": 2,
    "planning_interval": 4,
    "provide_run_summary": True
}
```

### Browser Configuration
```python
BROWSER_CONFIG = {
    "viewport_size": 1024 * 5,  # Large viewport (5KB per page)
    "downloads_folder": "downloads_folder",
    "request_kwargs": {
        "headers": {"User-Agent": "..."},
        "timeout": 300,  # 5 minutes
        "cookies": COOKIES  # Pre-configured cookies
    },
    "serpapi_key": os.getenv("SERPAPI_API_KEY")
}
```

### Search Tool Configuration
```python
# Google Search options
google_tool = GoogleSearchTool(
    provider="serper"  # or "serpapi"
)

# DuckDuckGo options
ddg_tool = DuckDuckGoSearchTool()

# Wikipedia options
wiki_tool = WikipediaSearchTool(
    user_agent="OpenDeepResearch/1.0",
    language="en"
)

# API Web Search (Brave)
brave_tool = ApiWebSearchTool()  # Uses BRAVE_API_KEY env var

# Simple Web Search
web_tool = WebSearchTool()  # No API key required
```

## Troubleshooting

### Common Issues

#### 1. API Key Errors
```python
# Error: Missing API keys
# Solution: Check environment variables
import os
print("OpenAI Key:", os.getenv("OPENAI_API_KEY")[:10] + "..." if os.getenv("OPENAI_API_KEY") else "NOT SET")
print("Search Key:", os.getenv("SERPAPI_API_KEY")[:10] + "..." if os.getenv("SERPAPI_API_KEY") else "NOT SET")
```

#### 2. Model Access Issues
```python
# Error: o1 model access denied
# Solution: Ensure tier-3 OpenAI access or use alternative models
model = LiteLLMModel(model_id="gpt-4o-mini")  # Alternative
```

#### 3. Browser Timeout Issues
```python
# Error: Request timeouts
# Solution: Increase timeout or disable VPN
BROWSER_CONFIG["request_kwargs"]["timeout"] = 600  # 10 minutes
```

#### 4. File Processing Errors
```python
# Error: Unsupported file format
# Solution: Check supported formats and file integrity
try:
    result = inspector.forward(file_path, question)
except UnsupportedFormatException as e:
    print(f"Unsupported format: {e}")
except FileConversionException as e:
    print(f"Conversion error: {e}")
```

#### 5. Memory Issues
```python
# Error: Out of memory with large documents
# Solution: Reduce text_limit
inspector = TextInspectorTool(model, text_limit=50000)  # Reduced from 100000
```

### Debugging Tips

#### 1. Enable Verbose Logging
```python
agent = CodeAgent(
    model=model,
    tools=tools,
    verbosity_level=2  # Enable detailed logging
)
```

#### 2. Check Agent Memory
```python
# After agent execution
memory = agent.write_memory_to_messages()
for step in memory:
    print(f"Step: {step}")
```

#### 3. Monitor Token Usage
```python
# Check token consumption
token_counts = agent.monitor.get_total_token_counts()
print(f"Input tokens: {token_counts['input']}")
print(f"Output tokens: {token_counts['output']}")
```

#### 4. Test Individual Components
```python
# Test browser independently
browser = SimpleTextBrowser(**BROWSER_CONFIG)
content = browser.visit_page("https://example.com")
print(content)

# Test document processing
inspector = TextInspectorTool(model, 100000)
result = inspector.forward("test_document.pdf")
print(result)
```

### Performance Optimization

#### 1. Concurrent Processing
```python
from concurrent.futures import ThreadPoolExecutor

def process_multiple_queries(queries, max_workers=4):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(agent.run, query) for query in queries]
        results = [f.result() for f in futures]
    return results
```

#### 2. Caching Strategy
```python
# Implement result caching for repeated queries
import hashlib
import pickle
import os

def cached_agent_run(agent, query, cache_dir="cache"):
    query_hash = hashlib.md5(query.encode()).hexdigest()
    cache_file = os.path.join(cache_dir, f"{query_hash}.pkl")
    
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    
    result = agent.run(query)
    
    os.makedirs(cache_dir, exist_ok=True)
    with open(cache_file, 'wb') as f:
        pickle.dump(result, f)
    
    return result
```

#### 3. Resource Management
```python
# Clean up downloads periodically
import glob
import time

def cleanup_downloads(folder="downloads_folder", max_age_hours=24):
    cutoff_time = time.time() - (max_age_hours * 3600)
    for file_path in glob.glob(f"{folder}/*"):
        if os.path.getctime(file_path) < cutoff_time:
            os.remove(file_path)
```

### Integration Best Practices

#### 1. Error Handling
```python
def robust_research_agent(query, max_retries=3):
    for attempt in range(max_retries):
        try:
            agent = create_research_agent()
            return agent.run(query)
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

#### 2. Resource Monitoring
```python
import psutil

def monitor_system_resources():
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    print(f"Memory usage: {memory.percent}%")
    print(f"Disk usage: {disk.percent}%")
    
    if memory.percent > 80:
        print("Warning: High memory usage")
```

#### 3. Configuration Management
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class ODRConfig:
    model_id: str = "o1"
    api_base: Optional[str] = None
    api_key: Optional[str] = None
    manager_type: str = "CodeAgent"
    search_type: str = "ToolCallingAgent"
    max_steps: int = 12
    search_max_steps: int = 20
    viewport_size: int = 1024 * 5
    timeout: int = 300
    text_limit: int = 100000
    
    @classmethod
    def from_env(cls):
        return cls(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_id=os.getenv("ODR_MODEL_ID", "o1")
        )

# Usage
config = ODRConfig.from_env()
agent = create_research_agent(
    model_id=config.model_id,
    manager_type=config.manager_type
)
```

This comprehensive guide provides everything needed to understand, integrate, and effectively use the Open Deep Research system. The modular architecture allows for flexible customization while maintaining the powerful multi-agent research capabilities that achieve state-of-the-art performance on the GAIA benchmark.